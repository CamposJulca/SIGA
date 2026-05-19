# Módulo 1 — Dashboard

| Campo                | Valor                                                                  |
|----------------------|------------------------------------------------------------------------|
| Orden en la cinta    | 1 / 8                                                                  |
| Tiempo sugerido demo | 5 minutos                                                              |
| Estado               | Implementado                                                            |
| Fuente               | `docs/01-funcional/requerimientos-funcionales.md` (RF-206); `docs/00-overview/vision.md` |

---

## En una frase

> El Dashboard es la **foto del estado actual** del proceso: cuánto se ha procesado, cuántos beneficiarios hay, qué proveedores están al día, y cómo viene la evolución periodo a periodo.

## ¿Para qué sirve?

Permite que cualquier persona del área tenga, en un solo vistazo, un resumen ejecutivo del trabajo del mes y del histórico:

- Saber **si ya están cargadas** las facturas del periodo.
- Saber **cuántos beneficiarios** están cubiertos por cada proveedor.
- Detectar **desviaciones** frente a periodos anteriores (más afiliados, menos, valor diferente).
- Tener una respuesta rápida a la pregunta "¿cómo vamos este mes con la medicina prepagada?".

No reemplaza al detalle de cada módulo: es una entrada de orientación. El detalle se ve en Facturas EPS, en Planilla, en Causación.

## ¿Quién lo usa?

- Analista de Gestión Humana (consulta diaria/semanal).
- Responsable de prepagada (revisión antes del cierre del mes).
- Usuarios administrativos para reporte directivo.

## ¿Qué información entra?

> El dashboard no recibe carga manual. Es una vista de lectura sobre los datos ya cargados en los demás módulos.

## ¿Qué información sale?

- Total de archivos procesados (acumulado histórico).
- Beneficiarios del último periodo (cuántos afiliados en total).
- Valor total del último periodo (suma de lo facturado por AXA + Colsanitas).
- Cantidad de proveedores activos.
- Distribución por parentesco (Titular, Cónyuge, Hijo, Padres, Otros).
- Distribución por proveedor (AXA vs Colsanitas).
- Evolución reciente (últimos periodos).

> ⚠️ VALIDAR CON TH: confirmar qué indicadores quiere ver TH **en primer plano** (la primera fila de tarjetas KPI).

## Flujo paso a paso (demo en vivo)

1. **Entrar** al portal: `https://automation-hub-finagro.ngrok.io/siga` → **Beneficios de Salud**.
2. Mostrar la cinta superior con los 8 módulos. Explicar que el Dashboard es la entrada.
3. Recorrer las **tarjetas KPI** de arriba: "estas son las cifras que vemos al abrir".
4. Bajar a la **sección por proveedor**: contrato, periodo facturado, beneficiarios y valor por EPS.
5. Mostrar la **distribución por parentesco** y por proveedor.
6. Mostrar la **evolución de los últimos periodos** (si hay gráfico).

> ⏱ Si TH valida sin observaciones, no demorarse aquí. El valor del Dashboard se aprecia mejor cuando ya entendieron los demás módulos.

## Reglas de negocio aplicadas

| ID         | Regla                                                                                       |
|------------|----------------------------------------------------------------------------------------------|
| RF-206     | El dashboard muestra resumen por proveedor, parentesco, evolución y consolidado.              |
| MP-031     | Los valores presentados se agrupan por grupo familiar / titular.                              |
| MP-035/036 | Diferenciación visual entre AXA y Colsanitas.                                                 |

## Lo que aún NO hace (y conviene mencionar)

- No tiene **alertas automáticas** (por ejemplo: "ya pasó el día 5 del mes y aún no se ha cargado AXA"). Es una vista informativa, no proactiva.
- No tiene **personalización** por usuario; todos ven el mismo tablero.
- **Las cifras dependen de la carga**: si TH no ha subido los archivos del mes, el dashboard refleja lo último cargado, no la realidad del mes en curso.

## Preguntas que probablemente nos harán (anticipadas)

- **P:** "¿Por qué los beneficiarios del último periodo no coinciden con lo que tenemos en el reporte interno?"
  **R:** Porque depende del archivo cargado. Vamos a Facturas EPS para confirmar qué fue lo último que se cargó.

- **P:** "¿Puedo exportar el dashboard a un PDF para reportes?"
  **R:** Hoy no está implementada esa exportación. Lo registramos como posible mejora.

- **P:** "¿Qué tan en tiempo real son estas cifras?"
  **R:** Las cifras reflejan el estado de la base en el momento de abrir. Cuando se carga un archivo nuevo o se calcula una planilla, los KPIs se actualizan.

## Preguntas que NOSOTROS le hacemos a TH (validación)

- [ ] ¿Qué indicador es el primero que ustedes consultan cada mes? ¿Está en el dashboard?
- [ ] ¿Les sirve la distribución por parentesco como está, o necesitan otras categorías?
- [ ] ¿Necesitan ver evolución de **valor por persona** o solo el total agregado?
- [ ] ¿Hay algún KPI directivo o EFR que reportan hacia arriba y que les gustaría tener acá ya consolidado?
- [ ] ¿Qué tan útil sería una alerta del tipo "aún no se ha cargado el archivo de X proveedor del mes Y"?

---

**Fuente:** `docs/01-funcional/requerimientos-funcionales.md` §2 (RF-206); `docs/00-overview/vision.md` §4 (Dashboard como capacidad).
