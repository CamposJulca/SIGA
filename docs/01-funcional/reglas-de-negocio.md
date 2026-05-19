# Reglas de Negocio

| Campo        | Valor                                                                                                      |
|--------------|-------------------------------------------------------------------------------------------------------------|
| Versión      | 1.0                                                                                                         |
| Fecha        | 2026-05-13                                                                                                  |
| Fuente       | Documentación Funcional §6, §10; Matriz de Reglas Medicina Prepagada (MP-001..045); Reglas Talento Humano    |
| Responsable  | Talento Humano / Equipo SIGA                                                                                |
| Estado       | Borrador                                                                                                    |

---

## 1. Convención

- Las reglas con prefijo `RN-XX` provienen de la Documentación Funcional §6 (carga y validación).
- Las reglas con prefijo `MP-XXX` provienen de la Matriz de Reglas — Medicina Prepagada (`docs/matriz-reglas-medicina-prepagada-siga.md`) y representan el cruce entre el Manual de Talento Humano y el alcance funcional de SIGA.

Para cada regla MP se conserva el **estado de implementación** declarado en la matriz fuente:

- `Soportado` — el sistema actual ya tiene una estructura o cálculo cercano.
- `Parcial` — existe parte del dato o cálculo, pero falta validación/regla completa.
- `No soportado` — requiere modelo, dato, validación o flujo nuevo.
- `Por definir` — la regla del manual existe, pero requiere decisión funcional antes de implementar.

## 2. Reglas de carga y validación (`RN-XX`)

| Código | Regla                                                                                                                                       |
|--------|---------------------------------------------------------------------------------------------------------------------------------------------|
| RN-01  | El archivo debe llegar en el campo multipart `archivo`.                                                                                     |
| RN-02  | Si el usuario está autenticado, se registra su username; si no, se acepta `usuario` del formulario o `anonimo`.                              |
| RN-03  | AXA no trae descuento separado; SIGA lo registra como `0`.                                                                                  |
| RN-04  | Colsanitas excluye filas resumen como `TOTAL FAMILIA`, `TOTAL CONTRATO`, `TOTAL GENERAL`, `SUBTOTAL` y `GRAN TOTAL`.                          |
| RN-05  | La cédula vacía o inválida genera error fatal `CEDULA_INVALIDA`; el registro no se inserta como beneficio.                                    |
| RN-06  | `valor_base`, `iva` y `valor_total` deben ser numéricos. Valores negativos en esos campos generan error fatal salvo filas de ajuste permitidas. |
| RN-07  | `descuento` puede ser negativo porque Colsanitas puede registrar ajustes de esa forma.                                                       |
| RN-08  | La consistencia aritmética esperada es `valor_total = valor_base - descuento + iva`, con tolerancia de COP 1.                                |
| RN-09  | Diferencias aritméticas mayores a COP 1 generan `ADVERTENCIA`, pero el registro se almacena.                                                  |
| RN-10  | Cédulas duplicadas dentro del mismo `sub_contrato` generan `CEDULA_DUPLICADA` como advertencia, no rechazo.                                   |
| RN-11  | Una fila de ajuste Colsanitas con `valor_base = 0` y `valor_total < 0` se almacena como advertencia.                                          |

## 3. Reglas funcionales de medicina prepagada 80/20

Reglas operativas básicas del cálculo, declaradas en Documentación Funcional §10:

| Caso                                    | Resultado                                                                          |
|-----------------------------------------|------------------------------------------------------------------------------------|
| Empleado con cruce Kactus `OK`          | Aplica distribución según política, normalmente 80 empresa / 20 empleado.           |
| Pensionado activo                       | Se marca `PENSIONADO_100`; el 100 % queda a cargo del pensionado/empleado.         |
| Cruce distinto de `OK`                   | Se marca `BLOQUEADO_CRUCE`; no se calcula aporte empresa.                          |
| Apoyo empresa ≤ límite UVT               | Todo es no gravable.                                                               |
| Apoyo empresa > límite UVT               | La parte hasta el límite es no gravable y el excedente queda gravable.             |

Fórmula central del cálculo (ver detalle técnico en [`../03-tecnico/modelo-de-datos.md`](../03-tecnico/modelo-de-datos.md)):

```text
valor_empresa       = total_familia * (porcentaje_empresa / 100)
valor_empleado      = total_familia * (porcentaje_empleado / 100)
limite_no_gravable  = uvt_limite * valor_uvt
apoyo_no_gravable   = min(valor_empresa, limite_no_gravable)
apoyo_gravable      = max(0, valor_empresa - limite_no_gravable)
```

## 4. Matriz de elegibilidad — Manual THU-DOC-002 (`MP-XXX`)

| ID | Regla | Condición / disparador | Resultado esperado | Estado |
|----|-------|------------------------|--------------------|--------|
| MP-001 | Beneficio aplicable a colaboradores FINAGRO | Persona en factura o solicitud | Solo colaboradores directos activos elegibles | Parcial |
| MP-002 | Antigüedad mínima                          | Fecha de ingreso / corte      | Elegible si > 2 meses vinculado o pasó periodo de prueba | No soportado |
| MP-003 | Aceptación del beneficio                    | Ingreso al beneficio          | Sin aceptación no aplica aporte ni descuento | No soportado |
| MP-004 | Autorización descuento nómina               | Colaborador en póliza colectiva | Permitir descuento del 20 % | No soportado |
| MP-005 | Distribución base 80/20                     | Empleado activo elegible      | 80 % FINAGRO / 20 % empleado | Soportado |
| MP-006 | Pensionados                                  | Registro corresponde a pensionado | FINAGRO 0 %; pensionado 100 % | Parcial |
| MP-007 | Póliza colectiva para pensionados            | Pensionado en póliza colectiva | Tarifa colectiva, pago completo del pensionado | Parcial |
| MP-008 | Cónyuge elegible                             | Parentesco cónyuge            | Puede recibir aporte | Parcial |
| MP-009 | Compañero permanente elegible                | Unión ≥ 2 años + soporte      | Aporte si tiene soporte | No soportado |
| MP-010 | Hijos elegibles por edad                     | Parentesco hijo, edad         | Hasta 25 años con dependencia económica | Parcial |
| MP-011 | Hijos discapacitados                          | Discapacidad + dependencia     | Sin límite de edad con certificado | No soportado |
| MP-012 | Padres para colaborador soltero               | Soltero, sin hijos cubiertos   | Padres elegibles | No soportado |
| MP-013 | Familiar hasta segundo grado para soltero sin padres | Soltero sin padres        | Abuelo / nieto / hermano | No soportado |
| MP-014 | Soltero con hijos y padres                   | Hijos cubiertos                | Padres excluidos                  | No soportado |
| MP-015 | Casado/unión incluye padre en vez de cónyuge | Sustitución                    | Permitida con soporte | No soportado |
| MP-016 | Familiares no descritos                      | Parentesco no listado          | 100 % a cargo del colaborador | Por definir |
| MP-017 | Soportes de parentesco                       | Alta o cambio                  | Elegibilidad sólo con soporte válido | No soportado |
| MP-018 | Vigencia de nuevos beneficiarios             | Aceptación proveedor           | Aporte desde fecha de aceptación | No soportado |
| MP-019 | Póliza externa de mayor valor                | Póliza externa > promedio FINAGRO | Aporte sobre promedio, no sobre valor externo | No soportado |
| MP-020 | Póliza externa de menor valor                | Póliza externa < promedio      | Aporte sobre valor real          | No soportado |
| MP-021 | Recibo mensual para póliza externa           | Solicitud mensual              | Reembolso contra recibo validado | No soportado |
| MP-022 | Certificación inicial póliza externa         | Primera solicitud              | Solicitud sólo procede con certificación completa | No soportado |
| MP-023 | Actualización anual póliza externa           | Año nuevo / cambio             | Mantener auxilio sólo con certificación vigente | No soportado |
| MP-024 | Cambios en póliza externa                    | Cambio en condiciones          | Recalcular desde el cambio       | No soportado |
| MP-025 | Retroactividad póliza externa                 | Solicitud con meses pasados    | Máximo 3 meses calendario        | No soportado |
| MP-026 | Retiro del colaborador                        | Retiro durante periodo         | Aporte hasta último día laborado | No soportado |
| MP-027 | Ingreso o aceptación parcial                  | Ingreso durante periodo        | Aporte desde fecha aplicable     | No soportado |
| MP-028 | Cruce con Kactus                              | Cruce factura ↔ empleado       | Estado OK / inactivo / no encontrado | Soportado |
| MP-029 | Registros no encontrados en Kactus            | Cédula no cruza                | No calcular aporte FINAGRO        | Parcial |
| MP-030 | Empleado inactivo                              | Cruce inactivo                 | Sin aporte salvo parcial por retiro | Parcial |
| MP-031 | Valor total familia                            | Cálculo por grupo familiar     | Agrupar valores                  | Soportado |
| MP-032 | Política vigente                                | Cálculo de planilla            | Usar política vigente al periodo | Parcial |
| MP-033 | Límite no gravable / gravable                  | Clasificación tributaria       | Apoyo no gravable y gravable     | Soportado |
| MP-034 | Conceptos de nómina                            | Exportación a nómina           | Códigos por concepto              | Parcial |
| MP-035 | Proveedor AXA                                   | Carga AXA                      | Normalizar al modelo unificado    | Soportado |
| MP-036 | Proveedor Colsanitas                            | Carga Colsanitas               | Normalizar al modelo unificado    | Soportado |
| MP-037 | Proveedor desconocido                            | Archivo no detectado           | Rechazar o marcar error          | Soportado |
| MP-038 | Duplicados en factura                            | Misma cédula/subcontrato       | Advertencia                       | Soportado |
| MP-039 | Ajustes contables negativos                       | Ajuste en proveedor            | Advertencia                       | Soportado |
| MP-040 | Errores de valor                                  | Valor no numérico/negativo     | Rechazar fila o marcar error      | Soportado |
| MP-041 | Auditoría de cálculo                              | Cada planilla calculada        | Usuario, fecha, periodo, política | Parcial |
| MP-042 | Recálculo de planilla                              | Reciclar un periodo            | Definir reemplazo/versión         | Por definir |
| MP-043 | Excepciones Talento Humano                         | Caso especial autorizado       | Aplicar regla excepcional         | No soportado |
| MP-044 | Exclusión por falta de soportes                    | Beneficiario sin documentos    | No aporte hasta completar         | No soportado |
| MP-045 | Histórico de reglas                                | Cambio de política             | Calcular periodos con regla vigente de ese periodo | Parcial |

## 5. Datos mínimos requeridos por las reglas

| Dato                       | Uso                                                | Fuente probable           | Estado        |
|----------------------------|----------------------------------------------------|---------------------------|---------------|
| Cédula colaborador         | Cruce, agrupación y cálculo                        | Factura / Kactus          | Soportado     |
| Nombre colaborador         | Reportes y validación visual                       | Factura / Kactus          | Soportado     |
| Estado activo/inactivo     | Elegibilidad                                        | Kactus / `prepagada.db`   | Parcial       |
| Fecha ingreso              | Regla de dos meses / periodo prueba                 | Kactus                    | No soportado  |
| Fecha retiro               | Prorrateo y cierre de aporte                        | Kactus                    | No soportado  |
| Tipo contrato              | Validar colaborador directo                         | Kactus                    | Parcial       |
| Tipo salario               | Reportes y reglas generales                         | Kactus                    | Parcial       |
| Salario base               | Topes / reportes tributarios                        | Kactus                    | Parcial       |
| Parentesco                 | Elegibilidad beneficiario                           | Factura / maestro familiar | Parcial       |
| Edad / fecha nacimiento    | Elegibilidad hijos                                  | Factura / maestro familiar | Parcial       |
| Dependencia económica      | Elegibilidad hijos/familiares                       | Declaración / soporte TH  | No soportado  |
| Estado civil               | Reglas de padres/cónyuge                            | TH / Kactus               | No soportado  |
| Discapacidad               | Hijos sin límite de edad                            | Soporte EPS / TH          | No soportado  |
| Soporte parentesco         | Validación documental                               | EPS / TH                  | No soportado  |
| Fecha aceptación proveedor  | Vigencia de nuevo beneficiario                       | Proveedor / TH            | No soportado  |
| Valor factura              | Cálculo 80/20                                       | Factura proveedor         | Soportado     |
| Proveedor / EPS            | Reportes y agrupación                               | Factura proveedor         | Soportado     |
| Periodo factura            | Cálculo mensual                                     | Factura proveedor         | Soportado     |
| Política 80/20             | Distribución                                        | Configuración SIGA        | Soportado     |
| Valor UVT                  | Gravable / no gravable                              | Configuración SIGA        | Parcial       |
| Promedio póliza FINAGRO     | Tope póliza externa                                 | Cálculo SIGA              | No soportado  |
| Recibo póliza externa      | Reembolso mensual                                   | Colaborador / TH          | No soportado  |
| Autorización descuento     | Descuento empleado                                  | TH                        | No soportado  |

## 6. Priorización de implementación (roadmap de reglas)

### Fase 1 — Blindar el cálculo actual
- Usar política vigente por periodo, no simplemente la última creada.
- Aplicar explícitamente regla de pensionados al 100 %.
- Conectar estado de cruce Kactus con cálculo: `OK` calcula; no encontrado / inactivo queda bloqueado o en excepción.
- Agregar auditoría real de usuario cuando exista autenticación.
- Definir comportamiento de recálculo de planillas.

### Fase 2 — Elegibilidad de beneficiarios
- Normalizar parentescos AXA/Colsanitas a catálogo SIGA.
- Validar hijos hasta 25 años.
- Agregar soporte para hijos discapacitados.
- Agregar estado civil y reglas de sustitución: cónyuge, padre, padres, segundo grado.
- Definir tratamiento de familiares no elegibles.

### Fase 3 — Pólizas externas
- Crear registro de póliza externa por colaborador.
- Registrar certificación inicial, vigencia, tomador, beneficiarios, edades, costo y forma de pago.
- Calcular tope por promedio de pólizas FINAGRO.
- Validar recibos mensuales.
- Aplicar retroactividad máxima de tres meses.

### Fase 4 — Prorrateos y eventos laborales
- Aplicar fecha de ingreso, aceptación, inclusión de beneficiario y retiro.
- Definir prorrateo por días calendario o regla mensual de Talento Humano.
- Registrar excepciones aprobadas por Talento Humano.

## 7. Decisiones funcionales pendientes

> ⚠️ PENDIENTE: estas no son gaps de documentación sino **decisiones de negocio** sin resolver en el manual.

1. Si un familiar no elegible debe aparecer en planilla con `100 % empleado` o excluirse del archivo de aporte.
2. Cómo calcular el promedio de referencia para pólizas externas (promedio general, por proveedor, por tipo de plan, por grupo familiar o por beneficiario).
3. Si el prorrateo por ingreso/retiro se hace por días calendario, días laborales o corte administrativo mensual.
4. Si el periodo de prueba se valida como dato explícito o se asume cubierto por la regla de más de dos meses.
5. Si las excepciones autorizadas por Talento Humano tienen vigencia mensual, anual o abierta.
6. Si el recálculo reemplaza la planilla anterior o crea una nueva versión auditable.

## 8. Roadmap de reglas extendidas (fuera del alcance de medicina prepagada)

Las siguientes reglas viven en el Manual THU-DOC-002 y están documentadas en [`../01-funcional/requerimientos-funcionales.md`](requerimientos-funcionales.md) §6. Se identifican aquí sólo a nivel de bloque para no duplicar el detalle disponible en la fuente `docs/reglas-talento-humano-siga.md`:

- Auxilio educativo para hijos
- Vacaciones y compensaciones (incluida compensación en dinero con beneficio extralegal de 6 días por 15)
- Primas extralegales (vacaciones, navidad, antigüedad) y bonificación por quinquenio
- Auxilio de incapacidad
- Auxilio extralegal de alimentación
- Auxilio de parqueadero
- FONDEFIN
- Préstamo de libre inversión
- Permisos, licencias y flexibilidad
- Convocatorias internas, encargos y nivelación de escala salarial
- Crédito educativo condonable
- Póliza funeraria y seguro de vida

> ℹ️ Estas reglas se incluyen como **roadmap declarado**. Antes de implementarlas se debe definir si entran al alcance de SIGA (ver `gaps.md` Top 10 #8).

---

**Fuente:** `siga/DOCUMENTACION_FUNCIONAL.md` (§6, §10), `docs/matriz-reglas-medicina-prepagada-siga.md` (Matriz principal y datos mínimos), `docs/reglas-talento-humano-siga.md` (Reglas generales y secciones por beneficio).
