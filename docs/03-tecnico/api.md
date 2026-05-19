# API REST

| Campo        | Valor                                                                   |
|--------------|--------------------------------------------------------------------------|
| Versión      | 1.0                                                                      |
| Fecha        | 2026-05-13                                                               |
| Fuente       | Documentación Técnica §9; Arquitectura §8                                 |
| Responsable  | Líder técnico SIGA                                                       |
| Estado       | Borrador                                                                 |

---

## 1. Base

```text
/api/beneficios-salud/
```

- **Framework:** Django REST Framework 3.15.1.
- **Autenticación configurada:** `SessionAuthentication`, `BasicAuthentication`.
- **Permisos por defecto:** `AllowAny` (ver advertencia en seguridad).
- **Formato de respuesta:** JSON, excepto endpoints `exportar/*` que retornan `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet` (Excel).

> ⚠️ PENDIENTE: contratos JSON detallados (request/response) por endpoint. Las fuentes sólo listan ruta, método y vista. Tampoco hay versionado del API (`/v1/`, etc.).

## 2. Beneficios de Salud

| Método  | Ruta                                                | Vista              | Descripción                                                   |
|---------|------------------------------------------------------|--------------------|----------------------------------------------------------------|
| POST    | `/api/beneficios-salud/upload/`                      | `UploadView`       | Carga y procesa Excel. Multipart con campo `archivo` (y `usuario` opcional). |
| GET     | `/api/beneficios-salud/archivos/`                    | `ArchivoListView`  | Lista archivos. Filtros: `proveedor`, `estado`.                  |
| GET     | `/api/beneficios-salud/archivos/<id>/`               | `ArchivoDetailView`| Detalle de archivo con errores.                                    |
| GET     | `/api/beneficios-salud/beneficios/`                  | `BeneficioListView`| Lista beneficios. Filtros: `archivo_id`, `proveedor`, `cedula`, `estado_validacion`. |
| GET     | `/api/beneficios-salud/exportar/`                    | `ExportarExcelView`| Exporta beneficios a Excel (`Consolidado`, `AXA Colpatria`, `Colsanitas`). |
| GET     | `/api/beneficios-salud/novedades/`                   | `NovedadesView`    | Compara dos archivos del mismo proveedor.                          |
| GET     | `/api/beneficios-salud/dashboard/`                   | `DashboardView`    | Resumen ejecutivo.                                                 |

### 2.1 `POST /upload/`

| Aspecto       | Detalle                                                          |
|---------------|-------------------------------------------------------------------|
| Content-Type  | `multipart/form-data`                                              |
| Campo `archivo` | Archivo Excel (`.xls` o `.xlsx`).                                  |
| Campo `usuario` | Opcional. Usado si no hay sesión autenticada.                       |
| Comportamiento | Detecta proveedor, persiste el archivo, ejecuta ETL y retorna resumen. |

Ejemplo (extraído de `README.md`):

```bash
curl -X POST http://localhost:9010/api/beneficios-salud/upload/ \
  -F "archivo=@/ruta/al/archivo_AXACOLPATRIA_202401.xlsx" \
  -F "usuario=operador1"
```

Respuesta documentada:

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

## 3. Medicina Prepagada

| Método              | Ruta                                                             | Vista                  | Descripción                                              |
|---------------------|-------------------------------------------------------------------|-------------------------|-----------------------------------------------------------|
| GET                 | `/api/beneficios-salud/cruce/`                                    | `CruceView`             | Lista periodos o cruce por periodo desde `v_cruce`.        |
| GET / POST          | `/api/beneficios-salud/politica/`                                 | `PoliticaView`          | Lista o crea política.                                     |
| GET / PUT           | `/api/beneficios-salud/politica/<id>/`                            | `PoliticaDetailView`    | Consulta o actualiza política.                              |
| GET / POST          | `/api/beneficios-salud/pensionados/`                              | `PensionadosView`       | Lista o crea pensionado.                                     |
| GET / PUT / DELETE  | `/api/beneficios-salud/pensionados/<id>/`                         | `PensionadoDetailView`  | Administra pensionado.                                       |
| GET / POST          | `/api/beneficios-salud/auxilio-externo/`                          | `AuxilioExternoView`    | Lista o crea auxilio externo.                                 |
| GET / PUT / DELETE  | `/api/beneficios-salud/auxilio-externo/<id>/`                     | `AuxilioExternoDetailView` | Administra auxilio externo.                                |
| GET                 | `/api/beneficios-salud/planilla/`                                 | `PlanillaListView`      | Lista planillas; filtro `periodo`.                            |
| POST                | `/api/beneficios-salud/planilla/calcular/`                        | `PlanillaCalcularView`  | Calcula planilla por periodo y política opcional.             |
| GET                 | `/api/beneficios-salud/planilla/<id>/`                            | `PlanillaDetailView`    | Detalle con registros.                                         |
| GET                 | `/api/beneficios-salud/planilla/<id>/exportar/`                   | `PlanillaExportarView`  | Exporta planilla a Excel.                                       |
| GET                 | `/api/beneficios-salud/causacion/`                                | `CausacionView`         | Resumen por EPS para periodo.                                  |
| GET                 | `/api/beneficios-salud/conciliacion/`                             | `ConciliacionView`      | Compara planillas de dos periodos.                              |
| GET                 | `/api/beneficios-salud/informe-efr/`                              | `InformeEFRView`        | Informe mensual EFR.                                            |

## 4. Códigos de respuesta esperados

| Código | Caso típico                                                             |
|--------|--------------------------------------------------------------------------|
| 200    | Consulta o operación exitosa.                                            |
| 201    | Recurso creado (POST a política, pensionados, auxilio externo).           |
| 400    | Archivo sin proveedor detectable; parámetros inválidos.                   |
| 404    | Recurso por `id` no encontrado.                                           |
| 500 / 503 | `prepagada.db` no disponible al consultar cruce o calcular planilla. (T1 §14 menciona 503; F2 menciona 500). |

## 5. Headers y autenticación

> ⚠️ PENDIENTE: el flujo real de autenticación productivo no está documentado. Hoy con `AllowAny` cualquiera con red al backend puede invocar los endpoints. Ver [`../05-seguridad/autenticacion-autorizacion.md`](../05-seguridad/autenticacion-autorizacion.md).

## 6. Exportaciones

| Exportación                                           | Hojas                                              |
|--------------------------------------------------------|-----------------------------------------------------|
| `GET /api/beneficios-salud/exportar/`                  | `Consolidado`, `AXA Colpatria`, `Colsanitas`.       |
| `GET /api/beneficios-salud/planilla/<id>/exportar/`    | `Planilla 80-20`, `Apoyo Gravable`.                 |

## 7. Otros endpoints fuera del módulo

| Ruta             | Disponibilidad                                                        |
|------------------|------------------------------------------------------------------------|
| `/admin/`        | Admin Django. Disponible si hay superusuario creado.                   |

---

**Fuente:** `siga/DOCUMENTACION_TECNICA.md` (§9 API REST), `siga/ARQUITECTURA_SOFTWARE.md` (§8 Contratos de API), `siga/DOCUMENTO_FUNCIONAL_BENEFICIOS_SALUD.md` (API de Consulta y Exportación), `siga/README.md`.
