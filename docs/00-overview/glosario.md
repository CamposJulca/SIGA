# Glosario del Dominio SIGA

| Campo        | Valor                                                                                |
|--------------|---------------------------------------------------------------------------------------|
| Versión      | 1.0                                                                                   |
| Fecha        | 2026-05-13                                                                            |
| Fuente       | Documento Funcional Beneficios de Salud (Glosario); Documentación Técnica; Arquitectura |
| Responsable  | Equipo SIGA                                                                           |
| Estado       | Borrador                                                                              |

---

## A — Negocio

| Término | Definición |
|---------|------------|
| **SIGA** | Sistema Inteligente de Gestión Administrativa. Módulo administrativo de Finagro orientado a procesos de Talento Humano. |
| **Beneficios de Salud** | Subdominio de SIGA que procesa facturas EPS y calcula la planilla de medicina prepagada. |
| **EPS** | Entidad Promotora de Salud. En SIGA hoy: AXA Colpatria y Colsanitas. |
| **Titular** | Empleado de Finagro que tiene el plan de medicina prepagada. |
| **Beneficiario** | Familiar del titular cubierto por el plan (cónyuge, hijos, padres, otros). |
| **Sub-contrato (`sub_contrato`)** | Código que agrupa los beneficiarios de un mismo titular dentro de un contrato de seguro. Equivale a "núcleo familiar". |
| **Parentesco** | Relación del beneficiario con el titular (TITULAR, CÓNYUGE, HIJO, MADRE, PADRE, etc.). |
| **Periodo de facturación** | Mes facturado, expresado como `MMYYYY` (ej. `032026` = marzo 2026). |
| **Total familia** | Suma de cuotas de todos los miembros del grupo familiar para un periodo. |
| **Novedades** | Comparación entre dos archivos del mismo proveedor: altas, bajas y cambios de valor. |
| **Causación** | Registro contable del gasto de medicina prepagada en el periodo. |
| **Pensionado con prepagada** | Ex-empleado en pensión que conserva el beneficio activo; asume el 100 % del costo. |
| **Auxilio externo** | Reconocimiento de medicina prepagada contratada fuera del convenio corporativo. |
| **EFR** | Empresa Familiarmente Responsable. Certificación que distingue a empresas con políticas de conciliación trabajo-familia. SIGA produce el informe mensual asociado. |

## B — Modelo financiero y tributario

| Término | Definición |
|---------|------------|
| **Modelo 80/20** | Distribución del costo de la medicina prepagada: 80 % asume Finagro y 20 % el empleado. Es configurable por política. |
| **Política 80/20 (`PoliticaPrepagada`)** | Configuración de porcentajes empresa/empleado, UVT límite, valor UVT y conceptos contables vigente para un periodo. |
| **UVT** | Unidad de Valor Tributario. Es definida anualmente por la DIAN y es la base para el límite no gravable. |
| **Valor UVT** | Equivalencia en pesos colombianos de 1 UVT en el año en curso. Configurable por la política vigente. |
| **UVT límite** | Número de UVT que conforman el techo del apoyo no gravable. Valor típico: 16 UVT. |
| **Límite no gravable** | `uvt_limite × valor_uvt`. Hasta ese monto, el aporte de la empresa no genera retención en la fuente. |
| **Apoyo no gravable** | Porción del aporte de Finagro que **no** genera retención en la fuente (hasta el límite UVT). |
| **Apoyo gravable** | Porción del aporte de Finagro que **supera** el límite UVT y constituye ingreso gravable para el empleado. |
| **Art. 387 E.T.** | Artículo del Estatuto Tributario que regula las deducciones de salud del trabajador y fundamenta el límite UVT. |

## C — Pipeline ETL

| Término | Definición |
|---------|------------|
| **ETL** | Extract, Transform, Load. Pipeline de datos compuesto por tres fases. |
| **Fase E (Extracción)** | Recepción del archivo, hash SHA256, detección de proveedor, persistencia en disco y lectura del DataFrame. |
| **Fase T (Transformación)** | Normalización del esquema nativo del proveedor al esquema unificado + validación fila a fila. |
| **Fase L (Carga)** | Inserción masiva (`bulk_create`) en BD y actualización del estado del archivo. |
| **`sha256_archivo`** | Hash criptográfico del archivo cargado. Soporta deduplicación de archivos. |
| **Adaptador (proveedor)** | Componente que traduce las columnas nativas de un proveedor al esquema unificado `BeneficioSalud`. |
| **`bulk_create`** | Operación Django que inserta múltiples filas en una sola transacción. SIGA usa `batch_size=500`. |
| **`fila_origen`** | Número de fila en el Excel original donde se detectó un error o advertencia. Permite ubicar el dato problemático. |
| **`v_cruce`** | Vista en `prepagada.db` que cruza `facturas_eps` con `empleados_kactus` para identificar empleados con prepagada activa. |

## D — Estados

### Archivo

| Estado | Significado |
|--------|-------------|
| `RECIBIDO` | Archivo guardado y registro creado. |
| `PROCESANDO` | Lectura, normalización y validación en curso. |
| `PROCESADO` | Proceso finalizado y contadores actualizados. |
| `ERROR` | El archivo no pudo procesarse completamente. |

### Registro

| Estado | Significado |
|--------|-------------|
| `OK` | Registro válido sin observaciones. |
| `ADVERTENCIA` | Registro insertado, pero con duplicado, ajuste o diferencia aritmética. |
| `ERROR` | Registro rechazado y guardado como `ErrorProcesamiento`. |

### Cruce Kactus

| Estado | Significado |
|--------|-------------|
| `OK` | Cédula encontrada en Kactus y contrato activo. Cálculo 80/20 aplica. |
| `NO ENCONTRADO` | Cédula no existe en Kactus. Caso típico: pensionados o errores de cédula. |
| `INACTIVO` | Cédula existe pero el contrato está inactivo. Posible retiro pendiente. |

## E — Tipos de error y resultado

| Código / Estado de elegibilidad | Descripción |
|---------------------------------|-------------|
| `CEDULA_INVALIDA` | Cédula vacía o nula. Registro rechazado. |
| `VALOR_INVALIDO` | Valor monetario no numérico o negativo no permitido. Registro rechazado. |
| `CEDULA_DUPLICADA` | Misma cédula en mismo sub-contrato dentro del mismo archivo. Advertencia. |
| `PENSIONADO_100` | Empleado clasificado como pensionado activo → 0 % empresa / 100 % empleado. |
| `BLOQUEADO_CRUCE` | Cruce Kactus distinto de OK → no se calcula aporte empresa. |
| `ELEGIBLE_80_20` | Cruce OK y no pensionado → aplica política 80/20. |

## F — Plataforma técnica

| Término | Definición |
|---------|------------|
| **Django** | Framework Python usado para el backend (versión 4.2.11). |
| **DRF** | Django REST Framework. Expone los modelos como API REST. |
| **`AllowAny`** | Política de permisos por defecto de DRF en este proyecto. Permite acceso sin autenticación; ver advertencias en seguridad. |
| **Gunicorn** | Servidor WSGI usado para el despliegue en contenedor. |
| **pandas / openpyxl / xlrd** | Librerías de procesamiento de Excel. `openpyxl` para `.xlsx`; `xlrd` para `.xls` legacy de Colsanitas. |
| **Kactus** | Sistema de nómina de Finagro. Es la fuente de verdad de empleados activos y datos laborales. |
| **`prepagada.db`** | Base SQLite externa que contiene `facturas_eps`, `empleados_kactus` y la vista `v_cruce`. Es dependencia runtime del módulo de medicina prepagada. |
| **`storage/landing/`** | Carpeta del filesystem donde SIGA persiste los Excel recibidos, organizados por proveedor. |

---

**Fuente:** `siga/DOCUMENTO_FUNCIONAL_BENEFICIOS_SALUD.md` (Glosario Técnico), `siga/DOCUMENTACION_FUNCIONAL.md` §7, `siga/DOCUMENTACION_TECNICA.md` §2, §11.
