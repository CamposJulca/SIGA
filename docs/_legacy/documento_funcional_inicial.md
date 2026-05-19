# Documento Funcional
## SIGA – Sistema Inteligente de Gestión Administrativa

**Entidad:** FINAGRO  
**Sistema:** SIGA — Sistema Inteligente de Gestión Administrativa  
**Módulo inicial:** Beneficios de Salud  
**Referencia:** GTI-TH-2026-001  
**Fecha:** Marzo 2026  
**Estado:** Borrador inicial — sujeto a cambios

---

## 1. Problema actual

Los proveedores de medicina prepagada (AXA Colpatria, Colsanitas) envían periódicamente archivos Excel con información de beneficios de salud de los funcionarios de FINAGRO.

Cada proveedor utiliza una estructura de archivo diferente, lo que obliga al área de Talento Humano a realizar un proceso manual de consolidación con las siguientes dificultades:

- Formatos heterogéneos entre proveedores
- Procesamiento y cruce manual con información contractual
- Riesgo de errores en el cálculo de aportes
- Falta de trazabilidad del proceso
- Dificultad para aplicar sistemáticamente las políticas del Manual de Talento Humano

---

## 2. Objetivo

Automatizar la recepción, procesamiento y almacenamiento de los archivos de beneficios de salud enviados por proveedores, aplicando las políticas del Manual de Talento Humano para reducir el trabajo manual y mejorar la trazabilidad del cálculo.

---

## 3. Actores del sistema

| Actor | Rol | Área |
|---|---|---|
| Usuario Talento Humano | Carga archivos al sistema y consulta resultados | Dirección de Talento Humano |
| Administrador GTI | Mantiene el sistema y gestiona proveedores | Gerencia de Tecnologías de la Información |
| Proveedor de salud | Genera y envía los archivos Excel | Externo (AXA Colpatria, Colsanitas) |
| Sistema SIGA | Procesa, valida y almacena la información | Automático |

---

## 4. Flujo funcional

```
1. El proveedor envía el archivo Excel a FINAGRO
2. El usuario de Talento Humano carga el archivo en SIGA
3. El sistema almacena el archivo original sin modificar (Landing Zone)
4. El sistema detecta automáticamente el proveedor
5. Se omiten las filas de metadatos iniciales del archivo
6. Se ejecuta el adaptador correspondiente al proveedor
7. Se filtran filas de resumen o subtotales intercalados
8. Los datos se transforman al modelo unificado
9. Se validan los registros (integridad y reglas de negocio)
10. Los registros válidos se almacenan en la base de datos institucional
11. Los errores se registran con referencia a la fila de origen
12. El sistema muestra el resultado del procesamiento al usuario
```

---

## 5. Requerimientos funcionales

**RF01** — El sistema debe permitir cargar archivos Excel en formato `.xlsx` y `.xls`.

**RF02** — El sistema debe detectar automáticamente el proveedor a partir del nombre del archivo y/o su estructura de columnas.

**RF03** — El sistema debe localizar dinámicamente la fila de encabezados reales, omitiendo los bloques de metadatos iniciales presentes en los archivos de cada proveedor.

**RF04** — El sistema debe transformar los datos de cada proveedor al modelo de datos unificado de SIGA.

**RF05** — El sistema debe filtrar filas de subtotal y resumen intercaladas (ej. `TOTAL FAMILIA X` en Colsanitas) antes de procesar los registros.

**RF06** — El sistema debe validar que los campos obligatorios estén presentes y con formato válido.

**RF07** — El sistema debe validar la coherencia aritmética de los valores (cuota base, descuento, IVA, total).

**RF08** — El sistema debe almacenar los registros válidos en la base de datos institucional con referencia al archivo fuente.

**RF09** — El sistema debe registrar los errores de procesamiento con referencia a la fila de origen en el archivo.

**RF10** — El sistema debe mantener el archivo original sin modificar en la Landing Zone para fines de auditoría.

**RF11** — El sistema debe mostrar un resumen del procesamiento: total de registros, procesados correctamente y con error.

---

## 6. Requerimientos no funcionales

**RNF01** — El sistema debe procesar archivos con hasta 100.000 registros.

**RNF02** — El sistema debe garantizar la trazabilidad completa de cada archivo procesado.

**RNF03** — El sistema debe permitir incorporar nuevos proveedores sin modificar el núcleo del sistema.

**RNF04** — El sistema debe ejecutarse en la infraestructura institucional de FINAGRO (servidor 192.168.0.101).

**RNF05** — El sistema debe conservar los archivos originales en la Landing Zone para auditoría posterior.

---

## 7. Proveedores soportados (fase inicial)

### AXA Colpatria
- Formato: `.xlsx`
- Nombre de archivo: `AXACOLPATRIA*.xlsx`
- Columnas clave: `SUB CTO`, `NUMID`, `NOMBRE`, `PARENTESCO`, `NOVEDAD`, `SUBTOTAL`, `IVA`, `TOTAL`
- Particularidad: bloque de metadatos en filas 0–9, encabezados en fila ~10

### Colsanitas
- Formato: `.xls`
- Nombre de archivo: `COLSANITAS*.xls`
- Columnas clave: `Número de Familia`, `Número de Documento`, `Apellidos`, `Nombres`, `Cuota`, `Descuento Comercial`, `IVA`, `Total Us`
- Particularidad: bloque de metadatos en filas 0–11, encabezados en fila ~12, filas `TOTAL FAMILIA X` y `TOTAL CONTRATO` intercaladas

---

## 8. Beneficios esperados

- Eliminación del procesamiento manual de planillas de salud
- Reducción de errores en el cálculo de aportes
- Aplicación sistemática de las políticas del Manual de Talento Humano
- Trazabilidad completa del proceso de cálculo por período y funcionario
- Centralización de la información de todos los proveedores en una base única
- Tiempo de procesamiento reducido de horas a minutos

---

## 9. Módulos futuros del sistema SIGA

La plataforma está diseñada para escalar hacia otros procesos administrativos:

- Cajas de compensación
- Gestión de vacaciones
- Contratos con proveedores externos
- Reportería administrativa automatizada