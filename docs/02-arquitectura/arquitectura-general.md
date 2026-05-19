# Arquitectura General

| Campo        | Valor                                                                      |
|--------------|-----------------------------------------------------------------------------|
| Versión      | 1.0                                                                         |
| Fecha        | 2026-05-13                                                                  |
| Fuente       | Arquitectura de Software §1–§11; Documentación Técnica §1–§3                 |
| Responsable  | Arquitectura / Equipo SIGA                                                  |
| Estado       | Borrador                                                                    |

---

## 1. Vista general

SIGA es una aplicación **Django modular** orientada a procesamiento administrativo. El módulo principal actual es `beneficios_salud`, que concentra dos dominios relacionados:

1. ETL de archivos Excel de proveedores de salud.
2. Cálculo y reporte de medicina prepagada (planilla 80/20).

```mermaid
flowchart TB
    U[Usuario / Portal] -->|HTTP| B[SIGA Backend<br/>Django + DRF]
    B --> V[modules.beneficios_salud.views]
    V --> S1[services.detector]
    V --> S2[services.reader_excel]
    V --> S3[services.axa_adapter]
    V --> S4[services.colsanitas_adapter]
    V --> S5[services.validator]
    V --> S6[services.prepagada_service]
    V --> S7[services.eligibility]
    B --> DB[(Base principal Django<br/>SQLite o PostgreSQL)]
    B --> FS[/storage/landing/]
    S6 --> PDB[(prepagada.db<br/>SQLite externa)]
```

## 2. Estilo arquitectónico

| Aspecto                           | Decisión                                                  |
|------------------------------------|------------------------------------------------------------|
| Aplicación                         | Monolito Django modular                                    |
| API                                | REST con Django REST Framework                              |
| Dominio                             | App `modules.beneficios_salud`                             |
| Procesamiento                       | Servicios Python puros invocados desde vistas API           |
| Persistencia operacional            | ORM Django sobre SQLite/PostgreSQL                          |
| Persistencia documental             | Archivos originales en filesystem                            |
| Fuente externa prepagada            | SQLite separado (`prepagada.db`)                            |
| Exportación                         | Generación Excel bajo demanda con openpyxl                  |

## 3. Vista C4 — Nivel 1 (Contexto)

```mermaid
flowchart LR
    subgraph Finagro
      Analista[Analista Gestion Humana]
      Resp[Responsable prepagada]
      Contab[Contabilidad / Tributaria]
    end

    Analista -->|Sube facturas| SIGA[SIGA<br/>Backend Django + DRF]
    Resp -->|Configura politica<br/>y calcula planillas| SIGA
    Contab -->|Consulta causacion| SIGA

    SIGA -->|Lee v_cruce| Kactus[(prepagada.db<br/>Kactus snapshot)]
    AXA[Proveedor AXA] -.->|Excel mensual| Analista
    COL[Proveedor Colsanitas] -.->|Excel mensual| Analista
```

## 4. Vista C4 — Nivel 2 (Contenedores)

```mermaid
flowchart TB
    subgraph Contenedor_SIGA[Contenedor SIGA - Docker]
      G[Gunicorn<br/>2 workers] --> D[Django + DRF]
      D --> M[modules.beneficios_salud<br/>views / services / models]
    end

    subgraph Persistencia
      DB[(Base Django<br/>SQLite o PostgreSQL)]
      PDB[(prepagada.db<br/>SQLite externa)]
      Storage[/storage/landing/]
    end

    M --> DB
    M --> PDB
    M --> Storage

    Portal[Portal web<br/>de Finagro] -->|REST| G
```

> ⚠️ PENDIENTE: el portal web es referenciado en F2 pero no se aporta repositorio, contrato de consumo ni equipo responsable. Sólo se sabe que consume la API en `/api/beneficios-salud/`.

## 5. Vista C4 — Nivel 3 (Componentes del módulo `beneficios_salud`)

```mermaid
flowchart LR
    V[views.py<br/>11 vistas API] --> Det[detector.py<br/>Deteccion proveedor]
    V --> Rd[reader_excel.py<br/>Lectura Excel + cabecera]
    V --> AdA[axa_adapter.py]
    V --> AdC[colsanitas_adapter.py]
    V --> Val[validator.py<br/>4 reglas]
    V --> Pre[prepagada_service.py<br/>Lectura v_cruce]
    V --> Eli[eligibility.py<br/>80/20 - pensionado - bloqueo]

    V --> Mod[models.py<br/>8 modelos]
    Mod --> DB[(bs_archivos_recibidos<br/>bs_beneficios_salud<br/>bs_errores_procesamiento<br/>bs_politica_prepagada<br/>bs_pensionados_prepagada<br/>bs_auxilio_externo<br/>bs_planilla_calculo<br/>bs_detalle_calculo)]
    Pre --> PDB[(prepagada.db<br/>facturas_eps<br/>empleados_kactus<br/>v_cruce)]
```

## 6. Vista de flujo ETL (Beneficios)

```mermaid
flowchart TB
    A[Excel proveedor] --> B[UploadView]
    B --> B1[SHA256]
    B --> B2[detectar_proveedor]
    B --> B3[guardar archivo en storage/landing]
    B --> B4[crear ArchivoRecibido]
    B4 --> C[leer_excel]
    C --> C1[detectar fila de encabezado]
    C --> C2[extraer numero_contrato y periodo]
    C --> D[Adaptador del proveedor]
    D --> D1[adaptar_axa]
    D --> D2[adaptar_colsanitas]
    D --> E[validar_registros]
    E --> E1[registros OK / ADVERTENCIA]
    E --> E2[errores fatales]
    E1 --> F[bulk_create]
    E2 --> F2[bulk_create errores]
    F --> G[ArchivoRecibido = PROCESADO]
    F2 --> G
```

## 7. Vista de flujo de medicina prepagada

```mermaid
flowchart TB
    U[Usuario selecciona periodo] --> P[PlanillaCalcularView]
    P --> P1[Obtener politica vigente]
    P --> P2[prepagada_service.get_cruce_periodo]
    P2 --> V[(v_cruce en prepagada.db)]
    V --> E[eligibility.evaluar_elegibilidad]
    E --> E1[PENSIONADO_100]
    E --> E2[BLOQUEADO_CRUCE]
    E --> E3[ELEGIBLE_80_20]
    E1 --> C[Calcular valores]
    E2 --> C
    E3 --> C
    C --> R[PlanillaCalculo + DetalleCalculo]
```

## 8. Vista de despliegue (alto nivel)

```mermaid
flowchart LR
    H[Host / Docker] --> Cont[Contenedor siga]
    Cont --> Gun[gunicorn core.wsgi:application<br/>2 workers · puerto 8000]
    Cont --> Vol1[/storage]
    Cont --> Vol2[/db<br/>db.sqlite3 + prepagada.db]
    Host_user[Usuario:9010] --> H
```

Detalles operativos en [`../04-operacion/despliegue.md`](../04-operacion/despliegue.md).

## 9. Vista de datos (resumen)

```mermaid
erDiagram
    ArchivoRecibido ||--o{ BeneficioSalud : "1..N"
    ArchivoRecibido ||--o{ ErrorProcesamiento : "1..N"
    PoliticaPrepagada ||--o{ PlanillaCalculo : "1..N"
    PlanillaCalculo ||--o{ DetalleCalculo : "1..N"
    PensionadoPrepagada }o..o{ DetalleCalculo : "afecta calculo"
    AuxilioExterno }o..o{ DetalleCalculo : "informe EFR"
```

Detalle del modelo de datos: [`../03-tecnico/modelo-de-datos.md`](../03-tecnico/modelo-de-datos.md).

## 10. Dependencia externa: `prepagada.db`

```text
prepagada.db (SQLite)
├── facturas_eps         -> Datos facturados por EPS
├── empleados_kactus     -> Snapshot de la planta activa
└── v_cruce              -> Vista que cruza ambas y es lo que SIGA consume
```

Campos leídos desde `v_cruce`:

```text
periodo, eps, cedula, nombre_en_factura, nombre_en_kactus,
num_beneficiarios, total_familia, sub_cto, nro_cont,
sue_basi, tip_cont, estado, archivo
```

> ⚠️ PENDIENTE: el contrato de actualización de `prepagada.db` (frecuencia, responsable, formato de ingesta desde Kactus) no está documentado en las fuentes. Es dependencia runtime crítica.

## 11. Decisiones arquitectónicas relevantes (resumen)

Las decisiones detalladas y sus ADRs viven en [`decisiones/`](decisiones/README.md). En resumen:

| Decisión                            | Justificación                                          | Consecuencia                                                            |
|-------------------------------------|---------------------------------------------------------|--------------------------------------------------------------------------|
| Adaptador por proveedor             | Aísla formatos distintos de Excel                       | Nuevos proveedores requieren nuevo adaptador                              |
| Esquema unificado `BeneficioSalud`   | Permite consultas y reportes multi-proveedor             | Puede requerir campos opcionales vacíos según proveedor                   |
| Errores como entidad persistente     | Facilita auditoría y corrección operativa                | Aumenta volumen de datos por carga                                        |
| `prepagada.db` separado              | Permite consumir cruce/Kactus sin acoplarlo a tablas Django | Requiere disponibilidad y versionado de esa base externa               |
| Exportación bajo demanda             | Evita almacenar archivos derivados innecesarios           | Exportaciones grandes consumen memoria durante el request                 |
| Bulk insert                          | Mejora rendimiento en cargas masivas                      | Validaciones deben ejecutarse antes de persistir                           |

## 12. Puntos de extensión

| Necesidad                          | Lugar de cambio                                                                           |
|------------------------------------|-------------------------------------------------------------------------------------------|
| Nuevo proveedor                    | Crear adaptador en `services/`, ampliar `detector.py` y `UploadView`.                      |
| Nuevas reglas de validación        | `services/validator.py`.                                                                  |
| Nuevos campos de beneficio          | `models.py`, migración, serializers, adaptadores y exportación.                            |
| Nueva política de elegibilidad      | `services/eligibility.py`.                                                                 |
| Nueva fuente Kactus                 | `services/prepagada_service.py`.                                                           |
| Nuevos reportes                     | Agregar vista DRF y ruta en `urls.py`.                                                     |

## 13. Riesgos arquitectónicos

| Riesgo                                  | Impacto                                                                  |
|-----------------------------------------|---------------------------------------------------------------------------|
| Cambio de plantilla Excel               | Puede romper detección de encabezados o mapeo de columnas.                |
| `AllowAny` en API                       | Riesgo si el servicio se publica sin control perimetral. Ver `05-seguridad/`. |
| `prepagada.db` faltante                  | Endpoints de cruce y planilla fallan con 503.                              |
| Reprocesamiento de archivo duplicado     | Hash se almacena, pero no hay rechazo automático implementado (T1 §14).    |
| Excel muy grande                         | Exportación / carga puede consumir memoria por uso de pandas/openpyxl en request. |
| Datos sensibles                          | Cédulas, nombres y valores requieren protección de acceso y backup seguro. |

---

**Fuente:** `siga/ARQUITECTURA_SOFTWARE.md` (§1 Vista general, §2 Estilo, §3 Componentes, §4 Flujo ETL, §5 Flujo prepagada, §6 Despliegue, §7 Datos, §11 Decisiones, §12 Extensión, §13 Riesgos); `siga/DOCUMENTACION_TECNICA.md` (§1 Resumen técnico, §3 Estructura).
