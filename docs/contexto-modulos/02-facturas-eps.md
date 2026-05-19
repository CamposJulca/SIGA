# Módulo 2 — Facturas EPS: Investigación Técnica

| Campo         | Valor                                                                  |
|---------------|------------------------------------------------------------------------|
| Fecha         | 2026-05-13                                                             |
| Generado por  | Verificación directa de código fuente                                   |
| Alcance       | 4 bloques UI + comportamientos detectados en pantallas reales           |
| Archivos leídos | `views.py`, `urls.py`, `serializers.py`, `models.py`, `services/*.py`, `admin.py` |

---

## Bloque 1 — Cargar archivo de proveedor

### Flujo real (resumen en lenguaje funcional)

1. El usuario sube un archivo Excel desde el portal.
2. SIGA calcula la huella SHA256 del archivo (**solo para almacenarla**, no para rechazar duplicados).
3. SIGA intenta identificar el proveedor por el **nombre del archivo**. Si no lo logra, lo marca como `desconocido` y sigue.
4. Crea la carpeta `storage/landing/{axa_colpatria | colsanitas | desconocido}/` si no existe y **escribe el archivo** allí. Si ya existía un archivo con el mismo nombre, **lo sobrescribe sin avisar**.
5. Crea un registro `ArchivoRecibido` en estado `RECIBIDO`.
6. Cambia el estado a `PROCESANDO`.
7. Llama al lector de Excel. Si el proveedor seguía siendo `desconocido`, vuelve a intentar detectarlo por las **columnas** del DataFrame leído.
8. Si el proveedor todavía es `desconocido`, lanza error: el archivo queda en estado `ERROR` con el `ArchivoRecibido` ya creado (no se elimina).
9. Llama al adaptador correspondiente (AXA o Colsanitas). El adaptador normaliza al esquema común.
10. Llama al validador: cada fila queda como `OK`, `ADVERTENCIA` (se inserta) o rechazada (no se inserta, va a `ErrorProcesamiento`).
11. Inserta en lote los beneficios válidos y los errores.
12. Actualiza contadores y deja el archivo en estado `PROCESADO`.

### Evidencia técnica

- **Archivo:** `siga/backend/modules/beneficios_salud/views.py`
- **Clase:** `UploadView.post`
- **Líneas:** 79–197

Pasos clave con número de línea:

| Paso                                                       | Líneas       |
|-------------------------------------------------------------|--------------|
| Recibir archivo                                              | 80–85        |
| Resolver usuario (sesión / form / `'anonimo'`)               | 87–91        |
| Calcular hash SHA256                                          | 94           |
| Detectar proveedor por nombre                                 | 97           |
| Guardar en disco                                              | 101 (llama a `_guardar_archivo`, 48–69) |
| Crear `ArchivoRecibido` en `RECIBIDO`                         | 109–116      |
| Cambiar a `PROCESANDO`                                        | 120–121      |
| Leer Excel + metadatos                                        | 124          |
| Re-detectar por columnas si era `desconocido`                | 127–129      |
| Actualizar `numero_contrato` y `periodo_facturacion`         | 131–133      |
| Adaptador AXA / Colsanitas / error                            | 136–144      |
| Total registros                                                | 149–151      |
| Validar registros                                              | 154          |
| `bulk_create` beneficios y errores                             | 157–162      |
| Calcular contadores                                            | 164–166      |
| Marcar `PROCESADO`                                              | 171         |
| Responder 201                                                  | 178–185      |
| Catch general → `ERROR`                                        | 187–197      |

### Validaciones que aplica

Las cuatro reglas reales del validador (`services/validator.py`):

| Validación                                                              | Resultado                                                              | Líneas |
|--------------------------------------------------------------------------|------------------------------------------------------------------------|--------|
| Cédula vacía / `nan`                                                      | Error `CEDULA_INVALIDA` → **no inserta** el registro                    | 48–59  |
| `valor_base`/`iva`/`valor_total` no numéricos                             | Error `VALOR_INVALIDO` → **no inserta**                                 | 79–95  |
| `valor_base`/`iva`/`valor_total` negativos (salvo ajuste Colsanitas)      | Error `VALOR_INVALIDO` → **no inserta**                                 | 100–121 |
| Fila de ajuste Colsanitas (`valor_base=0` y `valor_total<0`)              | Inserta con `ADVERTENCIA`                                                | 100–103, 131 |
| Diferencia aritmética `\|valor_total − (valor_base − descuento + iva)\| > 1` | Inserta con `ADVERTENCIA`                                                 | 129–132 |
| Duplicado por `(cedula, sub_contrato)` dentro del mismo archivo           | Inserta con `ADVERTENCIA` + registra aviso `CEDULA_DUPLICADA`             | 34–40, 65, 131, 157–167 |

### Comportamientos confirmados / refutados

| # | Pregunta                                                                | Veredicto | Evidencia |
|---|--------------------------------------------------------------------------|-----------|-----------|
| 1 | ¿El hash SHA256 rechaza archivos duplicados?                              | ❌ **No** | `views.py` líneas 94, 109–116. El hash se calcula, se almacena en `ArchivoRecibido.hash_archivo`, pero **nunca se consulta antes de crear el registro**. `grep -n "hash_archivo" views.py` → 1 sola aparición (escritura). No hay `filter(hash_archivo=...)` en ninguna parte. |
| 2 | ¿`BeneficioSalud` tiene `unique_together` o constraint contra `(cedula, periodo)`/`(cedula, archivo_id)`? | ❌ **No** | `models.py` líneas 72–76: el `Meta` de `BeneficioSalud` solo tiene `db_table`, `ordering`, `verbose_name`. **Cero constraints únicos.** Búsqueda global confirma: el único `unique=True` en el módulo está en `PensionadoPrepagada.cedula` (línea 131). |
| 3 | Si cargo el mismo archivo dos veces, ¿se inserta el doble de registros en `BeneficioSalud`? | ✅ **Sí, se duplica** | Combinación de #1 y #2: el archivo entra dos veces, genera dos `ArchivoRecibido` (con IDs distintos) y dos sets de `BeneficioSalud` con `archivo_id` diferente. Nada los relaciona ni los deduplica. |
| 4 | ¿Detección por nombre primero, columnas después?                          | ✅ **Sí**  | `views.py` línea 97 (nombre) → `_leer_axa`/`_leer_colsanitas` necesita el proveedor para elegir motor; luego línea 127–129 vuelve a llamar al detector pasando las columnas. |
| 5 | Si detección falla, ¿se rechaza o se procesa como `desconocido`?         | ⚠️ **Mixto** | El archivo SÍ se guarda en disco (línea 101) y se crea `ArchivoRecibido` con `proveedor='desconocido'` (línea 109–116). Pero en línea 141–144 se lanza `ValueError` que cae al `except` línea 187–197 → archivo queda en `estado='ERROR'`. **El registro persiste, el archivo en disco persiste, pero no se procesan beneficios.** |
| 6 | Persistencia: ¿sobrescribe si el nombre se repite?                        | ✅ **Sí, sin avisar** | `_guardar_archivo` línea 65: `with open(ruta_destino, 'wb') as f:` → modo `wb` reemplaza el contenido del archivo si ya existe. No hay `if os.path.exists`. |

> ⚠️ **Implicación crítica:** las cargas duplicadas que se ven en la UI (mismo Colsanitas el 16/03 y 20/03) **sí están generando duplicados a nivel de fila en `BeneficioSalud`**. Pero **el archivo físico en disco es uno solo** (la segunda carga sobrescribió la primera). Si una auditoría futura quisiera ver el contenido exacto del archivo cargado el 16/03, ya no existe.

---

## Bloque 2 — Historial de archivos procesados

### Flujo real

- La tabla se alimenta desde `GET /api/beneficios-salud/archivos/`.
- Sin parámetros, devuelve **todos** los archivos cargados (`PROCESADO`, `ERROR`, `RECIBIDO`, `PROCESANDO`), ordenados por fecha de recepción descendente.
- Admite filtros `?proveedor=X` y `?estado=X`.
- "Ver detalle" pega a `GET /archivos/<id>/` y trae los errores anidados.
- "Excel" pega a `GET /exportar/?archivo_id=<id>` y descarga `.xlsx` con tres hojas.

### Evidencia técnica

| Operación              | Vista                             | Líneas (views.py) | Serializer                              |
|-------------------------|------------------------------------|-------------------|------------------------------------------|
| Listar historial         | `ArchivoListView.get`              | 200–218           | `ArchivoRecibidoListSerializer` (serializers.py 50–66) |
| Ver detalle              | `ArchivoDetailView.get`            | 221–236           | `ArchivoRecibidoDetailSerializer` (50–90) — incluye `errores` anidados |
| Exportar Excel           | `ExportarExcelView.get`            | 268–378           | Genera workbook con `Consolidado`, `AXA Colpatria`, `Colsanitas` |

Orden por defecto en la lista (model `Meta`):

```python
# models.py líneas 30–34
class Meta:
    db_table = 'bs_archivos_recibidos'
    ordering = ['-fecha_recepcion']
```

### Conteos: qué representa cada uno

| Campo                    | Cómo se calcula                                                                                  | Línea views.py |
|--------------------------|---------------------------------------------------------------------------------------------------|-----------------|
| `total_registros`        | `len(df_unificado)` — filas que llegaron del adaptador.                                            | 149             |
| `registros_procesados`   | `len(registros_ok)` — filas que el validador retornó. **Incluye las que quedaron en `ADVERTENCIA`**, no solo las `OK`. | 164             |
| `registros_con_error`    | `total_registros - registros_procesados`. Es decir: filas rechazadas (cédula inválida, valor inválido). | 166             |

> El "Errores=0 con Total = Procesados" que se ve en la UI ocurre cuando ninguna fila fue rechazada. Las advertencias (diferencia aritmética, duplicado) **no cuentan como error** en este contador — pasan a "procesadas" y al detalle de errores como avisos.

### Comportamientos confirmados / refutados

| # | Pregunta                                                                | Veredicto | Evidencia |
|---|--------------------------------------------------------------------------|-----------|-----------|
| 1 | ¿La lista está ordenada por fecha desc?                                  | ✅ **Sí** | `ArchivoRecibido._meta.ordering = ['-fecha_recepcion']`. |
| 2 | ¿Existe lógica de DELETE de `ArchivoRecibido` en la API?                  | ❌ **No** | `grep -n "def delete" views.py` → solo `PensionadoDetailView` (line 771) y `AuxilioExternoDetailView` (line 830). No hay método DELETE en ninguna vista de archivos. |
| 3 | Entonces, ¿cómo desaparece el #8 del historial?                           | ⚠️ **Hipótesis: borrado vía /admin/** | `admin.py` líneas 9–34: `ArchivoRecibido` y `BeneficioSalud` están **registrados en el admin de Django** y por defecto el `ModelAdmin` permite borrar. Una persona con credenciales de admin pudo eliminar el #8. **Alternativa:** un INSERT falló después de reservar el ID (SQLite/Postgres no lo recicla). No hay forma de distinguir cuál ocurrió sin logs. |
| 4 | ¿"Ver detalle" trae los errores anidados?                                  | ✅ **Sí** | `ArchivoRecibidoDetailSerializer` line 71: `errores = ErrorProcesamientoSerializer(many=True, read_only=True)`. |
| 5 | ¿"Excel" genera el archivo en el servidor o al vuelo?                      | ✅ **Al vuelo, sin guardar** | `ExportarExcelView` líneas 326–377: crea `openpyxl.Workbook()` en memoria, escribe a `BytesIO`, retorna como `HttpResponse`. No persiste nada en `storage/`. |
| 6 | Sin `archivo_id`, ¿exportar qué hace?                                       | ⚠️ **Toma el último procesado de CADA proveedor** | Líneas 298–309: si no se pasa `archivo_id`, calcula `Max('id')` agrupado por proveedor y filtra. **Esto significa que el "Excel" global ignora archivos previos del mismo proveedor.** |

---

## Bloque 3 — Consulta por funcionario

### Flujo real

- El buscador pega a `GET /api/beneficios-salud/beneficios/?cedula=<numero>`.
- Devuelve **todos** los `BeneficioSalud` con esa cédula exacta, **sin distinct, sin paginar**. Si la cédula aparece en 5 archivos distintos, retorna 5 filas (una por archivo).
- La búsqueda es **exacta** (`filter(cedula=X)`), **no es LIKE** ni admite parciales.

### Evidencia técnica

| Operación              | Vista                             | Líneas (views.py) | Serializer                       |
|-------------------------|------------------------------------|-------------------|-----------------------------------|
| Consulta por cédula     | `BeneficioListView.get`            | 239–265           | `BeneficioSaludSerializer` (serializers.py 22–47) |

Snippet del filtro:

```python
# views.py líneas 245–258
qs = BeneficioSalud.objects.select_related('archivo').all()
...
cedula = request.query_params.get('cedula')
if cedula:
    qs = qs.filter(cedula=cedula)
```

### Campo "Período" vacío — diagnóstico

**Veredicto:** ✅ **Es un bug de serializer / falta de campo expuesto.**

Evidencia:

1. **`BeneficioSalud` NO tiene campo `periodo`.**
   - `models.py` líneas 40–79: campos del modelo incluyen `numero_contrato`, `archivo_origen`, `fecha_corte`, `fecha_procesamiento`, pero **no `periodo` ni `periodo_facturacion`**.
2. **El periodo está en `ArchivoRecibido`.**
   - `models.py` línea 28: `periodo_facturacion = models.CharField(max_length=50, blank=True)`.
3. **El serializer no lo navega.**
   - `BeneficioSaludSerializer` (serializers.py 22–47) **no expone** ningún campo de `archivo.periodo_facturacion`. Aunque el queryset usa `select_related('archivo')` (line 246), el serializer no proyecta esa relación.

Por eso, en la UI:
- **Dashboard** sí ve el periodo porque `DashboardView` consulta directamente `ArchivoRecibido.periodo_facturacion` (líneas 537–553).
- **Consulta por funcionario** ve `—` porque el JSON de respuesta no incluye ningún campo de periodo.

**Pregunta para el equipo:** ¿el "período" en BD está poblado correctamente o el extractor de metadatos también falla? Lo que es seguro es que **aunque estuviera poblado, este endpoint no lo expondría hoy**.

### Estado "OK" — choices reales

Definidos en `models.py` líneas 41–45:

```python
ESTADO_CHOICES = [
    ('OK', 'OK'),
    ('ERROR', 'Error'),
    ('ADVERTENCIA', 'Advertencia'),
]
```

Default: `'OK'` (line 70).

Cuándo se aplica cada uno (de `validator.py`):

| Estado         | Condición                                                                 |
|----------------|---------------------------------------------------------------------------|
| `OK`           | Pasa todas las validaciones; sin advertencias.                              |
| `ADVERTENCIA`  | Pasa cédula y valores numéricos pero: diferencia aritmética > 1, ó duplicado por `(cedula, sub_contrato)`, ó fila de ajuste Colsanitas. Línea 131. |
| `ERROR`        | **Nunca se asigna en el flujo actual.** El choice existe en el modelo, pero ninguna línea del validador asigna `estado_validacion='ERROR'`. Los rechazos van a `ErrorProcesamiento`, no a `BeneficioSalud`. |

> ⚠️ **Hallazgo curioso:** el choice `ERROR` es **letra muerta** en `BeneficioSalud`. Si la UI muestra "estados posibles", ese valor jamás aparece en datos reales. Es residual.

### Comportamientos confirmados / refutados

| # | Pregunta                                              | Veredicto | Evidencia |
|---|--------------------------------------------------------|-----------|-----------|
| 1 | ¿La búsqueda es exacta o LIKE?                          | **Exacta** | `views.py` línea 258: `qs.filter(cedula=cedula)`. |
| 2 | ¿Devuelve todos los históricos o solo el más reciente?  | **Todos los históricos** | No hay `latest`, `distinct` ni `[:1]`. |
| 3 | ¿Por qué el campo Período aparece `—`?                  | **El serializer no lo expone** | `BeneficioSaludSerializer` no incluye `archivo.periodo_facturacion`. |
| 4 | ¿Existen `BeneficioSalud` con estado `ERROR`?            | **No deberían existir hoy** | El validador nunca asigna ese valor; los errores se van a `ErrorProcesamiento`. |

---

## Bloque 4 — Novedades entre períodos

### Flujo real

- Endpoint: `GET /api/beneficios-salud/novedades/?archivo_nuevo=<id>&archivo_anterior=<id>`.
- Compara **dos archivos cualquiera** (no dos periodos): se pasan los IDs.
- Carga los registros de cada archivo, indexados **por cédula sola** (no por `(cedula, sub_contrato)`).
- Calcula:
  - **Nuevos**: cédulas en el nuevo que no estaban en el anterior.
  - **Retirados**: cédulas en el anterior que no están en el nuevo.
  - **Cambios de valor**: cédulas en ambos con diferencia `|valor_total_nuevo − valor_total_anterior| > 1`.
  - **Sin cambios**: cédulas en ambos con diferencia ≤ 1.
- Si los proveedores difieren, **agrega un warning al JSON pero ejecuta igual** la comparación.
- Todo va en una sola respuesta (no hay paginación).

### Evidencia técnica

- **Archivo:** `views.py`
- **Clase:** `NovedadesView.get`
- **Líneas:** 381–509

Snippet clave del cruce:

```python
# views.py líneas 422–430
qs_nuevo = BeneficioSalud.objects.filter(archivo_id=archivo_nuevo_id).values(
    'cedula', 'nombre', 'parentesco', 'valor_total'
)
qs_anterior = BeneficioSalud.objects.filter(archivo_id=archivo_anterior_id).values(
    'cedula', 'nombre', 'parentesco', 'valor_total'
)

mapa_nuevo    = {r['cedula']: r for r in qs_nuevo}
mapa_anterior = {r['cedula']: r for r in qs_anterior}
```

> ⚠️ **Detalle importante:** al construir `mapa_nuevo` y `mapa_anterior` como `{cedula: registro}`, **si una cédula aparece dos veces en el mismo archivo** (caso típico: titular y beneficiario con el mismo número, o duplicado real entre familias), **solo queda la última ocurrencia**. La comparación pierde información. La validación interna del adaptador permite duplicados por `(cedula, sub_contrato)` como advertencia, pero esta vista cruza solo por cédula.

Snippet del warning sin bloqueo:

```python
# views.py líneas 414–419
warning = None
if archivo_nuevo.proveedor != archivo_anterior.proveedor:
    warning = (
        f'Los archivos son de distinto proveedor: '
        f'"{archivo_nuevo.proveedor}" vs "{archivo_anterior.proveedor}".'
    )
# ... continúa con la comparación normal ...
```

### Comportamientos confirmados / refutados

| # | Pregunta                                                                  | Veredicto | Evidencia |
|---|----------------------------------------------------------------------------|-----------|-----------|
| 1 | ¿Cruza por `(cedula, sub_contrato)` o solo `cedula`?                       | **Solo cédula** | Líneas 429–430: `{r['cedula']: r for ...}`. El `sub_contrato` se pierde al indexar. |
| 2 | ¿Bloquea cuando los proveedores son distintos?                              | ❌ **No bloquea** | Líneas 414–419: agrega `warning` en el response pero **continúa con `qs_nuevo`/`qs_anterior` y arma la respuesta normal**. Las "19 nuevos / 17 retirados" en AXA vs Colsanitas son **simplemente el set-diff de cédulas**, una métrica sin sentido funcional. |
| 3 | ¿Esta validación cruzada es intencional o un bug de UX?                    | ⚠️ **Pregunta de negocio** | El código indica que el comportamiento de "warning sin bloqueo" es **deliberado** (es código explícito, no un fallback). Si se considera incorrecto, hay que decidir si debe bloquear (`HTTP 400`) o solo advertir. |
| 4 | ¿Los acordeones cargan vía endpoints separados?                             | ❌ **No** | Líneas 482–504: toda la respuesta (nuevos, retirados, cambios_valor, resumen) viaja en un solo JSON. Sin paginación. |
| 5 | ¿"Cambio de valor" usa `valor_total` de `BeneficioSalud`?                  | ✅ **Sí** | Línea 470: `if abs(vn_f - va_f) > 1.0:`. Compara `valor_total` (total facturado por la EPS), no el aporte 80/20. |
| 6 | ¿Hay validación contra mismos archivos (`archivo_nuevo == archivo_anterior`)? | ❌ **No** | Si se pasa el mismo `id` para ambos, el código ejecuta y retorna 0 nuevos, 0 retirados, 0 cambios. No es error, solo desperdicio. |

---

# Verificación de los casos observados en UI

| # | Caso UI                                                                  | Respuesta del código                                                                                                                  |
|---|---------------------------------------------------------------------------|----------------------------------------------------------------------------------------------------------------------------------------|
| 1 | `COLSANITAS FinagroFebr2026-1010227487.xls` cargado 2 veces (323 reg c/u) | ✅ **El código lo permite y duplica.** Sin filtro por hash (Bloque 1, #1), sin constraint único en `BeneficioSalud` (Bloque 1, #2). Hay 2 × 323 = **646 registros en BD** asociados a 2 `ArchivoRecibido` distintos. |
| 2 | `AXACOLPATRIA000800116398_111006130000.xlsx` cargado 2 veces (24 c/u)     | ✅ Igual que #1. **48 registros en BD.** |
| 3 | Historial salta del #7 al #9 (falta #8)                                    | ⚠️ **No hay DELETE en la API.** Lo más probable es borrado desde `/admin/` (admin.py registra `ArchivoRecibido`). Alternativa: un INSERT falló y la BD no recicla el ID (típico en Postgres). Sin logs no se puede afirmar cuál. |
| 4 | Cédulas correlativas `12345001, 12345002…`                                 | ❌ **No existe flag de "datos de prueba"** en `BeneficioSalud` ni en `ArchivoRecibido`. Conviven con datos reales sin distinción. |
| 5 | Período `—` en consulta por funcionario, "MARZO 2026" en dashboard         | ✅ **Bug de exposición.** El periodo está en `ArchivoRecibido.periodo_facturacion`. El dashboard lo lee directo de ahí. La consulta por funcionario lo perdería incluso si el campo estuviera poblado, porque el serializer (`BeneficioSaludSerializer`) no proyecta `archivo.periodo_facturacion`. |
| 6 | Dashboard dice 730 beneficiarios                                            | ⚠️ **El conteo del dashboard NO infla por cargas duplicadas** porque solo considera el último archivo procesado por proveedor (`Max('id')` líneas 527–533). **PERO**: si la última carga (la duplicada del 20/03) trae los mismos 323 registros, son 323 únicos. Si fueran de meses distintos sí habría riesgo. La 730 es: 323 (último Colsanitas) + N (último AXA con sus advertencias) + etc. Hay que validar con un query directo si el número cuadra. |

---

# Resumen ejecutivo del módulo

## ✅ Lo que SÍ hace

1. Procesa archivos Excel de AXA y Colsanitas, normaliza al esquema unificado y persiste fila por fila con trazabilidad de origen.
2. Detecta el proveedor en dos pasos: primero por nombre, luego por columnas.
3. Aplica las 4 validaciones documentadas (cédula, valores numéricos, consistencia aritmética con tolerancia ±$1, duplicados `(cedula, sub_contrato)`).
4. Persiste el archivo físico en `storage/landing/{proveedor}/`.
5. Calcula y almacena el SHA256 de cada archivo.
6. Ordena el historial por fecha de recepción descendente y permite filtros por proveedor y estado.
7. Expone detalle de archivo con errores anidados.
8. Exporta a Excel con tres hojas (Consolidado / AXA / Colsanitas).
9. Compara dos archivos arbitrarios y entrega nuevos / retirados / cambios de valor.
10. Distingue rechazo fatal (no inserta) de advertencia (inserta con flag).

## ❌ Lo que NO hace (aunque la doc o la UI sugieran que sí)

| # | NO hace                                                                                            | Riesgo                                                                                                  |
|---|-----------------------------------------------------------------------------------------------------|----------------------------------------------------------------------------------------------------------|
| 1 | **NO rechaza archivos con SHA256 duplicado.** El hash se almacena, nunca se compara.                  | Cargas dobles del mismo archivo generan datos duplicados. Caso #1 y #2 de la UI lo demuestran en vivo.   |
| 2 | **NO tiene constraint único** en `BeneficioSalud` (ni por cédula+periodo, ni por cédula+archivo).    | Si se duplica el archivo, se duplica fila por fila en la base.                                            |
| 3 | **NO bloquea sobrescritura del archivo físico** si el nombre se repite. Modo `'wb'` reemplaza.       | Pierdes evidencia del primer archivo cargado para auditoría.                                              |
| 4 | **NO expone el período en la consulta por funcionario.** El serializer no proyecta `archivo.periodo_facturacion`. | El campo aparece como `—` aunque exista en `ArchivoRecibido`.                                              |
| 5 | **NO expone DELETE de archivos en la API.** Pero los borrados son posibles desde `/admin/` de Django. | Saltos de ID son rastreables solo si hay logs del admin; sin trazabilidad operativa.                      |
| 6 | **NO bloquea comparar archivos de proveedores distintos**, solo agrega un `warning` en el JSON.      | TH puede creer que los conteos AXA-vs-Colsanitas son válidos cuando son una métrica sin sentido funcional. |
| 7 | **NO deduplica cuando la misma cédula está en ambos archivos** en la vista de novedades; el `dict[cedula]` colapsa duplicados internos del mismo archivo. | Subreporte de cambios reales si una cédula aparece más de una vez en el archivo.                            |
| 8 | **NO usa el choice `ERROR`** de `BeneficioSalud.estado_validacion`. Los rechazos van a `ErrorProcesamiento`, no quedan en el modelo de beneficios. | La UI sugiere 3 estados pero solo se ven 2 (`OK`, `ADVERTENCIA`).                                          |
| 9 | **NO marca "datos de prueba" vs "producción".** Cédulas `12345001…` y reales conviven sin distinción.   | El dashboard puede estar contando ambos como producción.                                                  |
| 10 | **NO valida `archivo_nuevo == archivo_anterior`** en novedades. Acepta cualquier combinación.        | Posible llamada sin sentido devuelve respuesta vacía sin error.                                            |

## ⚠️ Pendiente validar con TH (decisiones de negocio, no de código)

1. **Cargas duplicadas:** ¿debe el sistema **rechazar** una segunda carga del mismo SHA256, **sobrescribir** silenciosamente los registros, o **versionar** ambas cargas? Hoy las acumula como duplicados sin marca.
2. **Comparación entre proveedores distintos:** ¿debe **bloquear** (HTTP 400), **advertir y permitir**, o **forzar** mismo proveedor? Hoy solo agrega warning.
3. **Saltos de IDs en el historial:** ¿quién tiene credenciales del `/admin/` Django? ¿Es aceptable que se pueda borrar `ArchivoRecibido` desde ahí, o se debe deshabilitar el delete del admin?
4. **Campo período en consulta por funcionario:** ¿quieren verlo? Es un cambio menor de serializer (exponer `archivo.periodo_facturacion`), pero hay que confirmar el formato esperado.
5. **Borrado / corrección operativa de archivos cargados por error:** hoy la única forma es admin. ¿TH necesita una vista funcional propia ("anular carga") o se queda en admin?
6. **Datos de prueba conviviendo con producción:** ¿se purgan antes de la reunión / antes del go-live? ¿O se necesita marcar formalmente "ambiente de prueba" en `ArchivoRecibido`?
7. **Cédulas duplicadas en el mismo archivo:** hoy se guardan como ADVERTENCIA pero igual entran al cálculo. ¿Es correcto? La hipótesis "es titular en dos familias" (Colsanitas) está hardcodeada en el comentario del validador línea 32–33. Validar si es el caso real.

---

**Fuente:** verificación directa de:
- `siga/backend/modules/beneficios_salud/views.py`
- `siga/backend/modules/beneficios_salud/urls.py`
- `siga/backend/modules/beneficios_salud/serializers.py`
- `siga/backend/modules/beneficios_salud/models.py`
- `siga/backend/modules/beneficios_salud/admin.py`
- `siga/backend/modules/beneficios_salud/services/validator.py`
- `siga/backend/modules/beneficios_salud/services/reader_excel.py`
- `siga/backend/modules/beneficios_salud/services/axa_adapter.py`
- `siga/backend/modules/beneficios_salud/services/detector.py`
