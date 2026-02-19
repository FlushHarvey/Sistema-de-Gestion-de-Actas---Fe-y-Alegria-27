import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from parser import parsear_acta, ParsingError
from unittest.mock import MagicMock
import re

# Mocking extracting_datos_pdf since we don't have the actual PDF files
# We will mock the return value of extrae_datos_pdf to simulate the text content that would be extracted

def mock_extraer_datos_pdf(pdf_file):
    # This function will return the text based on the "filename" passed in the mock object
    # We'll attach the test case text to the mock object for convenience
    return pdf_file.text_content, pdf_file.words

class MockPdfFile:
    def __init__(self, text_content, words=[]):
        self.text_content = text_content
        self.words = words
        self.seek = MagicMock()

def test_parsing(case_name, text_content, expected_section, expected_ie_name, words=[]):
    print(f"Testing Case: {case_name}")
    
    # Patch the function in parser module
    import parser
    original_func = parser.extraer_datos_pdf
    parser.extraer_datos_pdf = mock_extraer_datos_pdf
    
    mock_file = MockPdfFile(text_content, words)
    
    try:
        metadata = parsear_acta(mock_file, "test_file.pdf")
        
        print(f"  Result Section: '{metadata.grado_seccion}'")
        print(f"  Result IE Name: '{metadata.nombre_ie}'")
        
        # Check Section
        if expected_section and not metadata.grado_seccion.endswith(f" {expected_section}"):
            print(f"  [FAIL] Section mismatch. Expected end with '{expected_section}', got '{metadata.grado_seccion}'")
        elif expected_section:
             print(f"  [PASS] Section matches '{expected_section}'")

        # Check IE Name
        if expected_ie_name and metadata.nombre_ie != expected_ie_name:
             print(f"  [FAIL] IE Name mismatch. Expected '{expected_ie_name}', got '{metadata.nombre_ie}'")
        elif expected_ie_name:
             print(f"  [PASS] IE Name matches '{expected_ie_name}'")

    except ParsingError as e:
        print(f"  [ERROR] Parsing failed: {e}")
    except Exception as e:
        print(f"  [ERROR] Unexpected error: {e}")
    finally:
        # Restore original function
        parser.extraer_datos_pdf = original_func
    print("-" * 20)

# Case 1: UNICA Section
text_case_1 = """
MINISTERIO DE EDUCACION
ACTA CONSOLIDADA DE EVALUACION
Datos de la Institución Educativa o Programa Educativo
Número y/o Nombre 71009
Código Modular - Anexo 1154814 - 0 Forma Esc
Resolución de Creación N° R.D.N° 2020 Característica PM
Modalidad EBR Grado 1 Turno M
Gestión P Sección(8) UNICA
Nivel PRIMARIA
"""
# Mock words for geometric search if needed (simplified)
words_case_1 = [
    {'text': 'Sección(8)', 'top': 100, 'bottom': 110, 'x0': 50, 'x1': 100},
    {'text': 'UNICA', 'top': 100, 'bottom': 110, 'x0': 120, 'x1': 160} # Right of 'Sección(8)'
]

test_parsing("UNICA Section", text_case_1, "U", "71009", words_case_1)

# Case 2: Numeric Institution Name
text_case_2 = """
MINISTERIO DE EDUCACION
ACTA CONSOLIDADA DE EVALUACION
Datos de la Institución Educativa o Programa Educativo
Número y/o Nombre 71009
Código Modular - Anexo 1154814 - 0
Nivel PRIMARIA
"""
# No words needed if fallback text logic works, but let's provide empty to force text logic or minimal
test_parsing("Numeric IE Name", text_case_2, None, "71009")

# Case 3: "ÚNICA" with accent
text_case_3 = """
Modalidad EBR Grado 5
Sección(8) ÚNICA
Nivel SECUNDARIA
"""
words_case_3 = [
    {'text': 'Sección(8)', 'top': 100, 'bottom': 110, 'x0': 50, 'x1': 100},
    {'text': 'ÚNICA', 'top': 100, 'bottom': 110, 'x0': 120, 'x1': 160}
]
test_parsing("ÚNICA (accent) Section", text_case_3, "U", None, words_case_3)

# Case 4: Standard Case
text_case_4 = """
Datos de la Institución Educativa o Programa Educativo
Número y/o Nombre FE Y ALEGRIA 27 SANTA LUCIA
Sección B
Nivel SECUNDARIA
"""
words_case_4 = [
    {'text': 'Sección', 'top': 100, 'bottom': 110, 'x0': 50, 'x1': 90},
    {'text': 'B', 'top': 100, 'bottom': 110, 'x0': 110, 'x1': 120}
]
test_parsing("Standard Case", text_case_4, "B", "27 SANTA LUCIA FE Y ALEGRIA", words_case_4)

