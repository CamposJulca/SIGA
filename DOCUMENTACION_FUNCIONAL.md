# SIGA - Documentacion Funcional

## 1. Proposito

SIGA es el modulo de gestion administrativa para beneficios de salud de Finagro. Permite cargar archivos Excel de proveedores, normalizar estructuras distintas, validar informacion de beneficiarios, consultar resultados, exportar consolidados y calcular la planilla de medicina prepagada segun la politica institucional vigente.

El sistema reduce la conciliacion manual de archivos de AXA Colpatria y Colsanitas, conserva trazabilidad por archivo y fila de origen, y entrega informacion lista para analisis, causacion y reportes.

## 2. Alcance funcional

| Capacidad | Descripcion |
|---|---|
| Carga de archivos | Recibe archivos Excel `.xls` o `.xlsx` mediante portal/API. |
| Deteccion de proveedor | Identifica AXA Colpatria o Colsanitas por nombre de archivo y, si hace falta, por columnas. |
| Persistencia del original | Guarda el archivo recibido en `storage/landing/{proveedor}/`. |
| Lectura flexible | Detecta la fila real de encabezados aunque existan filas introductorias. |
| Normalizacion | Convierte los esquemas propios de AXA y Colsanitas a un modelo unificado. |
| Validacion | Valida cedula, valores numericos, consistencia aritmetica y duplicados. |
| Registro de errores | Guarda errores y advertencias con fila de origen y descripcion. |
| Consulta de beneficios | Permite filtrar por archivo, proveedor, cedula y estado de validacion. |
| Exportacion consolidada | Genera Excel con hojas de consolidado, AXA y Colsanitas. |
| Novedades | Compara dos archivos y detecta nuevos, retirados y cambios de valor. |
| Dashboard | Entrega resumen ejecutivo de ultimos periodos, parentescos, proveedores y evolucion. |
| Medicina prepagada | Calcula planilla 80/20, cruza contra `prepagada.db`, aplica UVT y elegibilidad. |
| Reportes administrativos | Entrega causacion, conciliacion e informe EFR mensual. |

## 3. Actores

| Actor | Responsabilidad |
|---|---|
| Analista de Gestion Humana | Carga archivos, revisa errores, consulta beneficios y genera reportes. |
| Usuario administrativo | Consulta dashboard, exporta consolidados y revisa novedades. |
| Responsable de prepagada | Define politicas, administra pensionados/auxilios y calcula planillas. |
| SIGA | Procesa archivos, valida datos, calcula planillas y persiste resultados. |
| Proveedores de salud | Entregan archivos Excel con beneficiarios y valores facturados. |
| Kactus / `prepagada.db` | Fuente de cruce para datos laborales y periodos de medicina prepagada. |

## 4. Flujo funcional de beneficios de salud

1. El usuario carga un archivo Excel.
2. SIGA calcula el hash SHA256 del archivo.
3. SIGA detecta el proveedor por nombre o columnas.
4. El archivo se guarda en `storage/landing/`.
5. Se crea un registro `ArchivoRecibido` en estado `RECIBIDO`.
6. El estado cambia a `PROCESANDO`.
7. El lector Excel detecta encabezados y extrae metadatos de contrato/periodo.
8. El adaptador del proveedor convierte columnas al esquema unificado.
9. El validador separa registros validos, advertencias y errores fatales.
10. SIGA inserta beneficios y errores mediante carga masiva.
11. El archivo queda en estado `PROCESADO` o `ERROR`.
12. El usuario consulta resultados o exporta el consolidado.

## 5. Proveedores soportados

| Proveedor | Identificador tecnico | Deteccion | Formato esperado |
|---|---|---|---|
| AXA Colpatria | `axa` | Nombre contiene `AXA` o columnas `SUB CTO` y `NUMID`. | Excel `.xlsx` con columnas como `SUB CTO`, `NUMID`, `NUMERO ID.BEN`, `NOMBRE`, `PARENTESCO`, `SUBTOTAL`, `IVA`, `TOTAL`. |
| Colsanitas | `colsanitas` | Nombre contiene `COLSANITAS` o columna `Numero de Familia`. | Excel `.xls` o `.xlsx` con columnas como `Numero de Familia`, `Numero de Documento`, `Apellidos`, `Nombres`, `Cuota`, `Descuento Comercial`, `IVA`, `Total Us` o `Total`. |

## 6. Reglas de negocio de carga y validacion

| Codigo | Regla |
|---|---|
| RN-01 | El archivo debe llegar en el campo multipart `archivo`. |
| RN-02 | Si el usuario esta autenticado, se registra su username; si no, se acepta `usuario` del formulario o `anonimo`. |
| RN-03 | AXA no trae descuento separado; SIGA lo registra como `0`. |
| RN-04 | Colsanitas excluye filas resumen como `TOTAL FAMILIA`, `TOTAL CONTRATO`, `TOTAL GENERAL`, `SUBTOTAL` y `GRAN TOTAL`. |
| RN-05 | La cedula vacia o invalida genera error fatal `CEDULA_INVALIDA`; el registro no se inserta como beneficio. |
| RN-06 | `valor_base`, `iva` y `valor_total` deben ser numericos. Valores negativos en esos campos generan error fatal salvo filas de ajuste permitidas. |
| RN-07 | `descuento` puede ser negativo porque Colsanitas puede registrar ajustes de esa forma. |
| RN-08 | La consistencia aritmetica esperada es `valor_total = valor_base - descuento + iva`, con tolerancia de COP 1. |
| RN-09 | Diferencias aritmeticas mayores a COP 1 generan `ADVERTENCIA`, pero el registro se almacena. |
| RN-10 | Cedulas duplicadas dentro del mismo `sub_contrato` generan `CEDULA_DUPLICADA` como advertencia, no rechazo. |
| RN-11 | Una fila de ajuste Colsanitas con `valor_base = 0` y `valor_total < 0` se almacena como advertencia. |

## 7. Estados

### Archivo

| Estado | Significado |
|---|---|
| `RECIBIDO` | Archivo guardado y registro creado. |
| `PROCESANDO` | Lectura, normalizacion y validacion en curso. |
| `PROCESADO` | Proceso finalizado y contadores actualizados. |
| `ERROR` | El archivo no pudo procesarse completamente. |

### Registro

| Estado | Significado |
|---|---|
| `OK` | Registro valido sin observaciones. |
| `ADVERTENCIA` | Registro insertado, pero con duplicado, ajuste o diferencia aritmetica. |
| `ERROR` | Registro rechazado y guardado como `ErrorProcesamiento`. |

## 8. Datos principales consultables

| Dato | Descripcion |
|---|---|
| Archivo recibido | Nombre, proveedor, ruta, fecha, hash, usuario, estado, contrato, periodo y contadores. |
| Beneficio de salud | Cedula, nombre, parentesco, subcontrato, titular, proveedor, plan, valores, fechas y estado. |
| Error de procesamiento | Archivo, fila de origen, tipo de error, descripcion, valor encontrado y timestamp. |
| Politica prepagada | Porcentajes empresa/empleado, limite UVT, valor UVT, conceptos contables y vigencia. |
| Planilla | Periodo, politica, totales empresa/empleado, gravable/no gravable y detalles por cedula. |

## 9. Funcionalidades de consulta y reporte

| Funcion | Resultado |
|---|---|
| Listar archivos | Historial de archivos con filtros por proveedor y estado. |
| Ver detalle de archivo | Informacion del archivo y errores asociados. |
| Listar beneficios | Registros normalizados con filtros de consulta. |
| Exportar beneficios | Excel con hojas `Consolidado`, `AXA Colpatria` y `Colsanitas`. |
| Novedades | Nuevos afiliados, retirados y cambios de valor entre dos archivos. |
| Dashboard | Ultimos periodos, distribucion por parentesco/proveedor, evolucion y consolidado. |
| Cruce | Periodos disponibles y registros cruzados desde `prepagada.db`. |
| Planilla | Calculo, consulta, detalle y exportacion de medicina prepagada. |
| Causacion | Resumen por EPS de la planilla mas reciente de un periodo. |
| Conciliacion | Comparacion entre dos periodos de planilla. |
| Informe EFR | Informe mensual con planilla, pensionados activos y auxilios externos. |

## 10. Medicina prepagada 80/20

SIGA calcula medicina prepagada a partir de los registros de `v_cruce` en `prepagada.db` y una politica vigente.

Reglas funcionales:

| Caso | Resultado |
|---|---|
| Empleado con cruce Kactus `OK` | Aplica distribucion segun politica, normalmente 80 empresa / 20 empleado. |
| Pensionado activo | Se marca `PENSIONADO_100`; el 100% queda a cargo del pensionado/empleado. |
| Cruce diferente de `OK` | Se marca `BLOQUEADO_CRUCE`; no se calcula aporte empresa. |
| Apoyo empresa superior al limite UVT | La parte hasta el limite es no gravable y el excedente queda gravable. |

## 11. Salidas del sistema

| Salida | Uso |
|---|---|
| Registros en base `bs_*` | Persistencia operacional y trazabilidad. |
| Archivos en `storage/landing/` | Evidencia del Excel original recibido. |
| Exportacion beneficios | Archivo Excel consolidado para revision o contabilidad. |
| Exportacion planilla | Excel de planilla 80/20 y hoja de apoyo gravable. |
| Respuestas API JSON | Consumo desde portal o integraciones. |

