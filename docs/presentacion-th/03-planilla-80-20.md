# Módulo 3 — Planilla 80/20

| Campo                | Valor                                                                                                |
|----------------------|------------------------------------------------------------------------------------------------------|
| Orden en la cinta    | 3 / 8                                                                                                |
| Tiempo sugerido demo | 8 minutos                                                                                            |
| Estado               | Implementado (con regla parcial de pensionados y vigencia de política) — ver "Lo que aún NO hace"    |
| Fuente               | `docs/01-funcional/requerimientos-funcionales.md` (RF-401..406); `casos-de-uso.md` (CU-007, CU-008); `reglas-de-negocio.md` §3, §4 (MP-005, MP-028..033) |

---

## En una frase

> La Planilla 80/20 es **el motor de cálculo**: cruza las facturas con la nómina y aplica la política institucional para decidir cuánto paga la empresa y cuánto el empleado, por cada titular con prepagada activa.

## ¿Para qué sirve?

Resuelve el cálculo mensual que antes se hacía en hojas externas. Una vez que las facturas del mes están cargadas y la política está al día, SIGA:

1. **Pregunta a la nómina** quién tiene prepagada activa en el periodo.
2. **Decide la regla aplicable** para cada persona: empleado activo elegible (80/20), pensionado (100% empleado), o cruce sin coincidencia (bloqueado).
3. **Calcula los valores** que paga la empresa y los que se descuentan al empleado.
4. **Separa la parte gravable de la no gravable** según la norma tributaria (apoyo gravable / no gravable, ver Módulo 4).
5. **Guarda la planilla** como histórico, con la política con la que se calculó.

Lo que queda al final es el documento de **soporte único** para registrar los movimientos en nómina y para la causación contable.

## ¿Quién lo usa?

- Analista de Gestión Humana (genera la planilla mensual).
- Responsable de prepagada (revisa y aprueba antes de exportar).
- Contabilidad (consume la salida para causación).
- Tributaria (revisa la clasificación gravable).

## ¿Qué información entra?

- **Periodo a calcular** (mes y año, formato `MMYYYY`, por ejemplo `032026`).
- **Política 80/20 vigente** (ver Módulo 8): porcentajes empresa/empleado, valor UVT, UVT límite, conceptos contables.
- **Facturas EPS** del periodo, ya cargadas (Módulo 2).
- **Cruce con la nómina** del periodo: el sistema lee de un repositorio de datos quién está activo, quién es pensionado y cuánto está facturando por familia.

## ¿Qué información sale?

- **Cruce del periodo**: lista de empleados/personas con su estado (OK, No encontrado, Inactivo).
- **Planilla calculada**: por cada empleado elegible, su valor empresa, valor empleado, apoyo no gravable y apoyo gravable.
- **Histórico de planillas**: cuántas se han calculado, en qué fecha, con qué política.
- **Detalle por planilla**: lista persona por persona con todos los valores.
- **Exportación a Excel** con dos hojas: "Planilla 80-20" (todos) y "Apoyo Gravable" (solo los que superan el límite UVT).

## Flujo paso a paso (demo en vivo)

1. **Abrir la pestaña Planilla 80/20**.
2. **Seleccionar el periodo** en la sección "Cruce del periodo". Por ejemplo, `032026`.
3. Mostrar el resultado del cruce: tabla con los empleados del periodo, su estado (OK, No encontrado, Inactivo) y un código de color.
   - **OK (verde)**: empleado activo en la nómina. Aplica 80/20.
   - **No encontrado (naranja)**: cédula no está en la nómina activa. Caso típico: pensionado o error de cédula.
   - **Inactivo (gris)**: contrato terminado pero todavía aparece en la factura.
4. Explicar qué se hace con cada caso:
   > "Los OK los calculamos normal. Los No Encontrado e Inactivo los revisamos: si es pensionado, lo registramos en el Módulo 6 y queda como 100% empleado. Si es retiro, hay que avisar a la EPS para darlo de baja."
5. **Calcular la planilla**: ingresar el periodo y hacer clic en **Calcular planilla**.
6. **Mostrar el detalle** de la planilla calculada:
   - Empleado, EPS, total familia, valor empresa (80%), valor empleado (20%), apoyo no gravable, apoyo gravable.
   - Señalar las **filas amarillas**: son las que tienen apoyo gravable mayor a cero (superan el límite UVT). Explicar que se coordinan con tributaria.
7. **Exportar la planilla a Excel** y abrir para mostrar las dos hojas.
8. **Mostrar el historial** de planillas calculadas por periodo.

## Reglas de negocio aplicadas

| ID      | Regla en lenguaje de negocio                                                                                                |
|---------|------------------------------------------------------------------------------------------------------------------------------|
| MP-005  | Para empleado activo con cruce OK, se aplica la distribución 80% empresa / 20% empleado (configurable en Módulo 8).            |
| MP-006  | Para pensionados, la empresa aporta 0% y el pensionado asume el 100%. **Estado: PARCIAL** — la regla existe en el modelo, pero hay que confirmar que se aplique automáticamente en cada cálculo. |
| MP-028  | El cruce con la nómina identifica si cada persona está activa, inactiva o no encontrada.                                       |
| MP-029  | Si una cédula de la factura no cruza con la nómina, NO se calcula aporte empresa para esa persona. **Estado: PARCIAL.**         |
| MP-030  | Si la persona está marcada como inactiva, NO se calcula aporte empresa. **Estado: PARCIAL** — falta cálculo parcial por retiro. |
| MP-031  | El cálculo agrupa los valores por grupo familiar (titular + beneficiarios) para aplicar el 80/20 sobre el total familia.        |
| MP-032  | Debe usarse la política vigente al periodo calculado. **Estado: PARCIAL** — hoy se toma la política más reciente. Hay que verificar al cambiar de política. |
| MP-033  | La porción que paga la empresa se separa en apoyo no gravable (hasta el límite UVT) y apoyo gravable (excedente). Ver Módulo 4. |
| MP-041  | Cada planilla calculada queda registrada con la política aplicada y la fecha. **Estado: PARCIAL** — falta el usuario real (depende de la autenticación). |

### Cómo se calcula (en términos simples)

Para cada empleado elegible:

```
Total familia        = suma de cuotas del titular + sus beneficiarios
Valor empresa        = Total familia × 80 %
Valor empleado       = Total familia × 20 %
Límite no gravable   = UVT límite × Valor UVT (ej.: 16 × $49.799 = $796.784)
Apoyo no gravable    = mínimo entre (Valor empresa, Límite no gravable)
Apoyo gravable       = lo que sobre por encima del límite
```

> Los porcentajes (80/20), el UVT límite y el valor UVT vigente se configuran en el Módulo 8 — Política 80/20.

## Lo que aún NO hace (y conviene mencionar — IMPORTANTE)

El cálculo base funciona, pero el manual de Talento Humano contempla reglas que **hoy NO se aplican automáticamente**. Hay que ser explícitos con TH:

| Regla del manual                                          | Estado actual en SIGA | Cómo se maneja hoy                                                 |
|-----------------------------------------------------------|------------------------|--------------------------------------------------------------------|
| Antigüedad mínima (más de 2 meses)                         | No implementado        | No se valida. Si está en la factura, se calcula.                    |
| Aceptación del beneficio por el colaborador                 | No implementado        | No se valida. No hay control de aceptación.                          |
| Autorización escrita del descuento del 20%                  | No implementado        | No se valida.                                                       |
| Elegibilidad por parentesco (cónyuge, hijos hasta 25, padres) | Parcial               | Se reciben los parentescos del proveedor, pero no se validan reglas de elegibilidad.|
| Hijos mayores de 25 con discapacidad                        | No implementado        | Se reciben de la factura pero sin validación de soporte.             |
| Compañero permanente con unión ≥ 2 años                     | No implementado        | No se valida soporte ni vigencia de la unión.                        |
| Reglas de sustitución (soltero con padres, casado con un padre en lugar del cónyuge) | No implementado | No se aplican.                                          |
| Prorrateo por ingreso o por retiro a mitad de mes           | No implementado        | Se calcula el mes completo o no se calcula.                           |
| Recálculo de una planilla previamente generada               | Por definir            | Hoy se genera una planilla nueva. No hay regla operativa formalizada. |

> Esto es **lo más importante que debemos validar con TH**. Estas reglas existen en el manual; SIGA no las hace solo. La pregunta de fondo es: *¿cómo las están aplicando hoy? ¿Manualmente? ¿No se aplican? ¿Quieren que SIGA las haga en una próxima fase?*

## Preguntas que probablemente nos harán (anticipadas)

- **P:** "¿Cómo sabe el sistema que esa persona es pensionado?"
  **R:** Porque se registró previamente en el Módulo 6 — Pensionados. Si no está registrado ahí, SIGA lo verá como No encontrado y lo dejará en estado bloqueado hasta que TH lo confirme.

- **P:** "¿Por qué este empleado quedó con apoyo gravable y este otro no?"
  **R:** Porque la parte empresa supera el límite de 16 UVT. Es una cuestión de magnitud del valor familiar, no de discriminación.

- **P:** "¿Qué pasa si cambia el UVT a mitad de año?"
  **R:** Hay que registrar una nueva política en el Módulo 8 con la fecha de vigencia. Hoy debemos confirmar manualmente que el cálculo use la política correcta al periodo. *(Esta es la regla MP-032 parcial.)*

- **P:** "¿Y si calculo dos veces el mismo periodo?"
  **R:** El sistema genera dos planillas. La regla de cuál se considera la oficial está por definir (MP-042).

## Preguntas que NOSOTROS le hacemos a TH (validación)

- [ ] **Regla de pensionados (MP-006):** ¿hoy aplican 100% al pensionado siempre, o hay excepciones?
- [ ] **Antigüedad mínima (MP-002):** ¿hoy verifican manualmente que el empleado lleve más de 2 meses antes de incluirlo? ¿Cómo?
- [ ] **Autorización de descuento (MP-004):** ¿cómo registran que un colaborador autorizó el descuento del 20% por nómina?
- [ ] **Elegibilidad de beneficiarios (MP-008..017):** ¿están validando hoy parentesco/edad/discapacidad/soportes? ¿Quién y cómo?
- [ ] **Prorrateos (MP-026/027):** si un colaborador se retira el día 15, ¿se reconoce medio mes o el mes completo? ¿Aplican algún corte administrativo?
- [ ] **Recálculo (MP-042):** si calcularon una planilla y descubren un error, ¿la reemplazan o crean una versión nueva auditable?
- [ ] **Política vigente (MP-032):** ¿cómo verifican que el cálculo aplique la política del periodo, no la última creada? ¿Lo revisan manualmente?
- [ ] **Familiares no elegibles (MP-016):** si aparece un familiar que no encaja en ninguna regla, ¿debe quedar en planilla con 100% empleado o debe excluirse del archivo de aporte?
- [ ] **Excepciones autorizadas (MP-043):** ¿hay casos especiales autorizados por TH? ¿Con qué vigencia?

---

**Fuente:** `docs/01-funcional/requerimientos-funcionales.md` §5 (RF-401..406); `docs/01-funcional/reglas-de-negocio.md` §3, §4 (MP-005..045 — destacar las en estado Parcial/No soportado); `docs/01-funcional/casos-de-uso.md` (CU-007, CU-008).
