"""
Servicio de acceso a datos de Medicina Prepagada (prepagada.db).
Contiene la lógica de lectura de la BD externa y el cálculo 80/20.
"""
import sqlite3
from decimal import Decimal

from django.conf import settings

from .eligibility import evaluar_elegibilidad


def _get_connection():
    """Abre y retorna una conexión a prepagada.db."""
    db_path = settings.PREPAGADA_DB_PATH
    try:
        conn = sqlite3.connect(db_path)
        return conn
    except Exception as e:
        raise RuntimeError(
            f"No se pudo conectar a prepagada.db en '{db_path}': {e}"
        )


def get_periodos_disponibles() -> list:
    """Retorna la lista de periodos distintos disponibles en prepagada.db."""
    try:
        conn = _get_connection()
        cur = conn.cursor()
        cur.execute(
            "SELECT DISTINCT periodo FROM facturas_eps "
            "WHERE periodo IS NOT NULL ORDER BY periodo DESC"
        )
        rows = cur.fetchall()
        conn.close()
        return [r[0] for r in rows]
    except RuntimeError:
        raise
    except Exception as e:
        raise RuntimeError(f"Error leyendo periodos de prepagada.db: {e}")


def get_cruce_periodo(periodo: str) -> list:
    """
    Retorna los registros de v_cruce para un periodo dado.
    Cada elemento es un dict con las columnas de la vista.
    """
    conn = _get_connection()
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute(
        """
        SELECT periodo, eps, cedula, nombre_en_factura, nombre_en_kactus,
               num_beneficiarios, total_familia, sub_cto, nro_cont,
               sue_basi, tip_cont, estado, archivo
        FROM v_cruce
        WHERE periodo = ?
        ORDER BY eps, cedula
        """,
        (periodo,),
    )
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows


def calcular_planilla(periodo: str, politica) -> list:
    """
    Calcula la planilla 80/20 para un periodo dado usando la política indicada.

    Para cada registro en v_cruce:
      - empleado elegible → calcula distribución empresa/empleado y límite no gravable.
      - pensionado activo → deja 100% a cargo del pensionado/empleado.
      - cruce no OK → incluye el registro bloqueado, con valores en cero.

    Retorna lista de dicts listos para crear DetalleCalculo.
    """
    rows = get_cruce_periodo(periodo)

    limite_no_grav = (
        Decimal(str(politica.uvt_limite)) * Decimal(str(politica.valor_uvt))
    )

    resultados = []
    for r in rows:
        cedula = str(r['cedula']) if r['cedula'] is not None else ''
        nombre_factura = r['nombre_en_factura'] or ''
        nombre_kactus = r['nombre_en_kactus'] or ''
        eps = r['eps'] or ''
        num_benef = r['num_beneficiarios'] or 0
        sue_basi = Decimal(str(r['sue_basi'])) if r['sue_basi'] is not None else None
        tip_cont = r['tip_cont'] or ''
        estado = r['estado']

        total = Decimal(str(r['total_familia'] or 0))
        elegibilidad = evaluar_elegibilidad(r, politica)

        if elegibilidad.estado_elegibilidad == 'PENSIONADO_100':
            resultados.append({
                'cedula': cedula,
                'nombre_en_factura': nombre_factura,
                'nombre_en_kactus': nombre_kactus,
                'eps': eps,
                'num_beneficiarios': num_benef,
                'total_familia': total,
                'valor_empresa': Decimal('0'),
                'valor_empleado': total,
                'apoyo_no_gravable': Decimal('0'),
                'apoyo_gravable': Decimal('0'),
                'estado_cruce': estado,
                'tipo_persona': elegibilidad.tipo_persona,
                'estado_elegibilidad': elegibilidad.estado_elegibilidad,
                'motivo_elegibilidad': elegibilidad.motivo_elegibilidad,
                'porcentaje_empresa_aplicado': elegibilidad.porcentaje_empresa,
                'porcentaje_empleado_aplicado': elegibilidad.porcentaje_empleado,
                'valor_no_cubierto': Decimal('0'),
                'sue_basi': sue_basi,
                'tip_cont': tip_cont,
            })
            continue

        if not elegibilidad.calcula_como_empleado_ok:
            resultados.append({
                'cedula': cedula,
                'nombre_en_factura': nombre_factura,
                'nombre_en_kactus': nombre_kactus,
                'eps': eps,
                'num_beneficiarios': num_benef,
                'total_familia': total,
                'valor_empresa': Decimal('0'),
                'valor_empleado': Decimal('0'),
                'apoyo_no_gravable': Decimal('0'),
                'apoyo_gravable': Decimal('0'),
                'estado_cruce': estado,
                'tipo_persona': elegibilidad.tipo_persona,
                'estado_elegibilidad': elegibilidad.estado_elegibilidad,
                'motivo_elegibilidad': elegibilidad.motivo_elegibilidad,
                'porcentaje_empresa_aplicado': elegibilidad.porcentaje_empresa,
                'porcentaje_empleado_aplicado': elegibilidad.porcentaje_empleado,
                'valor_no_cubierto': total,
                'sue_basi': sue_basi,
                'tip_cont': tip_cont,
            })
            continue

        valor_empresa = round(total * elegibilidad.porcentaje_empresa / 100, 2)
        valor_empleado = round(total * elegibilidad.porcentaje_empleado / 100, 2)
        apoyo_no_grav = min(valor_empresa, limite_no_grav)
        apoyo_grav = max(Decimal('0'), valor_empresa - limite_no_grav)

        resultados.append({
            'cedula': cedula,
            'nombre_en_factura': nombre_factura,
            'nombre_en_kactus': nombre_kactus,
            'eps': eps,
            'num_beneficiarios': num_benef,
            'total_familia': total,
            'valor_empresa': valor_empresa,
            'valor_empleado': valor_empleado,
            'apoyo_no_gravable': round(apoyo_no_grav, 2),
            'apoyo_gravable': round(apoyo_grav, 2),
            'estado_cruce': estado,
            'tipo_persona': elegibilidad.tipo_persona,
            'estado_elegibilidad': elegibilidad.estado_elegibilidad,
            'motivo_elegibilidad': elegibilidad.motivo_elegibilidad,
            'porcentaje_empresa_aplicado': elegibilidad.porcentaje_empresa,
            'porcentaje_empleado_aplicado': elegibilidad.porcentaje_empleado,
            'valor_no_cubierto': Decimal('0'),
            'sue_basi': sue_basi,
            'tip_cont': tip_cont,
        })

    return resultados


def get_empleados_kactus() -> list:
    """
    Retorna empleados activos de kactus junto con su última factura EPS.
    Útil para detección de pensionados y validaciones cruzadas.
    """
    conn = _get_connection()
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute(
        """
        SELECT k.cod_empl, k.nom_completo, k.ind_acti, k.tip_cont,
               f.eps, f.total_familia, f.periodo
        FROM facturas_eps f
        LEFT JOIN empleados_kactus k ON k.cod_empl = f.cedula
        WHERE k.ind_acti != 'I' OR k.cod_empl IS NULL
        """
    )
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows
