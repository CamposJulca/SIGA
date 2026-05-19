# Monitoreo y Alertas

| Campo        | Valor                                                                       |
|--------------|------------------------------------------------------------------------------|
| Versión      | 1.0                                                                          |
| Fecha        | 2026-05-13                                                                   |
| Fuente       | Arquitectura §10 (Observabilidad)                                            |
| Responsable  | Operación / DevOps                                                            |
| Estado       | **Borrador — cobertura BAJA**, ver `gaps.md` Top 10 #5                        |

---

> ⚠️ PENDIENTE: las fuentes documentan **observabilidad de aplicación** (estados internos, contadores, dashboard funcional) pero **no** observabilidad técnica (logs centralizados, métricas, alertas, dashboards externos, SLOs).

## 1. Observabilidad documentada (a nivel funcional)

| Mecanismo                              | Uso                                                              |
|----------------------------------------|-------------------------------------------------------------------|
| `ArchivoRecibido.estado_procesamiento` | Trazabilidad de carga y procesamiento.                            |
| Contadores de archivo                   | `total_registros`, `registros_procesados`, `registros_con_error`. |
| `ErrorProcesamiento`                    | Diagnóstico por fila de origen.                                    |
| Endpoint `/dashboard/`                  | Resumen ejecutivo de estado de datos.                              |
| `PlanillaCalculo` persistido            | Historial de cálculos realizados por periodo.                       |

Estos mecanismos sirven al usuario operacional; **no sustituyen** un stack de observabilidad técnica.

## 2. Logs

| Tema                                    | Estado documentado                            |
|-----------------------------------------|------------------------------------------------|
| Destino de logs                          | `PENDIENTE` — por defecto Django escribe a stdout. |
| Formato                                  | `PENDIENTE` — recomendado JSON estructurado.    |
| Niveles                                  | `PENDIENTE` (info/warn/error).                  |
| Retención                                | `PENDIENTE`.                                    |
| Centralización (Loki, ELK, Datadog…)    | `PENDIENTE`.                                    |
| Correlación request ↔ log               | `PENDIENTE` (request id).                       |

## 3. Métricas

| Métrica candidata                                | Fuente                                                  |
|---------------------------------------------------|----------------------------------------------------------|
| Archivos cargados por periodo / proveedor          | `ArchivoRecibido` (BD).                                  |
| Archivos en estado `ERROR` (último 24 h / 7 d)      | `ArchivoRecibido` (BD).                                  |
| Registros con `ADVERTENCIA` por archivo            | `BeneficioSalud` (BD).                                   |
| Tasa de error de carga (`registros_con_error / total_registros`) | `ArchivoRecibido` (BD).                  |
| Latencia de `/upload/` (p50/p95/p99)                | `PENDIENTE` — instrumentar.                              |
| Disponibilidad de `prepagada.db`                   | `PENDIENTE` — health check.                              |
| Planillas calculadas por mes                        | `PlanillaCalculo` (BD).                                  |
| Tiempo de cálculo de planilla                       | `PENDIENTE` — instrumentar.                              |

> ⚠️ PENDIENTE: stack de métricas no definido (Prometheus / Datadog / CloudWatch / ...).

## 4. Health checks

| Endpoint deseado                  | Comprobación                                                  |
|------------------------------------|---------------------------------------------------------------|
| `GET /health/` (liveness)          | Servicio responde HTTP 200.                                    |
| `GET /readiness/`                  | Conexión a BD principal + lectura de `prepagada.db` (`v_cruce`). |

> ⚠️ PENDIENTE: las fuentes no listan endpoints de health check. Estos son recomendaciones.

## 5. Alertas sugeridas

| Alerta                                                 | Umbral propuesto                              | Severidad |
|---------------------------------------------------------|------------------------------------------------|-----------|
| Archivo cargado pasa a estado `ERROR`                   | Inmediata                                       | Alta       |
| Tasa de error en un archivo > 5 %                        | Por archivo                                      | Media      |
| `prepagada.db` no accesible                             | Health check rojo                                 | Alta       |
| Sin archivos cargados en el mes esperado (D+5 del mes)   | Cronograma de cierre                              | Media      |
| Latencia `/upload/` p95 > 30 s (RNF PERF-01 mantiene < 20 s) | Métrica de instrumentación                  | Media      |
| `/planilla/calcular/` falla en producción                | Métrica de instrumentación                       | Alta       |

> ⚠️ PENDIENTE: enrutamiento de alertas (Slack/email/PagerDuty) no documentado.

## 6. Dashboards

| Audiencia       | Dashboard sugerido                                              | Estado |
|-----------------|------------------------------------------------------------------|--------|
| Operación        | Estado de cargas del mes (archivos, errores, advertencias).      | `PENDIENTE` |
| Talento Humano    | Cobertura por proveedor, totales por periodo, novedades.         | Cubierto por `/dashboard/` del módulo. |
| Tributaria       | Apoyo gravable por periodo y por empleado.                       | Cubierto por `/causacion/` y exportación. |
| Técnica          | Latencia, throughput, errores HTTP, disponibilidad de `prepagada.db`. | `PENDIENTE` |

---

**Fuente:** `siga/ARQUITECTURA_SOFTWARE.md` (§10 Observabilidad). El resto de la sección es esqueleto a definir por el equipo.
