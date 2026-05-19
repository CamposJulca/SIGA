# Componentes

| Campo        | Valor                                                              |
|--------------|---------------------------------------------------------------------|
| Versión      | 1.0                                                                 |
| Fecha        | 2026-05-13                                                          |
| Fuente       | Arquitectura §3; Documentación Técnica §3, §6–§11                    |
| Responsable  | Equipo SIGA                                                         |
| Estado       | Borrador                                                            |

---

## 1. Vista jerárquica

```text
siga/
├── backend/
│   ├── core/                  # Configuración Django (settings, urls, wsgi)
│   ├── modules/
│   │   └── beneficios_salud/
│   │       ├── admin.py        # Admin Django
│   │       ├── models.py       # 8 modelos
│   │       ├── serializers.py  # Serializers DRF
│   │       ├── urls.py         # 16 patrones de URL
│   │       ├── views.py        # 11 vistas API
│   │       ├── migrations/
│   │       └── services/
│   │           ├── detector.py
│   │           ├── reader_excel.py
│   │           ├── axa_adapter.py
│   │           ├── colsanitas_adapter.py
│   │           ├── validator.py
│   │           ├── prepagada_service.py
│   │           └── eligibility.py
│   ├── db/                    # SQLite dev + prepagada.db
│   ├── manage.py
│   └── requirements.txt
├── docker/
│   └── Dockerfile
├── docker-compose.yml
└── storage/
    └── landing/                # Archivos Excel persistidos
        ├── axa_colpatria/
        ├── colsanitas/
        └── desconocido/
```

## 2. Capa API (`views.py`)

| Vista                          | Propósito                                                     |
|--------------------------------|----------------------------------------------------------------|
| `UploadView`                   | Recibe Excel, dispara el pipeline ETL.                          |
| `ArchivoListView`              | Lista archivos cargados con filtros.                            |
| `ArchivoDetailView`            | Detalle de archivo + errores asociados.                          |
| `BeneficioListView`            | Lista beneficios normalizados.                                  |
| `ExportarExcelView`            | Genera Excel consolidado (3 hojas).                              |
| `NovedadesView`                | Compara dos archivos del mismo proveedor.                        |
| `DashboardView`                | Resumen ejecutivo.                                              |
| `CruceView`                    | Lista periodos o cruce por periodo desde `prepagada.db`.          |
| `PoliticaView` / `PoliticaDetailView` | CRUD de política 80/20.                                       |
| `PensionadosView` / `PensionadoDetailView` | CRUD de pensionados.                                       |
| `AuxilioExternoView` / `AuxilioExternoDetailView` | CRUD de auxilios externos.                            |
| `PlanillaListView`             | Lista planillas; filtro por periodo.                              |
| `PlanillaCalcularView`         | Calcula planilla del periodo.                                    |
| `PlanillaDetailView`           | Detalle de planilla con registros.                                |
| `PlanillaExportarView`         | Exporta planilla a Excel.                                         |
| `CausacionView`                | Resumen por EPS para periodo.                                    |
| `ConciliacionView`             | Compara planillas de dos periodos.                                |
| `InformeEFRView`               | Informe mensual EFR.                                              |

Responsabilidades comunes a las vistas:
- Recibir requests HTTP.
- Orquestar servicios de procesamiento.
- Persistir entidades con ORM.
- Serializar respuestas JSON.
- Generar archivos Excel descargables.

## 3. Capa de dominio y datos (`models.py`)

Detalle completo: [`../03-tecnico/modelo-de-datos.md`](../03-tecnico/modelo-de-datos.md). Responsabilidades:

- Definir entidades persistentes.
- Mantener relaciones entre archivos, beneficios, errores y planillas.
- Representar políticas y maestros de prepagada.

## 4. Servicios ETL

| Servicio                  | Responsabilidad                                                          |
|---------------------------|--------------------------------------------------------------------------|
| `detector.py`             | Detectar proveedor por nombre o columnas.                                 |
| `reader_excel.py`         | Leer Excel, detectar fila de encabezado, extraer metadatos.               |
| `axa_adapter.py`          | Transformar AXA Colpatria al esquema unificado.                            |
| `colsanitas_adapter.py`   | Transformar Colsanitas al esquema unificado y filtrar filas resumen.       |
| `validator.py`            | Validar integridad y clasificar errores/advertencias.                       |

### 4.1 Detección de proveedor

| Estrategia                 | Regla                                                                       |
|----------------------------|------------------------------------------------------------------------------|
| Nombre                      | `AXACOLPATRIA` o `AXA` → `axa`; `COLSANITAS` → `colsanitas`.                  |
| Columnas (fallback)         | `SUB CTO` y `NUMID` → `axa`; `Numero de Familia` → `colsanitas`.              |
| Sin coincidencia             | `desconocido`.                                                                |

### 4.2 Lectura Excel

| Proveedor                  | Motor      | Detección de cabecera                                                          |
|----------------------------|------------|--------------------------------------------------------------------------------|
| AXA                         | `openpyxl` | Escanea hasta 16 filas buscando `NUMID` o `SUB CTO`.                            |
| Colsanitas `.xls`           | `xlrd`     | Escanea hasta 21 filas buscando `Numero de Documento` o `Apellidos`.            |
| Colsanitas `.xlsx`          | `openpyxl` | Misma detección por cabecera.                                                   |

Además intenta extraer `numero_contrato` y `periodo_facturacion` de las filas anteriores al encabezado.

### 4.3 Adaptadores — Mapeo de columnas

**AXA Colpatria:**

| Columna origen     | Campo destino           |
|--------------------|--------------------------|
| `SUB CTO`          | `sub_contrato`           |
| `NUMID`            | `cedula_titular`         |
| `NUMERO ID.BEN`    | `cedula`                 |
| `NOMBRE`           | `nombre`                 |
| `PARENTESCO`       | `parentesco`             |
| `SUBTOTAL`         | `valor_base`             |
| `IVA`              | `iva`                    |
| `TOTAL`            | `valor_total`            |
| (sin campo)        | `descuento = 0`          |
| (constante)         | `proveedor = axa`        |

**Colsanitas:**

| Columna origen          | Campo destino                                |
|--------------------------|----------------------------------------------|
| `Numero de Familia`      | `sub_contrato`                                |
| `Numero de Documento`    | `cedula`                                      |
| `Apellidos` + `Nombres`  | `nombre` (concatenado con espacio)            |
| `Cuota`                  | `valor_base`                                   |
| `Descuento Comercial`    | `descuento` (puede ser negativo en ajustes)    |
| `IVA`                    | `iva`                                          |
| `Total Us` o `Total`     | `valor_total`                                   |

Filas excluidas por palabra clave: `TOTAL FAMILIA`, `TOTAL CONTRATO`, `TOTAL GENERAL`, `SUBTOTAL`, `GRAN TOTAL`.

### 4.4 Validación

Reglas detalladas en [`../01-funcional/reglas-de-negocio.md`](../01-funcional/reglas-de-negocio.md) §2.

Resumen:

| Validación                                         | Resultado                                              |
|-----------------------------------------------------|---------------------------------------------------------|
| Cédula vacía o `nan`                                | Error fatal `CEDULA_INVALIDA`; no inserta beneficio.    |
| Campos monetarios no numéricos                       | Error fatal `VALOR_INVALIDO`; no inserta beneficio.     |
| `valor_base`, `iva`, `valor_total` negativos        | Error fatal, salvo ajuste Colsanitas.                    |
| Ajuste Colsanitas (`valor_base = 0` y `valor_total < 0`) | Inserta con `ADVERTENCIA`.                            |
| Diferencia aritmética > 1                             | Inserta con `ADVERTENCIA`.                              |
| Duplicado por `cedula + sub_contrato`                | Inserta con `ADVERTENCIA` y registra `CEDULA_DUPLICADA`. |

## 5. Servicios de prepagada

| Servicio                  | Responsabilidad                                                              |
|---------------------------|-------------------------------------------------------------------------------|
| `prepagada_service.py`    | Leer `prepagada.db`, consultar `v_cruce` y exponer registros por periodo.       |
| `eligibility.py`          | Evaluar si aplica 80/20, pensionado 100 % o bloqueo por cruce.                 |

### 5.1 Reglas de elegibilidad

| Estado            | Criterio                                          | Cálculo                                                              |
|-------------------|----------------------------------------------------|----------------------------------------------------------------------|
| `PENSIONADO_100`   | Existe pensionado activo por cédula y EPS.        | Empresa `0`; empleado `100 %`.                                       |
| `BLOQUEADO_CRUCE`  | Estado de cruce distinto de `OK`.                 | Valores empresa/empleado en `0`; `valor_no_cubierto = total`.        |
| `ELEGIBLE_80_20`   | Cruce Kactus `OK` y no pensionado.                | Aplica porcentajes de política.                                       |

### 5.2 Cálculo numérico

```text
valor_empresa       = total_familia * porcentaje_empresa / 100
valor_empleado      = total_familia * porcentaje_empleado / 100
limite_no_gravable  = uvt_limite * valor_uvt
apoyo_no_gravable   = min(valor_empresa, limite_no_gravable)
apoyo_gravable      = max(0, valor_empresa - limite_no_gravable)
```

## 6. Almacenamiento de archivos

```text
siga/storage/landing/
├── axa_colpatria/
├── colsanitas/
└── desconocido/
```

La ruta guardada en `ArchivoRecibido.ruta_archivo` permite reconstruir el origen del dato procesado.

## 7. Configuración (`backend/core/settings.py`)

Detalle de variables de entorno: [`../03-tecnico/stack-tecnologico.md`](../03-tecnico/stack-tecnologico.md) y [`../04-operacion/ambientes.md`](../04-operacion/ambientes.md).

| Configuración         | Valor                                       |
|-----------------------|----------------------------------------------|
| `MEDIA_ROOT`           | `siga/storage/landing`                       |
| `MEDIA_URL`            | `/media/`                                    |
| SQLite dev             | `siga/backend/db/db.sqlite3`                  |
| Base externa prepagada | `PREPAGADA_DB_PATH`                          |

---

**Fuente:** `siga/ARQUITECTURA_SOFTWARE.md` (§3, §4, §5), `siga/DOCUMENTACION_TECNICA.md` (§3, §6, §7, §8, §10, §11).
