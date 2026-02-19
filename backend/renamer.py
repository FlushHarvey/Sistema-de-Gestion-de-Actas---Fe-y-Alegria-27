import re
from pathlib import Path
from models import ActaMetadata

def limpiar_nombre(texto: str) -> str:
    """Elimina caracteres no permitidos en nombres de archivos de Windows."""
    return re.sub(r'[\\/*?:"<>|]', '', texto).strip()

def obtener_nombre_oficial(metadata: ActaMetadata) -> str:
    """
    Construye el nombre oficial del archivo según la nomenclatura de Minka Data:
    Año - Código Modular - NombreIE - Grado Sección
    """
    # Minka Data requiere UN ESPACIO entre el dato y el guion
    rec_suffix = " REC" if metadata.es_recuperacion else ""
    nombre_base = f"{metadata.anio} - {metadata.codigo_modular} - {metadata.nombre_ie} - {metadata.grado_seccion}{rec_suffix}"
    
    # Limpiar y asegurar el formato
    nombre_base = re.sub(r'\s+', ' ', nombre_base).strip()
    
    # El límite de ruta en Windows es 260. Limitamos el nombre a 180 para seguridad
    if len(nombre_base) > 180:
        nombre_base = nombre_base[:177] + "..."
        
    return limpiar_nombre(nombre_base + ".pdf")

def obtener_ruta_organizacion(metadata: ActaMetadata, base_path: Path) -> Path:
    """
    Determina la ruta de destino basada en la estructura:
    /base_path/Año/Nivel/NombreOficial.pdf
    """
    # Estructura: /ActasProcesadas/Año/Nivel/
    nivel_dir = base_path / metadata.anio / metadata.nivel
    nivel_dir.mkdir(parents=True, exist_ok=True)
    
    nombre_final = obtener_nombre_oficial(metadata)
    return nivel_dir / nombre_final
