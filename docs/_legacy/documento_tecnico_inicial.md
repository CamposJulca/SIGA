# Documento Técnico
## SIGA – Sistema Inteligente de Gestión Administrativa

**Entidad:** FINAGRO  
**Proyecto:** SIGA – Sistema Inteligente de Gestión Administrativa  
**Módulo inicial:** Beneficios de Salud  
**Referencia:** GTI-TH-2026-001  
**Autor:** Cristhiam Daniel Campos Julca — Gerencia de Tecnologías de la Información  
**Fecha:** Marzo 2026  
**Estado:** Borrador inicial — sujeto a cambios

---

## 1. Introducción

SIGA (Sistema Inteligente de Gestión Administrativa) es una plataforma modular desarrollada en FINAGRO para automatizar procesos administrativos que actualmente requieren consolidación manual de información proveniente de fuentes externas.

El primer módulo implementado es **Beneficios de Salud**, que automatiza el procesamiento de archivos Excel enviados periódicamente por proveedores de medicina prepagada.

---

## 2. Objetivo

Construir una plataforma modular que permita:

- Automatizar la recepción y procesamiento de archivos de proveedores
- Detectar automáticamente el formato y estructura de cada proveedor
- Normalizar la información a un modelo de datos unificado
- Validar los registros aplicando políticas del Manual de Talento Humano
- Almacenar los datos en la base institucional con trazabilidad completa
- Escalar hacia nuevos módulos administrativos sin modificar el núcleo

---

## 3. Alcance inicial

El módulo **Beneficios de Salud** procesará archivos de los siguientes proveedores:

- **AXA Colpatria** — archivos `.xlsx`, encabezados en fila ~10
- **Colsanitas** — archivos `.xls`, encabezados en fila ~12, con filas de subtotal intercaladas

Ambos archivos contienen bloques de metadatos del contrato antes de la tabla de datos. El sistema debe manejar esta estructura dinámicamente.

---

## 4. Tecnologías

| Componente | Tecnología |
|---|---|
| Backend API | Django + Django REST Framework |
| Procesamiento de datos | Python / Pandas |
| Lectura de Excel | Openpyxl (`.xlsx`) / xlrd >= 2.0.1 (`.xls`) |
| Base de datos (desarrollo) | SQLite |
| Base de datos (producción) | PostgreSQL |
| Contenedores | Docker / Docker Compose |
| Servidor | Linux — 192.168.0.101 |

> La migración de SQLite a PostgreSQL está planificada para la fase de producción. Los modelos están escritos con Django ORM / SQLAlchemy para que esta transición no requiera cambios en la lógica de negocio.

---

## 5. Estructura del repositorio

```
Finagro/
└── siga/
    ├── backend/
    │   ├── core/
    │   │   ├── settings.py
    │   │   ├── urls.py
    │   │   └── wsgi.py
    │   ├── modules/
    │   │   └── beneficios_salud/
    │   │       ├── models.py
    │   │       ├── serializers.py
    │   │       ├── views.py
    │   │       ├── urls.py
    │   │       ├── admin.py
    │   │       ├── migrations/
    │   │       └── services/
    │   │           ├── reader_excel.py
    │   │           ├── detector.py
    │   │           ├── axa_adapter.py
    │   │           ├── colsanitas_adapter.py
    │   │           └── validator.py
    │   ├── manage.py
    │   └── requirements.txt
    ├── storage/
    │   └── landing/
    │       ├── axa_colpatria/
    │       └── colsanitas/
    ├── docker/
    │   └── Dockerfile
    ├── docker-compose.yml
    ├── docs/
    │   ├── documento_tecnico_siga.md
    │   ├── documento_funcional_siga.md
    │   └── arquitectura_siga.md
    └── README.md
```

---

## 6. Modelo de datos

### Tabla: `bs_archivos_recibidos`

| Campo | Tipo | Descripción |
|---|---|---|
| `id` | integer PK | Identificador único |
| `proveedor` | varchar(50) | axa / colsanitas / desconocido |
| `nombre_archivo` | varchar(300) | Nombre original del archivo |
| `ruta_archivo` | varchar(500) | Ruta en storage/landing |
| `fecha_recepcion` | timestamp | Fecha/hora de carga |
| `estado_procesamiento` | varchar(20) | RECIBIDO / PROCESANDO / PROCESADO / ERROR |
| `hash_archivo` | varchar(64) | SHA256 para integridad |
| `usuario_carga` | varchar(150) | Usuario que cargó el archivo |
| `total_registros` | integer | Total de filas encontradas |
| `registros_procesados` | integer | Filas insertadas correctamente |
| `registros_con_error` | integer | Filas con error |
| `numero_contrato` | varchar(50) | Extraído del bloque de metadatos |
| `periodo_facturacion` | varchar(50) | Período del archivo |

### Tabla: `bs_beneficios_salud`

| Campo | Tipo | Descripción |
|---|---|---|
| `id` | integer PK | Identificador único |
| `archivo_id` | FK | Referencia a `bs_archivos_recibidos` |
| `cedula` | varchar(20) | Número de documento del afiliado |
| `tipo_id` | varchar(5) | CC / TI / CE / RC / PA |
| `nombre` | varchar(200) | Nombre completo |
| `parentesco` | varchar(5) | T / CO / HI / P / OT |
| `sub_contrato` | varchar(20) | SUB CTO (AXA) / Número de Familia (Colsanitas) |
| `cedula_titular` | varchar(20) | Cédula del titular cuando el registro es beneficiario |
| `proveedor` | varchar(50) | axa / colsanitas |
| `tipo_plan` | varchar(100) | Extraído de metadatos del contrato |
| `valor_base` | numeric(14,2) | Cuota base / SUBTOTAL |
| `descuento` | numeric(14,2) | Descuento comercial (Colsanitas) |
| `iva` | numeric(14,2) | Valor de IVA |
| `valor_total` | numeric(14,2) | Valor total a pagar |
| `fecha_nacimiento` | varchar(20) | Fecha de nacimiento del afiliado |
| `edad` | integer | Edad del afiliado |
| `fecha_corte` | date | Período de facturación |
| `numero_contrato` | varchar(50) | Número de contrato |
| `archivo_origen` | varchar(300) | Nombre del archivo fuente |
| `fecha_procesamiento` | timestamp | Fecha de procesamiento |
| `estado_validacion` | varchar(20) | OK / ERROR / ADVERTENCIA |

### Tabla: `bs_errores_procesamiento`

| Campo | Tipo | Descripción |
|---|---|---|
| `id` | integer PK | Identificador único |
| `archivo_id` | FK | Referencia a `bs_archivos_recibidos` |
| `fila_origen` | integer | Número de fila en el archivo fuente |
| `tipo_error` | varchar(50) | Categoría del error |
| `descripcion` | text | Detalle del error |
| `valor_encontrado` | varchar(200) | Valor que causó el error |
| `timestamp` | timestamp | Fecha/hora del error |

---

## 7. Validaciones aplicadas

- Cédula no nula y con formato válido
- Valores numéricos en columnas de moneda (valor_base, iva, valor_total)
- `valor_total` ≈ `valor_base` - `descuento` + `iva` (verificación aritmética)
- Sin cédulas duplicadas en el mismo archivo y período
- Valores no negativos (excepto descuentos justificados)

---

## 8. Consideraciones técnicas críticas

- Los archivos de ambos proveedores incluyen **bloques de metadatos** en las primeras filas antes de la tabla de datos. El `reader_excel.py` detecta dinámicamente la fila de encabezados reales.
- El archivo de **Colsanitas** contiene filas `TOTAL FAMILIA X` y `TOTAL CONTRATO` intercaladas que deben filtrarse explícitamente antes de procesar.
- El archivo de **Colsanitas** es `.xls` y requiere `xlrd >= 2.0.1` como dependencia explícita.
- La detección del proveedor se hace primero por nombre de archivo y como fallback por columnas reales.

---

## 9. Escalabilidad

Para agregar un nuevo proveedor se requiere únicamente:

1. Crear `nuevo_proveedor_adapter.py` en `services/`
2. Registrar las keywords de detección en `detector.py`
3. No se modifica ningún otro componente del sistema

---

## 10. Evolución futura

- Integración vía API con proveedores (eliminando envío manual)
- Módulos adicionales: cajas de compensación, vacaciones, contratos
- Cruce automatizado con sistema de nómina de FINAGRO
- Analítica histórica de beneficios por funcionario