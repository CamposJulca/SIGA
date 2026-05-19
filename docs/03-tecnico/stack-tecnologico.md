# Stack Tecnológico

| Campo        | Valor                                                            |
|--------------|-------------------------------------------------------------------|
| Versión      | 1.0                                                               |
| Fecha        | 2026-05-13                                                        |
| Fuente       | Documentación Técnica §1–§4, §13                                   |
| Responsable  | Líder técnico SIGA                                                |
| Estado       | Borrador                                                          |

---

## 1. Resumen

SIGA es un backend **Django 4.2 + Django REST Framework**. Expone el módulo `beneficios_salud` con la API REST bajo `/api/beneficios-salud/`. Puede operar con **SQLite** para desarrollo o **PostgreSQL** mediante variables de entorno. Se ejecuta con **Gunicorn** en contenedor Docker.

## 2. Capas y dependencias

| Capa                       | Tecnología                       |
|----------------------------|----------------------------------|
| Lenguaje                    | Python 3.11                       |
| Framework backend           | Django 4.2.11                     |
| API REST                    | Django REST Framework 3.15.1     |
| Procesamiento Excel         | pandas 2.2.1, openpyxl 3.1.2, xlrd 2.0.1 |
| Servidor WSGI                | gunicorn 21.2.0                   |
| Base de datos               | SQLite (dev) o PostgreSQL         |
| Driver PostgreSQL           | psycopg2-binary 2.9.9             |
| Configuración por entorno   | python-dotenv 1.0.1               |
| Base externa prepagada      | SQLite (`PREPAGADA_DB_PATH`)       |

## 3. Variables de entorno

| Variable             | Default                    | Uso                                                            |
|----------------------|----------------------------|----------------------------------------------------------------|
| `SECRET_KEY`         | Valor dev inseguro          | Clave secreta Django. Debe ser único y secreto en prod.        |
| `DEBUG`              | `1`                          | Activa/desactiva modo debug. En prod **debe ser** `0`.         |
| `DATABASE_URL`       | (vacío)                      | URL PostgreSQL completa.                                       |
| `DB_ENGINE`           | (vacío)                      | Si es `postgresql`, fuerza configuración PostgreSQL.            |
| `DB_HOST`            | (vacío)                      | Host PostgreSQL; si está presente, fuerza configuración PostgreSQL. |
| `DB_NAME`            | `siga`                       | Nombre de la base PostgreSQL.                                  |
| `DB_USER`            | `siga`                       | Usuario PostgreSQL.                                            |
| `DB_PASSWORD`        | (vacío)                      | Password PostgreSQL.                                           |
| `DB_PORT`            | `5432`                       | Puerto PostgreSQL.                                             |
| `PREPAGADA_DB_PATH`  | `backend/db/prepagada.db`    | Ruta del SQLite externo de prepagada.                          |

> ⚠️ PENDIENTE: política de gestión de secretos en producción (vault / sealed secrets / variables de entorno cifradas) no documentada en las fuentes.

## 4. Rutas de almacenamiento

| Configuración             | Valor                                |
|---------------------------|--------------------------------------|
| `MEDIA_ROOT`              | `siga/storage/landing`                |
| `MEDIA_URL`               | `/media/`                             |
| SQLite dev                | `siga/backend/db/db.sqlite3`           |
| Base externa prepagada    | `PREPAGADA_DB_PATH`                    |

## 5. Estructura del proyecto

```text
siga/
├── backend/
│   ├── core/                # settings.py, urls.py, wsgi.py
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

## 6. Imagen Docker

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY backend/ .
RUN mkdir -p /app/db
EXPOSE 8000
CMD ["gunicorn", "core.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "2"]
```

## 7. Docker Compose

| Aspecto              | Valor                                |
|----------------------|--------------------------------------|
| Servicio             | `siga`                               |
| Puerto host          | 9010                                 |
| Puerto contenedor    | 8000                                 |
| Volumen archivos     | `./storage:/app/../storage`          |
| Volumen BD            | `siga_db:/app/db`                    |
| `PREPAGADA_DB_PATH`  | `/app/db/prepagada.db`                |

## 8. Versionado y mantenimiento

> ⚠️ PENDIENTE: estrategia explícita de upgrade de dependencias, política de seguridad de paquetes (Dependabot/Renovate), y branch policy del repo de SIGA no figuran en las fuentes.

---

**Fuente:** `siga/DOCUMENTACION_TECNICA.md` (§1 Resumen técnico, §2 Stack, §3 Estructura, §4 Configuración, §13 Despliegue).
