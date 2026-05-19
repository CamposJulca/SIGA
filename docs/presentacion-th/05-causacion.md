# Módulo 5 — Causación

| Campo                | Valor                                                                  |
|----------------------|------------------------------------------------------------------------|
| Orden en la cinta    | 5 / 8                                                                  |
| Tiempo sugerido demo | 5 minutos                                                              |
| Estado               | Implementado                                                            |
| Fuente               | `docs/01-funcional/requerimientos-funcionales.md` (RF-407, RF-408); `casos-de-uso.md` (CU-009, CU-010) |

---

## En una frase

> Causación es **la salida para contabilidad**: presenta, por cada EPS, cuánto se causa como gasto empresa, cuánto se descuenta al empleado y cómo se separa entre gravable y no gravable, listo para registrarlo en los libros contables del mes.

## ¿Para qué sirve?

Cierra el ciclo del periodo: una vez calculada la planilla (Módulo 3) y validada la separación tributaria (Módulo 4), Causación entrega el **resumen por proveedor** que contabilidad necesita para registrar el gasto del mes y los descuentos de nómina.

También permite **comparar dos periodos** (conciliación) para ver variaciones entre meses, lo cual es útil para:
- Detectar desviaciones inesperadas antes de cerrar.
- Justificar a presidencia o a auditoría el crecimiento/decrecimiento del gasto.
- Identificar casos individuales que cambian de un mes a otro.

## ¿Quién lo usa?

- Contabilidad (consume el resumen para registrar el asiento del mes).
- Responsable de prepagada (valida que la planilla esté lista para cerrar).
- Analista de Gestión Humana (consulta y exporta).

## ¿Qué información entra?

- **Periodo** a consultar (`MMYYYY`).
- (Para conciliación) **Dos periodos** a comparar.

## ¿Qué información sale?

- **Tabla por EPS** con:
  - Número de empleados/titulares incluidos.
  - Total empresa (a causar como gasto).
  - Total empleado (a descontar de nómina).
  - Total factura (suma empresa + empleado).
  - Apoyo no gravable y apoyo gravable.
- **Fila TOTAL** consolidando todas las EPS.
- **Comparativo** entre dos periodos: variaciones por EPS y por concepto.

## Flujo paso a paso (demo en vivo)

1. **Abrir la pestaña Causación**.
2. **Escribir el periodo** (`MMYYYY`) y hacer clic en **Consultar**.
3. Mostrar la **tabla por EPS**: AXA, Colsanitas, y la fila TOTAL.
4. Explicar cada columna:
   - EPS, cantidad de empleados, total empresa, total empleado, total factura, no gravable, gravable.
5. Plantear el **asiento contable de referencia** (lo que contabilidad espera registrar con esta información):
   ```
   Débito : Gasto Salud — No Gravable    (apoyo_no_gravable)
   Débito : Gasto Salud — Gravable       (apoyo_gravable)
   Crédito: Descuento por Nómina         (total_empleado)
   Crédito: Cuentas por Pagar EPS        (total_empresa)
   ```
   > Los códigos contables específicos los define contabilidad y se registran en el Módulo 8 — Política 80/20.
6. (Si hay tiempo) **Mostrar la conciliación**: ingresar dos periodos y mostrar las variaciones por EPS y total.

## Reglas de negocio aplicadas

| ID     | Regla en lenguaje de negocio                                                                          |
|--------|---------------------------------------------------------------------------------------------------------|
| MP-031 | El total se agrupa por grupo familiar y luego por EPS.                                                  |
| MP-033 | Se mantiene la separación gravable/no gravable en la salida contable.                                   |
| MP-034 | Cada concepto contable usa el código configurado en la política. **Estado: PARCIAL** — falta confirmar el formato esperado por nómina/contabilidad. |

## Lo que aún NO hace (y conviene mencionar)

- **No genera el asiento contable directamente**. Entrega los valores; contabilidad arma el asiento en su sistema con los códigos de la Política 80/20.
- **No envía el resumen a contabilidad por correo automáticamente**. La salida es la pantalla y la exportación a Excel desde la planilla.
- **No bloquea** el cierre de un periodo. Es decir: si TH revisa la causación y detecta algo raro, puede recalcular la planilla, pero el sistema no impide consultar una causación sobre una planilla provisional.
- **No incluye históricos** automáticos por más de los periodos seleccionados. La conciliación compara dos a la vez.

## Preguntas que probablemente nos harán (anticipadas)

- **P:** "¿Estos valores ya están listos para registrar en el sistema contable?"
  **R:** Sí, las cifras son las definitivas del periodo, siempre que la planilla del Módulo 3 esté aprobada. Contabilidad debe usar los códigos definidos en la Política 80/20.

- **P:** "¿Por qué este mes el total empresa cambió tanto frente al anterior?"
  **R:** Lo revisamos con la conciliación (este mismo módulo) y/o las novedades (Módulo 2 — Facturas EPS).

- **P:** "¿Y si necesito un detalle empleado por empleado de la causación?"
  **R:** Eso está en la planilla del Módulo 3, exportada a Excel.

## Preguntas que NOSOTROS le hacemos a TH (validación)

- [ ] ¿La estructura de la tabla por EPS (empleados, total empresa, total empleado, total factura, gravable, no gravable) es la que contabilidad necesita ver? ¿Falta alguna columna?
- [ ] ¿Contabilidad consume hoy un Excel específico? ¿O ven la pantalla directamente?
- [ ] ¿Necesitan que la causación quede **firmada o aprobada** por TH antes de ser usada por contabilidad? ¿Hay un flujo de aprobación?
- [ ] ¿Cómo manejan hoy las variaciones grandes entre periodos? ¿Se documentan? ¿Se justifican a alguien?
- [ ] ¿Necesitan ver la causación de meses ya cerrados, o solo del mes en curso?
- [ ] ¿Los códigos contables actuales que conoce TH son los que están registrados en la Política 80/20?

---

**Fuente:** `docs/01-funcional/requerimientos-funcionales.md` §5 (RF-407 Causación, RF-408 Conciliación); `docs/01-funcional/casos-de-uso.md` (CU-009, CU-010).
