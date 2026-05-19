# Levantar Ambiente Local

| Campo        | Valor                                                |
|--------------|-------------------------------------------------------|
| Versión      | 1.0                                                   |
| Fecha        | 2026-05-13                                            |
| Fuente       | README de SIGA; Documentación Técnica §4, §13          |
| Responsable  | Líder técnico SIGA                                    |
| Estado       | Borrador                                              |

---

## 1. Requisitos

| Requisito          | Valor                                                                  |
|--------------------|--------------------------------------------------------------------------|
| Python              | 3.11                                                                    |
| Docker / Compose     | Requerido para el modo contenedor                                      |
| Acceso al repo SIGA  | `PENDIENTE` — URL y permisos                                            |
| Acceso a `prepagada.db` | Necesario para probar endpoints de cruce/planilla. `PENDIENTE` cómo obtenerlo. |

## 2. Opción A — Docker Compose

```bash
cd ~/Finagro/siga
docker compose up --build -d

# Migraciones
docker compose exec siga python manage.py migrate

# Superusuario (opcional, para /admin/)
docker compose exec siga python manage.py createsuperuser
```

Verificar:

```bash
curl http://localhost:9010/api/beneficios-salud/archivos/
```

## 3. Opción B — Local sin Docker

```bash
cd ~/Finagro/siga/backend
pip install -r requirements.txt
mkdir -p db
python manage.py migrate
python manage.py runserver 0.0.0.0:9010
```

## 4. Variables de entorno

Configurar `.env` o variables del sistema según [`../03-tecnico/stack-tecnologico.md`](../03-tecnico/stack-tecnologico.md) §3. Para desarrollo bastan los defaults (SQLite + `DEBUG=1`).

## 5. Prueba de carga

```bash
curl -X POST http://localhost:9010/api/beneficios-salud/upload/ \
  -F "archivo=@/ruta/al/archivo_AXACOLPATRIA_202401.xlsx" \
  -F "usuario=operador1"
```

Respuesta esperada:

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

## 6. `prepagada.db` mínima para pruebas

Para probar `/cruce/` y `/planilla/calcular/`, el backend espera que `PREPAGADA_DB_PATH` apunte a un SQLite con (al menos):

- Tabla `facturas_eps`.
- Tabla `empleados_kactus`.
- Vista `v_cruce` con las columnas listadas en [`../03-tecnico/modelo-de-datos.md`](../03-tecnico/modelo-de-datos.md) §4.

> ⚠️ PENDIENTE: el equipo SIGA debe publicar fixtures o un script de generación de `prepagada.db` para desarrollo.

## 7. Acceso al admin

- URL: `http://localhost:9010/admin/`
- Credenciales: las del superusuario creado con `createsuperuser`.

## 8. Comandos útiles

| Acción                        | Comando                                                                       |
|--------------------------------|--------------------------------------------------------------------------------|
| Ver logs (Docker)              | `docker compose logs -f siga`                                                  |
| Abrir shell Python              | `python manage.py shell`                                                       |
| Crear migración                  | `python manage.py makemigrations beneficios_salud`                              |
| Aplicar migraciones              | `python manage.py migrate`                                                     |
| Listar migraciones              | `python manage.py showmigrations`                                              |
| Reiniciar contenedor             | `docker compose restart siga`                                                  |

---

**Fuente:** `siga/README.md`, `siga/DOCUMENTACION_TECNICA.md` (§4 Configuración, §13 Despliegue).
