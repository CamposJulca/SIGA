# Cumplimiento

| Campo        | Valor                                                                  |
|--------------|------------------------------------------------------------------------|
| Versión      | 1.0                                                                    |
| Fecha        | 2026-05-13                                                             |
| Fuente       | Informe EFR (mencionado en F1 §9, F2, A1 §3)                            |
| Responsable  | Legal / Auditoría / Talento Humano                                      |
| Estado       | **Borrador — cobertura BAJA**, ver `gaps.md` Top 10 #3                  |

---

> ⚠️ PENDIENTE: las fuentes mencionan **EFR** como una salida del sistema pero no establecen marcos formales de cumplimiento. Esta sección es esqueleto a complementar por el área legal/cumplimiento de Finagro.

## 1. Marco regulatorio identificado

| Marco                                     | Relación con SIGA                                                                                  | Estado actual                                                  |
|--------------------------------------------|----------------------------------------------------------------------------------------------------|----------------------------------------------------------------|
| **Art. 387 Estatuto Tributario**            | Fundamenta el límite UVT del aporte no gravable de la empresa.                                       | Implementado en el cálculo de planilla 80/20.                  |
| **EFR (Empresa Familiarmente Responsable)** | SIGA emite informe mensual con planilla, pensionados activos y auxilios externos (`/informe-efr/`).  | Salida implementada; auditoría externa `PENDIENTE` documentar.  |
| **Ley 1581 / 1377 (Habeas Data)**           | SIGA almacena datos personales (cédulas, nombres, valores, salarios).                                | `PENDIENTE` — ver [`manejo-de-datos-sensibles.md`](manejo-de-datos-sensibles.md). |
| **Manual THU-DOC-002 v13 Finagro**          | Define la política de beneficios extralegales que SIGA debe ejecutar.                                | Cobertura parcial (sólo medicina prepagada). Ver [`../01-funcional/reglas-de-negocio.md`](../01-funcional/reglas-de-negocio.md). |

## 2. Otros marcos potencialmente aplicables (a confirmar)

> ⚠️ PENDIENTE: confirmar aplicabilidad con el área legal.

- **Resoluciones DIAN anuales sobre UVT**: actualización anual del campo `valor_uvt`.
- **Decretos de retención en la fuente** sobre rentas de trabajo.
- **Normas contables (NIIF / PUC)**: Finagro requiere mapeo a su PUC vigente; los conceptos `cod_conc_apoyo_no_grav`, `cod_conc_apoyo_grav`, `cod_conc_dcto_empleado` lo soportan.
- **Circulares de la Superfinanciera** si aplican a Finagro como entidad de redescuento.
- **Ley 1010 / clima organizacional** asociado al beneficio EFR.

## 3. Obligaciones de auditoría

> ⚠️ PENDIENTE: las fuentes no detallan obligaciones de auditoría (frecuencia, alcance, evidencias). Recomendación mínima:

| Audiencia                | Evidencia que SIGA puede aportar                                                          |
|---------------------------|--------------------------------------------------------------------------------------------|
| Auditoría interna          | `ArchivoRecibido` + `BeneficioSalud` + `ErrorProcesamiento` para reconstruir cualquier carga. |
| Auditoría tributaria       | `PlanillaCalculo` + `DetalleCalculo` + `PoliticaPrepagada` aplicable al periodo.            |
| Auditoría EFR              | `/informe-efr/` mensual + `PensionadoPrepagada` + `AuxilioExterno` activos.                  |
| Auditoría contable         | `/causacion/` por periodo + soporte de planilla exportada.                                   |
| Auditoría de protección de datos | Política de tratamiento (`PENDIENTE`) + accesos al sistema (`PENDIENTE`).                |

## 4. Trazabilidad disponible

| Pregunta de auditoría                                                | ¿Lo cubre el sistema?                                                                 |
|-----------------------------------------------------------------------|----------------------------------------------------------------------------------------|
| ¿Quién cargó el archivo y cuándo?                                     | Parcial. `ArchivoRecibido.usuario_carga`, pero la identidad **no** está autenticada hoy. |
| ¿Qué archivo concreto del proveedor se procesó?                       | Sí. Hash SHA256 + ruta en disco preservada.                                            |
| ¿Por qué se rechazó un registro?                                       | Sí. `ErrorProcesamiento.tipo_error`, `descripcion`, `fila_origen`.                       |
| ¿Qué política se aplicó al calcular la planilla de X?                  | Sí, por la FK `politica` en `PlanillaCalculo`.                                           |
| ¿Quién calculó la planilla?                                            | Parcial. `generada_por` existe (MP-041), pero depende de la autenticación.              |
| ¿Quién creó/cambió la política?                                        | `PENDIENTE` — no se documenta auditoría de cambio sobre `PoliticaPrepagada`.            |
| ¿Se mantienen históricos de cambios en pensionados / auxilios externos? | `PENDIENTE` — no se documenta historial.                                                |

## 5. Brechas de cumplimiento detectadas

| Brecha                                                                    | Sección donde se trata                                                |
|----------------------------------------------------------------------------|------------------------------------------------------------------------|
| Sin autenticación obligatoria                                              | [`autenticacion-autorizacion.md`](autenticacion-autorizacion.md)        |
| Sin tratamiento formal de datos personales                                 | [`manejo-de-datos-sensibles.md`](manejo-de-datos-sensibles.md)          |
| Sin estrategia de backup y restore                                          | [`../04-operacion/despliegue.md`](../04-operacion/despliegue.md) §7     |
| Sin observabilidad técnica ni alertas                                       | [`../04-operacion/monitoreo-y-alertas.md`](../04-operacion/monitoreo-y-alertas.md) |
| Reglas del manual aún no implementadas (elegibilidad, prorrateos, etc.)   | [`../01-funcional/reglas-de-negocio.md`](../01-funcional/reglas-de-negocio.md) |
| Sin matriz formal de trazabilidad Requerimiento ↔ Componente ↔ Prueba        | [`../07-entrega/matriz-trazabilidad.md`](../07-entrega/matriz-trazabilidad.md) |

---

**Fuente:** referencias a EFR en `siga/DOCUMENTACION_FUNCIONAL.md` §9 y `siga/ARQUITECTURA_SOFTWARE.md`; mención de Art. 387 E.T. y UVT en `siga/DOCUMENTO_FUNCIONAL_BENEFICIOS_SALUD.md`. El marco normativo restante no se documenta en las fuentes.
