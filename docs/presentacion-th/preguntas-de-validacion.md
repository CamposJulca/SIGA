# Checklist de Validación con Talento Humano

| Campo                | Valor                                                                  |
|----------------------|------------------------------------------------------------------------|
| Fecha de la reunión  | 2026-05-13                                                             |
| Uso                  | Tener abierto en una segunda pestaña durante la reunión.                |
| Cómo marcar          | `[ ]` pendiente · `[x]` validado · `[~]` parcial / requiere seguimiento |

---

## Módulo 1 — Dashboard
- [ ] ¿Qué indicador es el primero que ustedes consultan cada mes? ¿Está en el dashboard?
- [ ] ¿Les sirve la distribución por parentesco como está, o necesitan otras categorías?
- [ ] ¿Necesitan ver evolución de **valor por persona** o solo el total agregado?
- [ ] ¿Hay algún KPI directivo o EFR que reportan hacia arriba y que les gustaría tener acá ya consolidado?
- [ ] ¿Qué tan útil sería una alerta del tipo "aún no se ha cargado el archivo de X proveedor del mes Y"?

## Módulo 2 — Facturas EPS
- [ ] ¿El formato actual de los archivos de AXA y Colsanitas se ha mantenido estable en los últimos 12 meses? ¿Ha cambiado en algún momento?
- [ ] ¿Han recibido alguna vez un archivo con la cabecera en una fila distinta a la habitual?
- [ ] ¿Cómo manejan hoy las advertencias por diferencia aritmética (RN-08/9)? ¿Las revisan o se aceptan?
- [ ] ¿Han tenido casos de cédulas duplicadas dentro del mismo sub-contrato? ¿Eso debería ser advertencia o error fatal?
- [ ] ¿Conocen casos de filas de ajuste negativo de Colsanitas (RN-11)? ¿Qué hacen con esas filas hoy?
- [ ] ¿Necesitan poder **reemplazar** un archivo ya cargado, o que el sistema bloquee la doble carga?
- [ ] ¿Quién es hoy el responsable de revisar los errores y advertencias después de cada carga?
- [ ] El comparativo de novedades, ¿les sirve para detectar retirados que la EPS no ha dado de baja?

## Módulo 3 — Planilla 80/20
- [ ] **MP-006 — Pensionados:** ¿hoy aplican 100 % al pensionado siempre, o hay excepciones?
- [ ] **MP-002 — Antigüedad mínima:** ¿hoy verifican manualmente que el empleado lleve más de 2 meses antes de incluirlo? ¿Cómo?
- [ ] **MP-004 — Autorización de descuento:** ¿cómo registran que un colaborador autorizó el descuento del 20 % por nómina?
- [ ] **MP-008..017 — Elegibilidad de beneficiarios:** ¿están validando hoy parentesco/edad/discapacidad/soportes? ¿Quién y cómo?
- [ ] **MP-026/027 — Prorrateos:** si un colaborador se retira el día 15, ¿se reconoce medio mes o el mes completo? ¿Aplican algún corte administrativo?
- [ ] **MP-042 — Recálculo:** si calcularon una planilla y descubren un error, ¿la reemplazan o crean una versión nueva auditable?
- [ ] **MP-032 — Política vigente:** ¿cómo verifican que el cálculo aplique la política del periodo, no la última creada? ¿Lo revisan manualmente?
- [ ] **MP-016 — Familiares no elegibles:** si aparece un familiar que no encaja en ninguna regla, ¿debe quedar en planilla con 100 % empleado o debe excluirse del archivo de aporte?
- [ ] **MP-043 — Excepciones autorizadas:** ¿hay casos especiales autorizados por TH? ¿Con qué vigencia?

## Módulo 4 — Apoyo Gravable / No Gravable
- [ ] ¿Quién es hoy la persona o el rol que **actualiza el UVT** al inicio de cada año en el sistema?
- [ ] ¿Cómo coordinan hoy con tributaria los casos con apoyo gravable? ¿Por correo? ¿En una reunión específica?
- [ ] ¿Los códigos contables (no gravable, gravable, descuento empleado) los definen TH o contabilidad? ¿Están confirmados los códigos actuales o se necesitan ajustar?
- [ ] ¿Necesitan recibir alertas cuando aparezcan **casos nuevos** de apoyo gravable (alguien que no lo tenía y empieza a tenerlo)?
- [ ] ¿El reporte de apoyo gravable se entrega a tributaria como Excel del Módulo 3, o necesitan un formato específico?

## Módulo 5 — Causación
- [ ] ¿La estructura de la tabla por EPS (empleados, total empresa, total empleado, total factura, gravable, no gravable) es la que contabilidad necesita ver? ¿Falta alguna columna?
- [ ] ¿Contabilidad consume hoy un Excel específico? ¿O ven la pantalla directamente?
- [ ] ¿Necesitan que la causación quede **firmada o aprobada** por TH antes de ser usada por contabilidad? ¿Hay un flujo de aprobación?
- [ ] ¿Cómo manejan hoy las variaciones grandes entre periodos? ¿Se documentan? ¿Se justifican a alguien?
- [ ] ¿Necesitan ver la causación de meses ya cerrados, o solo del mes en curso?
- [ ] ¿Los códigos contables actuales que conoce TH son los que están registrados en la Política 80/20?

## Módulo 6 — Pensionados
- [ ] ¿Cuántos pensionados activos manejan hoy aproximadamente? ¿Esa cifra ha crecido en el último año?
- [ ] ¿Cómo identifican hoy a un pensionado para registrarlo? ¿Lo notifica el área de pensiones? ¿Lo detecta TH en el cruce mensual?
- [ ] ¿Necesitan poder **adjuntar documentos** al registro del pensionado (carta, resolución de pensión)?
- [ ] ¿Hay reglas distintas según el tipo de pensión (vejez, invalidez, sobrevivencia)?
- [ ] ¿Necesitan **carga masiva** desde Excel, o el alta uno a uno cubre la frecuencia real?
- [ ] **Importante:** ¿el 100 % empleado es siempre 100 %, o pueden existir excepciones (por ejemplo, beneficios diferenciales por antigüedad)?
- [ ] ¿Qué hacer con un pensionado que también tiene cónyuge o hijo cubierto? ¿Cómo se factura?

## Módulo 7 — Auxilio Externo
- [ ] ¿Cuántos casos de auxilio externo manejan hoy? ¿Es frecuente o excepcional?
- [ ] ¿Cómo aplican hoy las reglas del manual para esos casos (MP-019..MP-025)? ¿Hay un Excel? ¿Una persona responsable?
- [ ] **Decisión funcional pendiente:** el promedio de pólizas Finagro, ¿es general, por proveedor, por tipo de plan o por grupo familiar?
- [ ] ¿Reciben los recibos mensuales hoy? ¿Quién los valida y cómo?
- [ ] ¿Tienen alguna certificación inicial estándar que la aseguradora externa envía? ¿En qué formato?
- [ ] ¿Cómo manejan hoy la retroactividad de 3 meses?
- [ ] ¿Necesitan que SIGA **alerte** cuando vence la certificación anual o cuando un colaborador no presenta el recibo del mes?
- [ ] ¿Estos casos los reportan en el informe EFR? ¿Cómo los separan de los del convenio?

## Módulo 8 — Política 80/20
- [ ] **Actualización anual del UVT:** ¿quién es la persona o rol responsable? ¿Cuál es el procedimiento hoy?
- [ ] **Gobierno de cambios:** ¿quién debería tener permisos para modificar la política? ¿Solo el Responsable de prepagada? ¿Requiere aprobación de jefatura o de tributaria?
- [ ] **Códigos contables:** ¿están los códigos actuales registrados confirmados con contabilidad? ¿Hay un proceso para actualizarlos si cambia el PUC?
- [ ] **Política por periodo (MP-032):** ¿cuántas veces al año cambian la política? ¿Es solo el UVT en enero o hay otros cambios intermedios?
- [ ] **Recálculo de planillas (MP-042):** si después de un cambio de política se detecta una planilla mal calculada, ¿quieren que el sistema permita recalcular y reemplazar, o que cree una nueva versión con histórico?
- [ ] **% pensionado:** ¿hay casos donde el porcentaje sería distinto de 0/100? (Diferentes tipos de pensión, autorización gerencial, etc.)
- [ ] **Notas / fundamento:** ¿deberían quedar referenciados los documentos formales (resolución interna, acta de Junta) que respaldan cada cambio de política?

---

## Sección final — Roadmap y decisiones de cierre

Estas preguntas son para el cierre de la reunión (no por módulo, sino transversales).

### Roadmap dentro de Medicina Prepagada
- [ ] De las reglas no implementadas (antigüedad, elegibilidad, pólizas externas, prorrateos, excepciones, recálculo), ¿cuál es la más urgente para TH?
- [ ] ¿Hay alguna regla del manual que no aparezca en la lista y que sí están aplicando hoy manualmente?

### Roadmap fuera de Medicina Prepagada
- [ ] ¿Cuál es el siguiente proceso del manual THU-DOC-002 que tiene mayor dolor operativo hoy?
  - [ ] Auxilio educativo
  - [ ] Vacaciones y compensaciones
  - [ ] Primas extralegales / bonificación quinquenio
  - [ ] Auxilio de incapacidad
  - [ ] Auxilio extralegal de alimentación
  - [ ] Auxilio de parqueadero
  - [ ] FONDEFIN
  - [ ] Préstamo de libre inversión
  - [ ] Crédito educativo condonable
  - [ ] Permisos, licencias y flexibilidad
  - [ ] Convocatorias internas, encargos, nivelación
  - [ ] Otro: ____________________

### Decisiones funcionales pendientes (cierre)
- [ ] Familiar no elegible en planilla: ¿100 % empleado o excluido?
- [ ] Promedio de pólizas Finagro: ¿general / por proveedor / por plan / por grupo familiar?
- [ ] Prorrateo por ingreso/retiro: ¿días calendario / días laborales / corte mensual?
- [ ] Periodo de prueba: ¿dato explícito o cubierto por la regla de 2 meses?
- [ ] Excepciones autorizadas: ¿vigencia mensual / anual / abierta?
- [ ] Recálculo de planilla: ¿reemplaza o versiona?

### Cierre administrativo
- [ ] Próxima reunión: fecha y agenda.
- [ ] Owner del seguimiento de preguntas abiertas.
- [ ] Compromisos del equipo SIGA (definir).
- [ ] Compromisos del equipo Talento Humano (definir).

---

**Fuente consolidada:** todas las preguntas de validación de los archivos `01-dashboard.md` a `08-politica-80-20.md` y del cierre `99-cierre-y-siguientes-pasos.md`.
