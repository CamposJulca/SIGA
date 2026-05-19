# Módulo 6 — Pensionados

| Campo                | Valor                                                                  |
|----------------------|------------------------------------------------------------------------|
| Orden en la cinta    | 6 / 8                                                                  |
| Tiempo sugerido demo | 5 minutos                                                              |
| Estado               | Implementado (con regla de aplicación parcial — ver "Lo que aún NO hace") |
| Fuente               | `docs/01-funcional/requerimientos-funcionales.md` (RF-302); `casos-de-uso.md` (CU-005); `reglas-de-negocio.md` (MP-006, MP-007) |

---

## En una frase

> Pensionados es el **registro de quienes asumen el 100% del beneficio**: ex-colaboradores que conservan la prepagada del convenio pero ya no son nómina activa de Finagro.

## ¿Para qué sirve?

Cuando una persona pasa a pensión, **sale de la nómina activa** pero puede mantener la medicina prepagada bajo la póliza colectiva de Finagro. En ese caso, Finagro **no aporta el 80%**; el pensionado asume el 100% del valor, aprovechando solo la tarifa colectiva.

Estos casos son los que en el cruce del Módulo 3 aparecen como **"No encontrado"** o **"Inactivo"**. Pensionados es la pestaña donde TH registra a esa persona para que el sistema sepa cómo tratarla en el cálculo: aplicar 100% empleado.

Esto evita que TH tenga que excluir manualmente del cálculo a estos casos cada mes.

## ¿Quién lo usa?

- Responsable de prepagada (registra y mantiene la lista).
- Analista de Gestión Humana (consulta y revisión).

## ¿Qué información entra?

Por cada pensionado:

| Campo            | Descripción                                              |
|------------------|----------------------------------------------------------|
| Cédula           | Documento del pensionado.                                |
| Nombre           | Nombre completo.                                          |
| EPS              | AXA Colpatria o Colsanitas.                                |
| Valor mensual    | Cuota del grupo familiar.                                  |
| Fecha inicio     | Cuándo empieza el beneficio bajo régimen pensionado.        |
| Fecha fin        | (Opcional) Cuándo termina, si se conoce.                   |
| Activo           | Si el beneficio está vigente.                              |
| Observaciones    | Notas adicionales (Ley 100, plan, etc.).                   |

## ¿Qué información sale?

- **Lista de pensionados activos** con todos sus datos.
- **Vista del estado** (activo / no activo).
- Indirectamente, **impacto en la planilla**: cuando se calcula el Módulo 3, los pensionados registrados quedan marcados con regla "100% empleado".

## Flujo paso a paso (demo en vivo)

1. **Abrir la pestaña Pensionados**.
2. Mostrar la **lista actual** de pensionados activos.
3. **Crear un nuevo pensionado** en vivo (con datos de ejemplo o de un caso real conocido):
   - Ingresar cédula, nombre, EPS, valor mensual.
   - Marcar fecha inicio.
   - Dejar fecha fin vacía (beneficio vigente).
   - Marcar "Activo".
4. **Guardar** y mostrar que aparece en la lista.
5. **Editar** un pensionado existente (mostrar el ícono de lápiz).
6. **Desactivar** uno (sin borrar): desmarcar "Activo" y guardar. Explicar que el histórico se mantiene.
7. Conectar con el flujo:
   > "Cuando vayamos al Módulo 3 a calcular la planilla del mes, este pensionado aparecerá con regla 100% empleado, así no tenemos que excluirlo a mano."

## Reglas de negocio aplicadas

| ID     | Regla en lenguaje de negocio                                                                                  |
|--------|----------------------------------------------------------------------------------------------------------------|
| MP-006 | Para un pensionado registrado y activo, Finagro aporta 0% y el pensionado asume 100%. **Estado: PARCIAL** — la regla existe en el modelo, pero hay que confirmar que se aplique automáticamente en cada cálculo. |
| MP-007 | El pensionado aprovecha la tarifa colectiva, pero asume el pago completo. **Estado: PARCIAL** — falta asegurar la separación visual en la planilla y la exportación. |

## Lo que aún NO hace (y conviene mencionar)

- **No se sincroniza automáticamente con la nómina**. El alta y la baja de pensionados son **manuales**: TH debe identificar el caso y registrarlo aquí.
- **No tiene historial detallado de cambios** (quién editó qué y cuándo).
- **No tiene auditoría documental**: no hay forma de adjuntar el documento de pensión, la carta de aceptación, etc.
- **No avisa** cuando una persona deja de aparecer en la factura de la EPS (puede haber sido retiro de la póliza colectiva sin que TH lo refleje).
- **Hoy no hay autenticación nominal**, así que no queda registro del usuario humano que creó/editó el pensionado.

## Preguntas que probablemente nos harán (anticipadas)

- **P:** "¿Cómo sabe TH cuándo registrar a alguien acá?"
  **R:** Cuando en el cruce del Módulo 3 aparece como "No encontrado" o "Inactivo" y se confirma con nómina/talento humano que es un pensionado.

- **P:** "¿Puedo cargar un Excel masivo de pensionados?"
  **R:** *(VALIDAR: las fuentes consolidadas no documentan carga masiva; hoy se entiende como creación uno a uno.)*

- **P:** "¿Qué pasa si dejo el pensionado activo pero la EPS lo dio de baja?"
  **R:** En la planilla del periodo siguiente no va a aparecer porque no estará en la factura. La regla del pensionado solo se aplica si la persona efectivamente está en la factura del periodo.

## Preguntas que NOSOTROS le hacemos a TH (validación)

- [ ] ¿Cuántos pensionados activos manejan hoy aproximadamente? ¿Esa cifra ha crecido en el último año?
- [ ] ¿Cómo identifican hoy a un pensionado para registrarlo? ¿Lo notifica el área de pensiones? ¿Lo detecta TH en el cruce mensual?
- [ ] ¿Necesitan poder **adjuntar documentos** al registro del pensionado (carta, resolución de pensión)?
- [ ] ¿Hay reglas distintas según el tipo de pensión (vejez, invalidez, sobrevivencia)?
- [ ] ¿Necesitan **carga masiva** desde Excel, o el alta uno a uno cubre la frecuencia real?
- [ ] **Confirmar (importante):** ¿el 100% empleado es siempre 100%, o pueden existir excepciones (por ejemplo, beneficios diferenciales por antigüedad)?
- [ ] ¿Qué hacer con un pensionado que también tiene cónyuge o hijo cubierto? ¿Cómo se factura?

---

**Fuente:** `docs/01-funcional/requerimientos-funcionales.md` §4 (RF-302); `docs/01-funcional/reglas-de-negocio.md` §4 (MP-006, MP-007); `docs/01-funcional/casos-de-uso.md` (CU-005).
