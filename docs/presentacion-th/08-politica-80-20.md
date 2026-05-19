# Módulo 8 — Política 80/20

| Campo                | Valor                                                                  |
|----------------------|------------------------------------------------------------------------|
| Orden en la cinta    | 8 / 8                                                                  |
| Tiempo sugerido demo | 6 minutos                                                              |
| Estado               | Implementado (con vigencia por periodo parcial — MP-032)                |
| Fuente               | `docs/01-funcional/requerimientos-funcionales.md` (RF-301); `casos-de-uso.md` (CU-004); `reglas-de-negocio.md` (MP-032, MP-034) |

---

## En una frase

> Política 80/20 es **el panel de parámetros**: define los porcentajes que aplica el motor de cálculo, el límite UVT, los conceptos contables y el valor UVT vigente para el año.

## ¿Para qué sirve?

Es la única pantalla donde se **configuran las reglas del cálculo** que aplica el Módulo 3. Sin política configurada, el motor no puede calcular planilla. Cuando cambian las condiciones tributarias (por ejemplo: la DIAN publica el UVT del nuevo año) o cuando Finagro modifica la distribución, se registra una **nueva política con fecha de vigencia**.

El sistema mantiene el **histórico** de todas las políticas registradas. Esto es importante para auditoría: cualquier planilla calculada queda asociada a la política que se usó en ese momento.

## ¿Quién lo usa?

- Responsable de prepagada (configura y mantiene).
- Tributaria (asesora el UVT y el límite).
- Contabilidad (valida los conceptos contables).

## ¿Qué información entra?

| Campo                       | Descripción                                                                         |
|-----------------------------|-------------------------------------------------------------------------------------|
| % empresa                   | Porcentaje que paga la empresa (normalmente 80).                                     |
| % empleado                  | Porcentaje que se descuenta al empleado (normalmente 20).                            |
| UVT límite                  | Número de UVT del límite (normalmente 16, Art. 387 E.T.).                            |
| Valor UVT                   | Valor en pesos de un UVT en el año vigente. **Se actualiza cada año.**                |
| % empresa pensionado         | Porcentaje para pensionados, si difiere (normalmente queda en 80, pero la regla MP-006 fija el caso pensionado en 0/100). |
| Cod. apoyo no gravable      | Código contable de Kactus para el aporte dentro del límite.                          |
| Cod. apoyo gravable         | Código contable de Kactus para el exceso.                                            |
| Cod. descuento empleado     | Código contable de Kactus para el descuento al empleado.                              |
| Notas                       | Fundamento de la política (ej.: "Resolución interna 2026-003").                       |
| Vigente desde              | Fecha a partir de la cual aplica la política.                                          |

## ¿Qué información sale?

- **Lista de políticas registradas** con su fecha de vigencia.
- **Política activa** (la que se aplica en los cálculos del Módulo 3).
- **Cálculo en pantalla** del **límite resultante** (UVT límite × Valor UVT).

## Flujo paso a paso (demo en vivo)

1. **Abrir la pestaña Política 80/20**.
2. **Mostrar la política vigente** con todos sus campos llenos.
3. Apuntar al campo **Valor UVT**:
   > "Este es el campo que hay que actualizar al inicio de cada año cuando la DIAN publique el nuevo UVT."
4. Mostrar el cálculo del **límite resultante**:
   > "16 UVT × Valor UVT = Límite mensual no gravable por empleado."
5. **Mostrar el histórico** de políticas: explicar que cada planilla calculada queda asociada a la política con la que se calculó.
6. (Si hay tiempo) **Crear una nueva política** (sin guardar realmente, solo demostrar):
   - Cambiar porcentajes, UVT o conceptos.
   - Asignar fecha de vigencia desde el 1 de enero del próximo año.

## Reglas de negocio aplicadas

| ID     | Regla en lenguaje de negocio                                                                            |
|--------|----------------------------------------------------------------------------------------------------------|
| RF-301 | Permite crear, listar, consultar y actualizar políticas.                                                  |
| MP-032 | El cálculo de la planilla debe usar la política vigente al periodo. **Estado: PARCIAL** — hoy se toma la política más reciente. Hay que confirmar manualmente al cambiar de política. |
| MP-034 | Los conceptos contables están como campos en la política. **Estado: PARCIAL** — confirmar formato exigido por nómina. |
| MP-041 | Cada planilla queda asociada a la política aplicada. **Estado: PARCIAL** — falta el usuario real (depende de autenticación). |
| MP-045 | El histórico de políticas se conserva. **Estado: PARCIAL** — sólo se versiona la política, no todas las reglas (parentescos, elegibilidad, etc.). |

## Lo que aún NO hace (y conviene mencionar)

- **No actualiza el UVT automáticamente** cada año desde la DIAN. La actualización es manual.
- **Hoy no aplica estrictamente la política vigente al periodo** (MP-032). El motor toma la política más reciente. **Esto es importante:** si se cambia la política a mitad de año, hay que validar manualmente que las planillas anteriores se hayan calculado con la política correcta.
- **No hay flujo de aprobación** para cambios de política. Cualquier usuario con permisos puede crear o modificar.
- **No hay validación de coherencia**: por ejemplo, no advierte si `% empresa + % empleado ≠ 100`.
- **No registra quién y cuándo cambió la política** con autenticación real (depende del módulo de identidad pendiente).

> ⚠️ Esta es una conversación delicada con TH: la política es un parámetro **tributario y contable**. Hay que validar cómo se gobiernan los cambios.

## Preguntas que probablemente nos harán (anticipadas)

- **P:** "Si cambio el UVT hoy, ¿afecta planillas que ya calculé este año?"
  **R:** Las planillas ya calculadas **no se recalculan** automáticamente. Quedan con la política que tenían al momento del cálculo. Si se necesita recalcular, hay que volver a generar la planilla. Y aquí entra la decisión funcional pendiente sobre recálculo (MP-042).

- **P:** "¿Quién debería poder modificar la política?"
  **R:** *(Hoy depende de la autenticación que se implemente. Es exactamente la pregunta que les queremos hacer.)*

- **P:** "¿Por qué hay un porcentaje para pensionado separado?"
  **R:** Por flexibilidad. La regla del manual hoy fija pensionado en 0/100, pero el campo permite documentar la política institucional si cambiara.

- **P:** "¿Los códigos contables son obligatorios?"
  **R:** Estructuralmente sí, pero su validación contra el sistema de nómina no está implementada. Hay que confirmar que los códigos registrados correspondan al PUC actual de Finagro.

## Preguntas que NOSOTROS le hacemos a TH (validación)

- [ ] **Actualización anual del UVT:** ¿quién es la persona o rol responsable? ¿Cuál es el procedimiento hoy?
- [ ] **Gobierno de cambios:** ¿quién debería tener permisos para modificar la política? ¿Solo el Responsable de prepagada? ¿Requiere aprobación de jefatura o de tributaria?
- [ ] **Códigos contables:** ¿están los códigos actuales registrados confirmados con contabilidad? ¿Hay un proceso para actualizarlos si cambia el PUC?
- [ ] **Política por periodo (MP-032):** ¿cuántas veces al año cambian la política? ¿Es solo el UVT en enero o hay otros cambios intermedios?
- [ ] **Recálculo de planillas (MP-042):** si después de un cambio de política se detecta una planilla mal calculada, ¿quieren que el sistema permita recalcular y reemplazar, o que cree una nueva versión con histórico?
- [ ] **% pensionado:** ¿hay casos donde el porcentaje sería distinto de 0/100? (Diferentes tipos de pensión, autorización gerencial, etc.)
- [ ] **Notas / fundamento:** ¿deberían quedar referenciados los documentos formales (resolución interna, acta de Junta) que respaldan cada cambio de política?

---

**Fuente:** `docs/01-funcional/requerimientos-funcionales.md` §4 (RF-301); `docs/01-funcional/reglas-de-negocio.md` §4 (MP-032, MP-034, MP-041, MP-042, MP-045); `docs/01-funcional/casos-de-uso.md` (CU-004).
