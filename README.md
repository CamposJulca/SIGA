# SIGA — Sistema Inteligente de Gestión Administrativa

Backend Django + DRF para procesar archivos Excel de proveedores de salud (AXA Colpatria y Colsanitas).

## Estructura del proyecto

```
siga/
├── backend/                    # Código Django
│   ├── core/                   # Configuración del proyecto
│   ├── modules/
│   │   └── beneficios_salud/   # App principal
│   │       └── services/       # Lógica de negocio
│   ├── manage.py
│   └── requirements.txt
├── storage/
│   └── landing/
│       ├── axa_colpatria/      # Archivos AXA recibidos
│       └── colsanitas/         # Archivos Colsanitas recibidos
├── docker/
│   └── Dockerfile
└── docker-compose.yml
```

## Endpoints REST

| Método | URL | Descripción |
|--------|-----|-------------|
| POST | `/api/beneficios-salud/upload/` | Carga y procesa un archivo Excel |
| GET | `/api/beneficios-salud/archivos/` | Lista archivos recibidos |
| GET | `/api/beneficios-salud/archivos/{id}/` | Detalle de archivo con errores |
| GET | `/api/beneficios-salud/beneficios/` | Lista beneficios (filtros: archivo_id, proveedor, cedula) |

## Levantamiento con Docker

```bash
cd /home/desarrollo/Finagro/siga
docker compose up --build -d

# Migraciones
docker compose exec siga python manage.py migrate

# Crear superusuario (opcional)
docker compose exec siga python manage.py createsuperuser
```

## Levantamiento local (desarrollo)

```bash
cd /home/desarrollo/Finagro/siga/backend
pip install -r requirements.txt
mkdir -p db
python manage.py migrate
python manage.py runserver 0.0.0.0:9010
```

## Uso del endpoint de carga

```bash
curl -X POST http://localhost:9010/api/beneficios-salud/upload/ \
  -F "archivo=@/ruta/al/archivo_AXACOLPATRIA_202401.xlsx" \
  -F "usuario=operador1"
```

Respuesta exitosa:
```json
{
  "archivo_id": 1,
  "proveedor": "axa",
  "total_registros": 150,
  "registros_procesados": 148,
  "registros_con_error": 2,
  "estado": "PROCESADO"
}
```

## Proveedores soportados

- **AXA Colpatria**: archivos `.xlsx` con columnas `SUB CTO`, `NUMID`, `NOMBRE`, `PARENTESCO`, `SUBTOTAL`, `IVA`, `TOTAL`.
- **Colsanitas**: archivos `.xls`/`.xlsx` con columnas `Número de Familia`, `Número de Documento`, `Apellidos`, `Nombres`, `Cuota`, `Descuento Comercial`, `IVA`, `Total Us`.

La detección del proveedor se realiza automáticamente por el nombre del archivo (debe contener `AXA` o `COLSANITAS`).

## Variables de entorno

| Variable | Default | Descripción |
|----------|---------|-------------|
| `SECRET_KEY` | valor dev inseguro | Clave secreta Django |
| `DEBUG` | `1` | Modo debug |
| `DATABASE_URL` | — | URL completa de PostgreSQL |
| `DB_HOST` | — | Host de PostgreSQL |
| `DB_NAME` | `siga` | Nombre de la base de datos |
| `DB_USER` | `siga` | Usuario de BD |
| `DB_PASSWORD` | — | Contraseña de BD |
| `DB_PORT` | `5432` | Puerto de BD |

Sin variables de BD configuradas, usa SQLite en `backend/db/db.sqlite3`.
# SIGA
