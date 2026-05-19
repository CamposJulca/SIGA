# Módulo 4 — Apoyo Gravable / No Gravable: Investigación Técnica

| Campo            | Valor                                                                 |
|------------------|------------------------------------------------------------------------|
| Fecha            | 2026-05-13                                                             |
| Generado por     | Verificación directa de código fuente                                   |
| Archivos leídos  | `urls.py`, `views.py`, `serializers.py`, `models.py`                    |
| Apoyo previo     | Cálculo gravable/no gravable ya verificado en `03-planilla-80-20.md`    |

---

## Pregunta arquitectónica de fondo

> ¿Es una vista derivada que lee de `DetalleCalculo`, o recalcula al vuelo desde `v_cruce`?

**Veredicto: ✅ Vista derivada pura.** No hay cálculo al vuelo. No hay siquiera un endpoint dedicado.

**Evidencia:**

- `grep -n "gravable" modules/beneficios_salud/urls.py` → **0 resultados**. No existe ninguna ruta tipo `/apoyo-gravable/`, `/planilla/<id>/apoyo-gravable/` ni similar.
- Las únicas referencias a `gravable` en `views.py` están en:
  - `PlanillaCalcularView` (líneas 884–898): suma totales **durante el cálculo** de la planilla y los persiste en `PlanillaCalculo`.
  - `PlanillaExportarView` (líneas 947, 964–965, 1019–1021): genera la hoja "Apoyo Gravable" del Excel filtrando los detalles con `apoyo_gravable > 0`.
- Los campos `apoyo_no_gravable` y `apoyo_gravable` ya están **almacenados** en `DetalleCalculo` (modelo, líneas 195–196) y los agregados `total_gravable` / `total_no_gravable` están **almacenados** en `PlanillaCalculo` (líneas 172–173).

**Consecuencia operativa importante:** el módulo es **idempotente respecto a la política actual**. Una vez calculada una planilla, sus valores gravables/no gravables y los UVT aplicados quedan congelados. Si TH cambia la política (ej. actualiza el UVT a 2027) y luego entra a este módulo a ver una planilla vieja, **verá los UVT con los que se calculó originalmente** (no los nuevos). Esto es correcto desde el punto de vista de auditoría.

---

## Endpoint y flujo

La pantalla del módulo 4 se alimenta exclusivamente de **dos endpoints existentes** del módulo 3:

| Necesidad de la pantalla         | Endpoint que la sirve                       | Archivo:Líneas |
|-----------------------------------|----------------------------------------------|----------------|
| Selector de planilla (lista)      | `GET /api/beneficios-salud/planilla/`         | `views.py` 912–924 |
| Detalle de planilla seleccionada  | `GET /api/beneficios-salud/planilla/<pk>/`    | `views.py` 927–939 |
| Export Excel (hoja Apoyo Gravable) | `GET /api/beneficios-salud/planilla/<pk>/exportar/` | `views.py` 942–1035 |

El detalle (`PlanillaDetailView`) responde con `PlanillaCalculoDetailSerializer`, que incluye **dos bloques anidados** clave para esta pantalla (`serializers.py` 199–218):

```python
class PlanillaCalculoDetailSerializer(serializers.ModelSerializer):
    detalles = DetalleCalculoSerializer(many=True, read_only=True)
    politica = PoliticaPrepagadaSerializer(read_only=True)

    class Meta:
        model = PlanillaCalculo
        fields = [
            'id', 'periodo', 'politica',
            'total_empleados', 'total_empresa', 'total_empleado',
            'total_gravable', 'total_no_gravable',
            'generada_en', 'generada_por',
            'detalles',
        ]
```

- **`politica` anidada** → alimenta el banner (`uvt_limite`, `valor_uvt`, `vigente_desde`).
- **`total_gravable` y `total_no_gravable` y `total_empresa`** → alimentan tres de los cuatro KPIs directamente.
- **`detalles[]`** → alimenta la tabla por empleado y el conteo de "Empleados con Exceso".

> ⚠️ **El conteo "Empleados con Exceso" NO está pre-calculado en el backend.** Hay que verificar dónde se hace (ver §"Definición de Empleados con Exceso").

---

## Origen del umbral mostrado en el banner

**UI:** *"Límite exento 80/20: 16 UVT = $796,784"*.

### De dónde viene cada parte

| Componente UI         | Origen                                          |
|------------------------|------------------------------------------------|
| `16` UVT               | `PlanillaCalculo.politica.uvt_limite`           |
| `$796,784`             | calculado como `uvt_limite × valor_uvt` (frontend; el backend no expone este producto pre-calculado, hay que multiplicarlo en el cliente) |
| `valor_uvt`             | `PlanillaCalculo.politica.valor_uvt`            |

### ¿Política asociada a la planilla o política vigente actual?

✅ **Asociada a la planilla.** Evidencia:

- `PlanillaCalculo.politica` es un `ForeignKey(PoliticaPrepagada, on_delete=models.PROTECT)` (`models.py:168`). Es decir: la política queda **inmutablemente referenciada** desde la planilla.
- `PROTECT` significa que `PoliticaPrepagada` **no puede ser eliminada** si tiene planillas asociadas. La auditoría está protegida a nivel de BD.
- El serializer de detalle anida `politica = PoliticaPrepagadaSerializer(read_only=True)`, que serializa **el objeto referenciado por la FK**, no la "última" política.

**Caso crítico verificado:** si TH consulta hoy una planilla de 2025 que se calculó con UVT 2025 = $47.065, y la política vigente actual es la de 2026 con UVT $49.799, **el banner mostrará $47.065**. Es lo que correspondería tributariamente.

> ⚠️ **Pero hay un matiz:** la política que quedó referenciada **es la que `PlanillaCalcularView` eligió al momento del cálculo**, y se sabe (módulo 3, MP-032 refutado, `views.py:860`) que ese view toma la política con `vigente_desde` más reciente, **no la vigente al período**. Esto significa que si se hubiera calculado mal una planilla pasada con la política nueva, el banner reflejaría fielmente esa política nueva — y la presentaría como si fuera la "correcta". El módulo 4 **no detecta esa inconsistencia**.

---

## Definición de "Empleados con Exceso"

El KPI **no está pre-calculado** en el backend. No existe campo `empleados_con_exceso` en `PlanillaCalculo` (verificado en `models.py:166–182`) ni en el serializer. Tampoco hay un endpoint que lo calcule.

**Implicación:** el frontend tiene que iterar la lista `detalles[]` y contar los que tienen `apoyo_gravable > 0`. Ese es trabajo del cliente.

### Casos que pueden inflar / desinflar el conteo

Recordando los estados de elegibilidad almacenados en `DetalleCalculo.estado_elegibilidad`:

| Estado                | `apoyo_gravable` típico                                    | ¿Cuenta como "exceso" si el frontend filtra por `> 0`? |
|-----------------------|-------------------------------------------------------------|---------------------------------------------------------|
| `ELEGIBLE_80_20`      | `max(0, valor_empresa − límite_no_grav)` — puede ser > 0    | Sí, si `valor_empresa > límite`.                         |
| `PENSIONADO_100`      | Explícitamente `Decimal('0')` (`prepagada_service.py:109`)  | No.                                                      |
| `BLOQUEADO_CRUCE`     | Explícitamente `Decimal('0')` (`prepagada_service.py:133`)  | No.                                                      |

> ✅ **Conclusión:** un filtro `apoyo_gravable > 0` en el frontend cuenta **exactamente** los elegibles 80/20 que superan el límite UVT. Pensionados y bloqueados quedan correctamente fuera por construcción del backend, sin necesidad de filtrar por estado.

### "Todos los 6 son AXA, ninguno Colsanitas": ¿coincidencia o filtro?

⚠️ **No hay filtro hardcoded por EPS en el backend.** El `DetalleCalculo` no se filtra por proveedor en ningún punto del cálculo o de la respuesta de `PlanillaDetailView`. La explicación es **natural del dato**:

- AXA típicamente trae `total_familia` más altos (planes empresariales con titular + familia).
- Colsanitas en los archivos vistos puede traer cuotas más bajas que no exceden 16 UVT.

Para confirmarlo definitivamente habría que hacer query directa a la BD, pero **el código no introduce ningún sesgo por EPS** en este módulo.

### Umbral mínimo

❌ **No hay umbral mínimo.** Si `apoyo_gravable = $0.01`, el empleado entraría al conteo. Tampoco hay redondeo a cero por debajo de un umbral.

---

## Tabla por empleado — qué expone

`DetalleCalculoSerializer` (serializers.py 154–178) expone los siguientes campos para cada empleado:

```
id, cedula, nombre_en_factura, nombre_en_kactus, eps, num_beneficiarios,
total_familia, valor_empresa, valor_empleado, apoyo_no_gravable,
apoyo_gravable, estado_cruce, tipo_persona, estado_elegibilidad,
motivo_elegibilidad, porcentaje_empresa_aplicado, porcentaje_empleado_aplicado,
valor_no_cubierto, sue_basi, tip_cont
```

La UI **solo muestra 6 columnas**: Cédula, Nombre, EPS, No Gravable, Gravable, Total Empresa. **Los otros 14 campos están en el response pero ocultos.** El frontend descarta:

- `nombre_en_factura` (a favor de `nombre_en_kactus`)
- `num_beneficiarios`, `total_familia`, `valor_empleado`
- `estado_cruce`, `tipo_persona`, `estado_elegibilidad`, `motivo_elegibilidad`
- `porcentaje_empresa_aplicado`, `porcentaje_empleado_aplicado`
- `valor_no_cubierto`, `sue_basi`, `tip_cont`

> ⚠️ Esto significa que si TH ve solo "$0 / $0 / $0" en la tabla para alguien, **no tiene forma desde esta pantalla** de saber por qué (¿pensionado? ¿bloqueado por cruce? ¿bloqueado por inactivo?). El motivo está en el response (`motivo_elegibilidad`), pero el frontend no lo muestra.

### ¿Incluye `BLOQUEADO_CRUCE` y `PENSIONADO_100`?

✅ **Sí, todos los `DetalleCalculo` viajan en el response.** No hay filtro en `PlanillaCalculoDetailSerializer.detalles` (línea 200: `detalles = DetalleCalculoSerializer(many=True, read_only=True)` — sin `filter`). La cabecera `PlanillaCalculo.detalles` se relaciona directo sin condición en la consulta (`views.py:935`).

Implicación: la tabla del módulo 4 muestra **también** a bloqueados y pensionados con sus valores en cero. Es ruido visual para una pantalla tributaria.

---

## Banner y semántica

**UI:** *"Límite exento 80/20: 16 UVT = $796,784. El exceso es apoyo gravable para el empleado."*

- **Origen del texto:** estático en el frontend. **No viene del backend.** El backend solo entrega los números (`uvt_limite`, `valor_uvt`).
- **Consistencia con el manual:** el manual no usa la frase "apoyo gravable para el empleado". El uso correcto en términos tributarios sería algo como "ingreso constitutivo de renta gravable para el trabajador" o "valor que incrementa la base de retención en la fuente del empleado". **La redacción actual es coloquial y puede confundir a tributaria/auditoría.**

> ⚠️ Hallazgo de UX/lenguaje: el texto del banner es funcional pero **no es preciso tributariamente**. Marcarlo para conversación con tributaria.

---

## Filtros, búsqueda y paginación

❌ **No existen** en el backend para este módulo:

- `GET /planilla/<pk>/` **no admite query params** (`PlanillaDetailView.get`, `views.py:933–939`). No hay filtros por EPS, por estado de exceso, ni búsqueda por nombre/cédula.
- No hay paginación. Toda la lista `detalles` viaja en un solo response. Para una planilla de 15 empleados (caso real observado) no es problema; para una de cientos o miles sí lo sería.

Cualquier filtro/búsqueda que la UI muestre **se ejecuta en el cliente** sobre la lista completa.

---

## Export Excel

✅ **Reutiliza el mismo endpoint del módulo 3:** `GET /api/beneficios-salud/planilla/<pk>/exportar/`.

- Generador en `PlanillaExportarView` (`views.py:942–1035`).
- Genera un workbook con dos hojas:
  - **Hoja 1: "Planilla 80-20"** — todos los `DetalleCalculo` (incluye bloqueados y pensionados con ceros).
  - **Hoja 2: "Apoyo Gravable"** — filtrado por `apoyo_gravable > 0` (`views.py:1019–1020`).

> ✅ **La hoja "Apoyo Gravable" es exactamente lo que TH necesita** para entregar a tributaria. No es necesario un export propio del módulo 4.

---

## Cambio de planilla en el selector

Caso: TH selecciona la planilla #2 con `period='03202026'` y 0 empleados (la planilla rara creada en el módulo 3 por el input no validado).

- `GET /planilla/2/` retorna `PlanillaCalculoDetailSerializer` (`views.py:935–939`).
- La política referenciada existe (gracias al `on_delete=PROTECT`), así que el banner se rellena.
- `detalles` viene como **lista vacía** (`[]`), porque ningún `DetalleCalculo` se creó para esa planilla (módulo 3 §"Validación del input periodo").
- Los KPIs muestran ceros (`total_gravable=0`, `total_no_gravable=0`, `total_empresa=0`).
- El conteo "Empleados con Exceso" da `0` por iteración vacía.

**Conclusión:** la vista funciona, no da error, pero presenta una pantalla totalmente vacía. **No hay mensaje** que indique a TH "esta planilla no tiene detalles, probablemente fue calculada con un período inválido".

---

## Comportamientos confirmados / refutados

| # | Pregunta                                                                                            | Veredicto                                  | Evidencia |
|---|------------------------------------------------------------------------------------------------------|--------------------------------------------|-----------|
| 1 | ¿Es vista derivada (lee `DetalleCalculo`) o recalcula al vuelo?                                       | ✅ **Vista derivada pura.**                | No hay endpoint en `urls.py`. El módulo consume `GET /planilla/<pk>/`. |
| 2 | ¿El banner usa la política asociada a la planilla o la vigente actual?                                 | ✅ **La asociada a la planilla.**         | FK `PROTECT` en `models.py:168` + serializer anida la política con id correcto. |
| 3 | Si una planilla histórica se ve hoy con política nueva, ¿qué muestra el banner?                       | ✅ **El UVT con el que se calculó la planilla.** | Idem. |
| 4 | ¿Hay heredado el riesgo de MP-032 refutado?                                                            | ⚠️ **Sí, indirectamente.**                  | El banner refleja fielmente la política que tenía la planilla, pero esa política pudo haber sido la "última" en vez de la "vigente al período" en el momento del cálculo. |
| 5 | ¿"Empleados con Exceso" es campo persistido en `PlanillaCalculo`?                                       | ❌ **No.** Se calcula en el frontend.      | No existe en `models.py:166–182` ni en serializers. |
| 6 | ¿`PENSIONADO_100` o `BLOQUEADO_CRUCE` pueden contar como exceso?                                       | ❌ **No.** Ambos tienen `apoyo_gravable=0` por construcción. | `prepagada_service.py:109, 133`. |
| 7 | ¿Hay filtro hardcoded por EPS?                                                                          | ❌ **No.**                                  | No hay filtros en `PlanillaDetailView`. |
| 8 | ¿Hay umbral mínimo (ignorar gravables pequeños)?                                                       | ❌ **No.**                                  | El cálculo es estricto `max(0, valor_empresa − límite)`. |
| 9 | ¿La tabla incluye `BLOQUEADO_CRUCE` y `PENSIONADO_100`?                                                  | ✅ **Sí, todos los `DetalleCalculo`.**     | `serializers.py:200`. No hay filter. |
| 10 | ¿El frontend muestra `motivo_elegibilidad` para registros con ceros?                                  | ❌ **No (asumido por UI con 6 columnas).** | El backend lo entrega; el frontend lo descarta. |
| 11 | ¿Banner muestra fecha de vigencia de la política?                                                       | ⚠️ **El backend la entrega; falta confirmar UI.**  | `PoliticaPrepagadaSerializer` incluye `vigente_desde` (line 111). |
| 12 | ¿Hay export Excel propio del módulo 4?                                                                   | ❌ **No.** Reutiliza `/planilla/<pk>/exportar/`. | Endpoint único en `urls.py:34`. |
| 13 | ¿Hay filtros, búsqueda o paginación en el backend?                                                       | ❌ **Ninguno.**                             | `PlanillaDetailView.get` no admite query params. |
| 14 | ¿Hay regla "si suma de gravables > X, alertar"?                                                          | ❌ **No.**                                  | Nada en el código indica alertas o umbrales de notificación. |
| 15 | ¿Si TH selecciona la planilla `03202026` (vacía), qué muestra?                                            | ⚠️ **Pantalla en ceros sin mensaje explicativo.** | Backend retorna `detalles=[]`, totales cero. |

---

# Resumen ejecutivo del módulo

## ✅ Lo que SÍ hace

1. Presenta los valores gravable / no gravable / total empresa **ya persistidos** en `PlanillaCalculo` y `DetalleCalculo` — sin recalcular al vuelo.
2. Muestra el umbral UVT **de la política con la que se calculó la planilla**, lo cual es correcto desde el punto de vista de auditoría y no se afecta por cambios posteriores de política.
3. La política asociada está protegida a nivel de BD (`on_delete=PROTECT`); no se puede perder por borrado accidental.
4. Identifica correctamente "empleados con exceso" filtrando por `apoyo_gravable > 0`. Pensionados y bloqueados quedan automáticamente excluidos por tener `apoyo_gravable = 0` por construcción del backend.
5. La hoja "Apoyo Gravable" del export Excel (módulo 3) ya cubre la necesidad de entregable a tributaria.
6. Si la planilla seleccionada está vacía, el módulo no rompe; muestra todo en ceros.

## ❌ Lo que NO hace (aunque la UI lo pueda sugerir)

| # | NO hace                                                                                                    | Riesgo |
|---|-------------------------------------------------------------------------------------------------------------|--------|
| 1 | **No tiene endpoint propio.** Es 100% un consumidor de `GET /planilla/<pk>/`.                                 | Cualquier necesidad de filtro/búsqueda/paginación tendría que hacerse en el frontend o requiere endpoint nuevo. |
| 2 | **No pre-calcula "Empleados con Exceso" en el backend.** El frontend itera y cuenta.                          | Con planillas grandes esto puede ser un problema de rendimiento del cliente. |
| 3 | **No filtra `BLOQUEADO_CRUCE` ni `PENSIONADO_100` de la tabla.**                                              | Aparecen como filas con ceros, ruido visual para una pantalla tributaria. |
| 4 | **No muestra `motivo_elegibilidad`** aunque el backend lo entregue.                                            | Si TH ve "$0 / $0 / $0" para alguien, no sabe si es pensionado, bloqueado o por qué. |
| 5 | **No muestra la `vigente_desde` de la política en el banner.**                                                 | TH no sabe a qué UVT específico corresponde la vista. Riesgo de confusión al cambio de año. |
| 6 | **No tiene umbral mínimo** (ej. ignorar exceso < $1.000).                                                       | Excesos triviales aparecen como casos a coordinar con tributaria. |
| 7 | **No alerta** cuando hay un cambio significativo de gravable mes a mes.                                         | TH solo descubre los excesos al entrar al módulo. |
| 8 | **No advierte cuando una planilla seleccionada está vacía.**                                                    | El usuario que abre la planilla `03202026` ve ceros sin explicación. |
| 9 | **No tiene texto preciso tributariamente.** "Apoyo gravable para el empleado" es coloquial.                     | Riesgo de mala interpretación por auditoría / tributaria. |
| 10 | **No tiene filtros, búsqueda ni paginación** en el backend.                                                     | Cualquier UX que las simule corre 100% en el cliente sobre la lista completa. |

## ⚠️ Pendiente validar con TH

1. **Vigencia de la política en el banner:** ¿quieren que el banner muestre también `vigente desde YYYY-MM-DD` para evitar confusión al cambio de año? (Cambio chico: el dato ya está en el response.)
2. **Filtrado de bloqueados y pensionados en la tabla:** ¿deben verse o solo los elegibles 80/20?
3. **Texto del banner:** ¿la frase "apoyo gravable para el empleado" es aceptable, o tributaria prefiere "ingreso gravable para retención en la fuente del trabajador"?
4. **Umbral mínimo de gravable:** ¿hay algún piso operativo (p. ej. ignorar excesos menores a $10.000)?
5. **Alerta de nuevos casos:** ¿es útil para TH una notificación tipo "estos 2 empleados pasaron a tener apoyo gravable este mes"?
6. **Visibilidad de `motivo_elegibilidad`:** cuando una fila tenga todo en ceros, ¿quieren ver el motivo (pensionado, no encontrado, inactivo)?
7. **Indicador de planilla vacía:** ¿poner un banner "esta planilla no tiene detalles, verifique el período" cuando `detalles` viene vacío?

---

**Fuente:** verificación directa de:
- `siga/backend/modules/beneficios_salud/urls.py` (confirmación de que no existe endpoint `/apoyo-gravable/`)
- `siga/backend/modules/beneficios_salud/views.py` — `PlanillaCalcularView` (845–909), `PlanillaListView` (912–924), `PlanillaDetailView` (927–939), `PlanillaExportarView` (942–1035)
- `siga/backend/modules/beneficios_salud/serializers.py` — `PlanillaCalculoDetailSerializer` (199–218), `PoliticaPrepagadaSerializer` (97–115), `DetalleCalculoSerializer` (154–178)
- `siga/backend/modules/beneficios_salud/models.py` — `PoliticaPrepagada` (108–127), `PlanillaCalculo` (166–182), `DetalleCalculo` (185–211)
- Apoyo previo: `docs/contexto-modulos/03-planilla-80-20.md` para la fórmula y el flujo de `PlanillaCalcularView`.
