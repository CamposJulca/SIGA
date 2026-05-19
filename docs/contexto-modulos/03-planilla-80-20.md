# Módulo 3 — Planilla 80/20: Investigación Técnica

| Campo            | Valor                                                                       |
|------------------|------------------------------------------------------------------------------|
| Fecha            | 2026-05-13                                                                   |
| Generado por     | Verificación directa de código fuente                                         |
| Alcance          | 3 bloques UI + reglas MP del manual + comportamientos detectados en pantallas |
| Archivos leídos  | `views.py`, `services/prepagada_service.py`, `services/eligibility.py`, `services/validator.py`, `services/axa_adapter.py`, `services/colsanitas_adapter.py`, `models.py`, `serializers.py`, `migrations/*.py` |

---

## Bloque A — Cruce del período

### Flujo real (en lenguaje funcional)

1. El usuario selecciona un período (`MMYYYY`) en la UI.
2. SIGA pide a `prepagada.db` la lista de períodos disponibles para mostrarlos en el selector.
3. Al elegir uno, SIGA consulta **una vista llamada `v_cruce`** que ya existe en `prepagada.db`. Esa vista entrega, por cada fila, la cédula del titular, el nombre como aparece en la factura, el nombre como aparece en la nómina (Kactus), su EPS, el número de beneficiarios del grupo familiar, el total del valor familiar, el sub-contrato, el número de contrato, el salario básico, el tipo de contrato y un campo `estado` que indica si el cruce es `OK` o no.
4. SIGA solo lee. No modifica `prepagada.db`. No reconstruye la vista. No re-cruza contra `BeneficioSalud`. Lo que vea la UI es **literalmente lo que devuelve `v_cruce`**.

### Evidencia técnica

| Operación                         | Vista / Servicio                            | Archivo:Líneas                                          |
|------------------------------------|---------------------------------------------|----------------------------------------------------------|
| Endpoint `GET /cruce/`             | `CruceView`                                  | `views.py` 636–666                                       |
| Listar períodos disponibles        | `prepagada_service.get_periodos_disponibles` | `services/prepagada_service.py` 25–40                    |
| Leer cruce del período             | `prepagada_service.get_cruce_periodo`        | `services/prepagada_service.py` 43–64                    |

Query exacta que ejecuta SIGA contra `prepagada.db`:

```python
# services/prepagada_service.py líneas 51–60
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
```

### Origen real de `v_cruce` y de los datos del cruce

**`v_cruce` NO está creada por SIGA.** Verificación:

- `find ~/Finagro/siga -name "*.sql"` → **0 archivos**.
- `grep -rn "CREATE VIEW\|v_cruce" backend/` → 0 ocurrencias de `CREATE VIEW`; las únicas referencias a `v_cruce` son **lecturas** (`SELECT ... FROM v_cruce`).
- Ningún punto del código abre `prepagada.db` con permisos de escritura. Toda interacción se hace por `_get_connection()` en `services/prepagada_service.py:13–22` y solo ejecuta `SELECT`.

**Consecuencia operativa:** quien sea que mantenga `prepagada.db` (un proceso externo, un export de Kactus, un script manual) es **la única fuente de verdad** del cruce. Si esa fuente no se actualiza, SIGA muestra y calcula sobre datos desactualizados sin alarma.

**Tablas implícitas:** la query sobre `v_cruce` deja entrever que la vista une al menos `facturas_eps` y `empleados_kactus` (esos nombres aparecen en `services/prepagada_service.py:184–191` en la función `get_empleados_kactus`). Pero el `CREATE VIEW` exacto **no está en el repo**.

### Sub-contrato (`Sub. Cto`) — origen

- En el **cruce** que ve la UI, el `sub_cto` viene de la columna `sub_cto` de la vista `v_cruce` en `prepagada.db` (línea 54 de `prepagada_service.py`). **No se calcula en SIGA.**
- En el **ETL** (carga de archivos), `sub_contrato` se mapea de:
  - AXA: columna `SUB CTO` del Excel (`services/axa_adapter.py:10`).
  - Colsanitas: columna `Número de Familia` del Excel (`services/colsanitas_adapter.py:43`).
- **Importante:** el `sub_contrato` que carga el ETL y el `sub_cto` que muestra el cruce **provienen de fuentes distintas**. El cruce no consume `BeneficioSalud.sub_contrato`; lo lee directo de la vista externa.

### Conteo de beneficiarios (`Benef.`)

- También viene de `v_cruce`, columna `num_beneficiarios` (línea 54). **No se cuenta sobre `BeneficioSalud` en tiempo de consulta**: lo que aparezca en pantalla depende de cómo la vista lo haya pre-agregado.
- No hay forma de saber, sin el `CREATE VIEW`, si `num_beneficiarios` incluye al titular o solo a los familiares.

### Estado del cruce — qué define cada valor

- El campo `estado` viene **literal** de `v_cruce` (`prepagada_service.py:54`). SIGA no clasifica nada; pasa el valor tal como llega.
- En `eligibility.py` líneas 52–60:
  ```python
  if estado_cruce != 'OK':
      return EligibilityResult(
          tipo_persona=TIPO_EMPLEADO,
          estado_elegibilidad=BLOQUEADO_CRUCE,
          motivo_elegibilidad=f'Cruce Kactus en estado {estado_cruce or "SIN_ESTADO"}; no se calcula aporte empresa.',
          ...
      )
  ```
  **El código solo distingue dos casos: `OK` y "todo lo demás".** Cualquier estado que no sea exactamente `OK` (case sensitive, ya pasa por `.upper()` en línea 36) se trata como bloqueado.
- **Búsqueda de `INACTIVO`:** `grep -rn "INACTIVO\|inactivo" backend/modules/beneficios_salud/` → **0 resultados**. El código no tiene lógica especial para `INACTIVO`. Si la UI muestra ese valor es porque `v_cruce` lo entregó, pero el comportamiento es idéntico al de `NO ENCONTRADO`: bloqueado.

### Comportamientos confirmados / refutados — Bloque A

| # | Pregunta                                                                                   | Veredicto                              | Evidencia |
|---|---------------------------------------------------------------------------------------------|-----------------------------------------|-----------|
| 1 | ¿`v_cruce` es una vista SQL en `prepagada.db`?                                                | ✅ **Sí, externa a SIGA**                | `services/prepagada_service.py:51–60`. No hay `CREATE VIEW` en el repo. |
| 2 | ¿SIGA construye o actualiza esa vista?                                                       | ❌ **No, solo lee.** Confirmado en H6.    | `_get_connection()` abre conexión sólo para SELECT (`services/prepagada_service.py:13–64, 184–191`). |
| 3 | ¿`nombre_en_factura` y `nombre_en_kactus` salen de fuentes distintas?                         | ✅ **Sí**                                 | Ambos vienen del SELECT a `v_cruce`; los nombres sugieren un LEFT JOIN entre `facturas_eps` y `empleados_kactus`. |
| 4 | ¿Hay más estados de cruce posibles además de `OK`/`NO ENCONTRADO`?                            | ⚠️ **Indeterminado por código**           | El código solo distingue `OK` vs "no OK". Cualquier otro estado (`INACTIVO`, `RETIRADO`, etc.) viaja en el JSON tal cual la vista lo entrega y se trata igual que `NO ENCONTRADO` en el cálculo. |
| 5 | ¿De dónde vienen los sub-contratos `SC-001…SC-008`, `COL-101…COL-108`?                       | ⚠️ **De `v_cruce.sub_cto` (no de los archivos cargados)** | Línea 54 de `prepagada_service.py`. El `sub_contrato` del ETL es independiente. La asignación de esos códigos es externa a SIGA. |
| 6 | ¿`num_beneficiarios` se calcula en SIGA o lo trae la vista?                                  | ✅ **Lo trae la vista.**                  | Línea 54. SIGA no hace `GROUP BY` ni `COUNT` para esto. |
| 7 | Si una cédula está duplicada en `BeneficioSalud` por carga doble, ¿se duplica en el cruce?    | ❌ **No afecta al cruce.**                | El cruce se lee de `v_cruce`, no de `BeneficioSalud`. Los duplicados del ETL son irrelevantes para este bloque (pero sí lo son para el dashboard y para Facturas EPS). |

---

## Bloque B — Calcular Planilla 80/20

### Flujo real (en lenguaje funcional)

1. El usuario escribe un período y opcionalmente un `politica_id`, y hace POST a `/planilla/calcular/`.
2. SIGA verifica que `periodo` no esté vacío. **No verifica formato, longitud ni valor real**.
3. Si vino `politica_id`, busca esa política puntual; si no, toma la política con `vigente_desde` más reciente (no la "vigente al período").
4. Llama a `calcular_planilla(periodo, politica)`. Ese servicio internamente vuelve a hacer `SELECT ... FROM v_cruce WHERE periodo = ?`.
5. Por cada fila de `v_cruce`:
   - Pregunta a `eligibility.evaluar_elegibilidad` cómo clasificar a la persona: empleado elegible, pensionado o cruce bloqueado.
   - Aplica el cálculo correspondiente (80/20, 0/100 o 0/0).
6. Suma totales sobre los registros **liquidables** (`ELEGIBLE_80_20` + `PENSIONADO_100`). Cuenta empleados solo los `ELEGIBLE_80_20`.
7. Crea **una nueva `PlanillaCalculo`** con todos los totales y un `DetalleCalculo` por cada fila procesada (incluyendo bloqueados, con valores en cero).
8. **No verifica si ya existía planilla para ese período.** No reemplaza, no versiona, simplemente crea una nueva fila con el mismo `periodo`.

### Evidencia técnica

| Operación                             | Vista / Servicio                          | Archivo:Líneas                                          |
|----------------------------------------|--------------------------------------------|----------------------------------------------------------|
| Endpoint `POST /planilla/calcular/`    | `PlanillaCalcularView.post`                | `views.py` 838–909                                       |
| Cálculo registro a registro            | `prepagada_service.calcular_planilla`      | `services/prepagada_service.py` 67–173                   |
| Clasificación de elegibilidad           | `eligibility.evaluar_elegibilidad`         | `services/eligibility.py` 33–69                          |
| Modelos persistidos                    | `PlanillaCalculo`, `DetalleCalculo`        | `models.py` 166–211                                      |

### Validación del input `periodo`

```python
# views.py líneas 845–848
def post(self, request, *args, **kwargs):
    periodo = request.data.get('periodo')
    if not periodo:
        return Response({'error': 'El campo "periodo" es requerido.'}, status=status.HTTP_400_BAD_REQUEST)
```

**Eso es toda la validación.** No hay:
- regex `^\d{6}$`;
- `len(periodo) == 6`;
- chequeo de mes ∈ `[01..12]`;
- normalización (`zfill`, slicing);
- consulta previa a `v_cruce` para confirmar que el período exista.

**Consecuencia directa:**

Si el usuario escribe `03202026`, el servidor lo acepta. El siguiente paso (`get_cruce_periodo("03202026")`) hace `SELECT ... FROM v_cruce WHERE periodo = '03202026'` y **retorna lista vacía** (no falla, solo no encuentra). El bucle `for r in rows` no ejecuta ninguna iteración. Se crea una `PlanillaCalculo` válida con `total_empleados=0`, todos los totales en 0 y **sin un solo `DetalleCalculo`**. Es exactamente lo que se ve en la UI: planilla #2 con `period='03202026'`, 0 empleados, totales en cero.

### Cómo decide qué política aplicar

```python
# views.py líneas 850–865
politica_id = request.data.get('politica_id')
if politica_id:
    try:
        politica = PoliticaPrepagada.objects.get(pk=politica_id)
    except PoliticaPrepagada.DoesNotExist:
        return Response(...)
else:
    politica = PoliticaPrepagada.objects.order_by('-vigente_desde').first()
    if politica is None:
        return Response(...)
```

**Esto refuta MP-032.** El manual exige "política vigente al período calculado". El código toma la política con la fecha de vigencia **más reciente en BD**, sin compararla contra el período.

Ejemplo: si hoy 2026-05-13 hay una política `vigente_desde=2026-01-01` (UVT 2026) y se calcula la planilla del período `032025`, el código aplica la política de 2026 a un período de 2025. **Es un bug funcional latente que entra en juego al cambio de año / cambio de UVT.**

### Cálculo línea por línea (CRÍTICO — snippet literal)

```python
# services/prepagada_service.py líneas 80–172 (fragmento esencial)
limite_no_grav = (
    Decimal(str(politica.uvt_limite)) * Decimal(str(politica.valor_uvt))
)
...
for r in rows:
    cedula = str(r['cedula']) if r['cedula'] is not None else ''
    ...
    total = Decimal(str(r['total_familia'] or 0))
    elegibilidad = evaluar_elegibilidad(r, politica)

    if elegibilidad.estado_elegibilidad == 'PENSIONADO_100':
        resultados.append({
            ...
            'valor_empresa': Decimal('0'),
            'valor_empleado': total,
            'apoyo_no_gravable': Decimal('0'),
            'apoyo_gravable': Decimal('0'),
            ...
        })
        continue

    if not elegibilidad.calcula_como_empleado_ok:
        resultados.append({
            ...
            'valor_empresa': Decimal('0'),
            'valor_empleado': Decimal('0'),
            'apoyo_no_gravable': Decimal('0'),
            'apoyo_gravable': Decimal('0'),
            'valor_no_cubierto': total,
            ...
        })
        continue

    valor_empresa  = round(total * elegibilidad.porcentaje_empresa  / 100, 2)
    valor_empleado = round(total * elegibilidad.porcentaje_empleado / 100, 2)
    apoyo_no_grav  = min(valor_empresa, limite_no_grav)
    apoyo_grav     = max(Decimal('0'), valor_empresa - limite_no_grav)
```

Verificaciones clave:

| Pregunta                                                                                   | Respuesta literal del código                                                              |
|---------------------------------------------------------------------------------------------|--------------------------------------------------------------------------------------------|
| ¿Aplica el % sobre `total_familia` directamente?                                              | **Sí**, sobre `Decimal(str(r['total_familia'] or 0))`. Sin pre-procesado.                  |
| ¿Considera `BeneficioSalud.descuento` (descuento comercial del proveedor)?                   | ❌ **No.** El cálculo no toca `BeneficioSalud`. Solo lee `v_cruce`.                          |
| ¿Considera `BeneficioSalud.iva` por separado?                                                 | ❌ **No.**                                                                                  |
| ¿El límite UVT se aplica antes o después del 80%?                                              | **Después.** Primero `valor_empresa = total × 80/100`, **luego** se aplica el límite UVT solo para separar gravable de no gravable. El UVT no recorta `valor_empresa`. |

**Implicación:** el valor que se reparte 80/20 es exclusivamente `total_familia` de `v_cruce`. Si esa columna ya viene "neta" (descontados IVA y descuento comercial) en la vista externa, el cálculo es consistente con lo que se esperaría. Si viene "bruta", el 80/20 está repartiendo bruto. **El código no sabe ni le importa.** Sigue siendo H4 confirmado.

### Pensionados — cómo se identifican en el cálculo

```python
# services/eligibility.py líneas 38–50
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
```

Confirmaciones:

- **Identificación 100% por tabla manual `bs_pensionados_prepagada`.**
- Si la cédula NO está registrada como pensionado activo Y el `estado` de cruce no es `OK`, queda como `BLOQUEADO_CRUCE` con todos los valores en cero (`prepagada_service.py:122–143`).
- Si la cédula NO está registrada como pensionado pero `v_cruce.estado = 'OK'`, se calcula como empleado activo normal (80/20). **No hay tercera vía**: ya es activo o ya está en la tabla manual.
- **El campo `NOM = PNS` del archivo AXA no se consulta en ningún momento.** Es la confirmación H2 aplicada al cálculo: si un pensionado del archivo nunca fue registrado a mano en el Módulo 6 pero su cruce está `OK`, **el sistema le calcula 80/20 como si fuera empleado activo**. Falsamente.

### Estados `NO ENCONTRADO` e `INACTIVO` en la planilla

| Estado de `v_cruce` | Estado resultante en planilla | Se persiste en `DetalleCalculo`? | Aporta a totales? |
|----------------------|--------------------------------|----------------------------------|-------------------|
| `OK`                  | `ELEGIBLE_80_20`                | Sí                                | Sí                |
| `OK` + cédula en tabla pensionados | `PENSIONADO_100`        | Sí                                | Sí (en empleado, no en empresa) |
| `NO ENCONTRADO`       | `BLOQUEADO_CRUCE`               | Sí (con todo en cero)             | **No**             |
| `INACTIVO`            | `BLOQUEADO_CRUCE`               | Sí (con todo en cero)             | **No**             |
| Cualquier otro valor  | `BLOQUEADO_CRUCE`               | Sí (con todo en cero)             | **No**             |

Evidencia: `views.py` líneas 874–885:

```python
liquidables = [
    r for r in resultados
    if r['estado_elegibilidad'] in ('ELEGIBLE_80_20', 'PENSIONADO_100')
]
empleados_elegibles = [
    r for r in resultados
    if r['estado_elegibilidad'] == 'ELEGIBLE_80_20'
]
total_empresa  = sum(r['valor_empresa']  for r in liquidables)
total_empleado = sum(r['valor_empleado'] for r in liquidables)
```

Es decir: **los bloqueados sí entran al detalle de la planilla**, pero no suman aportes. Esto es útil para auditoría ("aparecieron en la factura pero no liquidaron"), pero hay que tenerlo claro: el conteo `total_empleados` excluye pensionados (es solo los 80/20).

### Reglas MP del manual — verificación punto por punto

| ID    | Regla del manual                                                  | ¿Implementada? | Evidencia                                                                          |
|-------|--------------------------------------------------------------------|----------------|------------------------------------------------------------------------------------|
| MP-002 | Antigüedad > 2 meses                                                | ❌ **No**       | `grep -rn "antiguedad\|fecha_ingreso\|periodo_prueba" backend/` → 0 resultados.   |
| MP-003 | Aceptación del colaborador                                          | ❌ **No**       | `grep -rn "aceptacion" backend/` → 0 resultados.                                   |
| MP-004 | Autorización descuento por escrito                                  | ❌ **No**       | `grep -rn "autorizacion" backend/` → 0 resultados.                                 |
| MP-005 | Distribución 80/20                                                  | ✅ **Sí**       | `prepagada_service.py:146–147`.                                                    |
| MP-006 | Pensionado 100% empleado                                            | ✅ **Sí** (parcial) | `eligibility.py:42–50`. Pero depende de registro manual en `bs_pensionados_prepagada`. |
| MP-007 | Identificación de pensionados                                       | ❌ **No automática** | Confirmado H2: la columna `NOM` del archivo AXA no se consulta. El registro es 100% manual. |
| MP-008 | Cónyuge elegible                                                    | ❌ **No validado** | `grep -rn "conyuge\|compañero\|estado_civil" backend/` → 0 resultados. Si viene en la factura, se calcula sin más.  |
| MP-009 | Compañero permanente (unión ≥ 2 años)                                | ❌ **No**       | Idem.                                                                                |
| MP-010 | Hijos ≤ 25 años dependientes                                         | ❌ **No**       | `grep -rn "dependencia\|edad" backend/modules/beneficios_salud/services/` → solo `edad` como columna pasiva en validator (parseado pero no validado).  |
| MP-011 | Hijos discapacitados                                                 | ❌ **No**       | `grep -rn "discapacidad" backend/` → 0 resultados.                                  |
| MP-012 | Padres para colaborador soltero                                       | ❌ **No**       | Sin lógica de estado civil.                                                          |
| MP-013 | Segundo grado para soltero sin padres                                 | ❌ **No**       | Idem.                                                                                |
| MP-014 | Soltero con hijos y padres                                           | ❌ **No**       | Idem.                                                                                |
| MP-015 | Casado con un padre en lugar del cónyuge                              | ❌ **No**       | Idem.                                                                                |
| MP-016 | Familiar no descrito → 100% empleado                                  | ❌ **No diferenciado** | El cálculo aplica 80/20 a todo lo que entra en `v_cruce` con `estado=OK`. No hay distinción por elegibilidad de parentesco. |
| MP-017 | Soportes documentales                                                 | ❌ **No**       | No hay modelo de soportes.                                                          |
| MP-026 | Prorrateo por retiro (hasta último día laborado)                      | ❌ **No**       | `grep -rn "prorrateo\|prorrat\|dias_laborad" backend/` → 0 resultados.              |
| MP-027 | Prorrateo por ingreso                                                  | ❌ **No**       | Idem.                                                                                |
| MP-028 | Cruce factura ↔ Kactus                                                 | ✅ **Sí, externo** | Vía `v_cruce`. El cruce lo hace la fuente externa.                                  |
| MP-029 | Cédula no encontrada → sin aporte                                       | ✅ **Sí**       | `eligibility.py:52–60`. Bloquea.                                                    |
| MP-030 | Empleado inactivo → sin aporte                                          | ✅ **Sí** (parcial) | Trata `INACTIVO` igual que `NO ENCONTRADO`: bloqueado. No hay prorrateo por retiro. |
| MP-031 | Agrupación por grupo familiar                                            | ✅ **Sí, externa** | `total_familia` y `num_beneficiarios` vienen ya agregados por la vista.            |
| MP-032 | Política vigente al período                                              | ❌ **Refutado**  | `views.py:860`: `order_by('-vigente_desde').first()`. Toma la más reciente en BD, no la vigente al período. |
| MP-033 | Separación gravable / no gravable                                         | ✅ **Sí**       | `prepagada_service.py:148–149`.                                                     |
| MP-041 | Persistencia con política aplicada                                        | ✅ **Sí** (parcial) | `PlanillaCalculo.politica` FK; `generada_por` se llena con username solo si está autenticado, si no queda `'anonimo'` (`views.py:887–889`). |
| MP-042 | Recálculo de planilla                                                     | ❌ **Indefinido** | Cada POST crea una nueva `PlanillaCalculo`; no reemplaza ni versiona. Caso real: planillas duplicadas para `032026`. |
| MP-043 | Excepciones autorizadas                                                   | ❌ **No**       | No hay modelo de excepción ni overrides por cédula.                                  |

### Salida (modelo persistente)

Después de calcular, se persisten dos modelos:

- **`PlanillaCalculo`** (cabecera, `models.py:166–182`): campos clave `periodo`, `politica` (FK), `total_empleados`, `total_empresa`, `total_empleado`, `total_gravable`, `total_no_gravable`, `generada_en` (auto), `generada_por` (string, no FK).
- **`DetalleCalculo`** (un registro por cédula del cruce, `models.py:185–211`): incluye `cedula`, `nombre_en_factura`, `nombre_en_kactus`, `eps`, `num_beneficiarios`, `total_familia`, `valor_empresa`, `valor_empleado`, `apoyo_no_gravable`, `apoyo_gravable`, `estado_cruce`, `tipo_persona`, `estado_elegibilidad`, `motivo_elegibilidad`, `porcentaje_empresa_aplicado`, `porcentaje_empleado_aplicado`, `valor_no_cubierto`, `sue_basi`, `tip_cont`.

> Nota: `generada_por` queda con string `'anonimo'` si no hay sesión autenticada (`views.py:887–889`). Esto compromete MP-041 cuando el sistema corre sin autenticación obligatoria.

### Comportamientos confirmados / refutados — Bloque B

| # | Pregunta                                                                                  | Veredicto                                                  | Evidencia |
|---|--------------------------------------------------------------------------------------------|------------------------------------------------------------|-----------|
| 1 | ¿Valida que `periodo` sea `MMYYYY`?                                                          | ❌ **No.** Solo verifica `if not periodo`.                  | `views.py:845–848` |
| 2 | ¿Acepta `03202026`?                                                                          | ✅ **Sí.** Y crea planilla vacía sin error.                  | Confirmado en flujo. |
| 3 | ¿Toma política vigente al período (MP-032)?                                                  | ❌ **No.** Toma la más reciente por fecha de vigencia.       | `views.py:860` |
| 4 | ¿Aplica 80/20 literal sobre `total_familia`?                                                  | ✅ **Sí.**                                                  | `prepagada_service.py:146–147` |
| 5 | ¿Considera descuento comercial / IVA?                                                         | ❌ **No.** Si vienen pre-aplicados en `total_familia`, no se sabe. | Mismo snippet. |
| 6 | ¿UVT antes o después del 80%?                                                                 | ✅ **Después.** Solo separa gravable de no gravable.         | `prepagada_service.py:148–149` |
| 7 | ¿Aplica 100% empleado automáticamente para pensionados?                                       | ✅ **Sí, si están en `bs_pensionados_prepagada` activos.**   | `eligibility.py:42–50` |
| 8 | ¿Usa la columna `NOM` (ACT/PNS) del archivo AXA?                                             | ❌ **No.** Confirmado H2.                                    | `axa_adapter.py` mapeo cerrado. |
| 9 | Si una cédula tiene cruce `OK` y NO está en la tabla de pensionados pero AXA la marcó `PNS`: ¿cómo se calcula? | ⚠️ **Como empleado activo 80/20** (incorrecto desde negocio) | Por exclusión de los pasos anteriores. |
| 10 | ¿Los `NO ENCONTRADO`/`INACTIVO` entran al `DetalleCalculo`?                                     | ✅ **Sí, con todo en cero.**                                  | `prepagada_service.py:122–144` |
| 11 | ¿Aportan a totales?                                                                            | ❌ **No.**                                                    | `views.py:874–882` |
| 12 | ¿Hay alguna validación de antigüedad / aceptación / autorización / parentesco / edad / discapacidad? | ❌ **No, ninguna.**                                          | `grep -rnE "antiguedad\|fecha_ingreso\|aceptacion\|autorizacion\|periodo_prueba\|dependencia\|discapacidad\|conyuge\|compañero\|estado_civil" backend/ --include="*.py"` → 0 resultados. |
| 13 | ¿Hay validación de duplicidad de período (que ya exista planilla para `MMYYYY`)?              | ❌ **No.**                                                    | `views.py:891–900` ejecuta `PlanillaCalculo.objects.create(...)` sin chequeo. |
| 14 | ¿Hay snapshot del usuario que calculó?                                                          | ⚠️ **Sí pero débil.** Es un string `'anonimo'` si no hay sesión. | `views.py:887–889` |

> ⚠️ **Hallazgo adicional aplicable al cruce/planilla:** el adaptador de Colsanitas **no mapea `parentesco`** desde la factura. En `colsanitas_adapter.py:75–77` la columna `parentesco` se inicializa como string vacío. Aunque la factura traiga la columna `Parentesco`, no se lee. Esto explica que en cualquier flujo aguas abajo (dashboard, planilla, novedades, exportación) los registros de Colsanitas aparezcan con parentesco "Sin especificar". Es independiente del problema de hoja en AXA (H1).

---

## Bloque C — Historial de planillas

### Flujo real

- La UI consume `GET /planilla/` para mostrar la lista.
- "Ver detalle" pega a `GET /planilla/<pk>/` que devuelve la planilla con `politica` anidada y **todos** los `DetalleCalculo` (incluidos bloqueados).
- "Excel" pega a `GET /planilla/<pk>/exportar/`. El export genera un workbook con dos hojas: `Planilla 80-20` (todos los detalles) y `Apoyo Gravable` (solo los que tienen `apoyo_gravable > 0`).
- **No hay flujo de eliminación de planillas.** No hay endpoint DELETE.

### Evidencia técnica

| Operación               | Vista                              | Líneas (views.py) |
|--------------------------|-------------------------------------|-------------------|
| Listar planillas         | `PlanillaListView.get`              | 912–924           |
| Detalle de planilla       | `PlanillaDetailView.get`            | 927–939           |
| Exportar Excel             | `PlanillaExportarView.get`           | 942–1035          |

```python
# views.py líneas 912–924
class PlanillaListView(APIView):
    def get(self, request, *args, **kwargs):
        qs = PlanillaCalculo.objects.select_related('politica').all()
        periodo = request.query_params.get('periodo')
        if periodo:
            qs = qs.filter(periodo=periodo)
        serializer = PlanillaCalculoListSerializer(qs, many=True)
        return Response(serializer.data)
```

Orden por defecto: `Meta.ordering = ['-periodo']` (`models.py:179`). **Atención:** ordena por `periodo` como **string**, no por fecha. `'032026'` y `'03202026'` ordenan lexicográficamente; pueden quedar en orden no intuitivo.

### Recálculo y duplicados de período

- **No hay restricción de unicidad** sobre `(periodo, politica)` ni sobre `periodo` solo. `PlanillaCalculo` no tiene `unique_together` ni `unique=True` (`models.py:166–182`).
- Cada llamada a `POST /planilla/calcular/` ejecuta `PlanillaCalculo.objects.create(...)` (`views.py:891–900`).
- **Resultado real:** se pueden tener N planillas para el mismo período `032026`. Es exactamente lo que muestra la UI: una planilla legítima del 20/03 y otra del 13/05 con período mal escrito.
- Las consultas que usan "la planilla del período" (`/causacion/`, `/conciliacion/`, `/informe-efr/`) toman `order_by('-generada_en').first()` (p. ej. `views.py:1050, 1118–1119, 1217`). Es decir: se quedan con **la más reciente**, lo cual silenciosamente puede consolidar la planilla incorrecta si se cargó después.

> ⚠️ **Riesgo operativo importante:** una planilla mal recalculada (incluso con período mal escrito que dio 0 empleados) **no cambia el comportamiento de la del período correcto** porque las consultas filtran por `periodo` exacto. Pero si se recalcula `032026` con un error en parámetros y se genera vacía, **la causación y la conciliación tomarán esa vacía como la oficial** porque es la más reciente.

### Columna "Total Gravable" en rojo

- En el JSON de respuesta, `total_gravable` viene como número plano (sin flag). El formato en rojo es **de UI**, basado en `total_gravable > 0`.
- No hay umbral configurable en código (`grep -rn "umbral\|threshold" backend/` → no relevante).

### Export Excel

- Endpoint distinto del de Facturas EPS (`PlanillaExportarView` vs `ExportarExcelView`).
- Dos hojas exactas:
  - **Planilla 80-20** (`views.py:1014–1016`): todos los `DetalleCalculo` de la planilla, **incluidos `BLOQUEADO_CRUCE` y `PENSIONADO_100`**.
  - **Apoyo Gravable** (`views.py:1018–1021`): filtrado por `apoyo_gravable > 0`.
- Columnas exportadas (`views.py:950–967`): `cedula`, `nombre_en_kactus`, `eps`, `num_beneficiarios`, `total_familia`, `tipo_persona`, `estado_elegibilidad`, `motivo_elegibilidad`, `porcentaje_empresa_aplicado`, `porcentaje_empleado_aplicado`, `valor_empresa`, `valor_empleado`, `valor_no_cubierto`, `apoyo_no_gravable`, `apoyo_gravable`, `estado_cruce`.
- **No hay** filtro para excluir bloqueados de la hoja principal. Si TH abre el Excel esperando solo elegibles, verá filas en cero mezcladas.
- Las filas con `apoyo_gravable > 0` se resaltan en amarillo (`views.py:1010–1011`).

### Comportamientos confirmados / refutados — Bloque C

| # | Pregunta                                                                | Veredicto                                  | Evidencia |
|---|--------------------------------------------------------------------------|--------------------------------------------|-----------|
| 1 | ¿Hay endpoint DELETE para planillas?                                       | ❌ **No** (en la API)                       | `grep "def delete" views.py` no muestra `PlanillaCalculo`. Pero está registrada como tal en `admin.py` así que puede borrarse desde `/admin/`. |
| 2 | ¿Se puede recalcular y reemplazar?                                          | ❌ **No.** Se crea una nueva.                | `views.py:891–900`. |
| 3 | ¿Se versionan? ¿Hay número de versión?                                       | ❌ **No.** Solo timestamp `generada_en`.    | `models.py:166–182`. |
| 4 | ¿"Ver detalle" incluye bloqueados?                                            | ✅ **Sí**, vienen en `detalles`.             | `PlanillaCalculoDetailSerializer` con `detalles = DetalleCalculoSerializer(many=True)` (`serializers.py:199–218`). |
| 5 | ¿Export Excel filtra bloqueados?                                              | ❌ **No.** Hoja principal incluye todo.      | `views.py:1014–1016`. |
| 6 | ¿Existe alguna comparación entre dos planillas del mismo período?              | ❌ **No.** La conciliación compara dos *períodos* distintos, no dos planillas del mismo período. | `ConciliacionView` (views.py:1101–1197). |

---

# Verificación de casos observados en UI

| # | Caso UI                                                                                                                          | Respuesta del código                                                                                                                                                              |
|---|-----------------------------------------------------------------------------------------------------------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 1 | Período `03202026` (8 dígitos) aceptado, generó planilla #2 con 0 empleados.                                                       | ✅ **Confirmado.** `views.py:845–848` solo valida que no esté vacío. `prepagada_service.get_cruce_periodo("03202026")` no encuentra filas y retorna lista vacía. Planilla se crea con todos los totales en 0. |
| 2 | Cédula `99999001` (MARTINEZ LOPEZ ANDRES FELIPE) aparece como `NO ENCONTRADO` en el cruce.                                          | Significa que esa cédula **NO está en `v_cruce`** para el período consultado. Probablemente sí está en `BeneficioSalud` (vino del archivo cargado), pero `v_cruce` se construye desde la fuente externa (Kactus / facturas_eps), no desde `BeneficioSalud`. Cédulas correlativas `99999001` son típicos datos de prueba inyectados manualmente; **no hay flag de "test data" en ningún modelo.** |
| 3 | Sub-contratos `SC-001..SC-008`, `COL-101..COL-108`.                                                                                | Vienen literal de `v_cruce.sub_cto` (`prepagada_service.py:54`). SIGA **no genera** estos códigos; los lee de la fuente externa. Cualquiera de los dos: o la fuente los genera con esa convención, o son datos sembrados a mano para demo. |
| 4 | "Estado: OK" en 18/19 filas del cruce.                                                                                              | `OK` significa **solo** que la cédula está presente en `v_cruce` con el campo `estado = 'OK'`. **No** valida antigüedad, ni aceptación, ni autorización, ni parentesco, ni edad. El cálculo 80/20 se aplica a todo lo que llegue como `OK`. |
| 5 | Total empresa $12.271.280 + Total empleado $3.067.820 = $15.339.100. Empresa / total = 79.99%.                                      | ✅ **Confirma 80/20 literal sobre `total_familia`.** Pero **no se puede afirmar** que `total_familia` sea bruta o neta sin ver el `CREATE VIEW` de `v_cruce`. El código aplica el % sin pre-procesar. |
| 6 | Total Gravable $4.558.416 (rojo) + No Gravable $7.712.864 = $12.271.280 (= Total Empresa).                                         | ✅ **Confirma que la separación gravable/no gravable se aplica sobre `valor_empresa`**, no sobre el total factura. `prepagada_service.py:148–149`. La política aplicada fue la **más reciente** por `vigente_desde` (no necesariamente la del período). |
| 7 | Planilla #2 ejecutada hoy (13/05/2026) para período `032026` ya existente.                                                          | ⚠️ **No reemplaza; convive.** El sistema acepta múltiples planillas para el mismo período. Las vistas downstream (causación, conciliación, EFR) toman la más reciente por `generada_en`. **Aquí hay un riesgo:** si la nueva quedó vacía o mal, esa es la que verán los reportes. |

> Sobre el caso #1: la planilla #2 en el historial tiene `periodo='03202026'`, **no `032026`**. Por tanto **no compite** con la planilla legítima `032026` en las consultas de causación/conciliación. Pero deja un registro confuso en el historial y consume una FK de política. **Probablemente debería purgarse.**

---

# Reglas adicionales del manual (THU-DOC-002 §10.4–10.6)

| Regla literal del manual                                                              | Evidencia en código                                                                  | Estado                |
|----------------------------------------------------------------------------------------|--------------------------------------------------------------------------------------|-----------------------|
| "Llevaren vinculados con la compañía más de dos (2) meses"                              | `grep "antiguedad\|fecha_ingreso\|vinculacion" backend/` → 0 resultados.              | ❌ No implementado     |
| "Que hayan cumplido el periodo de prueba"                                                | `grep "periodo_prueba" backend/` → 0 resultados.                                       | ❌ No implementado     |
| "Deberán autorizar por escrito para que se descuente por nómina"                          | `grep "autorizacion" backend/` → 0 resultados.                                         | ❌ No implementado     |
| "Cónyuge o compañero(a) permanente, cuya unión sea igual o superior a dos (2) años"      | `grep "conyuge\|compañero\|estado_civil" backend/` → 0 resultados.                     | ❌ No implementado     |
| "Hijos hasta los veinticinco (25) años, siempre que dependan económicamente"             | `grep "edad\|dependencia" backend/modules/beneficios_salud/services/` → solo edad como columna pasiva en validator. Sin validación lógica. | ❌ No implementado     |
| "Hijos discapacitados de cualquier edad ... certificado de discapacidad"                  | `grep "discapacidad" backend/` → 0 resultados.                                         | ❌ No implementado     |
| PARÁGRAFO: "familiares no descritos ... colaborador cubrirá el costo total"               | El cálculo aplica 80/20 a **todo** lo que llegue como `estado=OK` en `v_cruce`. No diferencia parentesco. | ❌ No implementado     |
| "En caso de retiro, el aporte se reconocerá hasta el último día laborado"                 | `grep "prorrateo\|prorrat\|dias_laborad" backend/` → 0 resultados.                     | ❌ No implementado     |

---

# Resumen ejecutivo del módulo

## ✅ Lo que SÍ hace

1. Lee el cruce mensual desde una vista SQL externa (`v_cruce` en `prepagada.db`) y lo expone vía API.
2. Distingue tres estados de elegibilidad: `ELEGIBLE_80_20`, `PENSIONADO_100`, `BLOQUEADO_CRUCE`.
3. Aplica la distribución 80/20 (configurable por política) sobre `total_familia` recibido del cruce.
4. Aplica el límite UVT después del 80% y separa el aporte de la empresa en gravable y no gravable.
5. Identifica pensionados consultando la tabla manual `bs_pensionados_prepagada` y les calcula 100% empleado.
6. Persiste cada planilla calculada con su política aplicada y un detalle por cédula procesada (incluidos bloqueados).
7. Exporta a Excel con dos hojas: planilla completa y filtro de apoyo gravable.
8. Permite consultar histórico de planillas filtrado por período.

## ❌ Lo que NO hace (aunque la doc o TH lo asuma)

| # | NO hace                                                                                                                          | Riesgo                                                                                                                  |
|---|-----------------------------------------------------------------------------------------------------------------------------------|-------------------------------------------------------------------------------------------------------------------------|
| 1 | **No valida el formato del período.** Acepta cualquier string no vacío.                                                            | Inputs como `03202026` o `marzo 2026` crean planillas vacías sin error.                                                  |
| 2 | **No aplica política vigente al período (MP-032).** Usa siempre la última creada por `vigente_desde`.                              | Al cambio de año, planillas atrasadas se calcularán con UVT/política del año en curso.                                   |
| 3 | **No valida antigüedad, aceptación, autorización, parentesco, edad, dependencia, estado civil ni discapacidad.**                    | Cualquier persona con cruce `OK` recibe aporte 80/20, sin importar si el manual dice que no es elegible (MP-002..017).   |
| 4 | **No identifica pensionados desde el archivo AXA** (columna `NOM = PNS`). Solo desde la tabla manual.                              | Un pensionado de la factura que TH no haya registrado en el Módulo 6 recibe **80/20 como activo**, incorrectamente.       |
| 5 | **No aplica prorrateo por retiro o ingreso a mitad de mes (MP-026/027).**                                                            | Se reconoce mes completo o nada. Cualquier retiro/ingreso parcial queda mal liquidado.                                   |
| 6 | **No diferencia "familiar no elegible" según el manual (MP-016).** Aplica 80/20 a todos los beneficiarios que el cruce traiga.    | Familiares fuera de las reglas de elegibilidad reciben aporte empresa indebidamente.                                     |
| 7 | **No previene duplicación de planilla** del mismo período. Cada cálculo crea una fila nueva.                                       | Recálculos involuntarios sobreviven en BD. Causación y conciliación toman la más reciente; una recalculada mal queda como oficial. |
| 8 | **No mapea `parentesco` desde Colsanitas.** El adaptador lo inicializa vacío incluso si la factura trae la columna.                | El dashboard, la planilla y los reportes muestran "Sin especificar" para todos los Colsanitas — independiente del problema de hoja en AXA. |
| 9 | **No registra usuario autenticado al calcular** si no hay sesión. `generada_por = 'anonimo'`.                                       | Auditoría MP-041 queda débil mientras no haya autenticación obligatoria.                                                  |
| 10 | **No crea ni mantiene `v_cruce`.** Solo lee. El sub-contrato, `num_beneficiarios`, `total_familia` y el estado vienen externos.    | Si la fuente externa no se actualiza, SIGA muestra y calcula sobre datos desfasados sin alarma.                           |

## ⚠️ Pendiente validar con TH (decisiones de negocio)

1. **Validación del período:** ¿debe el sistema **rechazar** formatos distintos a `MMYYYY`, **normalizar** (zfill, recorte), o seguir permitiendo texto libre?
2. **Política por período (MP-032):** ¿confirman que es decisión funcional que el sistema busque la política vigente **al período** y no la más reciente? ¿Cómo se identifica "vigente al período" cuando hay solapamiento?
3. **Pensionados automáticos:** ¿quieren que el adaptador AXA mapee `NOM = PNS` y auto-poble `PensionadoPrepagada`? (Mejora barata identificada en H2.)
4. **Familiares no elegibles (MP-016):** ¿deben quedar en planilla con 100% empleado, o excluirse del cálculo? Hoy se les aplica 80/20 sin filtro.
5. **Prorrateos por ingreso/retiro:** ¿días calendario, días laborados, corte mensual? Hoy no se aplica ninguno.
6. **Recálculo de planilla (MP-042):** ¿reemplaza, versiona, o pide confirmación? Hoy se acumulan silenciosamente.
7. **Bloqueados en el Excel:** ¿quieren que la hoja principal del export incluya los `BLOQUEADO_CRUCE` o que los filtre a una hoja separada?
8. **Sincronización de `v_cruce`:** ¿quién la actualiza? ¿Con qué frecuencia? ¿SIGA debería tener un endpoint de "refresh" o una alerta cuando los datos están desfasados?
9. **Período `03202026` en el historial:** ¿se conserva o se purga? Es un dato accidental que ensucia el histórico.

---

**Fuente:** verificación directa de:
- `siga/backend/modules/beneficios_salud/views.py` (UploadView, CruceView, PlanillaCalcularView, PlanillaListView, PlanillaDetailView, PlanillaExportarView, ConciliacionView, CausacionView, InformeEFRView)
- `siga/backend/modules/beneficios_salud/services/prepagada_service.py`
- `siga/backend/modules/beneficios_salud/services/eligibility.py`
- `siga/backend/modules/beneficios_salud/services/validator.py`
- `siga/backend/modules/beneficios_salud/services/axa_adapter.py`
- `siga/backend/modules/beneficios_salud/services/colsanitas_adapter.py`
- `siga/backend/modules/beneficios_salud/models.py`
- `siga/backend/modules/beneficios_salud/serializers.py`
- `siga/backend/modules/beneficios_salud/migrations/0002_prepagada_modules.py`
- `siga/backend/modules/beneficios_salud/migrations/0003_elegibilidad_planilla.py`
