import os

# ==============================
# CONFIGURACIÓN
# ==============================
CODIGO_MODULAR = "0227900"
NOMBRE_IE = "27 SANTA LUCIA FE Y ALEGRIA"
RUTA_BASE = "ACTAS"  # Carpeta raíz en Antigravity
DRY_RUN = False      # True = solo simula | False = renombra realmente
# ==============================


def nombre_ya_correcto(nombre_archivo, anio):
    return nombre_archivo.startswith(f"{anio} - {CODIGO_MODULAR} - {NOMBRE_IE} - ")


def procesar_archivo(ruta_archivo, anio):
    directorio, archivo = os.path.split(ruta_archivo)

    if not archivo.lower().endswith(".pdf"):
        return

    nombre_sin_ext = archivo[:-4].strip()

    if nombre_ya_correcto(nombre_sin_ext, anio):
        print(f"⏭ Ya correcto: {archivo}")
        return

    nuevo_nombre = f"{anio} - {CODIGO_MODULAR} - {NOMBRE_IE} - {nombre_sin_ext}.pdf"
    ruta_nueva = os.path.join(directorio, nuevo_nombre)

    if os.path.exists(ruta_nueva):
        print(f"⚠ Ya existe: {nuevo_nombre} (omitido)")
        return

    if DRY_RUN:
        print(f"[SIMULACIÓN] {archivo} → {nuevo_nombre}")
    else:
        os.rename(ruta_archivo, ruta_nueva)
        print(f"✔ Renombrado: {archivo} → {nuevo_nombre}")


def main():
    if not os.path.exists(RUTA_BASE):
        print("❌ La carpeta ACTAS no existe.")
        return

    for anio in os.listdir(RUTA_BASE):
        ruta_anio = os.path.join(RUTA_BASE, anio)

        if not (os.path.isdir(ruta_anio) and anio.isdigit()):
            continue

        for root, _, archivos in os.walk(ruta_anio):
            for archivo in archivos:
                ruta_archivo = os.path.join(root, archivo)
                try:
                    procesar_archivo(ruta_archivo, anio)
                except Exception as e:
                    print(f"❌ Error procesando {archivo}: {e}")

    print("Proceso finalizado.")


if __name__ == "__main__":
    main()
