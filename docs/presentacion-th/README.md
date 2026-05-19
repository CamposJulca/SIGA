# Reunión con Talento Humano — SIGA Beneficios de Salud

| Campo               | Valor                                                                 |
|---------------------|------------------------------------------------------------------------|
| Fecha de la reunión | 2026-05-13                                                             |
| Audiencia           | Equipo de Talento Humano de Finagro                                    |
| Demo en pantalla    | `https://automation-hub-finagro.ngrok.io/siga` → Beneficios de Salud   |
| Duración prevista   | 60–75 minutos                                                           |
| Material            | Esta carpeta (`docs/presentacion-th/`)                                  |

---

## Objetivo de la reunión

Validar funcionalmente con Talento Humano los **8 módulos** del subdominio Beneficios de Salud:

1. Mostrar qué hace la herramienta hoy, en vivo.
2. Confirmar con TH que cada módulo refleja la operación real del área.
3. Capturar lo que falta, lo que sobra y lo que se debe ajustar.
4. Dejar acordados los compromisos y owners para los próximos pasos.

> No es una reunión de aprobación técnica. Es una reunión de **validación funcional**.

## Agenda sugerida

| Bloque                                       | Tiempo  | Archivo guía                                             |
|----------------------------------------------|---------|----------------------------------------------------------|
| Apertura (contexto y reglas del juego)        | 5 min   | [`00-apertura.md`](00-apertura.md)                       |
| Módulo 1 — Dashboard                          | 5 min   | [`01-dashboard.md`](01-dashboard.md)                     |
| Módulo 2 — Facturas EPS                       | 8 min   | [`02-facturas-eps.md`](02-facturas-eps.md)               |
| Módulo 3 — Planilla 80/20                     | 8 min   | [`03-planilla-80-20.md`](03-planilla-80-20.md)           |
| Módulo 4 — Apoyo Grav. / No Grav.             | 6 min   | [`04-apoyo-grav-no-grav.md`](04-apoyo-grav-no-grav.md)   |
| Módulo 5 — Causación                          | 5 min   | [`05-causacion.md`](05-causacion.md)                     |
| Módulo 6 — Pensionados                        | 5 min   | [`06-pensionados.md`](06-pensionados.md)                 |
| Módulo 7 — Auxilio Externo                    | 5 min   | [`07-auxilio-externo.md`](07-auxilio-externo.md)         |
| Módulo 8 — Política 80/20                     | 6 min   | [`08-politica-80-20.md`](08-politica-80-20.md)           |
| Cierre y siguientes pasos                     | 7 min   | [`99-cierre-y-siguientes-pasos.md`](99-cierre-y-siguientes-pasos.md) |
| **Total estimado**                            | **60 min** | (10 min de buffer recomendados)                         |

## Cómo usar este set

- Cada módulo tiene **su propio archivo** (`01-dashboard.md` … `08-politica-80-20.md`).
- En cada archivo hay un bloque **"Flujo paso a paso"** que es el **guion de la demo en vivo**.
- Al final de cada módulo hay **"Preguntas que NOSOTROS le hacemos a TH"** — son los puntos que necesitamos llevarnos respondidos.
- La lista consolidada de preguntas está en [`preguntas-de-validacion.md`](preguntas-de-validacion.md) — recomendado tenerla abierta en una segunda pestaña para ir marcando durante la reunión.

## Mensajes clave a transmitir

1. **SIGA es para ustedes.** Está construido para reducir trabajo manual de TH en la conciliación mensual de medicina prepagada. La reunión es para validar que efectivamente lo está haciendo bien.
2. **Lo que está hoy es Beneficios de Salud / Medicina Prepagada.** El resto del manual de Talento Humano (auxilio educativo, vacaciones, primas, FONDEFIN, préstamos, etc.) es **roadmap**, no está implementado.
3. **El sistema deja trazabilidad de todo.** Cada archivo cargado, cada error detectado y cada planilla calculada queda registrado. Eso nos sirve para auditoría y para responder a reclamaciones.
4. **Hay reglas del manual que aún no aplicamos automáticamente.** Cuando lleguemos a esos temas (elegibilidad de cónyuge, hijos, pólizas externas, prorrateos por retiro, etc.) los marcamos como pendientes y necesitamos su decisión funcional.
5. **No es para aprobar, es para validar.** Si algo no se parece a la operación real de TH, decirlo en el momento es exactamente lo que necesitamos.

## Roles esperados en la reunión

| Rol                           | Por qué                                                                 |
|-------------------------------|-------------------------------------------------------------------------|
| Analista/s de Gestión Humana  | Usuario principal de la herramienta. Validan flujo operativo mensual.    |
| Responsable de prepagada      | Configura política y revisa pensionados/auxilios externos.               |
| Contabilidad (deseable)        | Consume causación y planilla. Confirma conceptos contables.              |
| Tributaria (deseable)          | Valida la clasificación gravable/no gravable y el UVT vigente.           |

## Checklist previo (antes de iniciar la reunión)

- [ ] Tener un archivo de AXA Colpatria y uno de Colsanitas del mes para subir en vivo.
- [ ] Confirmar que la política 80/20 del periodo está configurada en el sistema.
- [ ] Confirmar que el cruce con la nómina del periodo está disponible.
- [ ] Abrir esta carpeta en pantalla para usar como guion.
- [ ] Tener abierta la URL: `https://automation-hub-finagro.ngrok.io/siga`.

## Fuente

Esta guía consolida material funcional ya documentado en:
- `docs/00-overview/vision.md`
- `docs/00-overview/glosario.md`
- `docs/01-funcional/requerimientos-funcionales.md`
- `docs/01-funcional/reglas-de-negocio.md`
- `docs/01-funcional/casos-de-uso.md`
- `docs/01-funcional/procesos-de-negocio.md`
- `docs/00-overview/gaps.md`
