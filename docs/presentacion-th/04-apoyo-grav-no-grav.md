# Módulo 4 — Apoyo Gravable / No Gravable

| Campo                | Valor                                                                  |
|----------------------|------------------------------------------------------------------------|
| Orden en la cinta    | 4 / 8                                                                  |
| Tiempo sugerido demo | 6 minutos                                                              |
| Estado               | Implementado                                                            |
| Fuente               | `docs/01-funcional/reglas-de-negocio.md` §3 y MP-033; `docs/00-overview/glosario.md` (sección B) |

---

## En una frase

> Este módulo es la **vista tributaria** de la planilla: muestra cuánto del aporte de la empresa está dentro del límite de UVT (no gravable) y cuánto lo supera (gravable y por tanto incrementa la base de retención).

## ¿Para qué sirve?

El Art. 387 del Estatuto Tributario fija un límite mensual en UVT para que el aporte de la empresa a la medicina prepagada del empleado **no genere retención en la fuente**. Hasta ese límite, el aporte es **no gravable** (deducible para la empresa y sin impacto fiscal para el empleado). Lo que pasa de ese límite es **gravable** (aún se paga, pero entra en la base de retención del empleado).

SIGA hace esa separación automáticamente y la presenta acá para que:

- TH revise cuántos empleados quedan con apoyo gravable en el periodo.
- Se coordine con Tributaria el ajuste a la base de retención de cada uno.
- Se documente el respaldo tributario del cálculo.

## ¿Quién lo usa?

- Responsable de prepagada (revisa el panorama mensual).
- Tributaria (valida el cálculo y aplica el ajuste a retención en la fuente).
- Contabilidad (registra los conceptos contables separados).

## ¿Qué información entra?

- **Planilla** calculada de un periodo (viene del Módulo 3).
- **Política 80/20** vigente (viene del Módulo 8): UVT límite, valor UVT.

> El módulo no requiere carga manual. Se alimenta de lo ya calculado.

## ¿Qué información sale?

- **Tarjetas KPI** del periodo: total no gravable, total gravable, número de empleados con apoyo gravable.
- **Marco tributario aplicado**: UVT vigente, número de UVT del límite, límite resultante en pesos.
- **Detalle por empleado**: valor empresa, apoyo no gravable, apoyo gravable. Los que superan el límite quedan resaltados.

## Flujo paso a paso (demo en vivo)

1. **Abrir la pestaña Apoyo Grav./No Grav.**
2. **Seleccionar la planilla del periodo** (la que se calculó en el Módulo 3).
3. **Mostrar las tarjetas KPI**: total no gravable, total gravable, empleados con gravable > 0.
4. **Explicar el marco tributario** que se ve en la parte superior:
   > "Hoy el UVT vale `$X` y el límite del Art. 387 es de `Y` UVT, lo que da un techo mensual de `$Z` por empleado."
5. **Mostrar la tabla detallada**. Apuntar a las filas con badge rojo (apoyo gravable > 0).
6. Tomar un caso concreto y explicar:
   > "Este empleado tiene un valor empresa de `$A`. El límite es `$Z`. Entonces `$Z` se reconocen como no gravable y la diferencia `$(A−Z)` queda como apoyo gravable. Eso suma a la base de retención del mes para ese empleado."
7. Comentar la acción a tomar:
   > "Para los empleados con apoyo gravable, hay que pasar la cifra a tributaria para que ajuste retención en la fuente con los códigos definidos en el Módulo 8."

## Reglas de negocio aplicadas

| ID     | Regla en lenguaje de negocio                                                                                       |
|--------|---------------------------------------------------------------------------------------------------------------------|
| MP-033 | El aporte de la empresa se separa en apoyo no gravable (hasta el límite UVT) y apoyo gravable (lo que excede).      |
| MP-034 | Cada concepto (no gravable, gravable, descuento empleado) tiene su código contable configurado en la política. **Estado: PARCIAL** — los códigos existen como campo pero falta confirmar el formato exigido por nómina. |

### Fórmula aplicada

```
Límite no gravable   = UVT límite (configurable) × Valor UVT (configurable)
Apoyo no gravable    = mínimo entre (Valor empresa, Límite no gravable)
Apoyo gravable       = máximo entre (0, Valor empresa − Límite no gravable)
```

## Lo que aún NO hace (y conviene mencionar)

- **No actualiza el UVT automáticamente** al inicio de año. TH debe registrar el nuevo valor en el Módulo 8 — Política 80/20.
- **No reporta automáticamente a Tributaria** los casos con apoyo gravable. Hoy la salida es la pantalla y el Excel exportado desde el Módulo 3.
- **No calcula impacto en retención**. Solo identifica la base gravable. El cálculo de retención se hace en nómina.
- **No envía alertas** cuando aparecen casos nuevos de apoyo gravable (por ejemplo: "este empleado pasó a tener apoyo gravable este mes y antes no").

> ⚠️ VALIDAR CON TH: confirmar que la actualización del UVT al cambiar de año está dentro del proceso operativo del responsable de prepagada o si requiere apoyo de tributaria.

## Preguntas que probablemente nos harán (anticipadas)

- **P:** "¿De dónde sale el valor UVT que está usando el sistema?"
  **R:** Del campo configurado en la política vigente (Módulo 8). Hay que actualizarlo cada año cuando la DIAN publique el nuevo valor.

- **P:** "¿Por qué este empleado quedó con apoyo gravable este mes si el mes pasado no?"
  **R:** Porque cambió algo: el valor de la cuota familiar, el tamaño del núcleo, o el UVT. Lo revisamos comparando contra el periodo anterior (Módulo 5 — Conciliación o Novedades del Módulo 2).

- **P:** "¿La parte gravable la deduce el sistema automáticamente del salario?"
  **R:** No. SIGA identifica el monto. La aplicación de la retención al salario la hace nómina/Kactus con los códigos contables configurados en el Módulo 8.

## Preguntas que NOSOTROS le hacemos a TH (validación)

- [ ] ¿Quién es hoy la persona o el rol que **actualiza el UVT** al inicio de cada año en el sistema?
- [ ] ¿Cómo coordinan hoy con tributaria los casos con apoyo gravable? ¿Por correo? ¿En una reunión específica?
- [ ] ¿Los códigos contables (no gravable, gravable, descuento empleado) los definen TH o contabilidad? ¿Están confirmados los códigos actuales o se necesitan ajustar?
- [ ] ¿Necesitan recibir alertas cuando aparezcan **casos nuevos** de apoyo gravable (alguien que no lo tenía y empieza a tenerlo)?
- [ ] ¿El reporte de apoyo gravable se entrega a tributaria como Excel del Módulo 3, o necesitan un formato específico?

---

**Fuente:** `docs/01-funcional/reglas-de-negocio.md` §3 (Reglas funcionales 80/20) y MP-033/034; `docs/00-overview/glosario.md` (sección B — modelo financiero y tributario).
