import sys
import os
sys.path.append(os.path.join(os.getcwd(), 'backend'))
from parser import parsear_acta
from unittest.mock import MagicMock

def mock_extraer_datos_pdf(pdf_file):
    return pdf_file.text_content, pdf_file.words

class MockPdfFile:
    def __init__(self, text_content, words=[]):
        self.text_content = text_content
        self.words = words
        self.seek = MagicMock()

import parser
parser.extraer_datos_pdf = mock_extraer_datos_pdf

def test(name, text, expected_sec, expected_ie, words=[]):
    try:
        m = parsear_acta(MockPdfFile(text, words), "test.pdf")
        sec_ok = m.grado_seccion.endswith(" " + expected_sec) if expected_sec else True
        ie_ok = m.nombre_ie == expected_ie if expected_ie else True
        
        if sec_ok and ie_ok:
            print(f"PASS: {name}")
        else:
            print(f"FAIL: {name} | Sec: {m.grado_seccion} (Exp: {expected_sec}) | IE: {m.nombre_ie} (Exp: {expected_ie})")
    except Exception as e:
        print(f"ERROR: {name} {e}")

# Case 1
t1 = """MINISTERIO DE EDUCACION\nDatos de la Institución Educativa o Programa Educativo\nNúmero y/o Nombre 71009\nCódigo Modular - Anexo 1154814 - 0\nNivel PRIMARIA\nSección(8) UNICA"""
w1 = [{'text': 'Sección(8)', 'top': 100, 'x0': 50, 'x1': 100, 'bottom': 110}, {'text': 'UNICA', 'top': 100, 'x0': 120, 'x1': 160, 'bottom': 110}]
test("UNICA Section", t1, "U", "71009", w1)

# Case 2 - Numeric text only
t2 = """MINISTERIO DE EDUCACION\nNúmero y/o Nombre 71009\nNivel PRIMARIA"""
test("Numeric IE", t2, None, "71009")

# Case 3 - ÚNICA
t3 = """Sección(8) ÚNICA\nNivel SECUNDARIA"""
w3 = [{'text': 'Sección(8)', 'top': 100, 'x0': 50, 'x1': 100, 'bottom': 110}, {'text': 'ÚNICA', 'top': 100, 'x0': 120, 'x1': 160, 'bottom': 110}]
test("ÚNICA Section", t3, "U", None, w3)

# Case 4 - Standard
t4 = """Número y/o Nombre FE Y ALEGRIA 27 SANTA LUCIA\nSección B\nNivel SECUNDARIA"""
w4 = [{'text': 'Sección', 'top': 100, 'x0': 50, 'x1': 90, 'bottom': 110}, {'text': 'B', 'top': 100, 'x0': 110, 'x1': 120, 'bottom': 110}]
test("Standard", t4, "B", "27 SANTA LUCIA FE Y ALEGRIA", w4)

# Case 5 - Distraction 'P' (Gestión P)
t5 = """Gestión P Sección(8) UNICA\nNivel PRIMARIA"""
# Simulate P being geometrically candidate if logic was flawed, or just present
w5 = [
    {'text': 'Gestión', 'top': 100, 'x0': 10, 'x1': 40, 'bottom': 110},
    {'text': 'P', 'top': 100, 'x0': 45, 'x1': 55, 'bottom': 110},
    {'text': 'Sección(8)', 'top': 100, 'x0': 60, 'x1': 110, 'bottom': 110},
    {'text': 'UNICA', 'top': 100, 'x0': 120, 'x1': 160, 'bottom': 110}
]
test("Distraction P", t5, "U", "IE DESCONOCIDA", w5)

# Case 6 - Full Layout Interference
# Row 1: Grado(5) 1 Turno(9) M
# Row 2: Gestión(4) P Sección(8) UNICA
t6 = """Grado(5) 1 Turno(9) M\nGestión(4) P Sección(8) UNICA\nNivel PRIMARIA"""
w6 = [
    # Row 1 (y=50)
    {'text': 'Grado(5)', 'top': 50, 'bottom': 60, 'x0': 100, 'x1': 140},
    {'text': '1', 'top': 50, 'bottom': 60, 'x0': 150, 'x1': 160},
    {'text': 'Turno(9)', 'top': 50, 'bottom': 60, 'x0': 180, 'x1': 220},
    {'text': 'M', 'top': 50, 'bottom': 60, 'x0': 230, 'x1': 240},
    
    # Row 2 (y=65) - Note: Close to Row 1 if tolerance is high
    {'text': 'Gestión(4)', 'top': 65, 'bottom': 75, 'x0': 50, 'x1': 90},
    {'text': 'P', 'top': 65, 'bottom': 75, 'x0': 100, 'x1': 110},
    {'text': 'Sección(8)', 'top': 65, 'bottom': 75, 'x0': 120, 'x1': 170},
    {'text': 'UNICA', 'top': 65, 'bottom': 75, 'x0': 180, 'x1': 220}
]
test("Layout Interference", t6, "U", "IE DESCONOCIDA", w6)

