# Requerimientos No Funcionales

| Campo        | Valor                                                                            |
|--------------|----------------------------------------------------------------------------------|
| Versión      | 1.0                                                                              |
| Fecha        | 2026-05-13                                                                       |
| Fuente       | Documento Funcional Beneficios de Salud (tiempos ETL); Arquitectura §9–§10, §13   |
| Responsable  | Equipo SIGA / Arquitectura                                                       |
| Estado       | **Borrador — cobertura BAJA**, ver `gaps.md` Top 10 #1                            |

---

> ⚠️ PENDIENTE: las fuentes no formalizan un catálogo de RNF. Lo que sigue es una extracción de mejor esfuerzo de tiempos, recomendaciones y riesgos mencionados. Es esqueleto para discusión.

## 1. Rendimiento

Las mediciones provienen del Documento Funcional Beneficios de Salud (sección "Pipeline ETL — Detalle Técnico").

| Indicador                                                       | Valor declarado    | Notas                                              |
|------------------------------------------------------------------|---------------------|-----------------------------------------------------|
| Hash SHA256 del archivo (Fase E.1)                               | < 100 ms            | En memoria sobre el stream del archivo              |
| Persistencia del Excel en disco (Fase E.2)                       | < 500 ms            |                                                     |
| Detección de proveedor (Fase E.3)                                | < 200 ms            |                                                     |
| Detección de fila de cabecera (Fase E.4)                         | 200–500 ms          | Lectura parcial: primeras 16–21 filas               |
| Lectura del DataFrame completo (Fase E.6)                        | 500 ms – 3 s        | Para 100–800 filas                                  |
| Normalización por adaptador (Fase T.1)                           | 100–300 ms          | Para 500 filas                                      |
| Validación fila a fila (Fase T.2)                                | < 250 ms            | Vectorizada con pandas                              |
| `bulk_create` de beneficios (Fase L.1)                           | < 2 s               | Batch de 500                                        |
| `bulk_create` de errores (Fase L.2)                              | < 500 ms            |                                                     |
| **Total ETL por archivo**                                        | **< 20 s**          | Archivos típicos                                    |

| RNF-PERF | Requerimiento                                                                              |
|----------|---------------------------------------------------------------------------------------------|
| PERF-01  | El procesamiento de un archivo Excel típico (≤ 800 registros) debe completarse en ≤ 20 s.   |
| PERF-02  | La inserción a BD debe realizarse en batches de hasta 500 registros para minimizar round-trips. |
| PERF-03  | El cálculo de la planilla de un periodo debe completarse en un único request HTTP.           |

> ⚠️ PENDIENTE: definir SLOs formales (p95, p99 de latencia de cada endpoint), umbrales de error y disponibilidad.

## 2. Disponibilidad y resiliencia

> ⚠️ PENDIENTE: las fuentes no especifican SLA de disponibilidad, RTO/RPO ni ventanas de mantenimiento. Esta tabla recoge el comportamiento defensivo conocido.

| Tema                                | Comportamiento documentado                                                                          |
|-------------------------------------|------------------------------------------------------------------------------------------------------|
| Fallo de `prepagada.db`             | Endpoints de cruce y planilla retornan error (HTTP 503 según T1 §14; HTTP 500 según F2). Resto de endpoints opera normalmente. |
| Fallo durante `bulk_create`         | El estado del `ArchivoRecibido` pasa a `ERROR`. El archivo en disco queda preservado para reprocesamiento manual. |
| Archivo duplicado (mismo SHA256)    | Rechazado antes de procesar (declarado en F2). Verificar contradicción documentada en `gaps.md`.     |
| Excel sin cabecera detectable        | Error descriptivo y archivo en estado `ERROR`.                                                       |
| Cédula vacía / valor no numérico     | Registro rechazado; el resto del archivo continúa.                                                   |

| RNF-AVAIL | Requerimiento                                                                          |
|-----------|-----------------------------------------------------------------------------------------|
| AVAIL-01  | El procesamiento de errores fila a fila no debe interrumpir la carga del resto del archivo. |
| AVAIL-02  | El archivo original recibido debe conservarse en disco aun cuando el procesamiento falle. |

> ⚠️ PENDIENTE: definir SLA de disponibilidad, RTO, RPO y ventanas de mantenimiento.

## 3. Capacidad

| Indicador                          | Valor típico documentado                |
|------------------------------------|------------------------------------------|
| Filas por archivo AXA Colpatria    | 100–400 beneficiarios                    |
| Filas por archivo Colsanitas       | 50–250 beneficiarios                     |
| Archivos por periodo                | 2 (uno por proveedor)                    |
| Workers Gunicorn (Docker)           | 2                                        |
| Puerto interno / host               | 8000 / 9010                              |

> ⚠️ PENDIENTE: definir capacidad máxima esperada (registros, archivos por mes, concurrencia de usuarios), límite de tamaño de archivo aceptado por el proxy.

## 4. Seguridad

Las restricciones críticas vienen señaladas por las fuentes como áreas que requieren endurecimiento:

| Tema                       | Estado actual                                            | Recomendación documentada           |
|----------------------------|-----------------------------------------------------------|--------------------------------------|
| Permisos DRF               | `AllowAny` por defecto                                    | Cambiar a autenticación obligatoria si SIGA queda expuesto fuera de red controlada |
| Tamaño máximo de subida    | Sin límite explícito en la app                             | Limitar tamaño en proxy / webserver  |
| Validación de archivo subido | Sólo por extensión y contenido al parsear                | Validar extensión y MIME explícitamente si se requiere hardening |
| Almacenamiento sensible    | Archivos en filesystem; `prepagada.db` accesible           | Proteger con permisos del sistema y backups |
| Datos personales          | Cédulas, nombres y valores almacenados                     | Requieren proteger acceso, retención y backups (Ley 1581) |

Ver `05-seguridad/*` para el detalle.

## 5. Mantenibilidad

| Tema                     | Comportamiento documentado                                                       |
|--------------------------|----------------------------------------------------------------------------------|
| Esquema unificado        | `BeneficioSalud` aísla a las consultas de la heterogeneidad de proveedores.        |
| Adaptadores por proveedor| Nuevo proveedor → nuevo adaptador en `services/`, ampliar `detector.py` y `UploadView`. Sin afectar el resto. |
| Validaciones             | Reglas concentradas en `validator.py`.                                            |
| Política de prepagada    | Versionable: histórico de políticas se conserva (T1 §5.2 `bs_politica_prepagada`).|
| Migraciones              | Carpeta `migrations/` por app; uso estándar de Django.                            |

| RNF-MAINT | Requerimiento                                                                                |
|-----------|------------------------------------------------------------------------------------------------|
| MAINT-01  | Agregar un nuevo proveedor no debe requerir cambios en los modelos persistentes.               |
| MAINT-02  | Cambios en la política 80/20 no deben requerir nueva migración: la política está modelada como dato. |

## 6. Trazabilidad y auditoría

| Mecanismo                            | Uso                                                                          |
|--------------------------------------|-------------------------------------------------------------------------------|
| `ArchivoRecibido.hash_sha256`        | Identifica unívocamente el archivo.                                           |
| `ArchivoRecibido.estado_procesamiento` | Permite reconstruir el avance de la carga.                                   |
| `BeneficioSalud.archivo` (FK)        | Liga cada registro normalizado a su archivo origen.                            |
| `ErrorProcesamiento.fila_origen`     | Permite ubicar la fila exacta del Excel donde se detectó un error.            |
| `PlanillaCalculo.generada_por / generada_en` | Trazabilidad del cálculo de planilla; ver gap MP-041 sobre usuario real.    |

| RNF-AUDIT | Requerimiento                                                                              |
|-----------|---------------------------------------------------------------------------------------------|
| AUDIT-01  | Todo registro normalizado debe poder rastrearse a su archivo y a su fila original.           |
| AUDIT-02  | Todo error y advertencia debe almacenarse de manera persistente, no sólo en logs.            |
| AUDIT-03  | El histórico de políticas aplicadas debe conservarse para auditoría tributaria.              |

## 7. Usabilidad

> ⚠️ PENDIENTE: las fuentes funcionales describen API y modelo de datos pero **no** ergonomía del portal (accesibilidad, idioma, formato de fecha/moneda, criterios WCAG). Falta documentación de UI/UX del portal SIGA.

## 8. Internacionalización y locale

> ⚠️ PENDIENTE: el sistema opera en español y en pesos colombianos. No hay documentación formal de criterios de localización.

## 9. Riesgos operativos relevantes (Arquitectura §13)

| Riesgo                                  | Impacto                                                                      |
|-----------------------------------------|------------------------------------------------------------------------------|
| Cambio de plantilla Excel               | Puede romper la detección de encabezados o el mapeo de columnas.              |
| `AllowAny` en API                       | Riesgo si el servicio se publica sin control perimetral.                      |
| `prepagada.db` faltante                  | Endpoints de cruce y planilla fallan con 503.                                 |
| Reprocesamiento de archivo duplicado     | El hash se almacena, pero no hay rechazo automático implementado (ver T1 §14). |
| Excel muy grande                         | Exportación o carga puede consumir memoria por uso de pandas/openpyxl en request. |
| Datos sensibles                          | Cédulas, nombres y valores requieren protección de acceso y backup seguro.    |

---

**Fuente:** `siga/DOCUMENTO_FUNCIONAL_BENEFICIOS_SALUD.md` (Pipeline ETL — sub-fases y tiempos), `siga/ARQUITECTURA_SOFTWARE.md` (§9 Seguridad, §10 Observabilidad, §13 Riesgos), `siga/DOCUMENTACION_TECNICA.md` (§14 Consideraciones).
