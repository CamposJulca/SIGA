"""
Lector de archivos Excel para AXA Colpatria y Colsanitas.
Detecta automáticamente la fila de encabezados y extrae metadatos.
"""
import pandas as pd


def _extraer_metadatos_filas(df_raw: pd.DataFrame, header_row: int) -> dict:
    """
    Intenta extraer numero_contrato y periodo_facturacion de las filas
    anteriores a la fila de encabezados.
    """
    metadatos = {
        'numero_contrato': '',
        'periodo_facturacion': '',
    }
    try:
        for i in range(min(header_row, df_raw.shape[0])):
            row_values = [str(v).strip() for v in df_raw.iloc[i].values if pd.notna(v) and str(v).strip()]
            row_str = ' '.join(row_values).upper()

            if not metadatos['numero_contrato']:
                for keyword in ('CONTRATO', 'NRO CONTRATO', 'NÚMERO DE CONTRATO', 'NO. CONTRATO'):
                    if keyword in row_str:
                        # Intenta tomar el valor siguiente a la keyword
                        for j, v in enumerate(df_raw.iloc[i].values):
                            if pd.notna(v) and keyword in str(v).upper():
                                # El valor está en la misma celda o en la siguiente
                                parts = str(v).split(':')
                                if len(parts) > 1 and parts[1].strip():
                                    metadatos['numero_contrato'] = parts[1].strip()
                                elif j + 1 < len(df_raw.iloc[i].values):
                                    next_val = df_raw.iloc[i].values[j + 1]
                                    if pd.notna(next_val) and str(next_val).strip():
                                        metadatos['numero_contrato'] = str(next_val).strip()
                                break
                        break

            if not metadatos['periodo_facturacion']:
                for keyword in ('PERIODO', 'MES', 'FACTURACION', 'FACTURACIÓN', 'VIGENCIA'):
                    if keyword in row_str:
                        for j, v in enumerate(df_raw.iloc[i].values):
                            if pd.notna(v) and keyword in str(v).upper():
                                parts = str(v).split(':')
                                if len(parts) > 1 and parts[1].strip():
                                    metadatos['periodo_facturacion'] = parts[1].strip()
                                elif j + 1 < len(df_raw.iloc[i].values):
                                    next_val = df_raw.iloc[i].values[j + 1]
                                    if pd.notna(next_val) and str(next_val).strip():
                                        metadatos['periodo_facturacion'] = str(next_val).strip()
                                break
                        break
    except Exception:
        pass

    return metadatos


def leer_excel(ruta_archivo: str, proveedor: str) -> tuple:
    """
    Lee un archivo Excel según el proveedor y retorna (DataFrame, metadatos_dict).

    - proveedor='axa': usa openpyxl, busca encabezados buscando 'NUMID' o 'SUB CTO' en filas 0-15.
    - proveedor='colsanitas': usa xlrd, busca encabezados con 'Número de Documento' o 'Apellidos' en filas 0-20.

    Retorna:
        df (pd.DataFrame): datos con los encabezados correctos.
        metadatos (dict): {'numero_contrato': str, 'periodo_facturacion': str}
    """
    if proveedor == 'axa':
        return _leer_axa(ruta_archivo)
    elif proveedor == 'colsanitas':
        return _leer_colsanitas(ruta_archivo)
    else:
        # Intento genérico con openpyxl
        df = pd.read_excel(ruta_archivo, engine='openpyxl', header=0)
        return df, {'numero_contrato': '', 'periodo_facturacion': ''}


def _leer_axa(ruta_archivo: str) -> tuple:
    """Lee un archivo Excel de AXA Colpatria."""
    # Leer sin encabezado para inspeccionar filas
    df_raw = pd.read_excel(ruta_archivo, engine='openpyxl', header=None)

    header_row = None
    for i in range(min(16, len(df_raw))):
        row_values = [str(v).strip().upper() for v in df_raw.iloc[i].values if pd.notna(v)]
        if 'NUMID' in row_values or 'SUB CTO' in row_values:
            header_row = i
            break

    metadatos = _extraer_metadatos_filas(df_raw, header_row if header_row is not None else 0)

    if header_row is None:
        # Asumir primera fila como encabezado
        header_row = 0

    df = pd.read_excel(ruta_archivo, engine='openpyxl', header=header_row)
    # Limpiar nombre de columnas
    df.columns = [str(c).strip() for c in df.columns]

    return df, metadatos


def _leer_colsanitas(ruta_archivo: str) -> tuple:
    """Lee un archivo Excel de Colsanitas."""
    # Intentar con xlrd primero (xls), luego openpyxl (xlsx)
    engine = None
    if str(ruta_archivo).lower().endswith('.xls'):
        engine = 'xlrd'
    else:
        engine = 'openpyxl'

    df_raw = pd.read_excel(ruta_archivo, engine=engine, header=None)

    header_row = None
    for i in range(min(21, len(df_raw))):
        row_values = [str(v).strip() for v in df_raw.iloc[i].values if pd.notna(v)]
        row_upper = [v.upper() for v in row_values]
        if 'NÚMERO DE DOCUMENTO' in row_upper or 'NUMERO DE DOCUMENTO' in row_upper or 'APELLIDOS' in row_upper:
            header_row = i
            break

    metadatos = _extraer_metadatos_filas(df_raw, header_row if header_row is not None else 0)

    if header_row is None:
        header_row = 0

    df = pd.read_excel(ruta_archivo, engine=engine, header=header_row)
    df.columns = [str(c).strip() for c in df.columns]

    return df, metadatos
