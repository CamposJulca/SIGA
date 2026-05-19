# Módulo 5 — Causación: Investigación Técnica

| Campo            | Valor                                                                |
|------------------|----------------------------------------------------------------------|
| Fecha            | 2026-05-13                                                           |
| Generado por     | Verificación directa de código fuente                                 |
| Archivos leídos  | `urls.py`, `views.py` (1038–1197), `serializers.py`, `models.py`     |
| Apoyo previo     | Módulos 3 y 4 (cálculo 80/20, política congelada por FK)              |

---

## Pregunta arquitectónica de fondo

> ¿Endpoint propio con su lógica de agrupación, o reconsume `PlanillaDetailView`?

**Veredicto: ✅ Endpoint propio con `GROUP BY eps` en backend.**

A diferencia del módulo 4 (puro visualizador), Causación tiene **dos endpoints dedicados**:

| Endpoint                                                                | Vista              | Líneas (views.py) |
|--------------------------------------------------------------------------|--------------------|-------------------|
| `GET /api/beneficios-salud/causacion/?periodo=MMYYYY`                    | `CausacionView`    | 1038–1098         |
| `GET /api/beneficios-salud/conciliacion/?periodo_nuevo=X&periodo_anterior=Y` | `ConciliacionView` | 1101–1197         |

Esto significa que el agrupado por EPS **se hace en BD** (con `values('eps').annotate(...)`), no en el cliente.

---

## Endpoint y flujo

### Flujo real (en lenguaje funcional)

1. TH ingresa el período en formato `MMYYYY`.
2. SIGA busca **la planilla más reciente** para ese período (`order_by('-generada_en').first()`).
3. Si no hay planilla calculada para ese período: HTTP 404 con mensaje "No existe planilla calculada para el periodo X".
4. Si hay planilla, agrupa los `DetalleCalculo` por EPS, **excluyendo los que tienen `estado_cruce ≠ 'OK'`**.
5. Calcula por cada EPS: cantidad de empleados, total empresa, total empleado, total general (suma de `total_familia`), apoyo no gravable, apoyo gravable.
6. Devuelve la lista por EPS y un bloque `totales` con los agregados **leídos directamente de `PlanillaCalculo`** (no recalculados).

### Evidencia técnica

```python
# views.py líneas 1044–1072
def get(self, request, *args, **kwargs):
    periodo = request.query_params.get('periodo')
    if not periodo:
        return Response({'error': 'El parámetro "periodo" es requerido.'}, status=status.HTTP_400_BAD_REQUEST)

    # Obtener la planilla más reciente del periodo
    planilla = PlanillaCalculo.objects.filter(periodo=periodo).order_by('-generada_en').first()
    if planilla is None:
        return Response(
            {'error': f'No existe planilla calculada para el periodo "{periodo}".'},
            status=status.HTTP_404_NOT_FOUND
        )

    from django.db.models import Sum, Count

    resumen_eps = (
        DetalleCalculo.objects
        .filter(planilla=planilla, estado_cruce='OK')
        .values('eps')
        .annotate(
            num_empleados=Count('id'),
            total_empresa=Sum('valor_empresa'),
            total_empleado=Sum('valor_empleado'),
            total_general=Sum('total_familia'),
            apoyo_no_gravable=Sum('apoyo_no_gravable'),
            apoyo_gravable=Sum('apoyo_gravable'),
        )
        .order_by('eps')
    )
```

---

## Lógica de agrupación por EPS

### ¿Qué `DetalleCalculo` entran al agrupado?

Filtro en `views.py:1061`:

```python
.filter(planilla=planilla, estado_cruce='OK')
```

| Tipo de registro                 | ¿Entra al agrupado por EPS?                                                      |
|----------------------------------|----------------------------------------------------------------------------------|
| `ELEGIBLE_80_20` con cruce `OK`  | ✅ **Sí.**                                                                        |
| `PENSIONADO_100` con cruce `OK`  | ✅ **Sí.** Aporta a `num_empleados` aunque su `valor_empresa = 0`.               |
| `PENSIONADO_100` con cruce ≠ `OK`| ❌ **No.** (Caso poco probable: pensionado activo en tabla manual pero su `v_cruce.estado` no es `OK`.) |
| `BLOQUEADO_CRUCE` (cruce ≠ `OK`) | ❌ **No.**                                                                        |

> ⚠️ **Inconsistencia interna potencial:** la cabecera `PlanillaCalculo.total_empleados` cuenta **solo** los `ELEGIBLE_80_20` (`views.py:878–894`). El conteo agrupado por EPS cuenta **`ELEGIBLE_80_20` + `PENSIONADO_100`** (los que pasan el filtro `estado_cruce='OK'`). En un período sin pensionados ambos cuadran. En un período con pensionados, **`SUM(num_empleados por EPS) > total_empleados`**.

### `total_general` (= "Total Factura" de la UI)

La columna "Total Factura" de la UI corresponde a `total_general = Sum('total_familia')` (línea 1067). **No es la suma `Empresa + Empleado`** (lo cual, para `ELEGIBLE_80_20`, coincide porque `total_familia = valor_empresa + valor_empleado`; pero para `PENSIONADO_100` también coincide porque `valor_empleado = total_familia` y `valor_empresa = 0`). Es decir: en la práctica `Total Factura = total_empresa + total_empleado` por construcción.

### ¿Filtro por proveedor / EPS hardcoded?

❌ **No.** El único filtro es `planilla=planilla, estado_cruce='OK'`. Cualquier valor de `eps` que aparezca en `DetalleCalculo` saldrá como una fila. Esto deja la puerta abierta a EPS no documentadas (ej. "COLMEDICA") si llegaran a aparecer en `v_cruce` algún día.

---

## Comportamiento ante múltiples planillas del mismo período

**Caso real:** el módulo 3 permite acumular planillas con el mismo `periodo` (MP-042 no implementado). Si hay 3 planillas para `032026`, la consulta de causación:

```python
# views.py línea 1050
planilla = PlanillaCalculo.objects.filter(periodo=periodo).order_by('-generada_en').first()
```

- ✅ Usa **la más reciente** (`order_by('-generada_en').first()`).
- ❌ **No suma las múltiples** (lo cual sería incorrecto).
- ❌ **No avisa al usuario** que existen otras planillas para el mismo período.

> ⚠️ **Riesgo operativo concreto:** si un analista calcula una planilla, le entrega los números a contabilidad, y otro analista recalcula la planilla (por error o intencionalmente) **antes** de que contabilidad registre, la causación cambia silenciosamente. El analista que volvió a consultar puede ver valores distintos sin saber por qué.

Verificación con el caso real del módulo 3:
- Planilla #1: `periodo='032026'`, 15 empleados, totales legítimos.
- Planilla #2: `periodo='03202026'`, 0 empleados.
- Como tienen `periodo` distinto, **no compiten**. La causación de `032026` sigue tomando la #1.
- **Pero** si alguien recalcula la planilla `032026` (no `03202026`), la nueva pasaría a ser la oficial sin advertencia.

---

## Validación del input `periodo`

Confirmado **mismo bug del módulo 3**. Líneas 1045–1047:

```python
periodo = request.query_params.get('periodo')
if not periodo:
    return Response({'error': 'El parámetro "periodo" es requerido.'}, ...)
```

No hay regex, longitud, ni rango. Casos:

| Input               | Comportamiento                                                                                              |
|---------------------|--------------------------------------------------------------------------------------------------------------|
| `032026`            | Encuentra la planilla legítima. OK.                                                                          |
| `03202026`          | Encuentra la planilla #2 vacía (la del bug del módulo 3). Causación retorna con `num_empleados=0` y totales en cero. ⚠️ **Sin error visible.** |
| `marzo2026`         | No encuentra planilla → HTTP 404.                                                                            |
| `3/2026`            | No encuentra planilla → HTTP 404.                                                                            |
| `132026` (mes 13)    | No encuentra planilla → HTTP 404.                                                                            |
| (vacío)              | HTTP 400.                                                                                                    |

> ⚠️ El caso `03202026` es el peligroso: TH ve "respuesta válida" pero la causación está vacía.

---

## La fila TOTAL: por qué guiones en algunas columnas

### Qué envía realmente el backend

Response completo (líneas 1086–1097):

```python
return Response({
    'periodo': periodo,
    'planilla_id': planilla.id,
    'generada_en': planilla.generada_en,
    'por_eps': resultado,
    'totales': {
        'total_empresa':       float(planilla.total_empresa),
        'total_empleado':      float(planilla.total_empleado),
        'total_gravable':      float(planilla.total_gravable),
        'total_no_gravable':   float(planilla.total_no_gravable),
        'total_empleados':     planilla.total_empleados,
    },
})
```

**Lo que SÍ envía** en `totales`: `total_empresa`, `total_empleado`, `total_gravable`, `total_no_gravable`, `total_empleados`.
**Lo que NO envía** en `totales`: ❌ `total_general` (la suma del "Total Factura").

### Por qué la UI muestra `—`

| Columna UI         | Por EPS (en `por_eps[]`)         | En `totales`                     | Causa del `—` en la fila TOTAL                             |
|---------------------|------------------------------------|------------------------------------|------------------------------------------------------------|
| Empleados           | ✅ `num_empleados`                  | ✅ `total_empleados`                 | Debería mostrarse. Si la UI muestra `—`, es bug de frontend. |
| Total Empresa       | ✅ `total_empresa`                  | ✅ `total_empresa`                   | ✅ Se ve.                                                    |
| Total Empleado      | ✅ `total_empleado`                  | ✅ `total_empleado`                   | ✅ Se ve.                                                    |
| Total Factura       | ✅ `total_general` (suma `total_familia`) | ❌ **NO existe en `totales`**        | ⚠️ **Bug del backend.** No envía el total consolidado.        |
| No Gravable         | ✅ `apoyo_no_gravable`              | ✅ `total_no_gravable`                | Debería mostrarse. Si la UI muestra `—`, es bug de frontend. |
| Gravable            | ✅ `apoyo_gravable`                  | ✅ `total_gravable`                   | Debería mostrarse. Si la UI muestra `—`, es bug de frontend. |

> ⚠️ **Dos problemas distintos en juego:**
>
> 1. **Backend:** no envía `total_general` (= "Total Factura") en el bloque `totales`. Para mostrarlo, el frontend tendría que sumar `total_empresa + total_empleado`.
> 2. **Frontend:** `No Gravable` y `Gravable` SÍ vienen del backend pero la UI los pinta como `—`. Esto es bug o decisión de presentación, hay que verificarlo en el cliente.

### ¿Quién calcula la fila TOTAL?

- **Empresa / Empleado / Gravable / No Gravable / Empleados:** el backend los lee directo de `PlanillaCalculo` (`views.py:1092–1096`). No los suma del `por_eps`.
- **Total Factura:** **nadie lo calcula** en el backend. El frontend tendría que sumar las filas o sumar `total_empresa + total_empleado`.

> ⚠️ **Consecuencia interesante:** los totales NO vienen del agrupado `por_eps`, sino de la cabecera `PlanillaCalculo`. Esto significa que **si por_eps no incluye pensionados (porque su `estado_cruce ≠ 'OK'`), pero `PlanillaCalculo.total_empleado` SÍ los incluye (porque la cabecera los suma), `SUM(por_eps.num_empleados) ≠ totales.total_empleados`**. En el caso típico cuadra; pero hay un escenario donde no.

---

## Conceptos contables / códigos PUC

❌ **El response de Causación NO expone los códigos contables de la política.**

Verificado en líneas 1086–1097: el response solo tiene `periodo`, `planilla_id`, `generada_en`, `por_eps[]`, `totales{}`. **No incluye `cod_conc_apoyo_no_grav`, `cod_conc_apoyo_grav`, `cod_conc_dcto_empleado`** que sí están en `planilla.politica`.

Los campos existen y están persistidos en `PoliticaPrepagada` (`models.py:114–116`), serializan correctamente vía `PoliticaPrepagadaSerializer` (`serializers.py:107–109`), pero **Causación no los entrega**.

Si contabilidad quiere ver los códigos junto con los valores, hoy debe ir a otro endpoint (`GET /politica/<id>/`) y cruzar manualmente.

> ⚠️ **Implicación para la reunión:** si TH responde "necesitamos el asiento contable listo para registrar", **hoy no se entrega completo**. Faltan los códigos para que sea autoejecutable.

---

## Conciliación entre períodos (vista hermana)

Existe **endpoint dedicado**: `GET /conciliacion/?periodo_nuevo=X&periodo_anterior=Y` (`views.py:1101–1197`).

### Qué hace

- Toma la planilla más reciente de cada período (`order_by('-generada_en').first()` por cada uno, líneas 1118–1119).
- Filtra `DetalleCalculo` con `estado_cruce='OK'` en ambos (líneas 1134, 1140).
- Indexa por **cédula** (no por `(cedula, sub_contrato)`).
- Calcula:
  - **Nuevos**: cédulas en periodo nuevo pero no en anterior.
  - **Retirados**: al revés.
  - **Cambios de valor**: cédulas en ambos con diferencia `|valor_empresa_nuevo − valor_empresa_anterior| > 1`.
  - **Sin cambios**: diferencia ≤ 1.

### Lo que hay que saber

- ✅ Es un endpoint legítimo y funcional.
- ⚠️ Compara **`valor_empresa`** (no `total_familia`). Es decir: detecta cambios de aporte de la empresa, no de cuotas totales.
- ⚠️ Mismo bug de períodos: cualquier string se acepta. Si TH compara `032026` con `03202026`, retorna la "conciliación" entre una planilla legítima y una vacía → "todos retirados" + 0 nuevos. **Es un sinsentido funcional pero el backend no detecta el error.**
- ⚠️ Misma fragilidad ante múltiples planillas: toma la más reciente de cada período silenciosamente.
- ❌ No tiene variación porcentual ni absoluta sobre totales — solo niveles individuales por cédula.
- ❌ Sin export propio.

> ⚠️ La pregunta del prompt "¿existe conciliación entre periodos en este módulo?" — **sí**, pero como **endpoint independiente**. La UI del módulo 5 puede estar mostrándolo o no; eso depende del frontend.

---

## Export

❌ **No existe export propio para Causación.**

Verificación: `grep "ExportarCausacion\|CausacionExport\|causacion.*export"` → 0 resultados. En `urls.py:35` solo existe `path('causacion/', CausacionView.as_view())` — sin variante `/exportar/`.

**Consecuencia:** si contabilidad necesita un Excel/CSV de causación, hoy debe:
- Copiar manualmente desde la UI, o
- Usar el export de Planilla del módulo 3 (`/planilla/<pk>/exportar/`) y agrupar a mano por EPS.

No hay un asiento contable listo para registrar (sin códigos PUC, sin formato contable estándar).

---

## Comportamientos confirmados / refutados

| # | Pregunta                                                                                  | Veredicto                              | Evidencia |
|---|--------------------------------------------------------------------------------------------|----------------------------------------|-----------|
| 1 | ¿Endpoint propio o reconsume planilla?                                                     | ✅ **Endpoint propio** con `GROUP BY` en BD. | `urls.py:35`, `views.py:1059–1072` |
| 2 | ¿Pensionados (`PENSIONADO_100`) entran al agrupado por EPS?                                 | ✅ **Sí**, si `estado_cruce='OK'`.        | Filtro `views.py:1061`. |
| 3 | ¿Bloqueados (`BLOQUEADO_CRUCE`) entran?                                                     | ❌ **No.**                              | Idem. |
| 4 | ¿Hay riesgo de doble contabilización entre `por_eps` y `totales`?                          | ⚠️ **Sí, en escenarios con pensionados.** | `total_empleados` cuenta solo `ELEGIBLE_80_20` (cabecera); `num_empleados` por EPS cuenta también pensionados con cruce OK. |
| 5 | ¿Múltiples planillas del mismo período?                                                     | ⚠️ **Usa la más reciente sin avisar.**    | `views.py:1050` |
| 6 | ¿Valida formato del período?                                                                  | ❌ **No.** Mismo bug del módulo 3.       | `views.py:1045–1047` |
| 7 | Si `period='03202026'` (caso del bug del módulo 3): ¿retorna error?                          | ❌ **No.** Retorna causación con ceros sin advertir. | Encuentra la planilla #2 vacía. |
| 8 | ¿La fila TOTAL incluye `total_factura` desde el backend?                                       | ❌ **No.** `totales` no tiene `total_general`. | `views.py:1090–1096` |
| 9 | ¿La fila TOTAL incluye gravable / no gravable?                                                 | ✅ **Sí, los envía el backend.**          | Líneas 1093–1094. Si la UI muestra `—` es por el frontend. |
| 10 | ¿Los códigos contables (PUC) están en el response?                                            | ❌ **No.** No se incluyen.                | Líneas 1086–1097 |
| 11 | ¿Hay filtro por EPS / búsqueda / paginación?                                                   | ❌ **Ninguno.**                          | Solo acepta `?periodo=`. |
| 12 | ¿Hay export Excel/CSV propio?                                                                  | ❌ **No.**                                | `grep "exportar"` 0 hits en `causacion`. |
| 13 | ¿Hay vista de drill-down por EPS (lista de empleados)?                                          | ❌ **No por Causación.** El detalle por empleado vive en módulos 3 y 4. | `urls.py` solo `/causacion/`. |
| 14 | ¿La causación es reproducible si nadie recalcula la planilla?                                  | ✅ **Sí.** Los valores vienen de `PlanillaCalculo` y `DetalleCalculo`, modelos persistentes. | Confirmado por el patrón. |
| 15 | ¿Hay concepto de "causación aprobada / cerrada"?                                                | ❌ **No.** No hay flujo de estados.       | Ningún campo `estado_causacion` en modelos. |
| 16 | ¿Existe conciliación entre periodos?                                                              | ✅ **Sí**, endpoint separado.             | `views.py:1101–1197`. Compara `valor_empresa` por cédula. |

---

# Verificación de casos observados en UI

| # | Caso UI                                                                                          | Respuesta del código                                                                                                                          |
|---|--------------------------------------------------------------------------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------|
| 1 | 8 + 7 = 15 empleados (= `PlanillaCalculo.total_empleados`).                                        | Coincide porque en ese período no hay pensionados activos. La fila `por_eps` cuenta `ELEGIBLE_80_20 + PENSIONADO_100`, la cabecera cuenta solo `ELEGIBLE_80_20`. Sin pensionados, cuadran. |
| 2 | Total Factura AXA $13.304.200 = $10.643.360 + $2.660.840.                                          | Por construcción: `total_general = SUM(total_familia)`. Para `ELEGIBLE_80_20`: `total_familia = valor_empresa + valor_empleado`. Para `PENSIONADO_100`: `total_familia = valor_empleado`. Ambos casos cuadran con la suma "Empresa + Empleado". |
| 3 | Fila TOTAL muestra `—` en Total Factura.                                                            | ⚠️ **Confirmado bug del backend:** `totales` no incluye `total_general`. |
| 4 | Fila TOTAL muestra `—` en No Gravable y Gravable.                                                   | ⚠️ **Bug del frontend o decisión UX.** El backend SÍ entrega `total_gravable` y `total_no_gravable` en `totales` (líneas 1093–1094). |
| 5 | Total Empresa $12.271.280 cuadra con `PlanillaCalculo.total_empresa`.                              | ✅ **Confirma idempotencia:** los totales se leen directo de la cabecera, no se recalculan. |
| 6 | Colsanitas Gravable = $0.                                                                          | Coincidencia del dato (cuotas Colsanitas más bajas que el límite UVT). Sin filtro hardcoded. |
| 7 | Si se ingresa `03202026`: ¿qué muestra la UI?                                                       | El backend encuentra la planilla #2 y retorna causación con `por_eps=[]` (sin filas que pasen `estado_cruce='OK'`) y totales en cero. **La UI mostrará una pantalla vacía sin explicación.** |
| 8 | No hay drill-down por EPS.                                                                          | ✅ **Confirmado:** no existe endpoint `/causacion/<eps>/empleados/`. El detalle por empleado vive en `PlanillaDetailView` (módulo 3). |

---

# Resumen ejecutivo del módulo

## ✅ Lo que SÍ hace

1. Endpoint dedicado (`/causacion/`) que **agrupa por EPS** en base de datos con `GROUP BY` + `SUM` + `COUNT`.
2. Lee la planilla más reciente del período seleccionado.
3. Excluye registros con cruce ≠ `OK` (es decir: bloqueados quedan fuera del agrupado).
4. Incluye pensionados activos (con cruce OK) en el agrupado, contribuyendo a `valor_empleado` por EPS.
5. Devuelve totales globales leídos directamente de `PlanillaCalculo` (idempotente y reproducible mientras la planilla no se recalcule).
6. Endpoint hermano de Conciliación (`/conciliacion/`) compara dos períodos por cédula y reporta nuevos/retirados/cambios de aporte empresa.

## ❌ Lo que NO hace

| # | NO hace                                                                                          | Riesgo                                                                                                                  |
|---|---------------------------------------------------------------------------------------------------|-------------------------------------------------------------------------------------------------------------------------|
| 1 | **No valida formato del período.** Mismo bug del módulo 3.                                          | `03202026` retorna pantalla vacía sin error.                                                                            |
| 2 | **No envía `total_factura` (total general) en el bloque `totales`.**                                | UI muestra `—` en la fila TOTAL para "Total Factura" — bug del backend.                                                  |
| 3 | **No expone los códigos contables (PUC) de la política asociada.**                                  | Contabilidad no recibe el asiento contable listo; hay que cruzar manualmente con `/politica/<id>/`.                       |
| 4 | **No advierte si existen múltiples planillas para el mismo período.**                                | Recálculo silencioso cambia los números entre dos consultas seguidas.                                                    |
| 5 | **No tiene export Excel / CSV propio.**                                                              | Contabilidad debe copiar manualmente o usar el export de Planilla y reagrupar.                                            |
| 6 | **No tiene concepto de "causación aprobada / cerrada".**                                              | Cualquier cambio aguas arriba (recálculo, edición admin) afecta lo que ve contabilidad sin trazabilidad de quién aprobó qué. |
| 7 | **No tiene drill-down por EPS** (lista de empleados que componen el agregado).                         | Para verificar un total hay que ir a la planilla del módulo 3 y reagrupar mentalmente.                                    |
| 8 | **No reporta variación absoluta ni porcentual** entre períodos (la Conciliación lo hace por cédula, no por agregados de EPS). | Para reporte directivo "variación mes a mes" se necesita cálculo externo.                                                 |
| 9 | **No detecta inconsistencias internas:** si `SUM(por_eps.num_empleados) ≠ totales.total_empleados` (caso con pensionados), no se reporta. | Posible confusión: TH ve la fila TOTAL diferente a la suma visual de las filas. |
| 10 | **No expone `motivo_elegibilidad`** ni desglose por estado. Solo agregados.                          | No se puede explicar desde Causación por qué cierta EPS tiene menos empleados de los esperados. |

## ⚠️ Pendiente validar con TH y/o contabilidad

1. **`Total Factura` en la fila TOTAL:** ¿el frontend debería sumar visualmente las filas, o el backend debe enviarlo? (Recomendación: enviarlo desde el backend para consistencia.)
2. **Gravable / No Gravable en la fila TOTAL:** ¿es decisión UX deliberada no mostrarlos, o un bug? El backend los entrega.
3. **Códigos contables (PUC):** ¿contabilidad los necesita en el reporte? ¿O los conoce de memoria y solo necesita los valores?
4. **Asiento contable listo:** ¿contabilidad espera un formato tipo "DEBE / HABER" con códigos, o le sirve la tabla actual?
5. **Aprobación de causación:** ¿debe haber un workflow "borrador / aprobada / cerrada"? ¿Quién aprueba? ¿Cuándo se "congela" un período?
6. **Múltiples planillas del mismo período:** ¿quieren bloqueo al recalcular, alerta visible en la causación ("hay 3 planillas para este período, mostrando la del DD/MM/YYYY"), o status quo?
7. **Export para contabilidad:** ¿Excel, CSV, formato propio del sistema contable de Finagro?
8. **Drill-down por EPS:** ¿útil tener una vista "ver los 8 empleados de AXA con sus valores"?
9. **Variación entre meses:** ¿en Causación o en otra pantalla? ¿Quién pide ese reporte y en qué granularidad (total, por EPS, por concepto gravable/no gravable)?

---

**Fuente:** verificación directa de:
- `siga/backend/modules/beneficios_salud/urls.py` (líneas 35–36)
- `siga/backend/modules/beneficios_salud/views.py` — `CausacionView` (1038–1098), `ConciliacionView` (1101–1197)
- `siga/backend/modules/beneficios_salud/models.py` — `PlanillaCalculo` (166–182), `DetalleCalculo` (185–211), `PoliticaPrepagada` (108–127)
- `siga/backend/modules/beneficios_salud/serializers.py` — `PoliticaPrepagadaSerializer` (97–115)
- Apoyo previo: `docs/contexto-modulos/03-planilla-80-20.md` (cálculo y estados de elegibilidad), `docs/contexto-modulos/04-apoyo-gravable-no-gravable.md` (FK política con PROTECT)
