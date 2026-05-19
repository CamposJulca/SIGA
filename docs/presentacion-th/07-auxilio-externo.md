# Módulo 7 — Auxilio Externo

| Campo                | Valor                                                                  |
|----------------------|------------------------------------------------------------------------|
| Orden en la cinta    | 7 / 8                                                                  |
| Tiempo sugerido demo | 5 minutos                                                              |
| Estado               | Implementado solo como **registro** — el motor de cálculo de las reglas del manual NO está implementado. Ver "Lo que aún NO hace". |
| Fuente               | `docs/01-funcional/requerimientos-funcionales.md` (RF-303); `casos-de-uso.md` (CU-006); `reglas-de-negocio.md` (MP-019..MP-025) |

---

## En una frase

> Auxilio Externo es **el registro de quienes están fuera del convenio**: empleados con prepagada contratada en otra aseguradora distinta a AXA o Colsanitas, a quienes Finagro reconoce un auxilio mediante recibo.

## ¿Para qué sirve?

El manual contempla casos en los que un colaborador **no está en la póliza colectiva de Finagro** pero tiene una prepagada propia (porque ingresó con un plan individual, porque su familia está en otra EPS, o por una autorización gerencial). En esos casos, Finagro puede reconocer un **auxilio económico** sobre esa póliza externa.

Hoy SIGA permite **dejar el registro** de esos colaboradores y su valor, pero **no tiene implementado el motor que aplica las reglas del manual** sobre pólizas externas (topes, promedio, recibos, retroactividad).

## ¿Quién lo usa?

- Responsable de prepagada (registra y mantiene la lista).
- Analista de Gestión Humana (consulta).

## ¿Qué información entra?

Por cada caso registrado (formato similar al de Pensionados):

| Campo            | Descripción                                              |
|------------------|----------------------------------------------------------|
| Cédula           | Documento del colaborador.                                |
| Nombre           | Nombre completo.                                          |
| Proveedor        | EPS o aseguradora externa al convenio.                    |
| Valor mensual    | Cuota mensual reconocida.                                  |
| Fecha inicio     | Cuándo empieza el auxilio.                                  |
| Fecha fin        | (Opcional) Cuándo termina.                                  |
| Activo           | Si el auxilio está vigente.                                  |
| Observaciones    | Notas adicionales (motivo, autorización, plan).              |

## ¿Qué información sale?

- **Lista de auxilios externos activos** con todos sus datos.
- Inclusión en el **informe EFR** (Módulo 5 / salida agregada).

## Flujo paso a paso (demo en vivo)

1. **Abrir la pestaña Auxilio Externo**.
2. Mostrar la **lista actual**.
3. **Crear un caso** con datos de ejemplo:
   - Cédula, nombre, proveedor externo, valor mensual, fecha inicio.
   - Observaciones (motivo).
4. **Guardar** y mostrar que aparece en la lista.
5. **Editar** un caso. **Desactivar** otro.
6. Aclarar el alcance:
   > "Hoy lo que tenemos es el registro. Cuando lleguemos a implementar las reglas del manual sobre pólizas externas, este registro será el insumo. Hoy NO calcula tope por promedio, NO valida recibos mensuales, NO aplica retroactividad."

## Reglas de negocio aplicadas

> ⚠️ A diferencia de los otros módulos, **el módulo de Auxilio Externo NO tiene reglas calculadas hoy**. Solo es un registro de catálogo. Esto debe ser muy explícito con TH.

## Lo que aún NO hace (y conviene mencionar — IMPORTANTE)

Todo lo que el manual prevé para pólizas externas está como **roadmap**:

| Regla del manual                                                                                                  | Estado en SIGA  |
|--------------------------------------------------------------------------------------------------------------------|-----------------|
| MP-019 — Si la póliza externa tiene mayor valor que la colectiva, reconocer aporte sobre el **promedio** de Finagro. | No implementado |
| MP-020 — Si la póliza externa tiene menor valor, reconocer aporte sobre el **valor real** de esa póliza.            | No implementado |
| MP-021 — Reconocimiento mensual contra **recibo de pago** validado.                                                  | No implementado |
| MP-022 — Primera solicitud requiere **certificación inicial** completa (vigencia, tomador, beneficiarios, costo, forma de pago). | No implementado |
| MP-023 — Certificación debe **actualizarse anualmente** o por cambio.                                                | No implementado |
| MP-024 — Cambios (vigencia, costo, beneficiarios) deben **recalcular** desde la fecha del cambio.                    | No implementado |
| MP-025 — Retroactividad máxima de **3 meses calendario**.                                                              | No implementado |

Además:

- No hay **carga de recibos mensuales** ni validación documental.
- No hay **historial documental** del caso.
- No hay **alertas** por vencimiento de certificación anual o por recibo no presentado.
- No hay un **cálculo automático del promedio** de pólizas Finagro.

## Preguntas que probablemente nos harán (anticipadas)

- **P:** "Entonces, ¿cómo aplicamos hoy el 80% al colaborador con póliza externa?"
  **R:** Hoy se hace **manualmente fuera del sistema**. El registro en SIGA sirve para tenerlo identificado y para el informe EFR, pero el cálculo del aporte real lo hace TH a mano.

- **P:** "¿Si tengo 5 casos de auxilio externo, los podemos cargar todos?"
  **R:** Sí. Se crean uno por uno. Carga masiva *(VALIDAR)*.

- **P:** "¿Tenemos hoy el promedio de pólizas Finagro?"
  **R:** Ese promedio **no se calcula en SIGA**. Es uno de los desarrollos pendientes (MP-019) y depende de una **decisión funcional**: cómo se calcula el promedio (general, por proveedor, por tipo de plan, por grupo familiar). Esto es algo que necesitamos definir con TH.

## Preguntas que NOSOTROS le hacemos a TH (validación)

- [ ] ¿Cuántos casos de auxilio externo manejan hoy? ¿Es frecuente o excepcional?
- [ ] ¿Cómo aplican hoy las reglas del manual para esos casos (MP-019..MP-025)? ¿Hay un Excel? ¿Una persona responsable?
- [ ] **Decisión funcional pendiente:** el promedio de pólizas Finagro, ¿es general, por proveedor, por tipo de plan o por grupo familiar?
- [ ] ¿Reciben los recibos mensuales hoy? ¿Quién los valida y cómo?
- [ ] ¿Tienen alguna certificación inicial estándar que la aseguradora externa envía? ¿En qué formato?
- [ ] ¿Cómo manejan hoy la retroactividad de 3 meses?
- [ ] ¿Necesitan que SIGA **alerte** cuando vence la certificación anual o cuando un colaborador no presenta el recibo del mes?
- [ ] ¿Estos casos los reportan en el informe EFR? ¿Cómo los separan de los del convenio?

---

**Fuente:** `docs/01-funcional/requerimientos-funcionales.md` §4 (RF-303), §6 (roadmap MP-019..MP-025); `docs/01-funcional/reglas-de-negocio.md` §4 (MP-019..MP-025 todos en estado **No soportado**), §6 Fase 3 (Pólizas externas), §7 decisiones pendientes; `docs/01-funcional/casos-de-uso.md` (CU-006).
