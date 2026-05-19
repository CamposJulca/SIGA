# SIGA - Documentacion Tecnica

## 1. Resumen tecnico

SIGA es un backend Django 4.2 con Django REST Framework. Expone el modulo `beneficios_salud`, que implementa procesamiento ETL de archivos Excel de proveedores de salud y calculo de medicina prepagada. Puede operar con SQLite para desarrollo o PostgreSQL mediante variables de entorno.

La aplicacion se ejecuta con Gunicorn y expone su API bajo:

```text
/api/beneficios-salud/
```

## 2. Stack y dependencias

| Capa | Tecnologia |
|---|---|
| Backend | Python 3.11, Django 4.2.11 |
| API | Django REST Framework 3.15.1 |
| Procesamiento Excel | pandas 2.2.1, openpyxl 3.1.2, xlrd 2.0.1 |
| Servidor WSGI | gunicorn 21.2.0 |
| Base de datos | SQLite o PostgreSQL |
| Driver PostgreSQL | psycopg2-binary 2.9.9 |
| Configuracion | python-dotenv 1.0.1 |
| Base externa prepagada | SQLite en `PREPAGADA_DB_PATH` |

## 3. Estructura del proyecto

```text
siga/
├── backend/
│   ├── core/
│   │   ├── settings.py
│   │   ├── urls.py
│   │   └── wsgi.py
│   ├── modules/
│   │   └── beneficios_salud/
│   │       ├── admin.py
│   │       ├── models.py
│   │       ├── serializers.py
│   │       ├── urls.py
│   │       ├── views.py
│   │       ├── migrations/
│   │       └── services/
│   │           ├── axa_adapter.py
│   │           ├── colsanitas_adapter.py
│   │           ├── detector.py
│   │           ├── eligibility.py
│   │           ├── prepagada_service.py
│   │           ├── reader_excel.py
│   │           └── validator.py
│   ├── db/
│   ├── manage.py
│   └── requirements.txt
├── docker/
│   └── Dockerfile
├── docker-compose.yml
└── storage/
    └── landing/
```

## 4. Configuracion

### 4.1 Variables de entorno

| Variable | Default | Uso |
|---|---|---|
| `SECRET_KEY` | Valor dev inseguro | Clave secreta Django. |
| `DEBUG` | `1` | Activa/desactiva modo debug. |
| `DATABASE_URL` | Vacio | URL PostgreSQL completa. |
| `DB_ENGINE` | Vacio | Si es `postgresql`, usa PostgreSQL. |
| `DB_HOST` | Vacio | Host PostgreSQL; si existe, fuerza configuracion PostgreSQL. |
| `DB_NAME` | `siga` | Nombre base PostgreSQL. |
| `DB_USER` | `siga` | Usuario PostgreSQL. |
| `DB_PASSWORD` | Vacio | Password PostgreSQL. |
| `DB_PORT` | `5432` | Puerto PostgreSQL. |
| `PREPAGADA_DB_PATH` | `backend/db/prepagada.db` | Ruta de la base SQLite externa de prepagada. |

### 4.2 Rutas de almacenamiento

| Configuracion | Valor |
|---|---|
| `MEDIA_ROOT` | `siga/storage/landing` |
| `MEDIA_URL` | `/media/` |
| SQLite dev | `siga/backend/db/db.sqlite3` |
| Base externa prepagada | `PREPAGADA_DB_PATH` |

## 5. Modelo de datos

### 5.1 Tablas ETL

| Modelo | Tabla | Proposito |
|---|---|---|
| `ArchivoRecibido` | `bs_archivos_recibidos` | Control de archivos cargados, estado, hash, contrato, periodo y contadores. |
| `BeneficioSalud` | `bs_beneficios_salud` | Registros normalizados por beneficiario. |
| `ErrorProcesamiento` | `bs_errores_procesamiento` | Errores y advertencias por fila de origen. |

### 5.2 Tablas medicina prepagada

| Modelo | Tabla | Proposito |
|---|---|---|
| `PoliticaPrepagada` | `bs_politica_prepagada` | Parametros de calculo 80/20 y UVT. |
| `PensionadoPrepagada` | `bs_pensionados_prepagada` | Pensionados activos con pago 100%. |
| `AuxilioExterno` | `bs_auxilio_externo` | Auxilios externos activos para informe EFR. |
| `PlanillaCalculo` | `bs_planilla_calculo` | Cabecera de planilla calculada por periodo. |
| `DetalleCalculo` | `bs_detalle_calculo` | Resultado por cedula/EPS de la planilla. |

## 6. Pipeline ETL de archivos

### 6.1 Endpoint de entrada

```text
POST /api/beneficios-salud/upload/
Content-Type: multipart/form-data
Campos:
  archivo: Excel
  usuario: opcional
```

### 6.2 Secuencia tecnica

1. `_sha256_archivo(file_obj)` calcula SHA256.
2. `detectar_proveedor(nombre_archivo)` intenta proveedor por nombre.
3. `_guardar_archivo()` guarda el archivo en `MEDIA_ROOT/{proveedor}/`.
4. `ArchivoRecibido.objects.create()` registra estado `RECIBIDO`.
5. El estado cambia a `PROCESANDO`.
6. `leer_excel(ruta_archivo, proveedor)` retorna DataFrame y metadatos.
7. Si el proveedor era `desconocido`, se reintenta deteccion por columnas.
8. `adaptar_axa()` o `adaptar_colsanitas()` normaliza el DataFrame.
9. `validar_registros()` retorna `registros_ok` y `errores_val`.
10. `BeneficioSalud.objects.bulk_create()` inserta beneficios.
11. `ErrorProcesamiento.objects.bulk_create()` inserta errores/advertencias.
12. El archivo queda `PROCESADO` con contadores.

### 6.3 Deteccion de proveedor

Archivo: `services/detector.py`

| Estrategia | Regla |
|---|---|
| Nombre | `AXACOLPATRIA` o `AXA` => `axa`; `COLSANITAS` => `colsanitas`. |
| Columnas | `SUB CTO` y `NUMID` => `axa`; `Numero de Familia` => `colsanitas`. |
| Sin coincidencia | `desconocido`. |

### 6.4 Lectura Excel

Archivo: `services/reader_excel.py`

| Proveedor | Motor | Deteccion encabezado |
|---|---|---|
| AXA | `openpyxl` | Escanea hasta 16 filas buscando `NUMID` o `SUB CTO`. |
| Colsanitas `.xls` | `xlrd` | Escanea hasta 21 filas buscando `Numero de Documento` o `Apellidos`. |
| Colsanitas `.xlsx` | `openpyxl` | Misma deteccion por cabecera. |

Tambien intenta extraer:

- `numero_contrato`
- `periodo_facturacion`

desde filas anteriores al encabezado.

## 7. Adaptadores

### 7.1 AXA Colpatria

Archivo: `services/axa_adapter.py`

| Columna origen | Campo destino |
|---|---|
| `SUB CTO` | `sub_contrato` |
| `NUMID` | `cedula_titular` |
| `NUMERO ID.BEN` | `cedula` |
| `NOMBRE` | `nombre` |
| `PARENTESCO` | `parentesco` |
| `SUBTOTAL` | `valor_base` |
| `IVA` | `iva` |
| `TOTAL` | `valor_total` |

Valores generados:

- `descuento = 0`
- `proveedor = axa`
- `numero_contrato` desde metadatos

### 7.2 Colsanitas

Archivo: `services/colsanitas_adapter.py`

| Columna origen | Campo destino |
|---|---|
| `Numero de Familia` | `sub_contrato` |
| `Numero de Documento` | `cedula` |
| `Apellidos` + `Nombres` | `nombre` |
| `Cuota` | `valor_base` |
| `Descuento Comercial` | `descuento` |
| `IVA` | `iva` |
| `Total Us` o `Total` | `valor_total` |

Filas excluidas por palabra clave:

- `TOTAL FAMILIA`
- `TOTAL CONTRATO`
- `TOTAL GENERAL`
- `SUBTOTAL`
- `GRAN TOTAL`

## 8. Validacion

Archivo: `services/validator.py`

| Validacion | Resultado |
|---|---|
| Cedula vacia o `nan` | Error fatal `CEDULA_INVALIDA`; no inserta beneficio. |
| Campos monetarios no numericos | Error fatal `VALOR_INVALIDO`; no inserta beneficio. |
| `valor_base`, `iva`, `valor_total` negativos | Error fatal, salvo ajuste Colsanitas. |
| Ajuste `valor_base = 0` y `valor_total < 0` | Inserta con `ADVERTENCIA`. |
| Diferencia `abs(valor_total - (valor_base - descuento + iva)) > 1` | Inserta con `ADVERTENCIA`. |
| Duplicado por `cedula + sub_contrato` | Inserta con `ADVERTENCIA` y registra `CEDULA_DUPLICADA`. |

## 9. API REST

### 9.1 Beneficios de salud

| Metodo | Ruta | Vista | Descripcion |
|---|---|---|---|
| `POST` | `/api/beneficios-salud/upload/` | `UploadView` | Carga y procesa Excel. |
| `GET` | `/api/beneficios-salud/archivos/` | `ArchivoListView` | Lista archivos; filtros `proveedor`, `estado`. |
| `GET` | `/api/beneficios-salud/archivos/<id>/` | `ArchivoDetailView` | Detalle de archivo con errores. |
| `GET` | `/api/beneficios-salud/beneficios/` | `BeneficioListView` | Lista beneficios; filtros `archivo_id`, `proveedor`, `cedula`, `estado_validacion`. |
| `GET` | `/api/beneficios-salud/exportar/` | `ExportarExcelView` | Exporta beneficios en Excel. |
| `GET` | `/api/beneficios-salud/novedades/` | `NovedadesView` | Compara dos archivos. |
| `GET` | `/api/beneficios-salud/dashboard/` | `DashboardView` | Resumen ejecutivo. |

### 9.2 Medicina prepagada

| Metodo | Ruta | Vista | Descripcion |
|---|---|---|---|
| `GET` | `/api/beneficios-salud/cruce/` | `CruceView` | Lista periodos o cruce por periodo. |
| `GET`/`POST` | `/api/beneficios-salud/politica/` | `PoliticaView` | Lista o crea politica. |
| `GET`/`PUT` | `/api/beneficios-salud/politica/<id>/` | `PoliticaDetailView` | Consulta o actualiza politica. |
| `GET`/`POST` | `/api/beneficios-salud/pensionados/` | `PensionadosView` | Lista o crea pensionado. |
| `GET`/`PUT`/`DELETE` | `/api/beneficios-salud/pensionados/<id>/` | `PensionadoDetailView` | Administra pensionado. |
| `GET`/`POST` | `/api/beneficios-salud/auxilio-externo/` | `AuxilioExternoView` | Lista o crea auxilio externo. |
| `GET`/`PUT`/`DELETE` | `/api/beneficios-salud/auxilio-externo/<id>/` | `AuxilioExternoDetailView` | Administra auxilio externo. |
| `GET` | `/api/beneficios-salud/planilla/` | `PlanillaListView` | Lista planillas; filtro `periodo`. |
| `POST` | `/api/beneficios-salud/planilla/calcular/` | `PlanillaCalcularView` | Calcula planilla por periodo y politica opcional. |
| `GET` | `/api/beneficios-salud/planilla/<id>/` | `PlanillaDetailView` | Detalle con registros. |
| `GET` | `/api/beneficios-salud/planilla/<id>/exportar/` | `PlanillaExportarView` | Exporta planilla Excel. |
| `GET` | `/api/beneficios-salud/causacion/` | `CausacionView` | Resumen por EPS para periodo. |
| `GET` | `/api/beneficios-salud/conciliacion/` | `ConciliacionView` | Compara planillas de dos periodos. |
| `GET` | `/api/beneficios-salud/informe-efr/` | `InformeEFRView` | Informe mensual EFR. |

## 10. Servicio de prepagada

Archivo: `services/prepagada_service.py`

Base externa:

```text
PREPAGADA_DB_PATH -> SQLite
```

Objetos esperados en la base externa:

| Objeto | Uso |
|---|---|
| `facturas_eps` | Periodos disponibles y datos facturados. |
| `v_cruce` | Vista de cruce factura/Kactus por periodo. |
| `empleados_kactus` | Datos laborales para cruces auxiliares. |

Campos leidos desde `v_cruce`:

```text
periodo, eps, cedula, nombre_en_factura, nombre_en_kactus,
num_beneficiarios, total_familia, sub_cto, nro_cont,
sue_basi, tip_cont, estado, archivo
```

## 11. Elegibilidad y calculo

Archivo: `services/eligibility.py`

| Estado | Criterio | Calculo |
|---|---|---|
| `PENSIONADO_100` | Existe pensionado activo por cedula y EPS. | Empresa `0`; empleado `100%`. |
| `BLOQUEADO_CRUCE` | Estado de cruce distinto de `OK`. | Valores empresa/empleado en `0`; `valor_no_cubierto = total`. |
| `ELEGIBLE_80_20` | Cruce Kactus `OK` y no pensionado. | Aplica porcentajes de politica. |

Calculo empleado elegible:

```text
valor_empresa = total_familia * porcentaje_empresa / 100
valor_empleado = total_familia * porcentaje_empleado / 100
limite_no_gravable = uvt_limite * valor_uvt
apoyo_no_gravable = min(valor_empresa, limite_no_gravable)
apoyo_gravable = max(0, valor_empresa - limite_no_gravable)
```

## 12. Exportaciones

| Exportacion | Ruta | Hojas |
|---|---|---|
| Beneficios | `/api/beneficios-salud/exportar/` | `Consolidado`, `AXA Colpatria`, `Colsanitas`. |
| Planilla | `/api/beneficios-salud/planilla/<id>/exportar/` | `Planilla 80-20`, `Apoyo Gravable`. |

## 13. Despliegue

Dockerfile:

```text
FROM python:3.11-slim
WORKDIR /app
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY backend/ .
RUN mkdir -p /app/db
EXPOSE 8000
CMD ["gunicorn", "core.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "2"]
```

Docker Compose:

```text
Servicio: siga
Puerto host: 9010
Puerto contenedor: 8000
Volumen archivos: ./storage:/app/../storage
Volumen DB: siga_db:/app/db
PREPAGADA_DB_PATH=/app/db/prepagada.db
```

## 14. Consideraciones tecnicas

| Tema | Consideracion |
|---|---|
| Permisos DRF | Configuracion actual usa `AllowAny` por defecto. Si se publica fuera de red controlada, debe endurecerse. |
| Hash de archivo | Se calcula y almacena, pero el flujo actual no rechaza automaticamente duplicados por hash. |
| Bulk insert | Los registros se insertan en batch de 500 para reducir round-trips. |
| Trazabilidad | Los errores guardan fila de origen 1-based respecto al DataFrame normalizado. |
| Excel variable | La deteccion de encabezados reduce dependencia de formato exacto, pero nuevas plantillas pueden requerir ajustar adaptadores. |
| `prepagada.db` | Es dependencia runtime; si no existe o no tiene las tablas/vistas esperadas, los endpoints de cruce/planilla retornan error 503. |

