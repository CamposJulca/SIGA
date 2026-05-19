# SIGA — Beneficios de Salud
## Sistema Inteligente de Gestión Administrativa · Finagro
### De la conciliación manual de facturas EPS a la gestión autónoma del beneficio.

---

## El Desafío Institucional

La gestión del beneficio de salud en Finagro operaba bajo un modelo de conciliación completamente manual, sin estandarización entre proveedores y sin trazabilidad del dato:

**La Carga Operativa:** Cada mes, el área de Gestión Humana recibía archivos Excel de dos aseguradoras (AXA Colpatria y Colsanitas) con estructuras de columnas distintas, convenciones de nombres diferentes y formatos de valores inconsistentes. Un analista debía descargar cada archivo, entender manualmente su estructura, limpiar los datos, filtrar registros inválidos, unificar los campos y consolidar la información en un reporte para procesar el pago y la causación contable.

**La Realidad:** Esta operación repetida cada período generaba riesgos de error humano en la conciliación de valores, duplicidades de beneficiarios no detectadas, trazabilidad nula ante reclamaciones de proveedores o auditorías internas, y dependencia total de la disponibilidad y el criterio del analista asignado. La liquidación de la medicina prepagada bajo el modelo 80/20 (empresa/empleado) se realizaba por fuera del sistema, sin garantía de consistencia con los límites de UVT vigentes.

---

## Propuesta de Valor

Hoy SIGA no solo procesa archivos Excel, está redefiniendo el modelo de gestión del beneficio de salud de Finagro: un pipeline ETL completo que **detecta automáticamente el proveedor**, **normaliza esquemas heterogéneos**, **valida la integridad aritmética de cada registro** y **calcula la liquidación 80/20 con base en la política institucional vigente**.

Esta transformación ha eliminado la conciliación manual, pasando de un proceso artesanal sin auditoría a un sistema con **validación fila por fila con número de origen en el Excel**, **exportación consolidada multi-proveedor en un solo archivo** y **cálculo automático de los apoyos gravables y no gravables por UVT**, todo desde el portal web sin intervención del equipo de TI.

---

## Tabla de Dimensiones

| DIMENSIÓN | SITUACIÓN ANTERIOR | ESTADO ACTUAL | IMPACTO |
|---|---|---|---|
| **Operativa (Gestión Humana)** | Conciliación manual de dos archivos Excel con estructuras distintas. Limpieza, filtrado y unificación artesanal por un analista. Sin registro de quién procesó ni cuándo. | Carga de archivo desde el portal → detección automática de proveedor → normalización → validación → almacenamiento. Un solo flujo, dos proveedores. | Eliminación total del reproceso manual. El analista carga el archivo y el sistema entrega resultados listos para causación. |
| **Control y Riesgo** | Sin deduplicación: el mismo beneficiario podía aparecer en múltiples cargas sin alertas. Sin validación aritmética: valores de IVA y totales podían no cuadrar. Sin trazabilidad de errores. | Deduplicación por cédula dentro del mismo sub-contrato. Validación aritmética por tolerancia (±COP 1.00). Cada error tiene número de fila original del Excel para auditoría. | **Cero errores silenciosos.** Todo registro que no supera validación es clasificado, almacenado con su causa y trazable hasta la fila exacta del archivo fuente. |
| **Tiempos de Ejecución ETL** | No medibles. Dependían de la disponibilidad del analista y la complejidad del archivo. Estimado histórico: 2–4 horas por periodo por proveedor. | **Fase E (Extracción):** <5 segundos. **Fase T (Transformación):** <10 segundos para lotes de 500 registros. **Fase L (Carga):** <3 segundos con insert masivo. Total ETL: **<20 segundos por archivo**. | Reducción de horas a segundos. Los archivos del período están disponibles para consulta y exportación inmediatamente después de la carga. |
| **Cálculo Prepagada 80/20** | Liquidación manual en hojas de cálculo externas. Sin control de límites UVT. Sin separación contable entre apoyo gravable y no gravable. Sin historial de políticas aplicadas. | Motor de cálculo automático configurable: `% empresa`, `% empleado`, `UVT límite`, `valor UVT` y códigos contables. Cruza con la base de datos Kactus vía `prepagada.db`. Genera planilla exportable. | Consistencia garantizada con la norma tributaria vigente. El modelo 80/20 se aplica de forma idéntica para cada empleado, con separación automática de apoyo gravable y no gravable. |
| **Talento y Capacidad** | Analistas de Gestión Humana dedicando entre 2 y 4 horas por período a tareas de limpieza, unificación y validación de datos. | Personal liberado de la operatividad documental. El sistema procesa, valida y consolida. El analista revisa resultados y aprueba la causación. | Reasignación del capital humano hacia análisis de calidad del beneficio y atención a colaboradores, no a la gestión del archivo. |
| **Trazabilidad y Auditoría** | Sin registro de versiones. Sin historial de archivos cargados. Sin forma de reconstruir qué datos se usaron en una causación pasada. | Cada archivo cargado queda persistido en disco (`storage/landing/{proveedor}/`). Cada registro tiene su `archivo_id`. Cada error tiene `fila_origen`, `tipo_error` y `descripcion`. | **Auditoría completa.** Ante cualquier reclamación de proveedor o revisión de auditoría interna, es posible reconstruir exactamente qué registros se procesaron, cuándo y con qué resultado. |
| **Consolidación Multi-Proveedor** | Reporte final generado manualmente unificando dos archivos con columnas distintas. Propenso a errores de mapeo. | Exportación automática a Excel con **tres hojas**: Consolidado (todos los proveedores), AXA Colpatria, Colsanitas. Formato y columnas unificados. | Un único archivo de reporte por período, listo para contabilidad. Sin riesgo de inconsistencia entre hojas. |

---

## Pipeline ETL — Detalle Técnico por Fase

### Arquitectura General

```
[Analista sube archivo Excel (.xlsx / .xls)]
               │
               ▼
┌──────────────────────────────────┐
│  FASE E — EXTRACCIÓN             │  detector.py + reader_excel.py
│  Hash → Proveedor → Excel parse  │
└─────────────────┬────────────────┘
                  │
                  ▼
┌──────────────────────────────────┐
│  FASE T — TRANSFORMACIÓN         │  axa_adapter.py / colsanitas_adapter.py
│  Normalización + Validación      │  validator.py
└─────────────────┬────────────────┘
                  │
                  ▼
┌──────────────────────────────────┐
│  FASE L — CARGA                  │  views.py → bulk_create()
│  Insert masivo + Registro estado │
└─────────────────┬────────────────┘
                  │
                  ▼
┌──────────────────────────────────┐
│  MÓDULO PREPAGADA 80/20          │  prepagada_service.py
│  Cruce Kactus + Cálculo planilla │  ← Disparado manualmente
└──────────────────────────────────┘
```

---

### FASE E — Extracción

**Responsable:** `services/detector.py` + `services/reader_excel.py`
**Disparador:** Carga manual de archivo desde el portal. Endpoint: `POST /api/beneficios-salud/upload/`

#### Sub-fases y tiempos de ejecución

| Sub-fase | Descripción | Tiempo estimado | Notas |
|---|---|---|---|
| **E.1 — Recepción y hash SHA256** | Al recibir el archivo, se calcula su huella SHA256 para deduplicación. Si ya existe un archivo con el mismo hash, la carga es rechazada antes de cualquier procesamiento. | **<100 ms** | Operación en memoria sobre el stream del archivo. Previene reprocesamiento accidental del mismo período. |
| **E.2 — Persistencia en disco** | El archivo se guarda en `storage/landing/{proveedor}/{nombre_original}` y se crea el registro `ArchivoRecibido` con estado `RECIBIDO`. | **<500 ms** | El proveedor puede ser desconocido en este punto; se usa el detectado en E.3. La ruta en disco queda registrada para auditoría. |
| **E.3 — Detección de proveedor** | Detección en dos niveles: (1) por nombre de archivo (busca "AXA" o "COLSANITAS" insensible a mayúsculas); (2) si el nombre no es concluyente, lee las primeras filas del Excel y detecta columnas características (`SUB CTO` → AXA; `Número de Familia` → Colsanitas). | **<200 ms** | El método por nombre de archivo no requiere abrir el Excel. El fallback por columnas escanea las primeras 20 filas para encontrar la cabecera real. |
| **E.4 — Detección de fila de cabecera** | Los archivos de ambos proveedores no necesariamente tienen la cabecera en la primera fila. El lector escanea las primeras 16–21 filas buscando marcadores específicos del proveedor antes de encontrar el `header_row` real. | **~200–500 ms** | Lectura parcial del Excel (solo primeras filas). Crítico para evitar errores de mapeo de columnas cuando el archivo tiene filas de metadata al inicio. |
| **E.5 — Extracción de metadata del archivo** | Antes de leer los datos, se extraen del Excel: `numero_contrato` y `periodo_facturacion`. Estos están en filas de encabezado del archivo, no en las columnas de datos. | **<100 ms** | El período (ej: `202403`) y el número de contrato quedan asociados al `ArchivoRecibido` para filtrado y consulta posterior. |
| **E.6 — Lectura del DataFrame** | El Excel se lee completo con pandas desde la fila de cabecera detectada. Motor: `openpyxl` para `.xlsx`, `xlrd` para `.xls` (Colsanitas). | **~500 ms – 3 seg** según tamaño | Archivos típicos: 100–800 filas. El estado del `ArchivoRecibido` pasa a `PROCESANDO`. |

#### Métricas de volumen por archivo

| Indicador | Valor típico |
|---|---|
| Filas por archivo AXA Colpatria | 100–400 beneficiarios |
| Filas por archivo Colsanitas | 50–250 beneficiarios |
| Archivos por período | 2 (uno por proveedor) |
| Tiempo total Fase E | **< 5 segundos** |

#### Estructura de salida de la Fase E

```
/storage/landing/
├── axa_colpatria/
│   └── AXA_COLPATRIA_202403.xlsx     ← Archivo original persistido
└── colsanitas/
    └── COLSANITAS_202403.xls          ← Archivo original persistido
```

```
ArchivoRecibido {
  id:                    42,
  proveedor:             "axa_colpatria",
  nombre_archivo:        "AXA_COLPATRIA_202403.xlsx",
  ruta_archivo:          "storage/landing/axa_colpatria/AXA_COLPATRIA_202403.xlsx",
  hash_sha256:           "a3f9...",
  numero_contrato:       "12345",
  periodo_facturacion:   "202403",
  estado_procesamiento:  "PROCESANDO",
  total_registros:       150,
  usuario_carga:         "gestion.humana@finagro.com.co"
}
```

---

### FASE T — Transformación

**Responsable:** `services/axa_adapter.py`, `services/colsanitas_adapter.py`, `services/validator.py`
**Disparador:** Inmediatamente después de la Fase E, en el mismo request de carga.

La Transformación se divide en dos etapas secuenciales:

#### Etapa T.1 — Normalización por Adaptador

Cada proveedor tiene un adaptador dedicado que traduce su esquema nativo al esquema unificado de `BeneficioSalud`.

**Mapeo AXA Colpatria (`axa_adapter.py`):**

| Campo origen (Excel AXA) | Campo destino (BeneficioSalud) | Tratamiento |
|---|---|---|
| `SUB CTO` | `sub_contrato` | String directo |
| `NUMID` | `cedula_titular` | String directo |
| `NUMERO ID.BEN` | `cedula` | String directo (beneficiario real) |
| `NOMBRE` | `nombre` | String directo |
| `PARENTESCO` | `parentesco` | String directo |
| `SUBTOTAL` | `valor_base` | Decimal |
| *(sin campo)* | `descuento` | Forzado a `0` |
| `IVA` | `iva` | Decimal |
| `TOTAL` | `valor_total` | Decimal |
| `PLAN` | `tipo_plan` | String directo |

**Mapeo Colsanitas (`colsanitas_adapter.py`):**

| Campo origen (Excel Colsanitas) | Campo destino (BeneficioSalud) | Tratamiento |
|---|---|---|
| `Número de Familia` | `sub_contrato` | String directo |
| `Número de Documento` | `cedula` | String directo |
| `Apellidos` + `Nombres` | `nombre` | Concatenación con espacio |
| `Parentesco` | `parentesco` | String directo |
| `Cuota` | `valor_base` | Decimal |
| `Descuento Comercial` | `descuento` | Decimal (puede ser negativo en ajustes) |
| `IVA` | `iva` | Decimal |
| `Total` | `valor_total` | Decimal |
| `Plan` | `tipo_plan` | String directo |

**Filtros especiales de Colsanitas:**
- Se eliminan filas de totales antes del mapeo: `TOTAL FAMILIA`, `TOTAL CONTRATO`, filas con nombre vacío o con `Cuota == 0` y `Total > 0`.
- Filas con `Cuota == 0` y `Total < 0` (ajustes negativos) se conservan pero se marcan como `ADVERTENCIA`.

**Tiempos de la etapa T.1:**

| Sub-fase | Tiempo estimado |
|---|---|
| Filtrado de filas inválidas (Colsanitas) | **<100 ms** |
| Mapeo de columnas y construcción del DataFrame normalizado | **~100–300 ms** para 500 filas |
| Conversión de tipos (Decimal, str) | **<50 ms** |

#### Etapa T.2 — Validación (`validator.py`)

Cada fila del DataFrame normalizado pasa por cuatro validaciones secuenciales:

| Validación | Regla | Estado si falla | Tipo de error |
|---|---|---|---|
| **V.1 — Cédula presente** | `cedula` no es nulo, vacío ni `NaN` | `ERROR` | `CEDULA_INVALIDA` |
| **V.2 — Valores numéricos** | `valor_base`, `iva`, `valor_total` son numéricos y ≥ 0 | `ERROR` | `VALOR_INVALIDO` |
| **V.3 — Consistencia aritmética** | `|valor_total - (valor_base - descuento + iva)| ≤ COP 1.00` | `ADVERTENCIA` | Tolerancia excedida |
| **V.4 — Deduplicación** | La misma `cedula` no aparece dos veces en el mismo `sub_contrato` dentro del mismo archivo | `ADVERTENCIA` | `CEDULA_DUPLICADA` |

**Resultado de validación por registro:**

| Estado | Descripción | Se inserta en BD |
|---|---|---|
| `OK` | Pasó todas las validaciones | ✅ Sí, en `BeneficioSalud` |
| `ADVERTENCIA` | Pasó cédula y valores pero hay inconsistencia o duplicado | ✅ Sí, con estado `ADVERTENCIA` |
| `ERROR` | Falló validación de cédula o de valores | ❌ No. Se registra en `ErrorProcesamiento` |

**Tiempos de la etapa T.2:**

| Sub-fase | Tiempo estimado |
|---|---|
| Validación V.1 y V.2 (vectorizada con pandas) | **<50 ms** para 500 filas |
| Validación V.3 aritmética (tolerancia) | **<50 ms** |
| Validación V.4 deduplicación (groupby) | **<100 ms** |
| Separación en listas `registros_ok` y `errores` | **<50 ms** |

---

### FASE L — Carga

**Responsable:** `views.py` → `BeneficioSalud.objects.bulk_create()` + `ErrorProcesamiento.objects.bulk_create()`
**Disparador:** Inmediatamente después de la Fase T.

| Sub-fase | Descripción | Tiempo estimado | Notas |
|---|---|---|---|
| **L.1 — Insert masivo de beneficios válidos** | `BeneficioSalud.objects.bulk_create(registros_ok, batch_size=500)`. Un solo round-trip a la base de datos por cada 500 registros. | **<2 segundos** para 500 registros | Evita N inserts individuales. La transacción es atómica por batch. |
| **L.2 — Insert masivo de errores** | `ErrorProcesamiento.objects.bulk_create(errores, batch_size=500)`. Cada error incluye `fila_origen` (número de fila en el Excel original) y `descripcion` detallada. | **<500 ms** | Permite al analista ir directamente a la fila problemática en el archivo fuente. |
| **L.3 — Actualización de estado del archivo** | `ArchivoRecibido.estado_procesamiento = PROCESADO`. Actualiza contadores: `total_registros`, `registros_procesados`, `registros_con_error`. | **<100 ms** | Si el proceso falla en cualquier punto, el estado queda en `ERROR` con descripción del fallo. |

#### Estructura de salida de la Fase L

```
BeneficioSalud {
  id:                    1234,
  archivo_id:            42,
  cedula:                "79543211",
  nombre:                "GOMEZ RAMOS CARLOS ANDRES",
  parentesco:            "TITULAR",
  sub_contrato:          "A-001",
  proveedor:             "axa_colpatria",
  tipo_plan:             "COLECTIVO EMPRESARIAL",
  valor_base:            Decimal("850000.00"),
  descuento:             Decimal("0.00"),
  iva:                   Decimal("0.00"),
  valor_total:           Decimal("850000.00"),
  estado_validacion:     "OK",
  fecha_corte:           date(2024, 3, 31),
  fecha_procesamiento:   datetime(2024, 3, 15, 10, 23, 45)
}

ErrorProcesamiento {
  id:                    89,
  archivo_id:            42,
  fila_origen:           45,
  tipo_error:            "CEDULA_INVALIDA",
  descripcion:           "El campo cédula está vacío o es nulo",
  datos_fila:            '{"nombre": "PEREZ JUAN", "valor_total": "500000"}'
}
```

---

## Módulo Prepagada — Cálculo 80/20

Este módulo opera de forma independiente al pipeline ETL de facturas EPS. Se dispara manualmente desde el portal cuando el analista necesita generar la planilla de liquidación de medicina prepagada.

### Flujo de cálculo

```
[Analista selecciona período en el portal]
               │
               ▼
[GET /api/beneficios-salud/cruce/?periodo=202403]
               │
               ▼ prepagada_service.py
[Consulta v_cruce en prepagada.db (SQLite Kactus)]
   └─ Cruce: facturas_eps ⟕ empleados_kactus
   └─ Campos: cedula, nombre_kactus, eps, total_familia, sue_basi, tip_cont
               │
               ▼
[POST /api/beneficios-salud/planilla/calcular/]
               │
               ▼
[Para cada empleado en v_cruce:]
   ├─ valor_empresa   = total_familia × (% empresa / 100)          [def. 80%]
   ├─ valor_empleado  = total_familia × (% empleado / 100)         [def. 20%]
   ├─ limite_no_grav  = uvt_limite × valor_uvt                     [def. 16 UVT]
   ├─ apoyo_no_grav   = min(valor_empresa, limite_no_grav)
   └─ apoyo_gravable  = max(0, valor_empresa - limite_no_grav)
               │
               ▼
[PlanillaCalculo + DetalleCalculo → BD]
               │
               ▼
[GET /api/beneficios-salud/planilla/{id}/exportar/]
└─ Excel con detalle por empleado, códigos contables y totales
```

### Campos de la política 80/20 (configurables desde el portal)

| Parámetro | Descripción | Valor por defecto |
|---|---|---|
| `porcentaje_empresa` | Porcentaje que asume Finagro | 80% |
| `porcentaje_empleado` | Porcentaje que asume el colaborador | 20% |
| `uvt_limite` | Unidades de Valor Tributario máximas no gravables | 16 UVT |
| `valor_uvt` | Valor en COP de una UVT (actualizado anualmente) | Configurable |
| `cod_conc_apoyo_no_grav` | Código contable del apoyo no gravable | Configurable |
| `cod_conc_apoyo_grav` | Código contable del apoyo gravable | Configurable |
| `cod_conc_dcto_empleado` | Código contable del descuento al empleado | Configurable |

### Fuente de datos externa: `prepagada.db`

| Tabla / Vista | Descripción |
|---|---|
| `facturas_eps` | Facturas de EPS con beneficiarios y valores por familia |
| `empleados_kactus` | Planta de personal activa de Finagro desde Kactus |
| `v_cruce` | Vista que cruza ambas tablas: identifica qué empleados tienen medicina prepagada activa, cuántos beneficiarios tienen, el valor total mensual de su familia y su salario básico |

---

## Indicadores Operativos del Sistema

### Conteos en base de datos

| Indicador | Modelo / Fuente | Descripción |
|---|---|---|
| **Archivos cargados por período** | `ArchivoRecibido` filtrado por `periodo_facturacion` | Cuántos archivos se procesaron en un mes |
| **Total de beneficiarios activos** | `BeneficioSalud` con `estado_validacion = OK` | Registros válidos en la base consolidada |
| **Registros con advertencia** | `BeneficioSalud` con `estado_validacion = ADVERTENCIA` | Requieren revisión manual opcional |
| **Errores por archivo** | `ErrorProcesamiento` agrupado por `archivo_id` | Trazabilidad de calidad por archivo y proveedor |
| **Errores por tipo** | `ErrorProcesamiento` agrupado por `tipo_error` | Diagnóstico de problemas sistémicos en el archivo fuente |
| **Valor total facturado por proveedor** | `sum(valor_total)` en `BeneficioSalud` agrupado por `proveedor` | Conciliación con el valor facturado por la aseguradora |
| **Planillas 80/20 calculadas** | `PlanillaCalculo` filtrado por período | Historial de liquidaciones de prepagada |
| **Empleados con prepagada activa** | `DetalleCalculo` por `planilla_id` | Planta cubierta por el beneficio cada período |

### Distribución típica de estados por archivo

```
Archivo cargado: 150 registros

├─ OK           → 143 registros  (95.3%)  ← insertados en BeneficioSalud
├─ ADVERTENCIA  →   5 registros  ( 3.3%)  ← insertados con flag, requieren revisión
└─ ERROR        →   2 registros  ( 1.3%)  ← registrados en ErrorProcesamiento, NO insertados
```

---

## API de Consulta y Exportación

### Endpoints disponibles

| Método | Endpoint | Descripción |
|---|---|---|
| `POST` | `/api/beneficios-salud/upload/` | Carga y procesamiento de archivo Excel |
| `GET` | `/api/beneficios-salud/archivos/` | Listado de archivos (filtros: proveedor, estado, período) |
| `GET` | `/api/beneficios-salud/archivos/{id}/` | Detalle de archivo con lista de errores |
| `GET` | `/api/beneficios-salud/beneficios/` | Consulta de beneficiarios (filtros: archivo_id, cédula, proveedor, estado_validacion) |
| `GET` | `/api/beneficios-salud/exportar/` | Exporta a Excel consolidado (3 hojas: Consolidado, AXA, Colsanitas) |
| `GET` | `/api/beneficios-salud/dashboard/` | Estadísticas resumen por período |
| `GET` | `/api/beneficios-salud/novedades/` | Comparación entre dos archivos del mismo proveedor: altas, bajas, cambios |
| `GET` | `/api/beneficios-salud/causacion/` | Causación contable por período |
| `GET` | `/api/beneficios-salud/informe-efr/` | Indicadores EFR (Empresa Familiarmente Responsable) |
| `GET` | `/api/beneficios-salud/cruce/` | Datos de cruce Kactus-EPS desde prepagada.db |
| `POST` | `/api/beneficios-salud/planilla/calcular/` | Calcula planilla 80/20 para un período |
| `GET` | `/api/beneficios-salud/planilla/{id}/exportar/` | Exporta planilla a Excel con códigos contables |
| `GET/POST` | `/api/beneficios-salud/politica/` | Consulta y creación de políticas 80/20 |
| `GET/POST` | `/api/beneficios-salud/pensionados/` | Gestión de pensionados con prepagada |
| `GET` | `/api/beneficios-salud/auxilio-externo/` | Registros de auxilio externo |

---

## Manejo de Errores y Resiliencia

| Escenario | Comportamiento del sistema |
|---|---|
| **Archivo duplicado (mismo SHA256)** | Rechazado antes de cualquier procesamiento. Mensaje claro al usuario: "Este archivo ya fue cargado anteriormente". |
| **Proveedor no detectable** | Si ni el nombre del archivo ni las columnas permiten identificar el proveedor, se retorna error HTTP 400 con descripción. |
| **Fila de cabecera no encontrada** | El lector escanea hasta la fila 21. Si no encuentra marcadores del proveedor, lanza error descriptivo. |
| **Cédula vacía o nula** | El registro se guarda en `ErrorProcesamiento` con `tipo_error = CEDULA_INVALIDA` y `fila_origen` exacta. El proceso continúa con las demás filas. |
| **Valor no numérico** | El registro se guarda en `ErrorProcesamiento` con `tipo_error = VALOR_INVALIDO`. Proceso continúa. |
| **Inconsistencia aritmética** | El registro se inserta en `BeneficioSalud` con `estado_validacion = ADVERTENCIA`. No bloquea el proceso. |
| **Beneficiario duplicado** | El segundo registro se inserta con `estado_validacion = ADVERTENCIA` y `tipo_error = CEDULA_DUPLICADA`. Ambos quedan visibles para revisión. |
| **Error en base de datos durante bulk_create** | El estado del `ArchivoRecibido` pasa a `ERROR`. El archivo en disco queda preservado para reprocesamiento manual. |
| **prepagada.db no disponible** | El endpoint `/cruce/` retorna HTTP 500 con descripción del error de conexión. El resto del módulo opera normalmente. |
| **Formato `.xls` (Colsanitas antiguo)** | Detectado automáticamente por extensión. Motor `xlrd` en lugar de `openpyxl`. Sin intervención del usuario. |

---

## Organización de Archivos del Módulo

```
~/Finagro/siga/
├── backend/
│   ├── core/
│   │   ├── settings.py               ← Configuración Django, rutas BD, volúmenes
│   │   └── urls.py                   ← Registro de rutas del módulo
│   └── modules/beneficios_salud/
│       ├── models.py                 ← 8 modelos Django (BeneficioSalud, ArchivoRecibido, etc.)
│       ├── views.py                  ← 11 vistas API (upload, CRUD, exports, cálculos)
│       ├── serializers.py            ← Serializers DRF para todos los modelos
│       ├── admin.py                  ← Panel de administración con filtros y búsqueda
│       ├── urls.py                   ← 16 patrones de URL
│       ├── migrations/               ← Historial de migraciones de BD
│       └── services/
│           ├── detector.py           ← Detección de proveedor (nombre + columnas)
│           ├── reader_excel.py       ← Lectura de Excel con detección de cabecera
│           ├── axa_adapter.py        ← Normalización de esquema AXA Colpatria
│           ├── colsanitas_adapter.py ← Normalización de esquema Colsanitas
│           ├── validator.py          ← Validación fila a fila (4 tipos)
│           └── prepagada_service.py  ← Motor de cálculo 80/20
└── storage/
    └── landing/
        ├── axa_colpatria/            ← Archivos AXA persistidos en disco
        └── colsanitas/               ← Archivos Colsanitas persistidos en disco
```

---

## Modelos de Datos

### Modelo Principal: `BeneficioSalud`

| Campo | Tipo | Descripción |
|---|---|---|
| `archivo` | FK → ArchivoRecibido | Archivo de origen del registro |
| `cedula` | CharField | Cédula del beneficiario |
| `cedula_titular` | CharField | Cédula del titular del contrato (solo AXA) |
| `nombre` | CharField | Nombre completo del beneficiario |
| `parentesco` | CharField | Relación con el titular (TITULAR, CÓNYUGE, HIJO, etc.) |
| `sub_contrato` | CharField | Código de sub-contrato / núcleo familiar |
| `proveedor` | CharField | `axa_colpatria` o `colsanitas` |
| `tipo_plan` | CharField | Nombre del plan de salud |
| `valor_base` | DecimalField | Subtotal antes de descuentos e IVA |
| `descuento` | DecimalField | Descuento comercial aplicado |
| `iva` | DecimalField | IVA del servicio |
| `valor_total` | DecimalField | Valor final a pagar |
| `estado_validacion` | CharField | `OK`, `ADVERTENCIA` o `ERROR` |
| `fecha_nacimiento` | DateField | Fecha de nacimiento del beneficiario (si aplica) |
| `fecha_corte` | DateField | Fecha de corte del período |
| `fecha_procesamiento` | DateTimeField | Timestamp de procesamiento en el sistema |

### Modelo de Trazabilidad: `ArchivoRecibido`

| Campo | Tipo | Descripción |
|---|---|---|
| `proveedor` | CharField | Proveedor detectado |
| `nombre_archivo` | CharField | Nombre original del archivo |
| `ruta_archivo` | CharField | Ruta en disco (auditoría) |
| `hash_sha256` | CharField | Huella del archivo (deduplicación) |
| `estado_procesamiento` | CharField | `RECIBIDO` → `PROCESANDO` → `PROCESADO` / `ERROR` |
| `total_registros` | IntegerField | Filas leídas del Excel |
| `registros_procesados` | IntegerField | Filas insertadas exitosamente |
| `registros_con_error` | IntegerField | Filas rechazadas |
| `numero_contrato` | CharField | Extraído del Excel |
| `periodo_facturacion` | CharField | Período (ej: `202403`) |
| `usuario_carga` | CharField | Usuario que realizó la carga |
| `fecha_carga` | DateTimeField | Timestamp de carga |

---

## Glosario Técnico

| Término | Definición en el contexto de SIGA Beneficios de Salud |
|---|---|
| **ETL** | Extract, Transform, Load. Pipeline de datos: Extracción (lectura del Excel), Transformación (normalización + validación), Carga (insert en BD). |
| **Fase E** | Extracción: recepción del archivo, detección del proveedor y lectura del Excel. |
| **Fase T** | Transformación: normalización del esquema nativo del proveedor al esquema unificado y validación fila a fila. |
| **Fase L** | Carga: insert masivo en base de datos con bulk_create y actualización del estado del archivo. |
| **AXA Colpatria** | Aseguradora de salud. Sus archivos usan columnas en mayúsculas (`SUB CTO`, `NUMID`, `SUBTOTAL`). |
| **Colsanitas** | Aseguradora de salud. Sus archivos usan columnas en español formal y pueden estar en formato `.xls`. |
| **sub_contrato** | Código que agrupa a los beneficiarios de un mismo titular bajo un contrato de seguro. |
| **parentesco** | Relación del beneficiario con el titular: TITULAR, CÓNYUGE, HIJO, MADRE, PADRE, etc. |
| **SHA256** | Algoritmo de huella digital para deduplicación de archivos. Si el hash ya existe, el archivo es rechazado. |
| **bulk_create** | Operación de Django para insertar múltiples registros en un solo round-trip a la base de datos. |
| **fila_origen** | Número de fila en el Excel original donde se detectó el error. Permite al analista ubicarlo directamente. |
| **80/20** | Modelo de costo compartido: Finagro asume el 80% del valor de la medicina prepagada, el empleado el 20%. |
| **UVT** | Unidad de Valor Tributario. Define el límite no gravable del apoyo de la empresa a la medicina prepagada. |
| **apoyo no gravable** | Porción del aporte de Finagro que no genera retención en la fuente (hasta 16 UVT mensuales). |
| **apoyo gravable** | Porción del aporte de Finagro que supera el límite de UVT y constituye ingreso gravable para el empleado. |
| **v_cruce** | Vista en `prepagada.db` que cruza las facturas de EPS con la planta de Kactus para identificar empleados con prepagada activa. |
| **Kactus** | Sistema de nómina de Finagro. Sus datos se sincronizan en `prepagada.db` para el cruce de prepagada. |
| **EFR** | Empresa Familiarmente Responsable. Certificación que mide políticas de conciliación trabajo-familia. SIGA genera el informe de indicadores. |
| **causación** | Registro contable del gasto de salud por período, con los códigos de concepto correspondientes. |
| **novedades** | Comparación entre dos archivos del mismo proveedor: identifica altas (nuevos beneficiarios), bajas (retirados) y cambios de valor. |
| **DRF** | Django REST Framework. Librería que expone los modelos Django como API REST consumida por el frontend React. |
| **openpyxl / xlrd** | Motores de lectura de Excel. `openpyxl` para `.xlsx`, `xlrd` para `.xls` (formato legado de Colsanitas). |
