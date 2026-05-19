# Onboarding — Ruta de Lectura por Rol

| Campo        | Valor                                                |
|--------------|-------------------------------------------------------|
| Versión      | 1.0                                                   |
| Fecha        | 2026-05-13                                            |
| Fuente       | Derivado del set consolidado                          |
| Responsable  | Líder técnico SIGA / Talento Humano                   |
| Estado       | Borrador                                              |

---

Esta guía propone un orden de lectura del set consolidado según el rol de la persona que se incorpora.

## 1. Para un nuevo desarrollador

1. [`00-overview/vision.md`](../00-overview/vision.md) — qué es SIGA y qué problema resuelve.
2. [`00-overview/glosario.md`](../00-overview/glosario.md) — vocabulario del dominio.
3. [`02-arquitectura/arquitectura-general.md`](../02-arquitectura/arquitectura-general.md) — vista C4 y flujos.
4. [`02-arquitectura/componentes.md`](../02-arquitectura/componentes.md) — capas y servicios.
5. [`03-tecnico/stack-tecnologico.md`](../03-tecnico/stack-tecnologico.md) — versiones y variables.
6. [`03-tecnico/modelo-de-datos.md`](../03-tecnico/modelo-de-datos.md) — entidades persistentes.
7. [`03-tecnico/api.md`](../03-tecnico/api.md) — endpoints.
8. [`06-onboarding/levantar-ambiente-local.md`](levantar-ambiente-local.md) — paso a paso para correrlo.
9. [`02-arquitectura/decisiones/`](../02-arquitectura/decisiones/README.md) — ADRs.
10. [`01-funcional/reglas-de-negocio.md`](../01-funcional/reglas-de-negocio.md) — reglas implementadas y roadmap.

## 2. Para un analista de Talento Humano / Nómina

1. [`00-overview/vision.md`](../00-overview/vision.md).
2. [`01-funcional/casos-de-uso.md`](../01-funcional/casos-de-uso.md) — qué puede hacer el sistema.
3. [`01-funcional/procesos-de-negocio.md`](../01-funcional/procesos-de-negocio.md) — proceso mensual.
4. [`01-funcional/reglas-de-negocio.md`](../01-funcional/reglas-de-negocio.md) — RN-01..11 y MP-001..045.
5. [`04-operacion/runbook.md`](../04-operacion/runbook.md) — qué hacer cuando algo sale mal.
6. [`07-entrega/checklist-entrega.md`](../07-entrega/checklist-entrega.md) — criterios de entrega.

## 3. Para alguien de contabilidad o tributaria

1. [`00-overview/vision.md`](../00-overview/vision.md).
2. [`01-funcional/reglas-de-negocio.md`](../01-funcional/reglas-de-negocio.md) §3 — fórmula 80/20.
3. [`03-tecnico/modelo-de-datos.md`](../03-tecnico/modelo-de-datos.md) §3 — `PoliticaPrepagada`, `PlanillaCalculo`, `DetalleCalculo`.
4. [`03-tecnico/api.md`](../03-tecnico/api.md) §3 — endpoints de planilla, causación, conciliación, EFR.
5. [`05-seguridad/cumplimiento.md`](../05-seguridad/cumplimiento.md).

## 4. Para operación / DevOps

1. [`00-overview/vision.md`](../00-overview/vision.md).
2. [`02-arquitectura/arquitectura-general.md`](../02-arquitectura/arquitectura-general.md) §8 (despliegue).
3. [`04-operacion/ambientes.md`](../04-operacion/ambientes.md).
4. [`04-operacion/despliegue.md`](../04-operacion/despliegue.md).
5. [`04-operacion/runbook.md`](../04-operacion/runbook.md).
6. [`04-operacion/monitoreo-y-alertas.md`](../04-operacion/monitoreo-y-alertas.md).
7. [`05-seguridad/autenticacion-autorizacion.md`](../05-seguridad/autenticacion-autorizacion.md).

## 5. Para un auditor o stakeholder externo

1. [`00-overview/vision.md`](../00-overview/vision.md).
2. [`07-entrega/checklist-entrega.md`](../07-entrega/checklist-entrega.md).
3. [`07-entrega/matriz-trazabilidad.md`](../07-entrega/matriz-trazabilidad.md).
4. [`05-seguridad/cumplimiento.md`](../05-seguridad/cumplimiento.md).
5. [`05-seguridad/manejo-de-datos-sensibles.md`](../05-seguridad/manejo-de-datos-sensibles.md).
6. [`00-overview/gaps.md`](../00-overview/gaps.md) — qué queda por completar.

## 6. Otros recursos

- [`primer-dia.md`](primer-dia.md) — checklist del primer día.
- [`levantar-ambiente-local.md`](levantar-ambiente-local.md) — instrucciones para correr SIGA.

---

**Fuente:** rutas construidas a partir del set consolidado de SIGA.
