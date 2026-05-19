# SIGA — Arquitectura Actual

> Estado: Producción — Marzo 2026

---

## Visión general

```mermaid
graph TB
    subgraph Usuario["Usuario (Navegador)"]
        Browser["React SPA\nport 9000"]
    end

    subgraph HubProd["automation-hub-finagro (Docker Compose)"]
        Nginx["Nginx\npuertos 9000-9004"]
        Frontend["frontend\nNginx SPA"]
        Backend["backend\nDjango + Gunicorn\n:8000 (interno)"]
        Siga["siga\nDjango + Gunicorn\n:8000 (interno)"]
        DB["db\nPostgreSQL 16\n:5432 (interno)"]
        SigaVol[("siga_db\nSQLite volume")]
        LandingVol[("siga_landing\n/storage/landing")]
    end

    Browser -- "HTTP :9000" --> Nginx
    Nginx -- "/ SPA" --> Frontend
    Nginx -- "/api/ proxy" --> Backend
    Nginx -- "/siga-api/ proxy" --> Siga
    Backend --> DB
    Siga --> SigaVol
    Siga --> LandingVol
```

---

## Flujo de carga de archivo Excel

```mermaid
sequenceDiagram
    actor TH as Talento Humano
    participant UI as React SigaPage
    participant Nginx
    participant View as UploadView
    participant Det as detector.py
    participant Reader as reader_excel.py
    participant Adapter as axa/colsanitas_adapter.py
    participant Val as validator.py
    participant DB as SQLite (BeneficioSalud)

    TH->>UI: Arrastra/selecciona Excel
    UI->>Nginx: POST /siga-api/beneficios-salud/upload/ (multipart)
    Nginx->>View: Proxy → siga:8000/api/beneficios-salud/upload/

    View->>View: SHA256 hash del archivo
    View->>Det: detectar_proveedor(nombre_archivo)
    Det-->>View: 'axa' | 'colsanitas'
    View->>View: Guarda archivo en /storage/landing/{proveedor}/
    View->>View: Crea ArchivoRecibido(estado=RECIBIDO)
    View->>Reader: leer_excel(ruta, proveedor)
    Reader->>Reader: Detecta fila de encabezados (rows 0-20)
    Reader->>Reader: Extrae metadatos (contrato, periodo)
    Reader-->>View: (DataFrame, metadatos)

    View->>Adapter: adaptar_axa/colsanitas(df, metadatos)
    Adapter->>Adapter: Mapea columnas → esquema unificado
    Adapter->>Adapter: Filtra filas de totales/vacías
    Adapter-->>View: df_unificado

    View->>Val: validar_registros(df_unificado, archivo_id)
    Val->>Val: Detecta duplicados por (cedula, sub_contrato)
    Val->>Val: Valida valores numéricos no negativos
    Val->>Val: Detecta filas de ajuste contable
    Val->>Val: Verifica aritmética: |total - (base - desc + iva)| <= 1
    Val-->>View: (registros_ok, errores)

    View->>DB: BeneficioSalud.bulk_create(registros_ok)
    View->>DB: ErrorProcesamiento.bulk_create(errores)
    View->>DB: ArchivoRecibido.update(estado=PROCESADO, stats)
    View-->>UI: {archivo_id, total, procesados, errores, estado}
    UI-->>TH: Resultado del procesamiento
```

---

## Estructura de contenedores

```mermaid
graph LR
    subgraph Red["finagro-net (bridge)"]
        N["nginx\n:9000-9004"]
        F["frontend\n(React build)"]
        B["backend\nDjango main\n:8000"]
        S["siga\nDjango SIGA\n:8000"]
        PG["db\nPostgres 16\n:5432"]
    end

    subgraph Volúmenes
        V1[("postgres_data")]
        V2[("siga_db\nSQLite3")]
        V3[("siga_landing\nArchivos Excel")]
    end

    N-->F
    N-->B
    N-->S
    B-->PG
    PG-->V1
    S-->V2
    S-->V3
```

---

## Modelo de datos

```mermaid
erDiagram
    ArchivoRecibido {
        int id PK
        varchar proveedor
        varchar nombre_archivo
        varchar ruta_archivo
        datetime fecha_recepcion
        varchar estado_procesamiento
        varchar hash_archivo
        varchar usuario_carga
        int total_registros
        int registros_procesados
        int registros_con_error
        varchar numero_contrato
        varchar periodo_facturacion
    }

    BeneficioSalud {
        int id PK
        int archivo_id FK
        varchar cedula
        varchar tipo_id
        varchar nombre
        varchar parentesco
        varchar sub_contrato
        varchar cedula_titular
        varchar proveedor
        varchar tipo_plan
        decimal valor_base
        decimal descuento
        decimal iva
        decimal valor_total
        varchar fecha_nacimiento
        int edad
        date fecha_corte
        varchar numero_contrato
        varchar archivo_origen
        datetime fecha_procesamiento
        varchar estado_validacion
    }

    ErrorProcesamiento {
        int id PK
        int archivo_id FK
        int fila_origen
        varchar tipo_error
        text descripcion
        varchar valor_encontrado
        datetime timestamp
    }

    ArchivoRecibido ||--o{ BeneficioSalud : "beneficios"
    ArchivoRecibido ||--o{ ErrorProcesamiento : "errores"
```

---

## Mapa de rutas API

```mermaid
graph LR
    U["/siga-api/beneficios-salud/"] --> UP["upload/\nPOST\nCarga y procesa Excel"]
    U --> AR["archivos/\nGET\nListado de archivos"]
    U --> AD["archivos/{id}/\nGET\nDetalle + errores"]
    U --> BE["beneficios/\nGET\nFiltros: archivo_id, proveedor, cedula, estado_validacion"]
    U --> EX["exportar/\nGET\nDescarga .xlsx 3 hojas"]
    U --> NO["novedades/\nGET\nComparación entre períodos"]
    U --> DA["dashboard/\nGET\nResumen ejecutivo"]
```

---

## Pipeline ETL interno

```mermaid
flowchart TD
    A[Archivo Excel recibido] --> B{Detectar proveedor}
    B -->|nombre contiene AXA| C[reader_excel: _leer_axa\nopenpyxl, header rows 0-15]
    B -->|nombre contiene COLSANITAS| D[reader_excel: _leer_colsanitas\nxlrd/.xls · openpyxl/.xlsx\nheader rows 0-20]
    B -->|desconocido| E[Fallback openpyxl header=0]

    C --> F[adaptar_axa\nMapeo: NUMID→cedula_titular\nNUMERO ID.BEN→cedula\nSUBTOTAL→valor_base]
    D --> G[adaptar_colsanitas\nFiltro filas TOTAL FAMILIA\nCuota→valor_base\nDescuento Comercial→descuento]
    E --> H[Sin adaptador específico]

    F --> I[validar_registros]
    G --> I
    H --> I

    I --> J{cedula vacía?}
    J -->|Sí| K[ErrorProcesamiento\nCEDULA_INVALIDA]
    J -->|No| L{valor base/iva/total < 0?}
    L -->|Sí y no es fila ajuste| M[ErrorProcesamiento\nVALOR_INVALIDO]
    L -->|No o fila ajuste| N{(cedula,sub_contrato)\nduplicado?}
    N -->|Sí| O[BeneficioSalud\nestado=ADVERTENCIA\n+ ErrorProcesamiento\nCEDULA_DUPLICADA]
    N -->|No| P{|total - base+desc-iva| > 1?}
    P -->|Sí| Q[BeneficioSalud\nestado=ADVERTENCIA]
    P -->|No| R[BeneficioSalud\nestado=OK]
```

---

## Stack tecnológico

| Capa | Tecnología |
|------|-----------|
| Backend SIGA | Django 4.2 + Django REST Framework |
| ORM / BD | Django ORM + SQLite 3 (volumen Docker) |
| ETL | Pandas + openpyxl + xlrd |
| Exportación | openpyxl (escritura .xlsx con estilos) |
| Servidor WSGI | Gunicorn |
| Proxy inverso | Nginx |
| Contenedores | Docker + Docker Compose |
| Frontend | React 18 (SPA, hooks, fetch API) |
| Red Docker | finagro-net (bridge) |
