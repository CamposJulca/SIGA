# Stakeholders y Responsabilidades

| Campo        | Valor                                                          |
|--------------|----------------------------------------------------------------|
| Versión      | 1.0                                                            |
| Fecha        | 2026-05-13                                                     |
| Fuente       | Documentación Funcional §3 (Actores)                            |
| Responsable  | Equipo SIGA                                                    |
| Estado       | Borrador — falta nominación oficial de responsables             |

---

## 1. Roles documentados en las fuentes

Las fuentes definen los siguientes actores funcionales. Los nombres propios, áreas formales y datos de contacto **no figuran** en las fuentes y aparecen como `PENDIENTE`.

| Actor                       | Responsabilidades                                                                                          | Sistema con el que interactúa             |
|-----------------------------|-------------------------------------------------------------------------------------------------------------|--------------------------------------------|
| **Analista de Gestión Humana** | Cargar archivos de proveedores, revisar errores y advertencias, consultar beneficios, generar reportes.       | Portal SIGA, módulo Beneficios de Salud.   |
| **Usuario administrativo**   | Consultar dashboard, exportar consolidados y revisar novedades entre periodos.                              | Portal SIGA, vistas de consulta.            |
| **Responsable de prepagada** | Definir y mantener la política 80/20, administrar pensionados y auxilios externos, calcular planillas.       | Pestañas Política, Pensionados, Auxilio Externo, Planilla. |
| **Proveedores de salud**     | AXA Colpatria y Colsanitas. Entregan los archivos Excel con beneficiarios y valores facturados.             | Fuera del sistema. Entrega vía correo corporativo. |
| **Kactus / `prepagada.db`**  | Sistema/base externa que provee el cruce de datos laborales y periodos de medicina prepagada.                | Lectura vía SQLite por `prepagada_service.py`. |
| **SIGA (sistema)**          | Procesa los archivos, valida los datos, calcula las planillas y persiste los resultados.                    | Es el propio sistema documentado.           |

## 2. Roles operacionales / técnicos

Estos roles **no figuran explícitamente** en las fuentes funcionales pero son necesarios para mantener el sistema. Quedan como esqueleto a confirmar.

> ⚠️ PENDIENTE: nombres, áreas y datos de contacto reales.

| Rol técnico                  | Responsabilidad esperada                                                                                |
|------------------------------|-----------------------------------------------------------------------------------------------------------|
| **Líder técnico SIGA**       | Mantenimiento del código, releases, decisiones arquitectónicas, gestión de migraciones.                  |
| **DevOps / Operación**       | Disponibilidad del servicio, despliegue, backups, monitoreo.                                              |
| **Administrador de BD**      | Mantenimiento de la base principal (PostgreSQL o SQLite) y de `prepagada.db`.                             |
| **Oficial de protección de datos** | Cumplimiento Ley 1581. Define retención, accesos y registro nacional. *(Ver gap 3 en `gaps.md`).*          |
| **Auditoría interna**         | Revisión de la trazabilidad de cargas y de planillas calculadas; cierre EFR.                              |
| **Equipo de Contabilidad**    | Consumidor de causación y planilla; valida códigos contables en la Política 80/20.                        |
| **Equipo Tributario**         | Valida el límite UVT vigente y el correcto tratamiento del apoyo gravable.                                |
| **Equipo de Talento Humano**  | Mantiene reglas de elegibilidad (manual THU-DOC-002) y autoriza excepciones.                              |

## 3. Matriz RACI (propuesta inicial)

> ⚠️ PENDIENTE: validación por el área responsable. Esta es una propuesta deducida del flujo descrito en las fuentes, no una RACI formalizada.

| Actividad                                  | Analista GH | Resp. prepagada | Contabilidad | Tributaria | Líder técnico | DevOps |
|--------------------------------------------|:-----------:|:---------------:|:------------:|:----------:|:-------------:|:------:|
| Carga mensual de archivos EPS              | **R**       | C               | I            |            |               | I      |
| Revisión de errores y advertencias         | **R**       | C               |              |            | C             |        |
| Definición / cambio de Política 80/20      | C           | **R / A**       | C            | C          | I             |        |
| Cálculo de planilla 80/20                  | **R**       | A               | I            | I          |               |        |
| Validación de apoyo gravable               | I           | C               | I            | **R / A**  |               |        |
| Generación de causación                    | R           | C               | **A**        |            |               |        |
| Cambio de valor UVT anual                  | I           | **R**           | I            | C / A      |               |        |
| Backups y restore                          |             |                 |              |            | C             | **R / A** |
| Despliegue de nuevas versiones             | I           |                 |              |            | A             | **R**  |

Convenciones: **R** Responsable, **A** Aprobador, **C** Consultado, **I** Informado.

---

**Fuente:** `siga/DOCUMENTACION_FUNCIONAL.md` §3 (Actores). El resto de roles deriva del flujo operativo documentado en `DOCUMENTO_FUNCIONAL_BENEFICIOS_SALUD.md`.
