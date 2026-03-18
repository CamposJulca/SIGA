"""
Validador de registros de beneficios de salud.
Realiza validaciones de integridad antes de la inserción en BD.
"""
import pandas as pd


def validar_registros(df: pd.DataFrame, archivo_id: int) -> tuple:
    """
    Valida los registros del DataFrame unificado.

    Validaciones:
    1. Cédula no nula y no vacía (tipo_error: CEDULA_INVALIDA).
    2. valor_base, iva, valor_total son numéricos y no negativos (tipo_error: VALOR_INVALIDO).
    3. Verificación aritmética: abs(valor_total - (valor_base - descuento + iva)) <= 1.0
       Si falla → estado_validacion='ADVERTENCIA' pero el registro pasa.
    4. Sin cédulas duplicadas en el mismo df (tipo_error: CEDULA_DUPLICADA).
       Marca TODAS las ocurrencias duplicadas como error.

    Args:
        df: DataFrame unificado (output de adapter).
        archivo_id: ID del ArchivoRecibido al que pertenecen los registros.

    Returns:
        (registros_ok, errores)
        - registros_ok: lista de dicts listos para BeneficioSalud.bulk_create
        - errores: lista de dicts listos para ErrorProcesamiento.bulk_create
    """
    registros_ok = []
    errores = []

    # Detectar duplicados por (cedula, sub_contrato) — la misma cédula en
    # familias distintas es un caso válido (titular con cobertura en varios grupos).
    clave_duplicada = (
        df['cedula'].astype(str).str.strip()
        + '_'
        + df['sub_contrato'].astype(str).str.strip()
    )
    duplicados_mask = clave_duplicada[clave_duplicada != '_'].duplicated(keep=False)
    indices_duplicados = set(df.index[duplicados_mask]) if len(duplicados_mask) > 0 else set()

    for idx, row in df.iterrows():
        fila_origen = idx + 1  # 1-based para facilitar localización en Excel
        cedula = str(row.get('cedula', '')).strip()
        es_valido = True

        # --- Validación 1: Cédula ---
        if not cedula or cedula == 'nan':
            errores.append({
                'archivo_id': archivo_id,
                'fila_origen': fila_origen,
                'tipo_error': 'CEDULA_INVALIDA',
                'descripcion': f'La cédula está vacía o no es válida en la fila {fila_origen}.',
                'valor_encontrado': cedula,
            })
            es_valido = False

        if not es_valido:
            continue

        # --- Validación 4: Cédulas duplicadas (advertencia, no rechazo) ---
        # Misma cédula en la misma familia puede indicar cobertura en múltiples
        # planes del mismo contrato — caso válido en Colsanitas. Se almacena el
        # registro con estado ADVERTENCIA y se registra el aviso en ErrorProcesamiento.
        advertencia_duplicado = es_valido and idx in indices_duplicados

        # --- Validación 2: Valores numéricos ---
        # valor_base, iva y valor_total deben ser >= 0.
        # descuento puede ser negativo (Colsanitas lo representa como valor negativo).
        CAMPOS_SOLO_POSITIVOS = {'valor_base', 'iva', 'valor_total'}
        campos_numericos = {
            'valor_base': row.get('valor_base', 0),
            'iva': row.get('iva', 0),
            'valor_total': row.get('valor_total', 0),
            'descuento': row.get('descuento', 0),
        }

        # Convertir todos los campos numéricos primero (sin validar signo aún)
        valor_invalido = False
        for campo, valor in campos_numericos.items():
            try:
                campos_numericos[campo] = float(valor)
            except (TypeError, ValueError) as e:
                errores.append({
                    'archivo_id': archivo_id,
                    'fila_origen': fila_origen,
                    'tipo_error': 'VALOR_INVALIDO',
                    'descripcion': f'El campo {campo} no es numérico en fila {fila_origen}: {e}',
                    'valor_encontrado': str(valor),
                })
                valor_invalido = True
                break

        if valor_invalido:
            continue

        # Detectar fila de ajuste contable: Cuota=0 y Total<0
        # Colsanitas usa este patrón para novedades de corrección (anulación parcial).
        # Se almacena como ADVERTENCIA en lugar de rechazarse.
        es_fila_ajuste = (
            campos_numericos['valor_base'] == 0
            and campos_numericos['valor_total'] < 0
        )

        if not es_fila_ajuste:
            for campo, v in campos_numericos.items():
                if campo in CAMPOS_SOLO_POSITIVOS and v < 0:
                    errores.append({
                        'archivo_id': archivo_id,
                        'fila_origen': fila_origen,
                        'tipo_error': 'VALOR_INVALIDO',
                        'descripcion': (
                            f'El campo {campo} tiene valor negativo en fila {fila_origen}: {v}'
                        ),
                        'valor_encontrado': str(v),
                    })
                    valor_invalido = True
                    break

        if valor_invalido:
            continue

        # --- Validación 3: Verificación aritmética (tolerancia 1 peso) ---
        valor_base  = campos_numericos['valor_base']
        descuento   = campos_numericos['descuento']
        iva         = campos_numericos['iva']
        valor_total = campos_numericos['valor_total']

        estado_validacion = 'OK'
        diferencia = abs(valor_total - (valor_base - descuento + iva))
        if diferencia > 1.0 or advertencia_duplicado or es_fila_ajuste:
            estado_validacion = 'ADVERTENCIA'

        # --- Construir registro ---
        registro = {
            'archivo_id': archivo_id,
            'cedula': cedula,
            'tipo_id': str(row.get('tipo_id', '')).strip() if pd.notna(row.get('tipo_id')) else '',
            'nombre': str(row.get('nombre', '')).strip(),
            'parentesco': str(row.get('parentesco', '')).strip() if pd.notna(row.get('parentesco')) else '',
            'sub_contrato': str(row.get('sub_contrato', '')).strip() if pd.notna(row.get('sub_contrato')) else '',
            'cedula_titular': str(row.get('cedula_titular', '')).strip() if pd.notna(row.get('cedula_titular')) else '',
            'proveedor': str(row.get('proveedor', '')).strip(),
            'tipo_plan': str(row.get('tipo_plan', '')).strip() if pd.notna(row.get('tipo_plan')) else '',
            'valor_base': round(valor_base, 2),
            'descuento': round(descuento, 2),
            'iva': round(iva, 2),
            'valor_total': round(valor_total, 2),
            'fecha_nacimiento': str(row.get('fecha_nacimiento', '')).strip() if pd.notna(row.get('fecha_nacimiento')) else '',
            'edad': _parse_edad(row.get('edad')),
            'fecha_corte': _parse_fecha(row.get('fecha_corte')),
            'numero_contrato': str(row.get('numero_contrato', '')).strip() if pd.notna(row.get('numero_contrato')) else '',
            'archivo_origen': str(row.get('archivo_origen', '')).strip() if pd.notna(row.get('archivo_origen')) else '',
            'estado_validacion': estado_validacion,
        }

        if advertencia_duplicado:
            errores.append({
                'archivo_id': archivo_id,
                'fila_origen': fila_origen,
                'tipo_error': 'CEDULA_DUPLICADA',
                'descripcion': (
                    f'La cédula {cedula} aparece más de una vez en el archivo '
                    f'(fila {fila_origen}). Registro almacenado con ADVERTENCIA.'
                ),
                'valor_encontrado': cedula,
            })

        registros_ok.append(registro)

    return registros_ok, errores


def _parse_edad(valor) -> int | None:
    """Convierte un valor a entero para la edad, o None si no es válido."""
    if valor is None or (isinstance(valor, float) and pd.isna(valor)):
        return None
    try:
        return int(float(valor))
    except (TypeError, ValueError):
        return None


def _parse_fecha(valor):
    """Convierte un valor a date, o None si no es válido."""
    if valor is None or (isinstance(valor, float) and pd.isna(valor)):
        return None
    if hasattr(valor, 'date'):
        return valor.date()
    try:
        return pd.to_datetime(valor).date()
    except Exception:
        return None
