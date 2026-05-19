# Registro de Gaps de Información — SIGA

| Campo        | Valor                                                         |
|--------------|---------------------------------------------------------------|
| Versión      | 1.0                                                           |
| Fecha        | 2026-05-13                                                    |
| Fuente       | Inventario derivado de los 6 documentos fuente listados abajo |
| Responsable  | Technical Writing / Equipo SIGA                                |
| Estado       | Borrador — requiere validación del equipo                     |

---

## 1. Documentos fuente considerados

Los siguientes documentos del repositorio se tomaron como insumo. Toda referencia "Fuente: …" en los archivos consolidados apunta a uno de estos:

| ID  | Documento                                                       | Ruta                                                                       | Peso  |
|-----|------------------------------------------------------------------|----------------------------------------------------------------------------|-------|
| F1  | SIGA — Documentación Funcional                                  | `siga/DOCUMENTACION_FUNCIONAL.md`                                          | 8 KB  |
| F2  | SIGA — Beneficios de Salud (funcional ampliado)                 | `siga/DOCUMENTO_FUNCIONAL_BENEFICIOS_SALUD.md`                             | 31 KB |
| T1  | SIGA — Documentación Técnica                                    | `siga/DOCUMENTACION_TECNICA.md`                                            | 12 KB |
| A1  | SIGA — Arquitectura de Software                                 | `siga/ARQUITECTURA_SOFTWARE.md`                                            | 9 KB  |
| R1  | Matriz de Reglas — Medicina Prepagada SIGA                       | `docs/matriz-reglas-medicina-prepagada-siga.md`                            | 16 KB |
| R2  | Reglas del Manual de Talento Humano para SIGA                    | `docs/reglas-talento-humano-siga.md`                                       | 30 KB |

> ℹ️ Existen también en `siga/docs/` los archivos `documento_funcional_actual.md`, `arquitectura_actual.md` y `documento_tecnico_actual.md`. **No** fueron incluidos como fuentes por decisión del solicitante; pueden contener material de portal/UI más detallado que la consolidación no recoge.

---

## 2. Resumen de cobertura por sección destino

Leyenda: `Alta` (≥ 70 % del contenido se puede escribir sin suposiciones) · `Media` (30–70 % cubierto) · `Baja` (< 30 % cubierto).

| Carpeta destino                      | Archivo                                  | Cobertura | Fuente principal           |
|---------------------------------------|-------------------------------------------|-----------|----------------------------|
| `00-overview/`                        | `vision.md`                               | Alta      | F1 §1–2, F2 (intro)        |
| `00-overview/`                        | `glosario.md`                             | Alta      | F2 (Glosario)              |
| `00-overview/`                        | `stakeholders.md`                         | Media     | F1 §3 (actores)            |
| `01-funcional/`                       | `requerimientos-funcionales.md`           | Alta      | F1 §2, F2, T1 §9           |
| `01-funcional/`                       | `requerimientos-no-funcionales.md`        | **Baja**  | F2 (tiempos ETL implícitos)|
| `01-funcional/`                       | `reglas-de-negocio.md`                    | Alta      | F1 §6, R1, R2              |
| `01-funcional/`                       | `casos-de-uso.md`                         | Media     | F1 §4, F2 (flujos)         |
| `01-funcional/`                       | `procesos-de-negocio.md`                  | Media     | F2, R2                     |
| `02-arquitectura/`                    | `arquitectura-general.md`                 | Alta      | A1                         |
| `02-arquitectura/`                    | `componentes.md`                          | Alta      | A1 §3, T1 §3               |
| `02-arquitectura/`                    | `integraciones.md`                        | Media     | A1, T1 §10                 |
| `02-arquitectura/decisiones/`         | ADRs                                      | Media     | A1 §11 (tabla decisiones)  |
| `03-tecnico/`                         | `stack-tecnologico.md`                    | Alta      | T1 §2                      |
| `03-tecnico/`                         | `modelo-de-datos.md`                      | Alta      | T1 §5, F2                  |
| `03-tecnico/`                         | `api.md`                                  | Alta      | T1 §9, A1 §8               |
| `03-tecnico/`                         | `estandares-y-convenciones.md`            | **Baja**  | No hay sección en fuentes  |
| `04-operacion/`                       | `ambientes.md`                            | **Baja**  | T1 §4, §13 (solo dev)      |
| `04-operacion/`                       | `despliegue.md`                           | Media     | T1 §13 (Docker + compose)  |
| `04-operacion/`                       | `runbook.md`                              | Media     | F2 (manejo de errores), R2 |
| `04-operacion/`                       | `monitoreo-y-alertas.md`                  | **Baja**  | A1 §10 (sólo observable.)  |
| `05-seguridad/`                       | `autenticacion-autorizacion.md`           | **Baja**  | A1 §9, T1 §14              |
| `05-seguridad/`                       | `manejo-de-datos-sensibles.md`            | **Baja**  | A1 §9, A1 §13              |
| `05-seguridad/`                       | `cumplimiento.md`                         | **Baja**  | Nada explícito             |
| `06-onboarding/`                      | `README.md`                               | Media     | Derivable de F1+T1+A1      |
| `06-onboarding/`                      | `primer-dia.md`                           | **Baja**  | Nada explícito             |
| `06-onboarding/`                      | `levantar-ambiente-local.md`              | Alta      | T1 §4, `siga/README.md`    |
| `07-entrega/`                         | `checklist-entrega.md`                    | **Baja**  | Nada explícito             |
| `07-entrega/`                         | `matriz-trazabilidad.md`                  | Media     | R1 (matriz reglas/estado)  |

---

## 3. Top 10 gaps críticos detectados

Los huecos siguientes impiden completar secciones enteras sin inventar. Se recomienda resolverlos con el equipo antes de aprobar la documentación consolidada.

| # | Gap                                                                                  | Impacto                                                | Quién debería responder                |
|---|--------------------------------------------------------------------------------------|--------------------------------------------------------|----------------------------------------|
| 1 | **Requerimientos No Funcionales formales** (SLOs, disponibilidad, RTO/RPO, latencia, capacidad, accesibilidad). Las únicas referencias cuantitativas son tiempos ETL estimados en F2.| Sección `01-funcional/requerimientos-no-funcionales.md` queda como esqueleto. | Arquitectura / Producto                |
| 2 | **Esquema de autenticación productivo.** A1 §9 y T1 §14 reconocen que DRF está hoy en `AllowAny`. No se documenta auth real (OIDC / SSO / API Keys), políticas de roles ni flujo de login del portal.| `05-seguridad/autenticacion-autorizacion.md` queda con advertencia "no implementado".| Seguridad / TI                         |
| 3 | **Clasificación de datos personales y tratamiento (Ley 1581).** Las fuentes mencionan que cédulas/nombres/valores requieren protección, pero no hay política de datos, encargado, finalidades ni retención.| `05-seguridad/manejo-de-datos-sensibles.md` y `cumplimiento.md`. | Oficial de protección de datos / Legal |
| 4 | **Ambientes (Dev/QA/Prod).** Sólo se documenta el `docker-compose` para desarrollo (`localhost:9010 → siga:8000`). No hay descripción de QA ni producción, ni de cómo se promueven cambios.| `04-operacion/ambientes.md` y `despliegue.md` quedan con info parcial.| DevOps / TI                            |
| 5 | **Monitoreo, alertas y logs.** A1 §10 enlista trazabilidad de aplicación (estados, contadores, dashboard interno), pero no hay stack de observabilidad (logs centralizados, métricas, alertas, dashboards externos).| `04-operacion/monitoreo-y-alertas.md` queda como gap principal. | Operación / DevOps                     |
| 6 | **Estándares de código y convenciones.** Ninguna fuente describe: estilo (PEP 8 / Black / Ruff), branching, commits, code review, política de tests, cobertura mínima, definición de "hecho".| `03-tecnico/estandares-y-convenciones.md` queda casi vacío. | Líder técnico                          |
| 7 | **Decisiones arquitectónicas con contexto histórico.** A1 §11 tiene una tabla "decisión / justificación / consecuencia", pero sin fecha, autor, alternativas evaluadas ni estado. Lo necesario para volver esa tabla en ADRs.| `02-arquitectura/decisiones/` se generará como ADRs "tipo borrador". | Arquitectura / Líder técnico           |
| 8 | **Reglas de Talento Humano más allá de medicina prepagada.** R2 lista decenas de reglas (auxilio educativo, vacaciones, primas, préstamos, FONDEFIN, parqueadero, licencias, escala salarial, crédito condonable). R1 declara que el alcance actual de SIGA es **solo** medicina prepagada. **No está confirmado** si esas reglas adicionales pertenecen al alcance documentado.| Define qué entra en `01-funcional/reglas-de-negocio.md` y `requerimientos-funcionales.md`. | Producto / Talento Humano              |
| 9 | **Stakeholders nominales y responsables.** F1 §3 lista actores genéricos (Analista de Gestión Humana, Usuario administrativo, Responsable de prepagada), pero sin nombres, áreas formales, mails ni RACI. F2 menciona a "Daniel Campos" como responsable técnico (en `documento_funcional_actual.md`, **no incluido como fuente**).| `00-overview/stakeholders.md` queda con tabla genérica.| Talento Humano / PMO                   |
|10 | **Matriz de trazabilidad Requerimiento → Componente → Prueba.** No hay catálogo de pruebas, ni IDs de requerimientos formales (solo "capacidades" de F1 §2 y reglas RN/MP). Sin IDs estables no se puede construir trazabilidad.| `07-entrega/matriz-trazabilidad.md` queda como tabla parcial basada en R1.| QA / Líder técnico                     |

---

## 4. Gaps secundarios (no bloqueantes pero relevantes)

| Ámbito                            | Gap específico                                                                          |
|-----------------------------------|------------------------------------------------------------------------------------------|
| Integraciones                     | No se describe el contrato/SLA con Kactus ni la frecuencia y mecanismo de actualización de `prepagada.db`. A1 §7.3 sólo enumera tablas/vistas. |
| Integraciones                     | El portal web React/UI se menciona en F2 pero no se aporta repositorio, contrato de consumo ni endpoints en uso real (todos los endpoints son `AllowAny`).|
| Modelo de datos                   | Diccionario de campos parcial: T1 §5 da tablas y propósito; F2 da ejemplos de instancia, pero faltan tipos, longitudes, nulabilidad, índices y reglas de unicidad formales.|
| Modelo de datos                   | No se describe la estrategia de migraciones (Django migrations vigentes, política de versionado de migraciones, freeze por release).|
| API                               | No hay contratos JSON detallados (esquemas request/response) para todos los endpoints; sólo se listan rutas, verbos y vistas.|
| Despliegue                        | Variables de entorno productivas, secrets management y proceso de rotación de claves no documentados.|
| Despliegue                        | Estrategia de backups (BD principal y `prepagada.db`) y procedimiento de restore no documentados, aunque A1 §9 los recomienda.|
| Operación                        | No hay procedimientos de incidentes (severidades, on-call, comunicación, postmortem). El "manejo de errores" descrito en F2 es del *sistema*, no del *equipo*.|
| Cumplimiento                     | EFR se cita como output, pero no como obligación auditada con frecuencia/responsable. No hay referencia a otras normativas (Habeas Data, retención contable, DIAN).|
| Reglas tributarias                | Valor UVT y "límite no gravable" se ejemplifican con $49.799 (2026) en `documento_funcional_actual.md` (no fuente). Las fuentes oficiales sólo mencionan "configurable". Falta procedimiento anual de actualización oficial.|
| Reglas de negocio                 | R1 tiene 31 reglas (de 45) en estado "No soportado" o "Por definir". Esto es información valiosa de roadmap pero no de funcionalidad actual. La consolidación debe diferenciar claramente "implementado" vs "pendiente".|
| Reglas de negocio                 | F2 enumera 4 validaciones (V.1–V.4); F1 §6 enumera 11 reglas (RN-01–RN-11). Hay **discrepancia menor**: F2 dice que valor negativo se marca como ERROR salvo ajuste Colsanitas, RN-07 admite descuento negativo en Colsanitas — coherente, pero el documento consolidado debe armonizar la redacción.|
| Onboarding                        | No hay ruta de lectura por rol declarada en las fuentes. Se construirá una "mejor esfuerzo" en `06-onboarding/README.md`.|
| Entrega / Auditoría              | No existe checklist formal de entrega al cliente (criterios de aceptación, evidencias requeridas). Se propondrá una versión genérica como `PENDIENTE`.|

---

## 5. Inconsistencias detectadas entre fuentes

| Tema                              | Fuente A dice…                                       | Fuente B dice…                                                   | Resolución sugerida |
|-----------------------------------|------------------------------------------------------|------------------------------------------------------------------|----------------------|
| Rechazo de duplicado por hash     | F2 (Fase E.1): el archivo duplicado por SHA256 es **rechazado** antes de procesamiento. | T1 §14 y A1 §13: "el hash se almacena, pero el flujo actual **no rechaza** automáticamente duplicados". | Verificar con el código fuente real cuál comportamiento está activo hoy. Marcar como `PENDIENTE` en el consolidado.|
| Detección de proveedor por columnas | T1 §6.3: `SUB CTO` y `NUMID` → AXA; `Numero de Familia` → Colsanitas. | F1 §5 lo confirma. F2 (Fase E.3) habla de "primeras 20 filas" y nombre del campo `Número de Familia` con tilde. | Unificar nomenclatura: el código usa `Numero de Familia` (sin tilde). |
| Profundidad de escaneo de encabezado | T1 §6.4: hasta **16 filas** (AXA), **21 filas** (Colsanitas). | F2 (Fase E.4): "16–21 filas". | Mantener la cifra técnica de T1, que es la más precisa.|
| Estado civil / parentesco         | R2 (Talento Humano): requiere `estado civil`, dependencia económica, soporte EPS. | F1, F2, T1: no expone esos campos como datos del modelo. | Documentar como **gap de datos**: el manual exige información que el sistema actual no captura.|
| Antigüedad mínima (2 meses)       | R2: "más de dos meses vinculado" / "superado periodo de prueba". | F1/F2/T1: no validan antigüedad en el cálculo 80/20. | Documentar como **regla no implementada** (MP-002 en R1). |

---

## 6. Decisiones funcionales pendientes (heredadas de R1 y R2)

Estas no son gaps de documentación sino **decisiones de negocio** que el manual de Talento Humano no resuelve. Se replican aquí para visibilidad:

1. Si un familiar no elegible debe aparecer en planilla con `100% empleado` o excluirse.
2. Cómo se calcula el promedio de referencia para pólizas externas (general, por proveedor, por plan, por grupo familiar).
3. Si el prorrateo por ingreso/retiro es por días calendario, días laborales o corte mensual.
4. Si el periodo de prueba se valida como dato explícito o se asume cubierto por la regla de "más de dos meses".
5. Vigencia de las excepciones autorizadas por Talento Humano (mensual, anual, abierta).
6. Comportamiento del recálculo de planilla (reemplaza, versiona, o crea nueva).
7. Si SIGA debe automatizar más allá de medicina prepagada (auxilio educativo, primas, etc.).
8. Fuente oficial automatizada de SMMLV, UVT, DTF y demás variables económicas.
9. Inconsistencia textual del manual: regla de crédito educativo menciona "promedio mínimo de tres punto cinco (3.0)" — contradictorio en texto vs número (R2).

---

## 7. Recomendación al solicitante

> ⚠️ De las 8 carpetas destino del esqueleto, **5 contienen al menos un archivo con cobertura Baja** (`requerimientos-no-funcionales.md`, `estandares-y-convenciones.md`, `ambientes.md`, `monitoreo-y-alertas.md`, los 3 de seguridad, `primer-dia.md`, `checklist-entrega.md`). Esto supera el umbral del 30 % de información faltante mencionado en el proceso de trabajo, por lo cual se **detiene la generación** hasta recibir confirmación.

**Posibles caminos a elegir:**

1. **Generar todo el set con marcas `> ⚠️ PENDIENTE` donde haga falta**, dejando esqueletos accionables para el equipo. Es la opción más rápida y resalta el trabajo restante.
2. **Generar sólo lo que tiene cobertura Alta y Media**, dejando los archivos de cobertura Baja sin crear hasta que se entregue información adicional.
3. **Pausar y recopilar primero información para los Top 10 gaps** antes de generar nada más. Es la opción más limpia pero la más lenta.

---

## 8. Fuente

Este archivo fue elaborado a partir del análisis transversal de:

- `siga/DOCUMENTACION_FUNCIONAL.md` (F1)
- `siga/DOCUMENTO_FUNCIONAL_BENEFICIOS_SALUD.md` (F2)
- `siga/DOCUMENTACION_TECNICA.md` (T1)
- `siga/ARQUITECTURA_SOFTWARE.md` (A1)
- `docs/matriz-reglas-medicina-prepagada-siga.md` (R1)
- `docs/reglas-talento-humano-siga.md` (R2)
