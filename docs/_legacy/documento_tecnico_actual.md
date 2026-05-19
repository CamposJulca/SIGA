# SIGA — Documento Técnico Actual

> Módulo: Beneficios de Salud
> Versión: Producción — Marzo 2026
> Entorno: Docker Compose integrado en automation-hub-finagro

---

## 1. Stack tecnológico

| Componente | Tecnología | Versión |
|-----------|-----------|---------|
| Framework backend | Django | 4.2 |
| API REST | Django REST Framework | 3.x |
| Lenguaje | Python | 3.11 |
| Base de datos | SQLite 3 (producción actual) | — |
| ETL / DataFrames | Pandas | 2.x |
| Lectura .xlsx | openpyxl | 3.x |
| Lectura .xls | xlrd | 2.x |
| Escritura Excel | openpyxl | 3.x |
| Servidor WSGI | Gunicorn | — |
| Proxy inverso | Nginx | — |
| Contenedores | Docker + Docker Compose | — |

---

## 2. Estructura de directorios

```
siga/
├── backend/
│   ├── core/
│   │   ├── settings.py          # Config Django (BD, MEDIA_ROOT, DRF)
│   │   ├── urls.py              # URLconf raíz → /api/beneficios-salud/
│   │   └── wsgi.py
│   ├── modules/
│   │   └── beneficios_salud/
│   │       ├── models.py        # ArchivoRecibido, BeneficioSalud, ErrorProcesamiento
│   │       ├── serializers.py   # DRF serializers (list, detail, beneficio)
│   │       ├── views.py         # 7 APIViews
│   │       ├── urls.py          # 7 rutas
│   │       ├── admin.py         # Registro Django Admin
│   │       ├── migrations/      # Migraciones Django
│   │       └── services/
│   │           ├── detector.py          # Detección de proveedor
│   │           ├── reader_excel.py      # Lectura de Excel con detección de header
│   │           ├── axa_adapter.py       # Transformación datos AXA
│   │           ├── colsanitas_adapter.py # Transformación datos Colsanitas
│   │           └── validator.py         # Validación de integridad
│   └── manage.py
├── storage/
│   └── landing/
│       ├── axa_colpatria/       # Archivos AXA guardados
│       ├── colsanitas/          # Archivos Colsanitas guardados
│       └── desconocido/
├── docker/
│   └── Dockerfile               # Python 3.11-slim, gunicorn, migrate, collectstatic
└── docs/
    ├── arquitectura_actual.md
    ├── documento_funcional_actual.md
    └── documento_tecnico_actual.md  ← este archivo
```

---

## 3. Configuración Django (`core/settings.py`)

### Base de datos
La BD se configura por prioridad mediante variables de entorno:

1. `DATABASE_URL` (postgres://...) → PostgreSQL vía URL
2. `DB_ENGINE=postgresql` o `DB_HOST` → PostgreSQL con variables individuales
3. Default → SQLite en `backend/db/db.sqlite3`

En producción actual se usa SQLite montado en el volumen Docker `siga_db`.

### Storage
```python
MEDIA_ROOT = BASE_DIR.parent / 'storage' / 'landing'
```
El volumen Docker `siga_landing` monta `/storage/landing` en el contenedor.

### DRF
- `AllowAny` — sin autenticación obligatoria (confiado en que el acceso ya está controlado por Nginx/portal)
- Parsers: JSON, MultiPart, Form

---

## 4. Modelos de datos

### `ArchivoRecibido` (tabla: `bs_archivos_recibidos`)

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `proveedor` | CharField(50) | `axa` \| `colsanitas` \| `desconocido` |
| `nombre_archivo` | CharField(300) | Nombre original del archivo subido |
| `ruta_archivo` | CharField(500) | Ruta absoluta en disco |
| `fecha_recepcion` | DateTimeField | Auto-set al crear |
| `estado_procesamiento` | CharField(20) | `RECIBIDO` → `PROCESANDO` → `PROCESADO` \| `ERROR` |
| `hash_archivo` | CharField(64) | SHA256 del archivo para trazabilidad |
| `usuario_carga` | CharField(150) | Usuario autenticado o 'anonimo' |
| `total_registros` | IntegerField | Filas en df_unificado (después de filtrar totales/vacíos) |
| `registros_procesados` | IntegerField | `len(registros_ok)` — registros insertados en BD |
| `registros_con_error` | IntegerField | `total_registros - registros_procesados` (rechazados fatales) |
| `numero_contrato` | CharField(50) | Extraído de metadatos del Excel |
| `periodo_facturacion` | CharField(50) | Extraído de metadatos del Excel |

### `BeneficioSalud` (tabla: `bs_beneficios_salud`)

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `archivo` | FK → ArchivoRecibido | `CASCADE` |
| `cedula` | CharField(20) | Cédula del afiliado (titular o beneficiario) |
| `tipo_id` | CharField(5) | Tipo de documento (CC, CE, etc.) |
| `nombre` | CharField(200) | Nombre completo |
| `parentesco` | CharField(5) | T, CO, HI, P, OT |
| `sub_contrato` | CharField(20) | Número de familia/grupo |
| `cedula_titular` | CharField(20) | Cédula del titular del contrato |
| `proveedor` | CharField(50) | `axa` \| `colsanitas` |
| `tipo_plan` | CharField(100) | Plan de cobertura |
| `valor_base` | Decimal(14,2) | Cuota base del plan |
| `descuento` | Decimal(14,2) | Descuento (puede ser negativo en Colsanitas) |
| `iva` | Decimal(14,2) | IVA aplicado |
| `valor_total` | Decimal(14,2) | Total a pagar (valor_base - descuento + iva) |
| `fecha_nacimiento` | CharField(20) | Fecha en formato del proveedor |
| `edad` | IntegerField(null) | Edad en años |
| `fecha_corte` | DateField(null) | Fecha de corte del período |
| `numero_contrato` | CharField(50) | Número de contrato |
| `archivo_origen` | CharField(300) | Nombre del archivo fuente |
| `fecha_procesamiento` | DateTimeField | Auto-set al crear |
| `estado_validacion` | CharField(20) | `OK` \| `ADVERTENCIA` |

### `ErrorProcesamiento` (tabla: `bs_errores_procesamiento`)

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `archivo` | FK → ArchivoRecibido | `CASCADE` |
| `fila_origen` | IntegerField | Número de fila (1-based) en el archivo fuente |
| `tipo_error` | CharField(50) | `CEDULA_INVALIDA` \| `VALOR_INVALIDO` \| `CEDULA_DUPLICADA` |
| `descripcion` | TextField | Mensaje descriptivo del error |
| `valor_encontrado` | CharField(200) | Valor que disparó el error |
| `timestamp` | DateTimeField | Auto-set al crear |

---

## 5. API REST

Base URL (desde el navegador): `/siga-api/beneficios-salud/`
Base URL (interno Docker): `http://siga:8000/api/beneficios-salud/`

### `POST /upload/`
- **Parser:** MultiPartParser, FormParser
- **Body:** `archivo` (file), `usuario` (str, opcional)
- **Proceso:** detector → reader → adapter → validator → bulk_create
- **Respuesta 201:**
  ```json
  {
    "archivo_id": 3,
    "proveedor": "axa",
    "total_registros": 24,
    "registros_procesados": 24,
    "registros_con_error": 0,
    "estado": "PROCESADO"
  }
  ```
- **Respuesta 422:** `{"error": "...", "archivo_id": N, "estado": "ERROR"}`

### `GET /archivos/`
- **Query params:** `proveedor`, `estado`
- **Respuesta:** Lista de `ArchivoRecibidoListSerializer`

### `GET /archivos/{id}/`
- **Respuesta:** `ArchivoRecibidoDetailSerializer` con errores anidados

### `GET /beneficios/`
- **Query params:** `archivo_id`, `proveedor`, `cedula`, `estado_validacion`
- **Respuesta:** Lista de `BeneficioSaludSerializer`

### `GET /exportar/`
- **Query params:** `archivo_id` (opcional)
- **Sin archivo_id:** exporta el último archivo `PROCESADO` de cada proveedor
- **Respuesta:** `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet`
- **Filename:** `SIGA_Beneficios_YYYYMMDD.xlsx`
- **Hojas:** Consolidado, AXA Colpatria, Colsanitas

### `GET /novedades/`
- **Query params requeridos:** `archivo_nuevo`, `archivo_anterior` (IDs de ArchivoRecibido)
- **Respuesta:**
  ```json
  {
    "archivo_nuevo": {...},
    "archivo_anterior": {...},
    "resumen": {"nuevos": N, "retirados": N, "cambios_valor": N, "sin_cambios": N},
    "nuevos": [...],
    "retirados": [...],
    "cambios_valor": [{"cedula": "...", "valor_anterior": X, "valor_nuevo": Y, "diferencia": Z}]
  }
  ```

### `GET /dashboard/`
- **Respuesta:**
  ```json
  {
    "ultimos_periodos": [...],        // último archivo procesado por proveedor
    "distribucion_parentesco": [...], // count + valor_total por tipo T/CO/HI/P/OT
    "distribucion_proveedor": [...],  // count + valor_total por proveedor
    "evolucion": [...],               // histórico por archivo procesado
    "consolidado": {
      "total_archivos_procesados": N,
      "beneficiarios_ultimo_periodo": N,
      "valor_total_ultimo_periodo": N,
      "proveedores_activos": N
    }
  }
  ```

---

## 6. Pipeline ETL — detalle técnico

### 6.1 `detector.py`

```
detectar_proveedor(nombre_archivo, columnas=None) → 'axa' | 'colsanitas' | 'desconocido'
```

Prioridad:
1. Nombre del archivo (`nombre_upper.contains('AXA')` → axa, `'COLSANITAS'` → colsanitas)
2. Fallback por columnas: `{'SUB CTO', 'NUMID'} ⊂ columnas` → axa; `'Número de Familia' ∈ columnas` → colsanitas

### 6.2 `reader_excel.py`

- **AXA:** `openpyxl`, busca fila con `NUMID` o `SUB CTO` en rows 0-15
- **Colsanitas:** `xlrd` para `.xls`, `openpyxl` para `.xlsx`; busca fila con `NÚMERO DE DOCUMENTO` o `APELLIDOS` en rows 0-20
- En ambos casos intenta extraer `numero_contrato` y `periodo_facturacion` de las filas previas al encabezado buscando keywords (`CONTRATO`, `PERIODO`, `MES`, etc.)

### 6.3 `axa_adapter.py`

Mapeo de columnas AXA → modelo unificado:

| Columna AXA | Campo unificado | Nota |
|------------|----------------|------|
| `SUB CTO` | `sub_contrato` | |
| `NUMID` | `cedula_titular` | Cédula del titular del contrato, NO del afiliado |
| `NUMERO ID.BEN` | `cedula` | Cédula real del afiliado |
| `NOMBRE` | `nombre` | |
| `PARENTESCO` | `parentesco` | |
| `SUBTOTAL` | `valor_base` | |
| `IVA` | `iva` | |
| `TOTAL` | `valor_total` | |

Campos fijos: `descuento=0`, `proveedor='axa'`. Filtro: elimina filas con `cedula` vacía o NaN.

### 6.4 `colsanitas_adapter.py`

Filtro previo: elimina filas donde la primera columna contiene `TOTAL FAMILIA`, `TOTAL CONTRATO`, `TOTAL GENERAL`, `SUBTOTAL`, `GRAN TOTAL`.

Mapeo de columnas Colsanitas → modelo unificado:

| Columna Colsanitas | Campo unificado | Nota |
|-------------------|----------------|------|
| `Número de Familia` | `sub_contrato` | |
| `Número de Documento` | `cedula` | |
| `Apellidos` + `Nombres` | `nombre` | Concatenados con espacio |
| `Cuota` | `valor_base` | |
| `Descuento Comercial` | `descuento` | Puede ser negativo |
| `IVA` | `iva` | |
| `Total Us` o `Total` | `valor_total` | Intenta `Total Us` primero |

Búsqueda de columnas case-insensitive via helper `_get_col`.

### 6.5 `validator.py`

Recibe `df_unificado` y `archivo_id`. Retorna `(registros_ok, errores)`.

**Pre-proceso:** Detecta duplicados por clave compuesta `cedula + '_' + sub_contrato` (misma cédula en distinto sub_contrato es válida — titular con cobertura en varios grupos familiares).

**Por cada fila:**

1. **CEDULA_INVALIDA** → `cedula` vacía o `'nan'` → rechaza fila
2. **Conversión numérica** → intenta `float()` en `valor_base`, `iva`, `valor_total`, `descuento` → `VALOR_INVALIDO` si falla → rechaza fila
3. **Detección fila ajuste** → `valor_base == 0 AND valor_total < 0` → marca `es_fila_ajuste=True` (no rechaza)
4. **Valores negativos** → solo en `CAMPOS_SOLO_POSITIVOS = {'valor_base', 'iva', 'valor_total'}` y solo si `not es_fila_ajuste` → `VALOR_INVALIDO` → rechaza fila
5. **Verificación aritmética** → `|valor_total - (valor_base - descuento + iva)| > 1.0` → `estado='ADVERTENCIA'`
6. **Duplicado** → si `idx in indices_duplicados` → `estado='ADVERTENCIA'` + crea `ErrorProcesamiento(CEDULA_DUPLICADA)`

Los registros que pasan todas las validaciones fatales se insertan con `estado='OK'` o `'ADVERTENCIA'`.

---

## 7. Exportación Excel

`ExportarExcelView` usa `openpyxl` para generar el `.xlsx` en memoria (`BytesIO`):

- **Encabezado:** fondo verde `#00853F`, texto blanco bold
- **Registros ADVERTENCIA:** fondo amarillo claro `#FFFDE7`
- **Hojas:** Consolidado (todas las filas + columna `archivo_origen`), AXA Colpatria, Colsanitas
- **Sin archivo_id:** toma el `MAX(id)` por proveedor entre archivos `PROCESADO`

---

## 8. Docker

### Servicio en `docker-compose.prod.yml`

```yaml
siga:
  build:
    context: ../siga
    dockerfile: docker/Dockerfile
  volumes:
    - siga_db:/app/db
    - siga_landing:/storage/landing
  networks:
    - finagro-net
  restart: unless-stopped
```

Sin puerto expuesto al host. Accesible únicamente vía Nginx en la red interna `finagro-net`.

### Proxy Nginx (`nginx.prod.conf`, server block port 9000)

```nginx
location /siga-api/ {
    proxy_pass         http://siga:8000/api/;
    proxy_read_timeout 120s;
    client_max_body_size 50M;
}
```

`client_max_body_size 50M` permite subir archivos Excel grandes.

### Comandos de gestión

```bash
# Reconstruir y forzar recreación (requerido para cambios de código)
docker compose -f docker-compose.prod.yml up --build --force-recreate -d siga

# Crear/aplicar migraciones (necesario al cambiar models.py)
docker compose -f docker-compose.prod.yml exec siga python manage.py makemigrations beneficios_salud
docker compose -f docker-compose.prod.yml exec siga python manage.py migrate

# Ver logs
docker compose -f docker-compose.prod.yml logs -f siga

# Shell Django
docker compose -f docker-compose.prod.yml exec siga python manage.py shell
```

> **Importante:** `docker compose restart siga` NO aplica cambios de código. Siempre usar `--build --force-recreate`.

---

## 9. Volúmenes Docker

| Volumen | Ruta en contenedor | Contenido |
|---------|-------------------|-----------|
| `siga_db` | `/app/db/` | `db.sqlite3` — base de datos SQLite |
| `siga_landing` | `/storage/landing/` | Archivos Excel recibidos, organizados por proveedor |

---

## 10. Variables de entorno

| Variable | Default | Descripción |
|----------|---------|-------------|
| `SECRET_KEY` | insegura (dev) | Clave secreta Django |
| `DEBUG` | `1` | `0` en producción |
| `DATABASE_URL` | — | URL completa PostgreSQL (opcional) |
| `DB_ENGINE` | — | `postgresql` para activar Postgres |
| `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT` | — | Parámetros PostgreSQL individuales |

Si ninguna variable de BD está definida, usa SQLite en `backend/db/db.sqlite3`.

---

## 11. Migraciones

Las tablas se crean via Django migrations. El `Dockerfile` NO ejecuta `migrate` automáticamente al arrancar — se debe ejecutar manualmente después de cada recreación del contenedor cuando hay cambios en modelos.

Tablas creadas:
- `bs_archivos_recibidos`
- `bs_beneficios_salud`
- `bs_errores_procesamiento`

---

## 12. Consideraciones de escala

- **SQLite → PostgreSQL:** El settings.py ya soporta PostgreSQL mediante variables de entorno. Para migrar: setear `DATABASE_URL` o `DB_*` variables y ejecutar `migrate`.
- **Archivos grandes:** El timeout de Nginx está en 120s y el límite de tamaño en 50MB. Para archivos mayores, aumentar `proxy_read_timeout` y `client_max_body_size`.
- **Concurrencia:** SQLite tiene limitaciones de escritura concurrente. Para múltiples usuarios simultáneos cargando archivos, migrar a PostgreSQL.
