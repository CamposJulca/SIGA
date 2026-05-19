# Apertura — 5 minutos

| Campo                | Valor                                                       |
|----------------------|-------------------------------------------------------------|
| Tiempo sugerido      | 5 minutos                                                   |
| Audiencia            | Talento Humano (no técnico)                                  |
| Fuente               | `docs/00-overview/vision.md`                                 |

---

## Cómo arrancar (guion del presentador)

> Buenos días. Antes de mostrarles la herramienta, vamos a poner contexto en dos minutos: por qué existe, qué hace hoy y qué les vamos a pedir durante la reunión.

## 1. Qué es SIGA y por qué nació

**SIGA — Sistema Inteligente de Gestión Administrativa** — es la herramienta que Finagro está construyendo para automatizar procesos administrativos del área de Talento Humano.

El primer alcance implementado es **Beneficios de Salud / Medicina Prepagada**, porque ahí estaba uno de los procesos más manuales y con más riesgo operativo del área:

| Cómo era antes                                                                 | Riesgo                                                  |
|---------------------------------------------------------------------------------|---------------------------------------------------------|
| Cada mes llegaban dos facturas en Excel (AXA Colpatria y Colsanitas) con estructuras distintas. | Errores al unificar columnas y consolidar el reporte.    |
| Un analista limpiaba, deduplicaba y unificaba los archivos a mano.              | Dependencia de la disponibilidad y el criterio de la persona. |
| Se calculaba el 80/20 en hojas de cálculo, sin control automático del UVT vigente. | Riesgo tributario y de inconsistencia entre periodos.    |
| No quedaba historial trazable de qué archivo se procesó cuándo.                  | Dificultad para responder a reclamaciones o auditorías. |

SIGA convierte ese flujo manual en uno **automático y auditable**: el archivo se carga, se valida fila por fila, se cruza con la nómina, se calcula el 80/20 y se generan las salidas para contabilidad y para el informe EFR.

## 2. Qué alcance les vamos a mostrar hoy

Vamos a recorrer **los 8 módulos** que ven en la cinta superior del sistema. Ese es **todo el alcance funcional** vigente de SIGA:

```
Dashboard | Facturas EPS | Planilla 80/20 | Apoyo Grav./No Grav. |
Causación | Pensionados | Auxilio Externo | Política 80/20
```

Lo que NO les vamos a mostrar (porque hoy no está implementado, es roadmap):

- Auxilio educativo para hijos.
- Vacaciones y compensaciones.
- Primas extralegales y bonificaciones.
- Auxilio de incapacidad, alimentación, parqueadero.
- FONDEFIN, préstamo de libre inversión, crédito educativo condonable.
- Permisos, licencias y convocatorias internas.

Si alguno de esos temas surge durante la reunión, lo apuntamos como prioridad de roadmap, pero hoy nos quedamos en medicina prepagada.

## 3. Cómo va a ser la sesión

- **Vamos módulo por módulo, en el orden de la cinta.**
- En cada módulo:
  1. Mostramos qué hace.
  2. Hacemos una demo en vivo (5–8 minutos).
  3. Paramos y les preguntamos: *¿esto refleja lo que ustedes hacen mes a mes?* *¿qué le falta?* *¿qué le sobra?*
- Las preguntas que les vayamos haciendo quedan registradas en una hoja de validación que tenemos abierta en otra pestaña.
- Al final dejamos 7 minutos para resumir, anotar compromisos y acordar los próximos pasos.

## 4. Qué esperamos de Talento Humano

| Lo que sí necesitamos                                                                 | Lo que NO necesitamos hoy                                |
|----------------------------------------------------------------------------------------|----------------------------------------------------------|
| Que nos digan si lo que hace cada módulo **se ajusta a la operación real**.            | Aprobación formal del sistema.                            |
| Que señalen lo que no se ajusta o que vean diferente.                                  | Decisiones jurídicas o tributarias en la reunión.         |
| Que nos resuelvan las preguntas funcionales pendientes (las marcaremos a lo largo).    | Aprobación del roadmap restante (eso es una siguiente conversación). |
| Que nos prioricen lo que más les duele que aún no esté.                                |                                                          |

> Tres cosas que les pedimos tener presentes durante la sesión:
> 1. **Si algo se ve raro, decirlo en el momento.** No esperar al final.
> 2. **Si un caso real que ustedes manejan no aparece, también es información valiosa.**
> 3. **Si un dato que necesitamos no lo tienen automatizado hoy** (por ejemplo: cómo identifican a un pensionado, dónde está el estado civil, cómo verifican dependencia económica), es importante que lo digan: nos permite definir qué información necesitará SIGA para crecer.

## 5. Antes de empezar — preguntas iniciales

- [ ] ¿Cuántos de los presentes han operado el proceso mensual de medicina prepagada en los últimos 12 meses?
- [ ] ¿En qué punto del mes están hoy en relación con el cierre? (¿Ya cargaron las facturas del mes? ¿Aún no?)
- [ ] ¿Hay algún tema puntual que ya saben que quieren plantear hoy?

---

**Fuente:** `docs/00-overview/vision.md` (§1 Qué es SIGA, §2 Problema que resuelve, §4 Alcance funcional, §5 Fuera de alcance).
