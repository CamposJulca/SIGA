# Cierre y Siguientes Pasos — 7 minutos

| Campo            | Valor                                                        |
|------------------|--------------------------------------------------------------|
| Tiempo sugerido  | 5–7 minutos                                                  |
| Fuente           | `docs/00-overview/vision.md`; `docs/00-overview/gaps.md`; `docs/01-funcional/reglas-de-negocio.md` |

---

## 1. Resumen de lo que vimos hoy

Recorrimos los **8 módulos** de SIGA — Beneficios de Salud:

| # | Módulo                         | Lo que valida                                                                 |
|---|--------------------------------|--------------------------------------------------------------------------------|
| 1 | Dashboard                       | Foto del estado actual y evolución.                                            |
| 2 | Facturas EPS                    | Carga de archivos, validación, errores, novedades, exportación consolidada.    |
| 3 | Planilla 80/20                  | Cruce con nómina y cálculo de la planilla mensual.                              |
| 4 | Apoyo Gravable / No Gravable     | Clasificación tributaria del aporte de la empresa.                              |
| 5 | Causación                       | Salida para contabilidad por EPS y conciliación entre periodos.                  |
| 6 | Pensionados                     | Registro de quienes asumen 100% del beneficio.                                  |
| 7 | Auxilio Externo                 | Registro de casos fuera del convenio (motor de cálculo aún no implementado).     |
| 8 | Política 80/20                   | Configuración del cálculo y de los parámetros tributarios/contables.            |

## 2. Mensaje de cierre (lo que queremos que se lleven)

> Lo que está hoy **automatiza la operación mensual de medicina prepagada** de extremo a extremo, con trazabilidad fila por fila y separación tributaria. Lo que NO está, no se les va a esconder: hay reglas del manual que necesitamos definir e implementar, y para eso necesitamos las decisiones funcionales de TH.

## 3. Recordatorio del roadmap (lo que aún NO está implementado)

### 3.1 Dentro del mismo subdominio (Medicina Prepagada)

Reglas del manual THU-DOC-002 que figuran como pendientes de implementar:

| Tema                                                                   | Reglas afectadas        | Estado          |
|-------------------------------------------------------------------------|-------------------------|-----------------|
| Antigüedad mínima (más de 2 meses)                                       | MP-002                   | No soportado    |
| Aceptación del beneficio y autorización del descuento                    | MP-003, MP-004           | No soportado    |
| Elegibilidad por parentesco, edad, dependencia económica, discapacidad    | MP-008..MP-017           | Parcial / No soportado |
| Sustitución de beneficiarios (reglas para soltero, casado, etc.)         | MP-012..MP-015           | No soportado    |
| Pólizas externas — todo el cálculo                                       | MP-019..MP-025           | No soportado    |
| Prorrateo por ingreso, aceptación parcial o retiro                       | MP-026, MP-027           | No soportado    |
| Soportes documentales de parentesco                                       | MP-017, MP-044           | No soportado    |
| Excepciones autorizadas por TH                                            | MP-043                   | No soportado    |
| Recálculo de planilla                                                     | MP-042                   | Por definir     |
| Política vigente por periodo (estricta)                                   | MP-032                   | Parcial         |

### 3.2 Fuera del subdominio actual (otros beneficios del manual)

El manual THU-DOC-002 cubre muchos más beneficios que **NO** están dentro del alcance actual de SIGA. Si TH los considera prioridad, los conversamos como roadmap:

- Auxilio educativo para hijos.
- Vacaciones y compensaciones (incluida compensación en dinero con 6 días extralegales por 15).
- Primas extralegales (vacaciones, navidad, antigüedad) y bonificación por quinquenio.
- Auxilio de incapacidad por escalones (1–90 días, 91–180 días).
- Auxilio extralegal de alimentación.
- Auxilio de parqueadero.
- FONDEFIN.
- Préstamo de libre inversión.
- Crédito educativo condonable.
- Permisos, licencias y flexibilidad.
- Convocatorias internas, encargos, nivelación de escala salarial.
- Póliza funeraria y seguro de vida.

## 4. Decisiones funcionales pendientes (las que necesitamos de TH)

Estas son **decisiones de negocio** que el manual no resuelve y que SIGA necesita para crecer:

1. Si un familiar no elegible debe aparecer en planilla con 100 % empleado o excluirse del archivo de aporte.
2. Cómo se calcula el **promedio de pólizas Finagro** para el tope de pólizas externas (promedio general, por proveedor, por tipo de plan, por grupo familiar o por beneficiario).
3. Si el **prorrateo** por ingreso o retiro se hace por días calendario, días laborales o por corte administrativo mensual.
4. Si el periodo de prueba se valida como dato explícito o se asume cubierto por la regla de "más de dos meses".
5. Si las **excepciones autorizadas por TH** tienen vigencia mensual, anual o abierta.
6. Si el **recálculo de planilla** reemplaza la planilla anterior o crea una nueva versión auditable.

## 5. Compromisos y owners

Plantilla para registrar en vivo durante la reunión.

| # | Compromiso                                                                                | Owner              | Fecha límite |
|---|--------------------------------------------------------------------------------------------|--------------------|--------------|
|   |                                                                                            |                    |              |
|   |                                                                                            |                    |              |
|   |                                                                                            |                    |              |
|   |                                                                                            |                    |              |
|   |                                                                                            |                    |              |

## 6. Próximos pasos sugeridos por el equipo SIGA

1. **Cerrar** los puntos de la lista [`preguntas-de-validacion.md`](preguntas-de-validacion.md) que queden abiertos hoy, en una sesión de seguimiento corta.
2. **Priorizar el roadmap** del subdominio actual: cuáles de las reglas no implementadas son más urgentes para TH (prorrateos, elegibilidad de beneficiarios, pólizas externas…).
3. **Definir las decisiones pendientes** (§4 arriba) para desbloquear las siguientes fases.
4. **Validar con tributaria y contabilidad** los códigos contables de la Política 80/20 y el procedimiento de actualización anual del UVT.
5. **Definir el esquema de autenticación** del sistema, dado que hoy no hay control de quién hace qué (afecta auditoría: MP-041, política, pensionados).
6. Acordar con TH la **siguiente reunión** y su agenda.

## 7. Cómo se documentará lo conversado hoy

Las respuestas a las preguntas de validación se irán cargando en [`preguntas-de-validacion.md`](preguntas-de-validacion.md) marcando cada ítem como resuelto/abierto.

Los compromisos pasarán a la herramienta de seguimiento del equipo (definir cuál).

---

**Cierre del presentador:**

> Gracias por el tiempo. Lo importante de hoy fue tener claro qué hace SIGA, qué no hace, y qué necesitamos definir entre los dos equipos para que la herramienta refleje exactamente la operación que ustedes esperan.

---

**Fuente:** `docs/00-overview/vision.md` §5 (Fuera de alcance); `docs/00-overview/gaps.md` Top 10 #8 (alcance Talento Humano); `docs/01-funcional/reglas-de-negocio.md` §4 (estados de las reglas MP), §6 (priorización roadmap), §7 (decisiones funcionales pendientes), §8 (roadmap extendido).
