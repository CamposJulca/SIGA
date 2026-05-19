# Requerimientos Funcionales

| Campo        | Valor                                                                          |
|--------------|---------------------------------------------------------------------------------|
| Versión      | 1.0                                                                             |
| Fecha        | 2026-05-13                                                                      |
| Fuente       | Documentación Funcional §2, §9; Documento Funcional Beneficios de Salud; Técnica §9 |
| Responsable  | Equipo SIGA                                                                     |
| Estado       | Borrador                                                                        |

---

## 1. Convención de identificadores

> ⚠️ PENDIENTE: las fuentes no enumeran requerimientos funcionales con un ID formal. Los IDs `RF-XXX` propuestos a continuación se derivan de las capacidades documentadas y deben ser validados por el área funcional antes de usarse en pruebas o contratos.

## 2. Beneficios de Salud — ETL de facturas

| ID       | Requerimiento                                                                                                                                          | Prioridad | Estado actual | Referencia API/Vista                          |
|----------|---------------------------------------------------------------------------------------------------------------------------------------------------------|-----------|----------------|------------------------------------------------|
| RF-101 | El sistema debe permitir cargar archivos Excel (`.xls`/`.xlsx`) de las EPS soportadas a través del portal o de un endpoint API.                            | Alta      | Implementado   | `POST /api/beneficios-salud/upload/`           |
| RF-102 | El sistema debe calcular un hash SHA256 del archivo recibido para soporte de deduplicación.                                                              | Alta      | Implementado (almacenamiento)  | `_sha256_archivo()`                            |
| RF-103 | El sistema debe detectar automáticamente el proveedor a partir del nombre del archivo y, si éste no es concluyente, a partir de las columnas.            | Alta      | Implementado   | `detector.py`                                  |
| RF-104 | El sistema debe persistir el archivo original recibido en `storage/landing/{proveedor}/`.                                                                | Alta      | Implementado   | `_guardar_archivo()`                           |
| RF-105 | El sistema debe registrar cada archivo cargado en `ArchivoRecibido` con su estado (`RECIBIDO → PROCESANDO → PROCESADO/ERROR`), hash, ruta y usuario de carga. | Alta      | Implementado   | Modelo `ArchivoRecibido`                       |
| RF-106 | El sistema debe detectar la fila real de encabezado en el Excel, soportando filas de metadatos previas (hasta 16 filas para AXA, 21 para Colsanitas).      | Alta      | Implementado   | `reader_excel.py`                              |
| RF-107 | El sistema debe extraer del Excel el `numero_contrato` y el `periodo_facturacion` cuando estén presentes en cabecera.                                     | Alta      | Implementado   | `reader_excel.py`                              |
| RF-108 | El sistema debe normalizar las columnas nativas de AXA Colpatria al esquema unificado `BeneficioSalud`.                                                  | Alta      | Implementado   | `axa_adapter.py`                               |
| RF-109 | El sistema debe normalizar las columnas nativas de Colsanitas al esquema unificado `BeneficioSalud`, incluyendo el filtrado de filas resumen (TOTAL FAMILIA, TOTAL CONTRATO, TOTAL GENERAL, SUBTOTAL, GRAN TOTAL). | Alta | Implementado | `colsanitas_adapter.py` |
| RF-110 | El sistema debe validar la integridad de cada registro (cédula, valores numéricos, consistencia aritmética, duplicados) y clasificarlo como `OK`, `ADVERTENCIA` o `ERROR`. | Alta | Implementado | `validator.py` |
| RF-111 | El sistema debe persistir los beneficios válidos y advertencias mediante carga masiva (`bulk_create`, batch 500).                                         | Alta      | Implementado   | `BeneficioSalud.objects.bulk_create()`          |
| RF-112 | El sistema debe persistir los errores con `fila_origen`, tipo de error y descripción, sin bloquear la carga del resto del archivo.                        | Alta      | Implementado   | `ErrorProcesamiento`                            |
| RF-113 | El sistema debe actualizar los contadores del archivo: `total_registros`, `registros_procesados`, `registros_con_error`.                                  | Alta      | Implementado   | `views.py`                                     |

> ⚠️ PENDIENTE — Discrepancia: el documento de Beneficios de Salud declara que un archivo duplicado por SHA256 es **rechazado** antes de procesamiento (Fase E.1), pero la Documentación Técnica (§14) y la Arquitectura (§13) indican que el hash se almacena **pero no se rechaza automáticamente**. Verificar el comportamiento real.

## 3. Beneficios de Salud — Consulta y reporte

| ID       | Requerimiento                                                                                                       | Prioridad | API/Vista                                            |
|----------|---------------------------------------------------------------------------------------------------------------------|-----------|-------------------------------------------------------|
| RF-201 | Listar archivos cargados con filtros por proveedor y estado.                                                          | Media     | `GET /api/beneficios-salud/archivos/`                  |
| RF-202 | Ver detalle de archivo incluyendo errores asociados.                                                                  | Media     | `GET /api/beneficios-salud/archivos/<id>/`             |
| RF-203 | Listar beneficios con filtros por archivo, proveedor, cédula y estado de validación.                                  | Media     | `GET /api/beneficios-salud/beneficios/`                |
| RF-204 | Exportar beneficios a Excel con hojas `Consolidado`, `AXA Colpatria`, `Colsanitas`.                                   | Alta      | `GET /api/beneficios-salud/exportar/`                  |
| RF-205 | Comparar dos archivos del mismo proveedor para identificar nuevos afiliados, retirados y cambios de valor.            | Media     | `GET /api/beneficios-salud/novedades/`                 |
| RF-206 | Dashboard ejecutivo con últimos periodos, distribución por parentesco/proveedor, evolución y consolidado.             | Media     | `GET /api/beneficios-salud/dashboard/`                 |

## 4. Medicina prepagada — Configuración

| ID       | Requerimiento                                                                                                | API/Vista                                            |
|----------|----------------------------------------------------------------------------------------------------------------|-------------------------------------------------------|
| RF-301 | Permitir crear, listar, consultar y actualizar políticas de prepagada (porcentajes, UVT, conceptos contables, vigencia). | `politica/`, `politica/<id>/`                          |
| RF-302 | Permitir CRUD de pensionados activos con prepagada.                                                            | `pensionados/`, `pensionados/<id>/`                    |
| RF-303 | Permitir CRUD de auxilios externos.                                                                            | `auxilio-externo/`, `auxilio-externo/<id>/`            |

## 5. Medicina prepagada — Cálculo y reporte

| ID       | Requerimiento                                                                                                       | Estado | API/Vista                                                |
|----------|---------------------------------------------------------------------------------------------------------------------|--------|-----------------------------------------------------------|
| RF-401 | Listar los periodos disponibles en `prepagada.db` y los registros cruzados por periodo.                              | Implementado | `GET /api/beneficios-salud/cruce/`                         |
| RF-402 | Calcular la planilla de un periodo aplicando la política vigente (porcentaje empresa/empleado, UVT, conceptos).      | Implementado | `POST /api/beneficios-salud/planilla/calcular/`            |
| RF-403 | Clasificar empleados según elegibilidad: `ELEGIBLE_80_20`, `PENSIONADO_100`, `BLOQUEADO_CRUCE`.                       | Implementado | `eligibility.py`                                          |
| RF-404 | Separar el aporte de la empresa en `apoyo_no_gravable` (≤ UVT × valor UVT) y `apoyo_gravable` (excedente).            | Implementado | `eligibility.py`                                          |
| RF-405 | Listar las planillas calculadas por periodo y mostrar su detalle (`PlanillaCalculo`, `DetalleCalculo`).               | Implementado | `planilla/`, `planilla/<id>/`                              |
| RF-406 | Exportar la planilla a Excel con hojas `Planilla 80-20` y `Apoyo Gravable`.                                          | Implementado | `planilla/<id>/exportar/`                                  |
| RF-407 | Generar resumen de causación por EPS para el periodo seleccionado.                                                  | Implementado | `GET /api/beneficios-salud/causacion/`                     |
| RF-408 | Generar comparación entre planillas de dos periodos (conciliación).                                                  | Implementado | `GET /api/beneficios-salud/conciliacion/`                  |
| RF-409 | Generar informe EFR mensual incluyendo planilla, pensionados activos y auxilios externos.                           | Implementado | `GET /api/beneficios-salud/informe-efr/`                   |

## 6. Roadmap declarado (no implementado)

Las siguientes reglas y datos del Manual de Talento Humano están en el alcance documental pero **no están implementadas** en SIGA. Se documentan como Roadmap Funcional para que el cliente y el equipo conozcan el alcance completo del manual:

| Bloque                                         | Estado en SIGA            | Sección de referencia                            |
|------------------------------------------------|---------------------------|--------------------------------------------------|
| Antigüedad mínima (2 meses / periodo de prueba) | No implementado            | Reglas MP-002 en `reglas-de-negocio.md`           |
| Aceptación del beneficio y autorización descuento | No implementado          | MP-003, MP-004                                    |
| Elegibilidad por parentesco / edad / dependencia económica / discapacidad | Parcial | MP-008 a MP-017                            |
| Reglas de sustitución (soltero/casado/padres)   | No implementado            | MP-012 a MP-015                                   |
| Pólizas externas (tope por promedio, retroactividad, recibos mensuales) | No implementado | MP-019 a MP-025                                   |
| Prorrateo por ingreso o retiro                  | No implementado            | MP-026, MP-027                                    |
| Soportes documentales por parentesco            | No implementado            | MP-017, MP-044                                    |
| Auxilio educativo para hijos                    | No implementado            | Manual THU-DOC-002 — sección auxilio educativo    |
| Vacaciones y compensaciones                     | No implementado            | Manual THU-DOC-002 — vacaciones                    |
| Primas extralegales y bonificaciones quinquenio | No implementado            | Manual THU-DOC-002 — primas                        |
| Auxilio de incapacidad                          | No implementado            | Manual THU-DOC-002 — incapacidad                   |
| Auxilio extralegal de alimentación              | No implementado            | Manual THU-DOC-002 — alimentación                  |
| Auxilio de parqueadero                          | No implementado            | Manual THU-DOC-002 — parqueadero                   |
| Aportes FONDEFIN                                | No implementado            | Manual THU-DOC-002 — FONDEFIN                      |
| Préstamo de libre inversión                     | No implementado            | Manual THU-DOC-002 — préstamo                      |
| Crédito educativo condonable                    | No implementado            | Manual THU-DOC-002 — crédito condonable            |
| Permisos, licencias y flexibilidad              | No implementado            | Manual THU-DOC-002 — permisos                      |
| Convocatorias, encargos, nivelación salarial    | No implementado            | Manual THU-DOC-002 — convocatorias                 |
| Póliza funeraria, seguro de vida                | No implementado            | Manual THU-DOC-002 — pólizas asociadas             |

> ℹ️ Las reglas anteriores existen documentalmente. Su implementación requiere primero resolver las decisiones funcionales pendientes listadas en [`reglas-de-negocio.md`](reglas-de-negocio.md) §"Decisiones pendientes".

---

**Fuente:** `siga/DOCUMENTACION_FUNCIONAL.md` (§2 Capacidades, §9 Funcionalidades), `siga/DOCUMENTO_FUNCIONAL_BENEFICIOS_SALUD.md` (API de Consulta y Exportación), `siga/DOCUMENTACION_TECNICA.md` (§9 API REST), `docs/matriz-reglas-medicina-prepagada-siga.md`, `docs/reglas-talento-humano-siga.md`.
