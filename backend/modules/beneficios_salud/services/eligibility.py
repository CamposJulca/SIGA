"""
Reglas de elegibilidad para medicina prepagada.

Esta primera versión usa reglas implementables con los datos actuales:
- Cruce Kactus OK permite 80/20.
- Pensionados activos pagan 100%.
- Cruces no OK quedan bloqueados para aporte empresa.
"""
from dataclasses import dataclass
from decimal import Decimal

from ..models import PensionadoPrepagada


TIPO_EMPLEADO = 'EMPLEADO'
TIPO_PENSIONADO = 'PENSIONADO'

ELEGIBLE_80_20 = 'ELEGIBLE_80_20'
PENSIONADO_100 = 'PENSIONADO_100'
BLOQUEADO_CRUCE = 'BLOQUEADO_CRUCE'


@dataclass(frozen=True)
class EligibilityResult:
    tipo_persona: str
    estado_elegibilidad: str
    motivo_elegibilidad: str
    porcentaje_empresa: Decimal
    porcentaje_empleado: Decimal
    calcula_como_empleado_ok: bool


def evaluar_elegibilidad(row: dict, politica) -> EligibilityResult:
    cedula = str(row.get('cedula') or '').strip()
    eps = str(row.get('eps') or '').strip()
    estado_cruce = str(row.get('estado') or '').strip().upper()

    pensionado_qs = PensionadoPrepagada.objects.filter(cedula=cedula, activo=True)
    if eps:
        pensionado_qs = pensionado_qs.filter(eps__iexact=eps)

    if pensionado_qs.exists():
        return EligibilityResult(
            tipo_persona=TIPO_PENSIONADO,
            estado_elegibilidad=PENSIONADO_100,
            motivo_elegibilidad='Pensionado activo: asume el 100% del valor de la poliza colectiva.',
            porcentaje_empresa=Decimal('0'),
            porcentaje_empleado=Decimal('100'),
            calcula_como_empleado_ok=False,
        )

    if estado_cruce != 'OK':
        return EligibilityResult(
            tipo_persona=TIPO_EMPLEADO,
            estado_elegibilidad=BLOQUEADO_CRUCE,
            motivo_elegibilidad=f'Cruce Kactus en estado {estado_cruce or "SIN_ESTADO"}; no se calcula aporte empresa.',
            porcentaje_empresa=Decimal('0'),
            porcentaje_empleado=Decimal('0'),
            calcula_como_empleado_ok=False,
        )

    return EligibilityResult(
        tipo_persona=TIPO_EMPLEADO,
        estado_elegibilidad=ELEGIBLE_80_20,
        motivo_elegibilidad='Empleado activo con cruce Kactus OK: aplica distribucion 80/20 vigente.',
        porcentaje_empresa=Decimal(str(politica.porcentaje_empresa)),
        porcentaje_empleado=Decimal(str(politica.porcentaje_empleado)),
        calcula_como_empleado_ok=True,
    )
