"""
Adaptador para archivos Excel de Colsanitas.
Mapea columnas Colsanitas al modelo unificado de BeneficioSalud.
"""
import pandas as pd


# Filas de totales/resumen que deben ser excluidas del procesamiento
FILAS_TOTALES_KEYWORDS = [
    'TOTAL FAMILIA',
    'TOTAL CONTRATO',
    'TOTAL GENERAL',
    'SUBTOTAL',
    'GRAN TOTAL',
]


def adaptar_colsanitas(df: pd.DataFrame, metadatos: dict) -> pd.DataFrame:
    """
    Transforma un DataFrame de Colsanitas al esquema unificado del modelo.

    Args:
        df: DataFrame leído del Excel de Colsanitas.
        metadatos: dict con 'numero_contrato' y 'periodo_facturacion'.

    Returns:
        DataFrame con columnas del modelo unificado.
    """
    df = df.copy()
    df.columns = [str(c).strip() for c in df.columns]

    # Filtrar filas de totales/resumen: la primera columna contiene strings como 'TOTAL FAMILIA'
    if len(df.columns) > 0:
        primera_col = df.columns[0]
        mask_totales = df[primera_col].astype(str).str.upper().str.strip().apply(
            lambda v: any(kw in v for kw in FILAS_TOTALES_KEYWORDS)
        )
        df = df[~mask_totales]

    unified = pd.DataFrame()

    # sub_contrato
    unified['sub_contrato'] = _get_col(df, 'Número de Familia', default='').astype(str).str.strip()
    unified['sub_contrato'] = unified['sub_contrato'].replace('nan', '')

    # cedula
    unified['cedula'] = _get_col(df, 'Número de Documento', default='').astype(str).str.strip()
    unified['cedula'] = unified['cedula'].replace('nan', '')

    # nombre: Apellidos + ' ' + Nombres
    apellidos = _get_col(df, 'Apellidos', default='').astype(str).str.strip().replace('nan', '')
    nombres = _get_col(df, 'Nombres', default='').astype(str).str.strip().replace('nan', '')
    unified['nombre'] = (apellidos + ' ' + nombres).str.strip()

    # valores numéricos
    unified['valor_base'] = pd.to_numeric(_get_col(df, 'Cuota', default=0), errors='coerce').fillna(0)
    unified['descuento'] = pd.to_numeric(_get_col(df, 'Descuento Comercial', default=0), errors='coerce').fillna(0)
    unified['iva'] = pd.to_numeric(_get_col(df, 'IVA', default=0), errors='coerce').fillna(0)

    # valor_total: intentar 'Total Us' primero, luego 'Total'
    if _col_exists(df, 'Total Us'):
        unified['valor_total'] = pd.to_numeric(_get_col(df, 'Total Us', default=0), errors='coerce').fillna(0)
    elif _col_exists(df, 'Total'):
        unified['valor_total'] = pd.to_numeric(_get_col(df, 'Total', default=0), errors='coerce').fillna(0)
    else:
        unified['valor_total'] = 0.0

    # Proveedor fijo
    unified['proveedor'] = 'colsanitas'

    # Número de contrato desde metadatos
    unified['numero_contrato'] = metadatos.get('numero_contrato', '')

    # Campos opcionales
    for col in ('tipo_id', 'parentesco', 'cedula_titular', 'tipo_plan', 'fecha_nacimiento'):
        if col not in unified.columns:
            unified[col] = ''

    # Filtrar filas donde cedula es NaN o vacía
    unified = unified[unified['cedula'].notna() & (unified['cedula'] != '') & (unified['cedula'] != 'nan')]

    unified = unified.reset_index(drop=True)
    return unified


# --- Helpers ---

def _col_exists(df: pd.DataFrame, nombre: str) -> bool:
    """Verifica si una columna existe (case insensitive)."""
    for c in df.columns:
        if c.strip().lower() == nombre.strip().lower():
            return True
    return False


def _get_col(df: pd.DataFrame, nombre: str, default=None) -> pd.Series:
    """
    Obtiene una columna por nombre (case insensitive).
    Retorna una Serie con valor default si no existe.
    """
    for c in df.columns:
        if c.strip().lower() == nombre.strip().lower():
            return df[c]
    # No encontrada: retornar serie de defaults
    return pd.Series([default] * len(df), index=df.index)
