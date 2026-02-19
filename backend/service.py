import os
import io
import shutil
import zipfile
import uuid
from pathlib import Path
from typing import List
from fastapi import UploadFile
from parser import parsear_acta, ParsingError
from models import ActaMetadata, ProcessResult, BatchProcessResponse
from renamer import obtener_ruta_organizacion, obtener_nombre_oficial

STORAGE_ROOT = Path("ActasProcesadas")

class ActaService:
    def __init__(self):
        # Asegurar que el directorio raíz existe
        STORAGE_ROOT.mkdir(exist_ok=True)

    async def procesar_lote_archivos(self, files: List[UploadFile]) -> BatchProcessResponse:
        """
        Procesa múltiples archivos UploadFile secuencialmente.
        """
        # Limpiar procesamiento anterior para evitar mezclar datos si es necesario
        # En una app multiusuario esto requeriría sesiones, para local/portátil
        # usaremos una carpeta temporal por ejecución si fuera necesario, 
        # pero aquí seguiremos el requisito de /ActasProcesadas/
        
        resultados = []
        exitosos = 0
        fallidos = 0

        for file in files:
            try:
                # Leer el contenido del archivo en memoria para parsing
                content = await file.read()
                pdf_buffer = io.BytesIO(content)
                
                # 1. Parsear metadata
                metadata = parsear_acta(pdf_buffer, file.filename)
                
                # 2. Obtener nombre oficial
                nombre_oficial = obtener_nombre_oficial(metadata)
                metadata.nuevo_nombre = nombre_oficial
                print(f"[*] Archivo: {file.filename}")
                print(f"[*] Metadata.ie: {metadata.nombre_ie}")
                print(f"[*] Nombre oficial: {nombre_oficial} (len: {len(nombre_oficial)})")
                
                # 3. Determinar ruta de destino y organizar
                ruta_final = obtener_ruta_organizacion(metadata, STORAGE_ROOT)
                print(f"[*] Ruta final: {ruta_final}")
                
                # 4. Guardar archivo
                with open(ruta_final, "wb") as f:
                    f.write(content)
                
                resultados.append(ProcessResult(
                    archivo=file.filename,
                    estado="exito",
                    metadata=metadata,
                    nuevo_nombre=nombre_oficial,
                    ruta_final=str(ruta_final)
                ))
                exitosos += 1

            except ParsingError as e:
                resultados.append(ProcessResult(
                    archivo=file.filename,
                    estado="error",
                    mensaje=str(e)
                ))
                fallidos += 1
            except Exception as e:
                resultados.append(ProcessResult(
                    archivo=file.filename,
                    estado="error",
                    mensaje=f"Error inesperado: {str(e)}"
                ))
                fallidos += 1
            finally:
                # El puntero ya se leyó, no es necesario seek(0) aquí si no se vuelve a usar el mismo UploadFile
                pass

        return BatchProcessResponse(
            resultados=resultados,
            total_procesados=len(files),
            exitosos=exitosos,
            fallidos=fallidos
        )

    def generar_zip(self) -> str:
        """
        Genera un archivo ZIP con toda la estructura de ActasProcesadas.
        Retorna la ruta al archivo ZIP generado.
        """
        zip_filename = f"Actas_Procesadas_{uuid.uuid4().hex[:8]}.zip"
        zip_path = Path(zip_filename)
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(STORAGE_ROOT):
                for file in files:
                    file_path = Path(root) / file
                    # El nombre en el zip debe ser relativo a STORAGE_ROOT
                    arcname = file_path.relative_to(STORAGE_ROOT)
                    zipf.write(file_path, arcname)
        
        return str(zip_path)

    def limpiar_procesados(self):
        """Limpia la carpeta de procesados."""
        if STORAGE_ROOT.exists():
            shutil.rmtree(STORAGE_ROOT)
        STORAGE_ROOT.mkdir(exist_ok=True)

# Instancia singleton del servicio
acta_service = ActaService()
