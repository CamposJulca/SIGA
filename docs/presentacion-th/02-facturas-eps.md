# Módulo 2 — Facturas EPS

| Campo                | Valor                                                                                                |
|----------------------|------------------------------------------------------------------------------------------------------|
| Orden en la cinta    | 2 / 8                                                                                                |
| Tiempo sugerido demo | 8 minutos                                                                                            |
| Estado               | Implementado                                                                                          |
| Fuente               | `docs/01-funcional/requerimientos-funcionales.md` (RF-101..113, RF-201..205); `casos-de-uso.md` (CU-001, CU-002, CU-003); `reglas-de-negocio.md` (RN-01..11) |

---

## En una frase

> Facturas EPS es **la puerta de entrada** del proceso: aquí TH carga los Excel mensuales de AXA Colpatria y Colsanitas, y el sistema los valida, los unifica y deja toda la trazabilidad lista.

## ¿Para qué sirve?

Resuelve el dolor histórico del área: dos archivos, dos formatos distintos, valores mezclados, sin trazabilidad. Cada mes, en lugar de limpiar y unificar a mano, TH sube el archivo y SIGA:

1. **Detecta automáticamente** si el archivo es de AXA o Colsanitas (por el nombre o por las columnas).
2. **Guarda el archivo original** intacto, para auditoría futura.
3. **Lee la cabecera real** del Excel, incluso si tiene filas de metadatos antes del encabezado.
4. **Normaliza** los campos a un esquema único, así no importa qué proveedor sea.
5. **Valida fila por fila**: cédula válida, valores numéricos, consistencia aritmética, duplicados.
6. **Clasifica** cada registro como OK, Advertencia o Error.
7. **Persiste todo** con la trazabilidad fila por fila.

Lo que antes tomaba **2–4 horas por proveedor por mes**, hoy queda en **menos de 20 segundos por archivo**.

## ¿Quién lo usa?

- Analista de Gestión Humana (uso principal mensual).
- Responsable de prepagada (consulta y revisión de errores).
- Usuario administrativo (consulta histórica y novedades).

## ¿Qué información entra?

- **Archivo Excel** del proveedor: `.xlsx` (AXA) o `.xls`/`.xlsx` (Colsanitas).
- Nombre del usuario que carga (si no hay autenticación activa).
- **Nada más**: el sistema extrae solo del archivo el número de contrato y el periodo de facturación.

> 📌 **Convención importante:** el nombre del archivo debe contener `AXA` o `COLSANITAS` para que la detección automática funcione al primer intento. Si no, SIGA intenta detectarlo por las columnas; si tampoco lo logra, lo marca como proveedor desconocido y lo rechaza.

## ¿Qué información sale?

- **Resumen del procesamiento**: total de registros, procesados correctamente, con advertencia y con error.
- **Listado histórico** de todos los archivos cargados, con filtros por proveedor y por estado.
- **Detalle por archivo**: cada error y advertencia con la **fila exacta del Excel** donde se detectó y la descripción del problema.
- **Exportación a Excel** consolidado, con tres hojas: Consolidado (los dos proveedores), AXA y Colsanitas por separado.
- **Comparativo de novedades** entre dos archivos: altas, bajas y cambios de valor.

## Flujo paso a paso (demo en vivo)

1. **Mostrar la pantalla principal**: drag-and-drop o botón "Seleccionar archivo".
2. **Subir un archivo AXA** real del mes. Mientras carga, decir:
   > "Está calculando una huella digital del archivo para reconocer si ya fue cargado, detectando el proveedor por el nombre, leyendo la cabecera real, validando cada fila…".
3. Cuando termine, **mostrar el resumen**: total / procesados / advertencias / errores.
4. **Abrir el detalle del archivo** y mostrar la lista de errores con su fila de origen. Explicar: "Si la EPS reclama, podemos ir directamente a esta fila del Excel original".
5. **Subir un archivo Colsanitas** y mostrar que el flujo es idéntico aunque el formato del archivo sea diferente.
6. **Ir al historial** y mostrar la lista de cargas anteriores. Filtrar por proveedor.
7. **Hacer el comparativo de novedades** entre el archivo del mes y el del mes anterior. Mostrar: nuevos afiliados, retirados, cambios de valor.
8. **Descargar el Excel consolidado** y abrirlo para mostrar las tres hojas.

> ⏱ Si el archivo tarda en cargarse, aprovechar para explicar las validaciones que están corriendo.

## Reglas de negocio aplicadas

| ID      | Regla en lenguaje de negocio                                                                                  |
|---------|----------------------------------------------------------------------------------------------------------------|
| RF-103  | El proveedor se detecta automáticamente por el nombre del archivo o, si hace falta, por las columnas.          |
| RF-104  | El archivo original siempre se guarda intacto en el sistema para auditoría.                                    |
| RF-105  | Cada archivo cargado queda registrado con su estado (Recibido → Procesando → Procesado / Error).                |
| RN-03   | AXA no trae descuento separado; el sistema lo registra como cero para mantener uniformidad.                    |
| RN-04   | Las filas resumen de Colsanitas (TOTAL FAMILIA, TOTAL CONTRATO, SUBTOTAL, GRAN TOTAL) se excluyen automáticamente. |
| RN-05   | Si una fila no trae cédula válida, el registro se rechaza y se guarda como error con su fila de origen.        |
| RN-06   | Los valores monetarios deben ser numéricos. Si algún campo está mal, el registro se rechaza.                    |
| RN-08/9 | El sistema verifica que `valor_total = valor_base − descuento + IVA` con tolerancia de COP 1. Diferencias mayores quedan como advertencia, pero el registro se almacena. |
| RN-10   | Si una misma cédula aparece dos veces dentro del mismo sub-contrato, queda registrada con advertencia, no se rechaza. |
| RN-11   | Las filas de ajuste de Colsanitas (cuota 0 y total negativo) se almacenan con advertencia, no se rechazan.      |
| MP-035/036 | AXA y Colsanitas se normalizan al mismo modelo unificado para que los reportes los presenten juntos.        |
| MP-037  | Si el archivo no parece de ninguno de los dos, el sistema lo rechaza explícitamente.                            |

## Lo que aún NO hace (y conviene mencionar)

- **No procesa automáticamente** archivos que lleguen por correo. La carga es manual: TH descarga del correo y sube al portal. *No hay integración con el correo corporativo.*
- **No envía notificaciones** cuando un archivo queda en Error. TH debe entrar al detalle para verlo.
- **Hoy no rechaza por sí solo un archivo duplicado** de manera automática (existe una inconsistencia documentada al respecto que vamos a verificar con código). El hash se guarda pero el comportamiento ante un mismo archivo cargado dos veces requiere validación.

> ⚠️ VALIDAR CON TH: confirmar si han tenido casos reales de carga doble del mismo archivo y cómo lo manejan hoy.

## Preguntas que probablemente nos harán (anticipadas)

- **P:** "¿Qué pasa si me equivoco y subo el archivo del mes anterior?"
  **R:** El archivo igual se procesa. SIGA detecta el periodo desde el contenido del Excel, así que queda registrado bajo el periodo real del archivo, no del momento de carga.

- **P:** "¿Y si la EPS me manda el archivo con un formato distinto al habitual?"
  **R:** Si las columnas siguen siendo las mismas (aunque la cabecera esté en otra fila), el sistema lo lee. Si cambian los nombres de columnas, debemos ajustar el lector.

- **P:** "¿Puedo borrar un archivo cargado por error?"
  **R:** *(VALIDAR CON EQUIPO SIGA: la funcionalidad de borrado no está confirmada en la documentación funcional consolidada.)*

- **P:** "Si una cédula sale como error, ¿qué hago?"
  **R:** Ese registro **no** entra a la base de beneficiarios. Hay que reportarlo a la EPS para corregirlo, o anotarlo como excepción si es un caso conocido.

## Preguntas que NOSOTROS le hacemos a TH (validación)

- [ ] ¿El formato actual de los archivos de AXA y Colsanitas se ha mantenido estable en los últimos 12 meses? ¿Ha cambiado en algún momento?
- [ ] ¿Han recibido alguna vez un archivo con la cabecera en una fila distinta a la habitual?
- [ ] ¿Cómo manejan hoy las advertencias por diferencia aritmética (RN-08/9)? ¿Las revisan o se aceptan?
- [ ] ¿Han tenido casos de cédulas duplicadas dentro del mismo sub-contrato? ¿Eso debería ser advertencia o error fatal?
- [ ] ¿Conocen casos de filas de ajuste negativo de Colsanitas (RN-11)? ¿Qué hacen con esas filas hoy?
- [ ] ¿Necesitan poder **reemplazar** un archivo ya cargado, o que el sistema bloquee la doble carga?
- [ ] ¿Quién es hoy el responsable de revisar los errores y advertencias después de cada carga?
- [ ] El comparativo de novedades, ¿les sirve para detectar retirados que la EPS no ha dado de baja?

---

**Fuente:** `docs/01-funcional/requerimientos-funcionales.md` §2 (RF-101..113, RF-201..206); `docs/01-funcional/reglas-de-negocio.md` §2 (RN-01..11) y §4 (MP-035..040); `docs/01-funcional/casos-de-uso.md` (CU-001, CU-002, CU-003).
