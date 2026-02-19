import os
import sys
import webbrowser
import threading
from pathlib import Path
from typing import List
from fastapi import FastAPI, UploadFile, File, HTTPException, status
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from models import BatchProcessResponse
from service import acta_service
from parser import ParsingError
from utils import get_resource_path

app = FastAPI(
    title="Sistema de Gestión de Actas",
    description="Sistema Institucional Portátil de Gestión de Actas",
    version="1.1.0"
)

# Configurar CORS (necesario para desarrollo local)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Manejador de errores global para ParsingError
@app.exception_handler(ParsingError)
async def parsing_error_handler(request, exc: ParsingError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": exc.message}
    )

@app.get("/health", tags=["General"])
async def health():
    return {"status": "ok", "message": "Sistema funcionando"}

@app.post("/procesar-carpeta", response_model=BatchProcessResponse, tags=["Procesamiento"])
async def procesar_carpeta(files: List[UploadFile] = File(...)):
    """
    Recibe múltiples archivos PDF (subidos vía webkitdirectory o drag & drop).
    """
    if not files:
        raise HTTPException(status_code=400, detail="No se enviaron archivos")
    
    # Validar que todos sean PDF
    for file in files:
        if not file.filename.lower().endswith(".pdf"):
            continue # Opcional: ignorar no-PDFs o lanzar error
            
    # Limpiar carpeta antes de procesar un nuevo lote (opcional según flujo)
    acta_service.limpiar_procesados()
    
    return await acta_service.procesar_lote_archivos(files)

@app.get("/descargar", tags=["Procesamiento"])
async def descargar_zip():
    """
    Genera un ZIP con la carpeta ActasProcesadas y lo descarga.
    """
    zip_path = acta_service.generar_zip()
    return FileResponse(
        path=zip_path,
        filename="Actas_Procesadas_Organizadas.zip",
        media_type="application/zip"
    )

# Servir archivos estáticos (Frontend)
# Obtener la ruta de la carpeta 'static' relativa a este archivo (backend/main.py)
current_dir = Path(__file__).parent.resolve()
static_path = current_dir / "static"

# Fallback para PyInstaller (recursos están en la raíz del bundle)
if getattr(sys, 'frozen', False):
    static_path = Path(sys._MEIPASS) / "static"

print(f"[*] Cargando archivos estáticos desde: {static_path.resolve()}")

if not static_path.exists():
    print(f"[!] ADVERTENCIA: La carpeta de archivos estáticos no existe en {static_path}")

app.mount("/", StaticFiles(directory=str(static_path), html=True), name="static")

def open_browser():
    """Abre el navegador automáticamente después de que el servidor cargue."""
    webbrowser.open("http://127.0.0.1:8000")

if __name__ == "__main__":
    import uvicorn
    
    # Iniciar el navegador en un hilo separado
    if os.environ.get("RELOAD") != "true":
        threading.Timer(1.5, open_browser).start()
    
    # Configuración de logs para PyInstaller (evita el error de isatty)
    log_config = uvicorn.config.LOGGING_CONFIG
    if getattr(sys, 'frozen', False):
        # Si estamos en modo ejecutable (sin consola), anulamos los handlers de consola
        log_config = None 
    
    # Usar el objeto app directamente
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=False, log_config=log_config)
