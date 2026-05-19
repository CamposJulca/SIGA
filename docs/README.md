# Documentación SIGA — Sistema Inteligente de Gestión Administrativa

| Campo        | Valor                                                                |
|--------------|----------------------------------------------------------------------|
| Versión      | 1.0                                                                  |
| Fecha        | 2026-05-13                                                           |
| Fuentes      | 6 documentos del repositorio (`siga/` y `docs/`)                      |
| Responsable  | Equipo SIGA                                                          |
| Estado       | Borrador                                                             |

---

Este set documental consolida la información funcional, técnica, arquitectónica y operacional del proyecto **SIGA**, con foco en el subdominio actualmente implementado: **Beneficios de Salud / Medicina Prepagada**. Las reglas adicionales del Manual de Talento Humano se documentan como **roadmap**.

## 1. Índice

### 00-overview — Información transversal
- [Visión](00-overview/vision.md)
- [Glosario](00-overview/glosario.md)
- [Stakeholders](00-overview/stakeholders.md)
- [Gaps detectados](00-overview/gaps.md) ← información faltante consolidada

### 01-funcional — Qué hace SIGA
- [Requerimientos funcionales](01-funcional/requerimientos-funcionales.md)
- [Requerimientos no funcionales](01-funcional/requerimientos-no-funcionales.md) ⚠️ baja
- [Reglas de negocio](01-funcional/reglas-de-negocio.md) (RN-01..11 + MP-001..045)
- [Casos de uso](01-funcional/casos-de-uso.md)
- [Procesos de negocio](01-funcional/procesos-de-negocio.md)

### 02-arquitectura — Cómo está estructurado
- [Arquitectura general](02-arquitectura/arquitectura-general.md) (vistas C4)
- [Componentes](02-arquitectura/componentes.md)
- [Integraciones](02-arquitectura/integraciones.md)
- [Decisiones (ADRs)](02-arquitectura/decisiones/README.md)

### 03-tecnico — Detalle técnico
- [Stack tecnológico](03-tecnico/stack-tecnologico.md)
- [Modelo de datos](03-tecnico/modelo-de-datos.md)
- [API REST](03-tecnico/api.md)
- [Estándares y convenciones](03-tecnico/estandares-y-convenciones.md) ⚠️ baja

### 04-operacion — Día a día
- [Ambientes](04-operacion/ambientes.md) ⚠️ baja
- [Despliegue](04-operacion/despliegue.md)
- [Runbook](04-operacion/runbook.md)
- [Monitoreo y alertas](04-operacion/monitoreo-y-alertas.md) ⚠️ baja

### 05-seguridad — Seguridad y cumplimiento
- [Autenticación y autorización](05-seguridad/autenticacion-autorizacion.md) ⚠️ baja
- [Manejo de datos sensibles](05-seguridad/manejo-de-datos-sensibles.md) ⚠️ baja
- [Cumplimiento](05-seguridad/cumplimiento.md) ⚠️ baja

### 06-onboarding — Para nuevos miembros
- [Ruta de lectura por rol](06-onboarding/README.md)
- [Primer día](06-onboarding/primer-dia.md) ⚠️ baja
- [Levantar ambiente local](06-onboarding/levantar-ambiente-local.md)

### 07-entrega — Para el cliente y auditores
- [Checklist de entrega](07-entrega/checklist-entrega.md) ⚠️ baja
- [Matriz de trazabilidad](07-entrega/matriz-trazabilidad.md)

> ℹ️ Las marcas ⚠️ baja indican secciones cuya cobertura desde las fuentes es **menor al 30 %** y que contienen bloques `PENDIENTE` que requieren información adicional del equipo. Detalle en [`00-overview/gaps.md`](00-overview/gaps.md).

## 2. Rutas de lectura recomendadas por audiencia

### Nuevo desarrollador (orden sugerido)
1. [`00-overview/vision.md`](00-overview/vision.md)
2. [`00-overview/glosario.md`](00-overview/glosario.md)
3. [`02-arquitectura/arquitectura-general.md`](02-arquitectura/arquitectura-general.md)
4. [`02-arquitectura/componentes.md`](02-arquitectura/componentes.md)
5. [`03-tecnico/stack-tecnologico.md`](03-tecnico/stack-tecnologico.md)
6. [`03-tecnico/modelo-de-datos.md`](03-tecnico/modelo-de-datos.md)
7. [`03-tecnico/api.md`](03-tecnico/api.md)
8. [`06-onboarding/levantar-ambiente-local.md`](06-onboarding/levantar-ambiente-local.md)
9. [`02-arquitectura/decisiones/`](02-arquitectura/decisiones/README.md)
10. [`01-funcional/reglas-de-negocio.md`](01-funcional/reglas-de-negocio.md)

### Analista de Talento Humano / Nómina
1. [`00-overview/vision.md`](00-overview/vision.md)
2. [`01-funcional/casos-de-uso.md`](01-funcional/casos-de-uso.md)
3. [`01-funcional/procesos-de-negocio.md`](01-funcional/procesos-de-negocio.md)
4. [`01-funcional/reglas-de-negocio.md`](01-funcional/reglas-de-negocio.md)
5. [`04-operacion/runbook.md`](04-operacion/runbook.md)

### Contabilidad / Tributaria
1. [`00-overview/vision.md`](00-overview/vision.md)
2. [`01-funcional/reglas-de-negocio.md#3-reglas-funcionales-de-medicina-prepagada-8020`](01-funcional/reglas-de-negocio.md) — fórmula 80/20
3. [`03-tecnico/modelo-de-datos.md#3-tablas-de-medicina-prepagada`](03-tecnico/modelo-de-datos.md)
4. [`03-tecnico/api.md#3-medicina-prepagada`](03-tecnico/api.md)
5. [`05-seguridad/cumplimiento.md`](05-seguridad/cumplimiento.md)

### Operación / DevOps
1. [`02-arquitectura/arquitectura-general.md#8-vista-de-despliegue-alto-nivel`](02-arquitectura/arquitectura-general.md)
2. [`04-operacion/ambientes.md`](04-operacion/ambientes.md)
3. [`04-operacion/despliegue.md`](04-operacion/despliegue.md)
4. [`04-operacion/runbook.md`](04-operacion/runbook.md)
5. [`04-operacion/monitoreo-y-alertas.md`](04-operacion/monitoreo-y-alertas.md)
6. [`05-seguridad/autenticacion-autorizacion.md`](05-seguridad/autenticacion-autorizacion.md)

### Cliente / Auditor externo
1. [`00-overview/vision.md`](00-overview/vision.md)
2. [`07-entrega/checklist-entrega.md`](07-entrega/checklist-entrega.md)
3. [`07-entrega/matriz-trazabilidad.md`](07-entrega/matriz-trazabilidad.md)
4. [`05-seguridad/cumplimiento.md`](05-seguridad/cumplimiento.md)
5. [`05-seguridad/manejo-de-datos-sensibles.md`](05-seguridad/manejo-de-datos-sensibles.md)
6. [`00-overview/gaps.md`](00-overview/gaps.md)

## 3. Convenciones del set

- Cada archivo inicia con una **tabla de metadatos** (versión, fecha, fuente, responsable, estado).
- Los datos faltantes se marcan como `> ⚠️ PENDIENTE: ...` y se registran en [`00-overview/gaps.md`](00-overview/gaps.md).
- Los enlaces entre archivos son **relativos**.
- Los diagramas usan **Mermaid** embebido.
- Las reglas mantienen sus IDs originales: `RN-XX` (carga/validación) y `MP-XXX` (matriz medicina prepagada).

## 4. Fuentes consolidadas

Este set consolida los siguientes documentos del repositorio:

| ID  | Documento                                                | Ruta                                                            |
|-----|----------------------------------------------------------|------------------------------------------------------------------|
| F1  | SIGA — Documentación Funcional                          | `siga/DOCUMENTACION_FUNCIONAL.md`                                |
| F2  | SIGA — Beneficios de Salud (funcional ampliado)         | `siga/DOCUMENTO_FUNCIONAL_BENEFICIOS_SALUD.md`                   |
| T1  | SIGA — Documentación Técnica                            | `siga/DOCUMENTACION_TECNICA.md`                                  |
| A1  | SIGA — Arquitectura de Software                         | `siga/ARQUITECTURA_SOFTWARE.md`                                  |
| R1  | Matriz de Reglas — Medicina Prepagada SIGA               | `docs/matriz-reglas-medicina-prepagada-siga.md`                  |
| R2  | Reglas del Manual de Talento Humano para SIGA            | `docs/reglas-talento-humano-siga.md`                             |

Archivos previos en `siga/docs/` (versiones inicial y actual de funcional/técnico/arquitectura) fueron movidos a `_legacy/` para evitar duplicación. Consultar si se requiere material histórico.
