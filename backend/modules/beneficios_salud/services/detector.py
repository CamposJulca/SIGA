"""
Detector de proveedor a partir del nombre de archivo y/o columnas del Excel.
"""


def detectar_proveedor(nombre_archivo: str, columnas: list = None) -> str:
    """
    Detecta el proveedor del archivo Excel.

    Orden de prioridad:
    1. Nombre del archivo (case insensitive).
    2. Columnas del DataFrame (fallback).

    Retorna: 'axa', 'colsanitas' o 'desconocido'.
    """
    nombre_upper = nombre_archivo.upper()

    # Detección por nombre de archivo
    if 'AXACOLPATRIA' in nombre_upper or 'AXA' in nombre_upper:
        return 'axa'
    if 'COLSANITAS' in nombre_upper:
        return 'colsanitas'

    # Fallback por columnas
    if columnas:
        columnas_str = [str(c).strip() for c in columnas]

        axa_markers = {'SUB CTO', 'NUMID'}
        if axa_markers.issubset(set(columnas_str)):
            return 'axa'

        if 'Número de Familia' in columnas_str:
            return 'colsanitas'

    return 'desconocido'
