# Ambientes

| Campo        | Valor                                                                  |
|--------------|------------------------------------------------------------------------|
| Versión      | 1.0                                                                    |
| Fecha        | 2026-05-13                                                             |
| Fuente       | Documentación Técnica §4, §13                                           |
| Responsable  | DevOps / TI                                                            |
| Estado       | **Borrador — cobertura BAJA**, ver `gaps.md` Top 10 #4                  |

---

> ⚠️ PENDIENTE: las fuentes sólo describen el ambiente de **desarrollo** (Docker Compose local). Los ambientes de QA y Producción **no figuran** en los documentos consolidados. Esta sección queda como esqueleto.

## 1. Ambientes documentados

### 1.1 Desarrollo (local / Docker Compose)

| Aspecto                  | Valor                                              |
|--------------------------|----------------------------------------------------|
| Puerto host               | 9010                                                |
| Puerto contenedor         | 8000                                                |
| Servidor                  | Gunicorn, 2 workers                                  |
| Base de datos             | SQLite por defecto (`backend/db/db.sqlite3`)         |
| `prepagada.db`            | SQLite en `backend/db/prepagada.db`                   |
| `DEBUG`                   | `1`                                                  |
| Permisos DRF              | `AllowAny`                                            |
| Almacenamiento            | `./storage` montado en `/app/../storage`              |

### 1.2 QA

> ⚠️ PENDIENTE: no documentado. Definir host, base de datos, fuentes de datos de prueba, datos sintéticos vs producción enmascarada, ventana de mantenimiento.

### 1.3 Producción

> ⚠️ PENDIENTE: no documentado. Definir:
> - URL pública y proxy reverso (¿nginx/Apache/Caddy?).
> - Motor BD productivo (PostgreSQL recomendado por T1 §2/§4).
> - Fuente y frecuencia de actualización de `prepagada.db`.
> - Política de TLS, certificados y headers de seguridad.
> - Estrategia de logs, métricas y alertas (ver `monitoreo-y-alertas.md`).
> - Estrategia de backup (BD principal y `prepagada.db`).
> - Política de secrets (no usar `SECRET_KEY` por defecto, no `DEBUG=1`).

## 2. Matriz comparativa propuesta

| Dimensión               | Desarrollo (documentado)           | QA (`PENDIENTE`)     | Producción (`PENDIENTE`) |
|-------------------------|--------------------------------------|-----------------------|---------------------------|
| Hostname                | `localhost:9010`                     | `PENDIENTE`           | `PENDIENTE`               |
| BD                      | SQLite                                | `PENDIENTE`           | `PENDIENTE`               |
| Motor BD                | sqlite3                                | `PENDIENTE`           | PostgreSQL (esperado)     |
| `DEBUG`                  | `1`                                    | `PENDIENTE`           | `0`                        |
| Permisos DRF             | `AllowAny`                             | `PENDIENTE`           | Requiere autenticación (recomendación A1 §9) |
| `prepagada.db`           | Archivo local                          | `PENDIENTE`           | `PENDIENTE`               |
| Backups                  | Manual                                 | `PENDIENTE`           | `PENDIENTE`               |
| Logs                     | stdout/stderr                          | `PENDIENTE`           | `PENDIENTE`               |
| Métricas / Alertas        | Sin instrumentación documentada        | `PENDIENTE`           | `PENDIENTE`               |
| Estrategia despliegue    | `docker compose up --build`             | `PENDIENTE`           | `PENDIENTE`               |
| TLS / dominio            | N/A (HTTP)                             | `PENDIENTE`           | `PENDIENTE`               |

## 3. Promoción entre ambientes

> ⚠️ PENDIENTE: no documentado el proceso de promoción Dev → QA → Prod (CI/CD, aprobaciones, freeze, ventanas). Ver `gaps.md` Top 10 #4.

## 4. Variables de entorno por ambiente

Lista de variables disponibles en [`../03-tecnico/stack-tecnologico.md`](../03-tecnico/stack-tecnologico.md) §3. Los valores por ambiente deben definirse en el repositorio de secretos correspondiente.

| Variable             | Dev (default)               | QA (`PENDIENTE`) | Prod (`PENDIENTE`) |
|----------------------|------------------------------|-------------------|---------------------|
| `SECRET_KEY`         | Valor dev inseguro           | `PENDIENTE`       | `PENDIENTE`         |
| `DEBUG`              | `1`                          | `PENDIENTE`       | `0`                  |
| `DATABASE_URL`       | (vacío → SQLite)             | `PENDIENTE`       | `PENDIENTE`         |
| `DB_*`               | Vacíos                       | `PENDIENTE`       | `PENDIENTE`         |
| `PREPAGADA_DB_PATH`  | `backend/db/prepagada.db`    | `PENDIENTE`       | `PENDIENTE`         |

---

**Fuente:** `siga/DOCUMENTACION_TECNICA.md` (§4 Configuración, §13 Despliegue).
