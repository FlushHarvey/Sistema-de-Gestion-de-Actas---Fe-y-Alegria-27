import sys
import os
from pathlib import Path

def get_base_path() -> Path:
    """
    Obtiene la ruta base del ejecutable, manejando el caso de PyInstaller.
    """
    if getattr(sys, 'frozen', False):
        # Si se ejecuta como bundle de PyInstaller
        return Path(sys._MEIPASS)
    # Si se ejecuta como script normal, la raíz del proyecto
    return Path(os.path.abspath("."))

def get_resource_path(relative_path: str) -> Path:
    """
    Obtiene la ruta absoluta a un recurso, compatible con PyInstaller.
    En modo desarrollo, prioriza la carpeta 'backend/' si existe.
    """
    base = get_base_path()
    
    # Si estamos congelados (exe), el recurso está en la raíz del bundle
    if getattr(sys, 'frozen', False):
        return base / relative_path
    
    # En desarrollo, priorizar backend/relative_path si existe
    dev_path = base / "backend" / relative_path
    if dev_path.exists():
        return dev_path
        
    return base / relative_path
