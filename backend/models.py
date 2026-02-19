from pydantic import BaseModel
from typing import List, Optional

class ActaMetadata(BaseModel):
    archivo_original: str
    anio: str
    codigo_modular: str
    anexo: str
    nombre_ie: str
    nivel: str
    grado_seccion: str
    es_recuperacion: bool
    nuevo_nombre: Optional[str] = None

class ProcessResult(BaseModel):
    archivo: str
    estado: str  # "exito" | "error"
    mensaje: Optional[str] = None
    metadata: Optional[ActaMetadata] = None
    nuevo_nombre: Optional[str] = None
    ruta_final: Optional[str] = None

class BatchProcessResponse(BaseModel):
    resultados: List[ProcessResult]
    total_procesados: int
    exitosos: int
    fallidos: int
