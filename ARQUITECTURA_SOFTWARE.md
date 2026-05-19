# SIGA - Arquitectura de Software

## 1. Vista general

SIGA es una aplicacion Django modular orientada a procesamiento administrativo. Su modulo principal actual es `beneficios_salud`, que concentra dos dominios relacionados:

- ETL de archivos Excel de proveedores de salud.
- Calculo y reporte de medicina prepagada.

```text
Usuario / Portal
    |
    | HTTP
    v
SIGA Backend Django + DRF
    |
    +-- modules.beneficios_salud.views
    |       |
    |       +-- services.detector
    |       +-- services.reader_excel
    |       +-- services.axa_adapter
    |       +-- services.colsanitas_adapter
    |       +-- services.validator
    |       +-- services.prepagada_service
    |
    +-- Base principal Django
    |       +-- bs_archivos_recibidos
    |       +-- bs_beneficios_salud
    |       +-- bs_errores_procesamiento
    |       +-- bs_politica_prepagada
    |       +-- bs_planilla_calculo
    |       +-- bs_detalle_calculo
    |
    +-- storage/landing
    |
    +-- prepagada.db
```

## 2. Estilo arquitectonico

| Aspecto | Decision |
|---|---|
| Aplicacion | Monolito Django modular. |
| API | REST con Django REST Framework. |
| Dominio | App `modules.beneficios_salud`. |
| Procesamiento | Servicios Python puros invocados desde vistas API. |
| Persistencia operacional | ORM Django sobre SQLite/PostgreSQL. |
| Persistencia documental | Archivos originales en filesystem. |
| Fuente externa prepagada | SQLite separado (`prepagada.db`). |
| Exportacion | Generacion Excel bajo demanda con openpyxl. |

## 3. Componentes

### 3.1 Capa API

Archivo principal: `backend/modules/beneficios_salud/views.py`

Responsabilidades:

- Recibir requests HTTP.
- Orquestar servicios de procesamiento.
- Persistir entidades con ORM.
- Serializar respuestas JSON.
- Generar archivos Excel descargables.

### 3.2 Capa de dominio y datos

Archivo principal: `backend/modules/beneficios_salud/models.py`

Responsabilidades:

- Definir entidades persistentes.
- Mantener relaciones entre archivos, beneficios, errores y planillas.
- Representar politicas y maestros de prepagada.

### 3.3 Servicios ETL

| Servicio | Responsabilidad |
|---|---|
| `detector.py` | Detectar proveedor por nombre o columnas. |
| `reader_excel.py` | Leer Excel, detectar encabezado y extraer metadatos. |
| `axa_adapter.py` | Transformar AXA al esquema unificado. |
| `colsanitas_adapter.py` | Transformar Colsanitas al esquema unificado. |
| `validator.py` | Validar integridad y clasificar errores/advertencias. |

### 3.4 Servicios de prepagada

| Servicio | Responsabilidad |
|---|---|
| `prepagada_service.py` | Leer `prepagada.db`, consultar `v_cruce` y calcular planillas. |
| `eligibility.py` | Evaluar si aplica 80/20, pensionado 100% o bloqueo por cruce. |

### 3.5 Almacenamiento de archivos

```text
siga/storage/landing/
├── axa_colpatria/
├── colsanitas/
└── desconocido/
```

La ruta guardada en `ArchivoRecibido.ruta_archivo` permite reconstruir el origen del dato procesado.

## 4. Vista de flujo ETL

```text
Excel proveedor
    |
    v
UploadView
    |
    +-- SHA256
    +-- detectar_proveedor()
    +-- guardar archivo en storage/landing
    +-- crear ArchivoRecibido
    |
    v
leer_excel()
    |
    +-- detectar fila de encabezado
    +-- extraer numero_contrato y periodo_facturacion
    |
    v
Adaptador proveedor
    |
    +-- adaptar_axa()
    +-- adaptar_colsanitas()
    |
    v
validar_registros()
    |
    +-- registros OK / ADVERTENCIA
    +-- errores fatales
    |
    v
bulk_create()
    |
    +-- BeneficioSalud
    +-- ErrorProcesamiento
    |
    v
ArchivoRecibido = PROCESADO
```

## 5. Vista de flujo prepagada

```text
Usuario selecciona periodo
    |
    v
PlanillaCalcularView
    |
    +-- obtener politica vigente o politica_id
    +-- prepagada_service.get_cruce_periodo(periodo)
    |
    v
v_cruce en prepagada.db
    |
    v
eligibility.evaluar_elegibilidad()
    |
    +-- PENSIONADO_100
    +-- BLOQUEADO_CRUCE
    +-- ELEGIBLE_80_20
    |
    v
calculo valores
    |
    +-- valor_empresa
    +-- valor_empleado
    +-- apoyo_no_gravable
    +-- apoyo_gravable
    |
    v
PlanillaCalculo + DetalleCalculo
```

## 6. Vista de despliegue

```text
Servidor / Docker
    |
    +-- contenedor siga
    |       +-- gunicorn core.wsgi:application
    |       +-- puerto interno 8000
    |       +-- workers 2
    |
    +-- volumen ./storage -> /app/../storage
    |
    +-- volumen siga_db -> /app/db
            +-- db.sqlite3
            +-- prepagada.db
```

Puerto publicado por `docker-compose.yml`:

```text
localhost:9010 -> siga:8000
```

## 7. Vista de datos

### 7.1 Entidades ETL

```text
ArchivoRecibido 1 --- N BeneficioSalud
ArchivoRecibido 1 --- N ErrorProcesamiento
```

### 7.2 Entidades prepagada

```text
PoliticaPrepagada 1 --- N PlanillaCalculo
PlanillaCalculo 1 --- N DetalleCalculo

PensionadoPrepagada
AuxilioExterno
```

### 7.3 Dependencia externa

```text
prepagada.db
├── facturas_eps
├── empleados_kactus
└── v_cruce
```

## 8. Contratos de API

### 8.1 Base

```text
/api/beneficios-salud/
```

### 8.2 Principales contratos

| Dominio | Rutas |
|---|---|
| Carga y archivos | `upload/`, `archivos/`, `archivos/<id>/` |
| Beneficios | `beneficios/`, `exportar/`, `novedades/`, `dashboard/` |
| Cruce | `cruce/` |
| Politicas | `politica/`, `politica/<id>/` |
| Pensionados | `pensionados/`, `pensionados/<id>/` |
| Auxilio externo | `auxilio-externo/`, `auxilio-externo/<id>/` |
| Planilla | `planilla/`, `planilla/calcular/`, `planilla/<id>/`, `planilla/<id>/exportar/` |
| Reportes | `causacion/`, `conciliacion/`, `informe-efr/` |

## 9. Seguridad

| Superficie | Estado actual |
|---|---|
| Autenticacion DRF | `SessionAuthentication` y `BasicAuthentication`. |
| Permisos DRF | `AllowAny` por defecto en settings. |
| Archivos cargados | Guardados en filesystem del servidor. |
| Base prepagada | Ruta configurable por entorno. |
| Admin Django | Disponible en `/admin/`. |

Recomendaciones de arquitectura:

- Cambiar permisos por defecto a autenticacion obligatoria si SIGA queda expuesto fuera de red controlada.
- Limitar tamano de subida en proxy/webserver.
- Validar extension y MIME de archivos cargados si se requiere hardening.
- Proteger `storage/landing` y `prepagada.db` con backups y permisos de sistema.

## 10. Observabilidad

| Mecanismo | Uso |
|---|---|
| Estado `ArchivoRecibido` | Trazabilidad de carga y procesamiento. |
| Contadores de archivo | Total, procesados y errores. |
| `ErrorProcesamiento` | Diagnostico por fila de origen. |
| Dashboard API | Resumen ejecutivo de estado de datos. |
| Planillas persistidas | Historial de calculos realizados por periodo. |

## 11. Decisiones arquitectonicas relevantes

| Decision | Justificacion | Consecuencia |
|---|---|---|
| Adaptador por proveedor | Aisla formatos distintos de Excel. | Nuevos proveedores requieren nuevo adaptador. |
| Esquema unificado `BeneficioSalud` | Permite consultas y reportes multi-proveedor. | Puede requerir campos opcionales vacios segun proveedor. |
| Errores como entidad persistente | Facilita auditoria y correccion operativa. | Aumenta volumen de datos por carga. |
| `prepagada.db` separado | Permite consumir cruce/Kactus sin acoplarlo a tablas Django. | Requiere disponibilidad y versionado de esa base externa. |
| Exportacion bajo demanda | Evita almacenar archivos derivados innecesarios. | Exportaciones grandes consumen memoria durante el request. |
| Bulk insert | Mejora rendimiento en cargas masivas. | Validaciones deben ejecutarse antes de persistir. |

## 12. Puntos de extension

| Necesidad | Lugar de cambio |
|---|---|
| Nuevo proveedor | Crear adaptador en `services/`, ampliar `detector.py` y `UploadView`. |
| Nuevas reglas de validacion | `services/validator.py`. |
| Nuevos campos de beneficio | `models.py`, migracion, serializers, adaptadores y exportacion. |
| Nueva politica de elegibilidad | `services/eligibility.py`. |
| Nueva fuente Kactus | `services/prepagada_service.py`. |
| Nuevos reportes | Agregar vista DRF y ruta en `urls.py`. |

## 13. Riesgos y consideraciones

| Riesgo | Impacto |
|---|---|
| Cambio de plantilla Excel | Puede romper deteccion de encabezados o mapeo de columnas. |
| `AllowAny` en API | Riesgo si el servicio se publica sin control perimetral. |
| `prepagada.db` faltante | Endpoints de cruce y planilla fallan con 503. |
| Reprocesamiento de archivo duplicado | El hash se almacena, pero no hay rechazo automatico implementado. |
| Excel muy grande | Exportacion/carga puede consumir memoria por uso de pandas/openpyxl en request. |
| Datos sensibles | Cedulas, nombres y valores requieren proteccion de acceso y backup seguro. |

