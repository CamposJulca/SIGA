# Primer Día

| Campo        | Valor                                                |
|--------------|-------------------------------------------------------|
| Versión      | 1.0                                                   |
| Fecha        | 2026-05-13                                            |
| Fuente       | Esqueleto — no documentado en fuentes                  |
| Responsable  | Líder técnico SIGA / Talento Humano                    |
| Estado       | **Borrador — cobertura BAJA**                          |

---

> ⚠️ PENDIENTE: ninguna fuente describe el onboarding formal. Esta checklist es un punto de partida.

## Checklist técnico (desarrollador)

- [ ] Acceso al repositorio Git de SIGA. **PENDIENTE**: URL y permisos.
- [ ] Acceso al backlog / tracker del proyecto. **PENDIENTE**.
- [ ] Acceso a los ambientes (Dev/QA/Prod si aplica). **PENDIENTE** (ver [`../04-operacion/ambientes.md`](../04-operacion/ambientes.md)).
- [ ] Acceso a `prepagada.db` de desarrollo o instrucciones para generar uno mínimo.
- [ ] Acceso al canal de comunicación del equipo. **PENDIENTE**.
- [ ] Clonar repo y levantar ambiente local siguiendo [`levantar-ambiente-local.md`](levantar-ambiente-local.md).
- [ ] Ejecutar la suite de pruebas (cuando exista — ver [`../03-tecnico/estandares-y-convenciones.md`](../03-tecnico/estandares-y-convenciones.md) §5).
- [ ] Subir un archivo Excel de prueba y verificar el flujo completo.

## Checklist funcional (analista Talento Humano / Nómina)

- [ ] Acceso al portal SIGA. **PENDIENTE**: URL y credenciales.
- [ ] Capacitación sobre el proceso mensual (ver [`../01-funcional/procesos-de-negocio.md`](../01-funcional/procesos-de-negocio.md)).
- [ ] Acceso a los correos corporativos donde llegan las facturas de AXA y Colsanitas.
- [ ] Confirmación de que la política 80/20 vigente está configurada.
- [ ] Lectura de [`../01-funcional/reglas-de-negocio.md`](../01-funcional/reglas-de-negocio.md) (foco en RN-01..11 y MP-001..045 con estado `Soportado` o `Parcial`).
- [ ] Lectura del [`../04-operacion/runbook.md`](../04-operacion/runbook.md) §2 (atención a errores típicos).

## Checklist operación / DevOps

- [ ] Acceso al ambiente productivo.
- [ ] Acceso al stack de logs/métricas (cuando exista — ver [`../04-operacion/monitoreo-y-alertas.md`](../04-operacion/monitoreo-y-alertas.md)).
- [ ] Procedimiento de despliegue revisado (ver [`../04-operacion/despliegue.md`](../04-operacion/despliegue.md)).
- [ ] Procedimiento de rollback revisado. **PENDIENTE**.
- [ ] Política de backups revisada. **PENDIENTE**.

## Lecturas obligatorias para todos

1. [`../00-overview/vision.md`](../00-overview/vision.md).
2. [`../00-overview/glosario.md`](../00-overview/glosario.md).
3. [`../00-overview/stakeholders.md`](../00-overview/stakeholders.md).
4. [`../00-overview/gaps.md`](../00-overview/gaps.md) — para entender qué información está en construcción.

---

**Fuente:** esqueleto construido por la consolidación. Ninguna fuente describe el primer día formalmente.
