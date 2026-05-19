# Matriz de Trazabilidad

| Campo        | Valor                                                                                |
|--------------|---------------------------------------------------------------------------------------|
| Versión      | 1.0                                                                                   |
| Fecha        | 2026-05-13                                                                            |
| Fuente       | Documentación Técnica §3, §6–§11; Matriz de Reglas Medicina Prepagada                  |
| Responsable  | QA / Líder técnico                                                                    |
| Estado       | Borrador — sin columna de pruebas formales                                            |

---

> ⚠️ PENDIENTE: las fuentes no aportan IDs de prueba, casos de prueba ni cobertura medida. Esta matriz cruza **Requerimiento → Componente → Endpoint/Modelo** con la información disponible. La columna `Prueba` queda como `PENDIENTE`.

## 1. Beneficios — pipeline ETL

| Requerimiento (RF-XX o RN/MP) | Componente principal                              | Endpoint / vista                     | Modelo persistente                          | Prueba |
|--------------------------------|----------------------------------------------------|---------------------------------------|----------------------------------------------|--------|
| RF-101 Cargar archivo Excel    | `views.UploadView`                                 | `POST /upload/`                       | `ArchivoRecibido`, `BeneficioSalud`, `ErrorProcesamiento` | `PENDIENTE` |
| RF-102 Hash SHA256              | `_sha256_archivo()` en `views.py`                  | `POST /upload/`                       | `ArchivoRecibido.hash_sha256`                | `PENDIENTE` |
| RF-103 Detección de proveedor   | `services/detector.py`                             | `POST /upload/`                       | `ArchivoRecibido.proveedor`                   | `PENDIENTE` |
| RF-104 Persistencia archivo     | `_guardar_archivo()`                                | `POST /upload/`                       | Filesystem `storage/landing/`                  | `PENDIENTE` |
| RF-105 Estado de archivo        | `views.UploadView`                                  | `POST /upload/`                       | `ArchivoRecibido.estado_procesamiento`         | `PENDIENTE` |
| RF-106 Detección de cabecera     | `services/reader_excel.py`                          | (interno)                              | -                                              | `PENDIENTE` |
| RF-107 Metadatos contrato/periodo | `services/reader_excel.py`                          | (interno)                              | `ArchivoRecibido.numero_contrato`, `periodo_facturacion` | `PENDIENTE` |
| RF-108 Adaptador AXA            | `services/axa_adapter.py`                           | (interno)                              | `BeneficioSalud`                                | `PENDIENTE` |
| RF-109 Adaptador Colsanitas      | `services/colsanitas_adapter.py`                    | (interno)                              | `BeneficioSalud`                                | `PENDIENTE` |
| RF-110 Validación fila a fila    | `services/validator.py`                              | (interno)                              | `BeneficioSalud.estado_validacion`, `ErrorProcesamiento` | `PENDIENTE` |
| RF-111 Bulk insert               | `BeneficioSalud.objects.bulk_create(batch_size=500)`| (interno)                              | `BeneficioSalud`                                | `PENDIENTE` |
| RF-112 Persistencia de errores    | `ErrorProcesamiento.objects.bulk_create()`          | (interno)                              | `ErrorProcesamiento`                            | `PENDIENTE` |
| RF-113 Contadores                | `views.UploadView`                                  | `POST /upload/`                       | `ArchivoRecibido` (`total_registros`, `procesados`, `con_error`) | `PENDIENTE` |
| RN-05 Cédula vacía / inválida    | `services/validator.py`                              | (interno)                              | `ErrorProcesamiento` (`CEDULA_INVALIDA`)         | `PENDIENTE` |
| RN-06 Valores numéricos inválidos | `services/validator.py`                             | (interno)                              | `ErrorProcesamiento` (`VALOR_INVALIDO`)          | `PENDIENTE` |
| RN-08/09 Tolerancia aritmética    | `services/validator.py`                             | (interno)                              | `BeneficioSalud.estado_validacion = ADVERTENCIA` | `PENDIENTE` |
| RN-10 Cédula duplicada            | `services/validator.py`                             | (interno)                              | `BeneficioSalud.estado_validacion = ADVERTENCIA` | `PENDIENTE` |
| RN-11 Ajuste Colsanitas            | `services/validator.py`                             | (interno)                              | `BeneficioSalud.estado_validacion = ADVERTENCIA` | `PENDIENTE` |
| MP-035 Soporte AXA                | `services/axa_adapter.py`                            | `POST /upload/`                       | `BeneficioSalud`                                | `PENDIENTE` |
| MP-036 Soporte Colsanitas         | `services/colsanitas_adapter.py`                     | `POST /upload/`                       | `BeneficioSalud`                                | `PENDIENTE` |
| MP-037 Proveedor desconocido      | `services/detector.py` + `views.UploadView`          | `POST /upload/`                       | Estado `ERROR` / `proveedor=desconocido`         | `PENDIENTE` |
| MP-038 Duplicados                  | `services/validator.py`                              | (interno)                              | `BeneficioSalud` con `ADVERTENCIA`              | `PENDIENTE` |
| MP-039 Ajustes contables negativos | `services/validator.py`                              | (interno)                              | `BeneficioSalud` con `ADVERTENCIA`              | `PENDIENTE` |
| MP-040 Errores de valor           | `services/validator.py`                              | (interno)                              | `ErrorProcesamiento` (`VALOR_INVALIDO`)         | `PENDIENTE` |

## 2. Beneficios — consulta y reportes

| Requerimiento                | Endpoint                                      | Modelo / Servicio                        | Prueba |
|------------------------------|------------------------------------------------|------------------------------------------|--------|
| RF-201 Lista archivos         | `GET /archivos/`                              | `ArchivoListView`                         | `PENDIENTE` |
| RF-202 Detalle de archivo     | `GET /archivos/<id>/`                         | `ArchivoDetailView`                       | `PENDIENTE` |
| RF-203 Lista beneficios       | `GET /beneficios/`                            | `BeneficioListView`                       | `PENDIENTE` |
| RF-204 Exportar Excel         | `GET /exportar/`                              | `ExportarExcelView`                        | `PENDIENTE` |
| RF-205 Novedades              | `GET /novedades/`                              | `NovedadesView`                            | `PENDIENTE` |
| RF-206 Dashboard              | `GET /dashboard/`                              | `DashboardView`                            | `PENDIENTE` |

## 3. Medicina prepagada — configuración

| Requerimiento                | Endpoint                                      | Modelo                                  | Prueba |
|------------------------------|------------------------------------------------|------------------------------------------|--------|
| RF-301 CRUD política          | `GET/POST /politica/`, `GET/PUT /politica/<id>/` | `PoliticaPrepagada`                       | `PENDIENTE` |
| RF-302 CRUD pensionados        | `GET/POST /pensionados/`, `GET/PUT/DELETE /pensionados/<id>/` | `PensionadoPrepagada` | `PENDIENTE` |
| RF-303 CRUD auxilio externo    | `GET/POST /auxilio-externo/`, `GET/PUT/DELETE /auxilio-externo/<id>/` | `AuxilioExterno` | `PENDIENTE` |

## 4. Medicina prepagada — cálculo y reportes

| Requerimiento                                | Endpoint / vista                            | Componente / modelo                         | Prueba |
|----------------------------------------------|----------------------------------------------|----------------------------------------------|--------|
| RF-401 Lista periodos y cruce                 | `GET /cruce/`                                | `prepagada_service.py` → `v_cruce`            | `PENDIENTE` |
| RF-402 Calcular planilla                      | `POST /planilla/calcular/`                   | `eligibility.py` + `PlanillaCalcularView`     | `PENDIENTE` |
| RF-403 Clasificación de elegibilidad          | -                                            | `eligibility.py`                              | `PENDIENTE` |
| RF-404 Apoyo gravable / no gravable           | -                                            | `eligibility.py`                              | `PENDIENTE` |
| RF-405 Lista y detalle de planilla            | `GET /planilla/`, `GET /planilla/<id>/`      | `PlanillaCalculo`, `DetalleCalculo`           | `PENDIENTE` |
| RF-406 Exportar planilla                      | `GET /planilla/<id>/exportar/`               | `PlanillaExportarView`                        | `PENDIENTE` |
| RF-407 Causación                              | `GET /causacion/`                             | `CausacionView`                                | `PENDIENTE` |
| RF-408 Conciliación                           | `GET /conciliacion/`                          | `ConciliacionView`                             | `PENDIENTE` |
| RF-409 Informe EFR                            | `GET /informe-efr/`                            | `InformeEFRView`                                | `PENDIENTE` |
| MP-005 Distribución 80/20                     | `POST /planilla/calcular/`                    | `eligibility.py`                                | `PENDIENTE` |
| MP-006 Pensionados al 100 %                   | `POST /planilla/calcular/`                    | `eligibility.py` + `PensionadoPrepagada`         | `PENDIENTE` |
| MP-028 Cruce con Kactus                       | `GET /cruce/`                                  | `prepagada_service.py`                          | `PENDIENTE` |
| MP-031 Total familia                           | `POST /planilla/calcular/`                    | `prepagada_service.py`                          | `PENDIENTE` |
| MP-033 Límite no gravable / gravable           | `POST /planilla/calcular/`                    | `eligibility.py`                                 | `PENDIENTE` |

## 5. Reglas con estado parcial / pendiente

Para cada regla MP en estado `Parcial`, `No soportado` o `Por definir`, ver [`../01-funcional/reglas-de-negocio.md`](../01-funcional/reglas-de-negocio.md) §4. La trazabilidad para estas reglas está en estado de **brecha**, lo cual debe reflejarse en el plan de trabajo y en [`checklist-entrega.md`](checklist-entrega.md) §5.

## 6. Cobertura de pruebas

| Bloque                                            | Cobertura objetivo recomendada | Estado |
|---------------------------------------------------|---------------------------------|--------|
| Validador (`services/validator.py`)                 | Alta                            | `PENDIENTE` |
| Adaptadores (AXA, Colsanitas)                      | Alta                            | `PENDIENTE` |
| Lector de Excel (`reader_excel.py`)                 | Media                            | `PENDIENTE` |
| Elegibilidad (`eligibility.py`)                     | Alta                            | `PENDIENTE` |
| Servicios de prepagada (lectura `v_cruce`)          | Media (mockear SQLite)            | `PENDIENTE` |
| Endpoints (DRF)                                     | Media                            | `PENDIENTE` |

---

**Fuente:** `siga/DOCUMENTACION_TECNICA.md` (§3, §6, §7, §8, §9, §10, §11), `docs/matriz-reglas-medicina-prepagada-siga.md`.
