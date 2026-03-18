"""
Adaptador para archivos Excel de AXA Colpatria.
Mapea columnas AXA al modelo unificado de BeneficioSalud.
"""
import pandas as pd


# Mapeo: columna AXA -> campo del modelo unificado
AXA_COLUMN_MAP = {
    'SUB CTO': 'sub_contrato',
    'NUMID': 'cedula_titular',     # cédula del titular del contrato
    'NUMERO ID.BEN': 'cedula',     # cédula real del afiliado (titular o beneficiario)
    'NOMBRE': 'nombre',
    'PARENTESCO': 'parentesco',
    'SUBTOTAL': 'valor_base',
    'IVA': 'iva',
    'TOTAL': 'valor_total',
}


def adaptar_axa(df: pd.DataFrame, metadatos: dict) -> pd.DataFrame:
    """
    Transforma un DataFrame de AXA Colpatria al esquema unificado del modelo.

    Args:
        df: DataFrame leído del Excel de AXA.
        metadatos: dict con 'numero_contrato' y 'periodo_facturacion'.

    Returns:
        DataFrame con columnas del modelo unificado.
    """
    # Normalizar nombres de columnas (strip)
    df = df.copy()
    df.columns = [str(c).strip() for c in df.columns]

    unified = pd.DataFrame()

    for src_col, dst_col in AXA_COLUMN_MAP.items():
        if src_col in df.columns:
            unified[dst_col] = df[src_col]
        else:
            # Intentar búsqueda case-insensitive
            match = [c for c in df.columns if c.upper() == src_col.upper()]
            if match:
                unified[dst_col] = df[match[0]]
            else:
                unified[dst_col] = None

    # AXA no tiene descuento separado
    unified['descuento'] = 0

    # Proveedor fijo
    unified['proveedor'] = 'axa'

    # Número de contrato desde metadatos
    unified['numero_contrato'] = metadatos.get('numero_contrato', '')

    # Campos opcionales que AXA puede no tener
    for col in ('tipo_id', 'tipo_plan', 'fecha_nacimiento'):
        if col not in unified.columns:
            unified[col] = ''

    # cedula_titular: normalizar a string si viene del mapeo, o vacío si no existe
    if 'cedula_titular' in unified.columns:
        unified['cedula_titular'] = unified['cedula_titular'].astype(str).str.strip()
        unified['cedula_titular'] = unified['cedula_titular'].replace('nan', '')
    else:
        unified['cedula_titular'] = ''

    # Convertir columnas numéricas
    for col in ('valor_base', 'iva', 'valor_total', 'descuento'):
        unified[col] = pd.to_numeric(unified[col], errors='coerce').fillna(0)

    # Convertir sub_contrato a string
    if 'sub_contrato' in unified.columns:
        unified['sub_contrato'] = unified['sub_contrato'].astype(str).str.strip()
        unified['sub_contrato'] = unified['sub_contrato'].replace('nan', '')

    # Convertir cedula a string
    if 'cedula' in unified.columns:
        unified['cedula'] = unified['cedula'].astype(str).str.strip()
        unified['cedula'] = unified['cedula'].replace('nan', '')

    # Convertir nombre a string
    if 'nombre' in unified.columns:
        unified['nombre'] = unified['nombre'].astype(str).str.strip()
        unified['nombre'] = unified['nombre'].replace('nan', '')

    # Filtrar filas donde cedula está vacía o es NaN
    unified = unified[unified['cedula'].notna() & (unified['cedula'] != '') & (unified['cedula'] != 'nan')]

    unified = unified.reset_index(drop=True)
    return unified
