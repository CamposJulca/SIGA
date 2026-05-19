# Arquitectura SIGA
## Sistema Inteligente de Gestión Administrativa

**Versión:** 1.0 — Borrador inicial, sujeto a cambios  
**Fecha:** Marzo 2026

---

## 1. Arquitectura general del sistema

```mermaid
flowchart TD
    A[Proveedor de salud\nAXA Colpatria / Colsanitas] -->|Envía archivo Excel| B[Usuario Talento Humano]
    B -->|Carga archivo| C[SIGA — Portal de carga]

    C --> D[Landing Zone\nstorage/landing/proveedor]

    D --> E[Detector de proveedor\nNombre de archivo + columnas]

    E --> F1[Adapter AXA Colpatria\naxa_adapter.py]
    E --> F2[Adapter Colsanitas\ncolsanitas_adapter.py]
    E --> F3[Adapter Genérico\nFuturos proveedores]

    F1 --> G[Normalización\nModelo unificado]
    F2 --> G
    F3 --> G

    G --> H[Validación\nIntegridad + Reglas de negocio]

    H --> I[(Base de datos\nSQLite dev / PostgreSQL prod)]

    I --> J[Respuesta al usuario\nResumen de procesamiento]
```

---

## 2. Arquitectura modular — SIGA como plataforma

```mermaid
flowchart LR
    SIGA --> CORE
    SIGA --> MODULES
    SIGA --> STORAGE

    CORE --> settings
    CORE --> urls
    CORE --> wsgi

    MODULES --> beneficios_salud
    MODULES --> futuro_modulo_1["cajas_compensacion\n(futuro)"]
    MODULES --> futuro_modulo_2["vacaciones\n(futuro)"]

    beneficios_salud --> services
    services --> reader_excel.py
    services --> detector.py
    services --> axa_adapter.py
    services --> colsanitas_adapter.py
    services --> validator.py

    STORAGE --> landing
    landing --> axa_colpatria
    landing --> colsanitas
```

---

## 3. Flujo ETL — Módulo Beneficios de Salud

```mermaid
sequenceDiagram
    participant U as Usuario TH
    participant API as SIGA API
    participant LS as Landing Zone
    participant DET as Detector
    participant ADP as Adapter
    participant VAL as Validador
    participant DB as Base de datos

    U->>API: POST /api/beneficios-salud/upload/
    API->>LS: Guarda archivo original
    API->>DET: Detectar proveedor
    DET-->>API: proveedor = axa | colsanitas

    API->>ADP: Ejecutar adapter(proveedor, archivo)
    ADP->>ADP: Localizar fila de encabezados
    ADP->>ADP: Filtrar metadatos y subtotales
    ADP->>ADP: Renombrar columnas al modelo unificado
    ADP-->>API: DataFrame normalizado

    API->>VAL: Validar registros
    VAL-->>API: registros_ok + registros_error

    API->>DB: Insertar registros válidos
    API->>DB: Registrar errores con fila de origen
    DB-->>API: Confirmación

    API-->>U: Resumen: total / procesados / errores
```

---

## 4. Estructura de la base de datos

```mermaid
erDiagram
    bs_archivos_recibidos {
        int id PK
        varchar proveedor
        varchar nombre_archivo
        varchar ruta_archivo
        timestamp fecha_recepcion
        varchar estado_procesamiento
        varchar hash_archivo
        varchar usuario_carga
        int total_registros
        int registros_procesados
        int registros_con_error
        varchar numero_contrato
        varchar periodo_facturacion
    }

    bs_beneficios_salud {
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
        numeric valor_base
        numeric descuento
        numeric iva
        numeric valor_total
        date fecha_corte
        varchar numero_contrato
        timestamp fecha_procesamiento
        varchar estado_validacion
    }

    bs_errores_procesamiento {
        int id PK
        int archivo_id FK
        int fila_origen
        varchar tipo_error
        text descripcion
        varchar valor_encontrado
        timestamp timestamp
    }

    bs_archivos_recibidos ||--o{ bs_beneficios_salud : "contiene"
    bs_archivos_recibidos ||--o{ bs_errores_procesamiento : "genera"
```

---

## 5. Infraestructura de despliegue

```mermaid
flowchart LR
    subgraph Servidor["Servidor 192.168.0.101"]
        SIGA["SIGA\n:9010"]
        DB[(PostgreSQL\n:5432)]
        LS[("Landing Zone\nstorage/landing")]
    end

    U[Usuario] -->|HTTP| SIGA
    SIGA <--> DB
    SIGA <--> LS
```