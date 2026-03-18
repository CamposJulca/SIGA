# SIGA — Documento Funcional Actual

> Módulo: Beneficios de Salud — Gestión de nómina de salud empresarial
> Versión: Producción — Marzo 2026
> Integración: Automation Hub Finagro (port 9000, ruta `/siga`)

---

## 1. Propósito del módulo

El módulo SIGA - Beneficios de Salud permite al área de Talento Humano de Finagro gestionar y controlar los beneficios de salud de los funcionarios y sus beneficiarios. Centraliza la información proveniente de los proveedores de salud (AXA Colpatria y Colsanitas), automatiza la ingesta y validación de los archivos de facturación mensuales, y proporciona herramientas para análisis, exportación y detección de novedades entre períodos.

---

## 2. Usuarios y roles

| Rol | Perfil | Acciones disponibles |
|-----|--------|---------------------|
| Talento Humano | Usuario principal del módulo | Cargar archivos, consultar beneficiarios, exportar, comparar novedades, ver dashboard |
| Administrador | Acceso técnico | Todo lo anterior + acceso Django Admin |

---

## 3. Proveedores soportados

### 3.1 AXA Colpatria
- **Formato:** `.xlsx`
- **Detección:** nombre del archivo contiene "AXA" o "AXACOLPATRIA"
- **Estructura:** Filas de metadatos opcionales en la parte superior (contrato, período). Encabezados detectados automáticamente buscando la columna `NUMID` o `SUB CTO` en las primeras 16 filas.
- **Campos clave:**
  - `SUB CTO` → sub-contrato (grupo familiar)
  - `NUMID` → cédula del titular del contrato
  - `NUMERO ID.BEN` → cédula del afiliado (titular o beneficiario)
  - `NOMBRE` → nombre completo
  - `PARENTESCO` → relación familiar
  - `SUBTOTAL` → cuota base
  - `IVA` → impuesto
  - `TOTAL` → valor total a pagar

### 3.2 Colsanitas
- **Formato:** `.xls` (Excel 97-2003)
- **Detección:** nombre del archivo contiene "COLSANITAS"
- **Estructura:** Filas de metadatos antes de los encabezados (hasta 20 filas). Filas de totales de familia (`TOTAL FAMILIA X`) intercaladas en los datos — se filtran automáticamente.
- **Campos clave:**
  - `Número de Familia` → sub-contrato (grupo familiar)
  - `Número de Documento` → cédula del afiliado
  - `Apellidos` + `Nombres` → nombre completo (concatenados)
  - `Cuota` → valor base
  - `Descuento Comercial` → descuento (puede ser negativo)
  - `IVA` → impuesto
  - `Total Us` o `Total` → valor total

---

## 4. Funcionalidades

### 4.1 Carga de archivos

El usuario carga un archivo Excel mediante arrastrar y soltar o selección directa. El sistema:

1. Calcula el hash SHA256 del archivo para trazabilidad.
2. Detecta el proveedor por el nombre del archivo.
3. Guarda el archivo físicamente en `/storage/landing/{proveedor}/`.
4. Crea un registro `ArchivoRecibido` con estado `RECIBIDO`.
5. Ejecuta el pipeline ETL completo (leer → adaptar → validar).
6. Inserta los registros válidos y registra los errores.
7. Actualiza el registro con estadísticas finales y estado `PROCESADO`.

El resultado visible para el usuario incluye:
- Total de registros detectados en el archivo
- Registros procesados exitosamente
- Registros con error (rechazados)
- Estado final del procesamiento

### 4.2 Historial de archivos

Lista todos los archivos cargados con:
- Nombre, proveedor, período de facturación, número de contrato
- Fecha de recepción, estado, estadísticas de registros
- Botón "Ver detalle" → modal con listado de errores de validación (fila, tipo, descripción, valor encontrado)
- Botón "⬇ Excel" → descarga el Excel de ese archivo específico

### 4.3 Consulta por cédula / funcionario

Permite buscar un beneficiario específico por número de cédula. Retorna todos los registros asociados a esa cédula en todos los archivos procesados, mostrando proveedor, nombre, parentesco, plan, valores y estado de validación.

### 4.4 Exportación a Excel

Genera un archivo `.xlsx` con formato corporativo (encabezados verde Finagro `#00853f`, registros con advertencia en amarillo claro) con tres hojas:

| Hoja | Contenido |
|------|-----------|
| Consolidado | Todos los registros de los últimos archivos procesados de ambos proveedores, con columna `archivo_origen` |
| AXA Colpatria | Solo registros AXA del último archivo procesado |
| Colsanitas | Solo registros Colsanitas del último archivo procesado |

Si se especifica `archivo_id`, exporta únicamente ese archivo.

Columnas incluidas: cédula, nombre, parentesco, sub_contrato, cédula_titular, proveedor, tipo_plan, valor_base, descuento, IVA, valor_total, fecha_corte, número_contrato, período_facturación, estado_validación.

### 4.5 Comparación de novedades entre períodos

Permite comparar dos archivos del mismo proveedor para detectar cambios entre períodos de facturación. Identifica:

| Tipo de novedad | Descripción |
|----------------|-------------|
| Nuevos afiliados | Cédulas presentes en el archivo nuevo que no existían en el anterior |
| Retirados | Cédulas del archivo anterior que no aparecen en el nuevo |
| Cambios de valor | Afiliados presentes en ambos archivos con variación de cuota > $1 peso |
| Sin cambios | Afiliados con la misma cuota en ambos períodos |

El sistema emite una advertencia si los dos archivos son de distintos proveedores.

### 4.6 Dashboard ejecutivo

Resumen visual del estado actual de beneficios. Secciones:

**Tarjetas de resumen global:**
- Total archivos procesados
- Beneficiarios en el último período (suma de ambos proveedores)
- Valor total del último período
- Proveedores activos

**Por proveedor (último período):**
- Período de facturación y número de contrato
- Total beneficiarios y valor total
- Registros con advertencia

**Distribución por parentesco:**
- Gráfico de barras con conteo y valor por tipo de relación familiar (T=Titular, CO=Cónyuge, HI=Hijo/a, P=Padres, OT=Otro)

**Distribución de valor por proveedor:**
- Comparativa de participación AXA vs Colsanitas en el total de nómina de salud

---

## 5. Validaciones de integridad

| Código de error | Condición | Acción |
|----------------|-----------|--------|
| `CEDULA_INVALIDA` | Cédula vacía o `NaN` | Registro rechazado |
| `VALOR_INVALIDO` | `valor_base`, `iva` o `valor_total` no numérico o negativo | Registro rechazado |
| `CEDULA_DUPLICADA` | Misma cédula con mismo sub_contrato en el mismo archivo | Registro almacenado con estado `ADVERTENCIA`, error registrado para trazabilidad |
| `ADVERTENCIA aritmética` | `|valor_total - (valor_base - descuento + iva)| > $1` | Registro almacenado con estado `ADVERTENCIA` |
| `ADVERTENCIA ajuste` | `valor_base = 0` y `valor_total < 0` (fila de corrección contable Colsanitas) | Registro almacenado con estado `ADVERTENCIA` |

**Nota importante sobre descuentos:** El campo `descuento` puede ser negativo (Colsanitas lo representa así para ajustes). Solo `valor_base`, `iva` y `valor_total` deben ser ≥ 0 en condiciones normales.

---

## 6. Estados del sistema

### Estado de ArchivoRecibido

```
RECIBIDO → PROCESANDO → PROCESADO
                      → ERROR
```

### Estado de BeneficioSalud (estado_validacion)

| Estado | Descripción |
|--------|-------------|
| `OK` | Registro válido, aritméticamente correcto, sin duplicados |
| `ADVERTENCIA` | Registro almacenado con inconsistencias no fatales (duplicado, aritmética, ajuste contable) |
| `ERROR` | No se usa en registros almacenados; los registros rechazados no se insertan |

---

## 7. Interfaz de usuario

La página SIGA (`/siga`) está integrada en el portal Automation Hub (puerto 9000) con las siguientes secciones:

1. **Barra de navegación lateral** — entrada "🏥 SIGA" activa
2. **KPIs del período** — 4 tarjetas: total beneficiarios, valor período, archivos cargados, registros con advertencia
3. **Zona de carga** — drag & drop con indicador de progreso, muestra resultado inmediato
4. **Tarjetas informativas de proveedores** — descripción de formatos AXA y Colsanitas
5. **Tabla historial** — archivos procesados con acciones Ver detalle y Exportar
6. **Modal de detalle** — errores de validación del archivo seleccionado
7. **Consulta por cédula** — búsqueda y tabla de resultados
8. **Comparador de novedades** — selector de archivo nuevo/anterior + tabla de diferencias
9. **Dashboard visual** — tarjetas, gráfico de barras parentesco, gráfico de barras proveedor

---

## 8. Integración con el portal

- **URL frontend:** `http://[dominio]:9000/siga`
- **API base:** `/siga-api/beneficios-salud/`
- **Proxy Nginx:** `location /siga-api/ { proxy_pass http://siga:8000/api/; }`
- El módulo SIGA aparece en el dashboard principal de Automation Hub como tarjeta de módulo activo
