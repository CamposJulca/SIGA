# SIGA — Documento Funcional
## Sistema Inteligente de Gestión Administrativa

> **Proyecto:** Automation Hub Finagro
> **Área solicitante:** Nómina / Talento Humano
> **Versión:** 2.1 — Marzo 2026
> **Acceso:** `https://automation-hub-finagro.ngrok.io/siga`
> **Responsable técnico:** Daniel Campos

---

## Tabla de contenido

1. [Propósito del sistema](#1-propósito-del-sistema)
2. [Usuarios y roles](#2-usuarios-y-roles)
3. [Arquitectura de navegación](#3-arquitectura-de-navegación)
4. [Portal SIGA — Pantalla principal](#4-portal-siga--pantalla-principal)
5. [Submódulo: Beneficios de Salud](#5-submódulo-beneficios-de-salud)
   - 5.1 [Dashboard](#51-dashboard)
   - 5.2 [Facturas EPS](#52-facturas-eps)
   - 5.3 [Planilla 80/20](#53-planilla-8020)
   - 5.4 [Apoyo Gravable / No Gravable](#54-apoyo-gravable--no-gravable)
   - 5.5 [Causación](#55-causación)
   - 5.6 [Pensionados](#56-pensionados)
   - 5.7 [Auxilio Externo](#57-auxilio-externo)
   - 5.8 [Política 80/20](#58-política-8020)
6. [Submódulos en desarrollo](#6-submódulos-en-desarrollo)
7. [Procedimiento operativo mensual](#7-procedimiento-operativo-mensual)
8. [Validaciones del sistema](#8-validaciones-del-sistema)
9. [Glosario](#9-glosario)

---

## 1. Propósito del sistema

SIGA es el sistema de gestión administrativa de Finagro dentro del Automation Hub. Agrupa múltiples submódulos de nómina y talento humano bajo una sola entrada, permitiendo escalar el alcance de automatización a medida que se definan nuevos requerimientos.

El primer submódulo implementado es **Beneficios de Salud**, que centraliza la gestión mensual de medicina prepagada:

| Tarea actual (manual) | Solución en SIGA |
|---|---|
| Abrir y revisar facturas de AXA y Colsanitas en Excel | Carga con detección automática de proveedor |
| Cruzar la factura con la nómina activa en Kactus | Cruce automático contra base de datos Kactus |
| Calcular el 80% empresa y el 20% empleado en hoja de cálculo | Cálculo automático con política configurable |
| Clasificar el apoyo como gravable o no gravable (Art. 387 E.T.) | Clasificación automática con límite de 16 UVT |
| Consolidar cifras para contabilidad por EPS | Resumen de causación por EPS en un clic |
| Detectar cambios entre mes y mes | Comparador de novedades integrado |

---

## 2. Usuarios y roles

| Rol | Quién | Acceso |
|---|---|---|
| **Analista de nómina** | Área de Nómina | Cargar facturas, calcular planillas, exportar, consultar |
| **Jefe de nómina** | Coordinador del área | Todo lo anterior + configurar la política 80/20 |
| **Contador** | Área Contable | Consultar causación, exportar planillas |
| **Administrador** | TI / Daniel Campos | Acceso completo + administración técnica |

---

## 3. Arquitectura de navegación

SIGA tiene dos niveles de navegación:

```
Automation Hub  →  /siga  →  Portal SIGA (landing con cards de submódulos)
                                │
                                ├──  Beneficios de Salud  →  8 pestañas
                                ├──  Vacaciones            →  (en desarrollo)
                                ├──  Cesantías             →  (en desarrollo)
                                └──  Nómina EFR            →  (en desarrollo)
```

**Nivel 1 — Portal SIGA:** pantalla de entrada con una card por submódulo. Muestra cuáles están activos y cuáles en desarrollo.

**Nivel 2 — Submódulo:** al hacer clic en una card activa se ingresa al submódulo. Una miga de pan en la parte superior (`← SIGA › Nombre del submódulo`) permite regresar al portal en cualquier momento.

---

## 4. Portal SIGA — Pantalla principal

Al ingresar a `/siga` se muestra el portal con las siguientes secciones:

**Banner superior:**
- Nombre completo: *Sistema Inteligente de Gestión Administrativa*
- Contador de submódulos totales, activos y en desarrollo

**Grid de submódulos:**

| Submódulo | Estado | Descripción |
|---|---|---|
| 🏥 **Beneficios de Salud** | Activo | Gestión de medicina prepagada: facturas EPS, planilla 80/20, causación contable, pensionados y auxilios externos |
| 🏖️ **Vacaciones** | En desarrollo | Control y liquidación de vacaciones |
| 💼 **Cesantías** | En desarrollo | Cálculo y control de cesantías e intereses |
| 📋 **Nómina EFR** | En desarrollo | Indicadores EFR relacionados con nómina y beneficios |

Los submódulos en desarrollo aparecen con opacidad reducida y botón deshabilitado. Solo los activos permiten ingreso.

---

## 5. Submódulo: Beneficios de Salud

Se accede haciendo clic en la card **Beneficios de Salud** en el portal SIGA.

El submódulo presenta un banner propio con estadísticas (archivos procesados, registros totales, proveedores activos) y una barra de **8 pestañas**:

```
📊 Dashboard  |  📁 Facturas EPS  |  🧮 Planilla 80/20  |  💰 Apoyo Grav./No Grav.
📒 Causación  |  👴 Pensionados   |  🏥 Auxilio Externo  |  ⚙️ Política 80/20
```

**Flujo mensual recomendado:** las pestañas se usan de izquierda a derecha.

---

### 5.1 Dashboard

Vista de resumen ejecutivo del estado actual del submódulo.

**Tarjetas KPI:**

| Tarjeta | Qué indica |
|---|---|
| Total archivos procesados | Acumulado histórico de facturas cargadas |
| Beneficiarios último período | Suma de afiliados en las facturas más recientes |
| Valor total último período | Total a pagar a AXA + Colsanitas en el período actual |
| Proveedores activos | Cuántas EPS tienen factura cargada |

**Sección por proveedor:** período de facturación, número de contrato, total de beneficiarios y valor de cada EPS por separado.

**Distribución por parentesco:** gráfico de barras con conteo y valor por tipo de relación familiar (Titular, Cónyuge, Hijo/a, Padres, Otro).

**Distribución por proveedor:** participación de AXA vs Colsanitas en el total de nómina de salud.

---

### 5.2 Facturas EPS

Carga los archivos Excel mensuales de AXA Colpatria y Colsanitas, revisa el historial y detecta novedades entre períodos.

**Proveedores y formatos soportados:**

| Proveedor | Extensión | Detección |
|---|---|---|
| AXA Colpatria | `.xlsx` | El nombre del archivo contiene "AXA" |
| Colsanitas | `.xlsx` / `.xls` | El nombre del archivo contiene "COLSANITAS" |

**Cómo cargar una factura:**
1. Arrastrar el archivo al área marcada o hacer clic en **"Seleccionar archivo"**.
2. El sistema detecta el proveedor, lee los metadatos (número de contrato, período de facturación), importa todos los afiliados y valida la integridad aritmética.
3. Al terminar muestra: total de registros, procesados correctamente y con advertencia.

> El nombre del archivo debe contener el nombre del proveedor. Un archivo llamado `factura_marzo.xlsx` sin mencionar AXA ni COLSANITAS será rechazado.

**Historial de archivos:** tabla con todos los archivos cargados. Por cada uno:
- **Ver detalle** → panel con errores o advertencias fila por fila.
- **⬇ Excel** → descarga los registros de ese archivo.

**Consulta por funcionario:** búsqueda por número de cédula en todos los archivos procesados.

**Novedades entre períodos:** compara dos archivos del mismo proveedor:

| Tipo | Color | Descripción |
|---|---|---|
| Nuevos afiliados | Verde | Aparecen en el archivo nuevo, no en el anterior |
| Retirados | Rojo | Estaban en el anterior, no en el nuevo |
| Cambios de valor | Amarillo | Misma cédula, cuota diferente |
| Sin cambios | Gris | Misma cédula, mismo valor |

---

### 5.3 Planilla 80/20

Genera la planilla de cálculo mensual: cuánto paga la empresa y cuánto se descuenta al empleado por cada titular con medicina prepagada.

**Prerrequisitos:**
- Facturas del período cargadas (pestaña **Facturas EPS**)
- Política 80/20 configurada (pestaña **Política 80/20**)

**Sección — Cruce del período:**

Resultado del cruce entre la factura de la EPS y la nómina activa de Kactus. Seleccionar el período en el dropdown:

| Estado | Color | Significado | Acción recomendada |
|---|---|---|---|
| `OK` | Verde | Empleado activo en Kactus. Se incluye en el cálculo | Ninguna |
| `NO ENCONTRADO` | Naranja | Cédula no existe en Kactus | Verificar. Si es pensionado, registrar en pestaña Pensionados |
| `INACTIVO` | Gris | Contrato finalizado en Kactus | Verificar si sigue activo en la EPS y notificar para retiro |

**Sección — Calcular planilla:**

Escribir el período en formato `MMYYYY` (ej. `032026`) y hacer clic en **Calcular planilla**. El sistema aplica por cada empleado con estado `OK`:

```
Total familia        = Suma de cuotas de todos los miembros del grupo familiar

Valor empresa (80%)  = Total familia × % empresa (configurable)
Valor empleado (20%) = Total familia × % empleado (configurable)

Límite no gravable   = UVT límite × Valor UVT vigente
                     = 16 × $49.799 = $796.784 (año 2026)

Apoyo NO gravable    = mínimo(Valor empresa, $796.784)
Apoyo gravable       = máximo(0, Valor empresa − $796.784)
```

> **Fila amarilla** = apoyo gravable > $0. El exceso supera el límite de 16 UVT e incrementa la base de retención en la fuente. Coordinar con el área tributaria.

**Historial de planillas:** lista de planillas calculadas. Al seleccionar una se despliega el detalle completo por empleado.

**Exportar a Excel:** genera un `.xlsx` con dos hojas:

| Hoja | Contenido |
|---|---|
| `Planilla 80-20` | Todos los empleados con sus valores calculados |
| `Apoyo Gravable` | Solo empleados que superan el límite de 16 UVT |

Este archivo es el soporte para el registro mensual en Kactus.

---

### 5.4 Apoyo Gravable / No Gravable

Vista tributaria de la planilla. Clasifica el aporte de la empresa según el **Art. 387 del Estatuto Tributario**.

**Marco tributario 2026:**

| Concepto | Valor |
|---|---|
| Valor UVT 2026 | $49.799 |
| Límite (16 UVT) | **$796.784 mensuales** |
| Hasta el límite | No gravable — no genera retención en la fuente |
| Sobre el límite | Gravable — incrementa la base de retención |

**Cómo usar:** seleccionar la planilla del período en el dropdown. Las tarjetas KPI muestran los totales consolidados. La tabla muestra el detalle por empleado; quienes superan el límite tienen un badge rojo.

**Acción ante empleados con apoyo gravable:** el exceso se suma a la base de retención en la fuente de ese empleado en el mes. Coordinar con tributaria y el configurador de Kactus usando los códigos de concepto de la Política 80/20.

---

### 5.5 Causación

Genera el resumen contable para que el área de contabilidad registre el gasto de medicina prepagada del mes.

**Cómo usar:** escribir el período (`MMYYYY`) y hacer clic en **Consultar**. La tabla muestra por EPS:

| Columna | Descripción |
|---|---|
| EPS | Nombre del proveedor |
| Empleados | Número de titulares incluidos |
| Total empresa | Valor a causar como gasto empresarial |
| Total empleado | Valor a descontar de nómina |
| Total factura | Suma total (empresa + empleado) |
| No gravable | Porción deducible del gasto empresa |
| Gravable | Porción no deducible del gasto empresa |

La fila **TOTAL** consolida todas las EPS.

**Asiento contable de referencia:**

```
Débito:  Gasto Salud — No Gravable     (apoyo_no_gravable)
Débito:  Gasto Salud — Gravable        (apoyo_gravable)
Crédito: Descuento por Nómina          (total_empleado)
Crédito: Cuentas por Pagar EPS         (total_empresa)
```

> Los códigos contables específicos los define el área de contabilidad según el PUC de Finagro.

---

### 5.6 Pensionados

Registra los empleados que pasaron a pensión pero conservan el beneficio de medicina prepagada activo. Estos no aparecen en la nómina activa de Kactus pero sí en las facturas de las EPS.

**Cómo identificarlos:** en **Planilla 80/20 → Cruce del período** aparecen como `NO ENCONTRADO` o `INACTIVO`. Al confirmar con nómina que tienen prepagada vigente, se registran aquí.

**Campos del formulario:**

| Campo | Descripción | Ejemplo |
|---|---|---|
| Cédula | Número de identificación | `52430287` |
| Nombre | Nombre completo | `DIANA CAROLINA GARCIA ARCILA` |
| EPS | Proveedor de salud | `AXA` |
| Valor mensual | Cuota del grupo familiar | `$1.880.200` |
| Fecha inicio | Inicio del beneficio | `2024-01-01` |
| Fecha fin | Terminación (opcional) | `2026-12-31` |
| Activo | Si el beneficio está vigente | ✓ |
| Observaciones | Notas adicionales | `Pensionado Ley 100, Plan Oro` |

**Gestión:** editar con el ícono de lápiz · desactivar desmarcando "Activo" · eliminar solo si fue creado por error.

---

### 5.7 Auxilio Externo

Registra empleados con medicina prepagada contratada fuera del convenio corporativo (EPS diferente a AXA o Colsanitas, o plan individual previo al ingreso).

**Cuándo registrar aquí:**
- Empleados con prepagada en EPS diferente al convenio.
- Empleados que mantienen su plan individual previo al ingreso a Finagro.
- Casos especiales autorizados por la gerencia.

El formulario es idéntico al de Pensionados.

---

### 5.8 Política 80/20

Configura los parámetros del motor de cálculo. Debe diligenciarse antes de calcular la primera planilla del año.

**Campos:**

| Campo | Descripción | Valor típico 2026 |
|---|---|---|
| % empresa | Porcentaje que paga la empresa | `80` |
| % empleado | Porcentaje que se descuenta al empleado | `20` |
| UVT límite | Número de UVT del límite Art. 387 E.T. | `16` |
| Valor UVT | Valor en pesos del UVT para el año | `$49.799` |
| % empresa pensionado | Porcentaje para pensionados si difiere | `80` |
| Cod. apoyo no gravable | Concepto Kactus para el aporte dentro del límite | *Pendiente confirmar con nómina* |
| Cod. apoyo gravable | Concepto Kactus para el exceso | *Pendiente confirmar con nómina* |
| Cod. descuento empleado | Concepto Kactus para el descuento al empleado | *Pendiente confirmar con nómina* |
| Notas | Fundamento de la política | `Resolución interna 2026-003` |
| Vigente desde | Fecha a partir de la cual aplica | `2026-01-01` |

El sistema calcula y muestra en tiempo real el límite resultante (`UVT límite × Valor UVT`). Cuando la DIAN publique el nuevo UVT en diciembre, actualizar este campo al inicio del año siguiente.

El sistema guarda el historial de todas las políticas. Si el porcentaje cambia, se crea una nueva política con su fecha de vigencia y el motor la aplica automáticamente.

---

## 6. Submódulos en desarrollo

Los siguientes submódulos están planificados y aparecen en el portal con estado **"En desarrollo"**. Su activación depende de la priorización del área de nómina.

| Submódulo | Funcionalidades previstas |
|---|---|
| **Vacaciones** | Programación, aprobación y liquidación. Cálculo automático de días y valores según contrato |
| **Cesantías** | Cálculo anual de cesantías e intereses. Archivos para consignación a fondos |
| **Nómina EFR** | Indicadores EFR relacionados con nómina y beneficios sociales |

---

## 7. Procedimiento operativo mensual

Proceso estándar para **Beneficios de Salud** cada vez que llegan las facturas de las EPS.

```
SEMANA DEL CIERRE DE MES
─────────────────────────────────────────────────────────

Día 1 — Recepción y carga
  1. Descargar factura AXA del correo corporativo
  2. Descargar factura Colsanitas del correo corporativo
  3. Verificar que el nombre del archivo contenga el proveedor
     (renombrar si es necesario: AXA_032026.xlsx / COLSANITAS_032026.xlsx)
  4. SIGA → Beneficios de Salud → Facturas EPS
     → Cargar AXA → verificar conteo
     → Cargar Colsanitas → verificar conteo
  5. Si hay registros con ERROR → revisar el detalle del archivo

Día 2 — Revisión del cruce
  6. Planilla 80/20 → Cruce del período → seleccionar el mes
  7. Revisar cada NO ENCONTRADO e INACTIVO:
     ¿Pensionado?        → Registrar en pestaña Pensionados
     ¿Error de cédula?   → Notificar a la EPS para corrección
     ¿Retirado activo?   → Notificar a la EPS para retiro del plan

Día 2 — Cálculo de planilla
  8. Planilla 80/20 → Calcular planilla → escribir período → Calcular
  9. Revisar filas amarillas → coordinar con tributaria
 10. Exportar Excel → compartir con nómina para validación

Día 3 — Validación y causación
 11. Comparar planilla automática vs Excel manual del mes anterior
 12. Si los valores coinciden → aprobar para registro en Kactus
 13. Causación → consultar período → cifras para contabilidad
 14. Facturas EPS → Novedades → comparar mes nuevo vs mes anterior

Días 4-5 — Registro en Kactus
 15. Ingresar descuentos del 20% empleado (código pendiente con nómina)
 16. Registrar devengo del 80% empresa (código pendiente con nómina)
```

**Tiempo estimado:**

| Actividad | Tiempo |
|---|---|
| Carga de archivos (2 EPS) | 5 minutos |
| Revisión del cruce | 10–20 minutos |
| Cálculo y validación de planilla | 15 minutos |
| Registro en Kactus | 30–60 minutos |
| **Total proceso mensual** | **~1.5 horas** |

---

## 8. Validaciones del sistema

### Al cargar un archivo de facturas

| Condición | Resultado |
|---|---|
| Nombre del archivo no contiene proveedor | Rechazo con mensaje de error |
| Cédula vacía o no numérica | Registro rechazado, error registrado |
| Valor total negativo | Registro rechazado |
| Cédula duplicada en el mismo archivo | Almacenado con estado `ADVERTENCIA` |
| Diferencia aritmética entre campos > $1 | Almacenado con estado `ADVERTENCIA` |

### Estados de un registro de beneficiario

| Estado | Significado |
|---|---|
| `OK` | Válido y aritméticamente correcto |
| `ADVERTENCIA` | Almacenado con inconsistencias no fatales |

### Estados del cruce con Kactus

| Estado | Significado |
|---|---|
| `OK` | Cédula encontrada en Kactus con contrato activo |
| `NO ENCONTRADO` | Cédula no existe en Kactus |
| `INACTIVO` | Cédula existe pero el contrato está inactivo |

---

## 9. Glosario

| Término | Definición |
|---|---|
| **SIGA** | Sistema Inteligente de Gestión Administrativa. Módulo del Automation Hub que agrupa submódulos de nómina y talento humano |
| **Submódulo** | Unidad funcional dentro de SIGA. Cada submódulo atiende un proceso específico |
| **EPS** | Entidad Promotora de Salud. En este contexto: AXA Colpatria o Colsanitas |
| **Grupo familiar** | Titular + beneficiarios cubiertos por un mismo contrato de prepagada |
| **Titular** | Empleado de Finagro que tiene el plan de medicina prepagada. Parentesco: T |
| **Beneficiario** | Familiar del titular cubierto por el plan (cónyuge, hijos, padres). Parentesco: CO, HI, P |
| **Total familia** | Suma de cuotas de todos los miembros del grupo familiar |
| **Valor empresa (80%)** | Porción del total familia que paga Finagro como beneficio |
| **Valor empleado (20%)** | Porción del total familia que se descuenta al empleado en nómina |
| **Apoyo no gravable** | Parte del valor empresa que no genera retención en la fuente (hasta 16 UVT) |
| **Apoyo gravable** | Exceso del valor empresa sobre 16 UVT. Incrementa la base de retención |
| **UVT** | Unidad de Valor Tributario. Definida anualmente por la DIAN. 2026: $49.799 |
| **Art. 387 E.T.** | Artículo del Estatuto Tributario que regula deducciones de salud del trabajador |
| **Kactus** | Sistema de nómina de Finagro. Fuente de verdad de empleados activos |
| **Cruce** | Comparación entre la factura de la EPS y la nómina activa de Kactus |
| **Período** | Mes de facturación en formato MMYYYY. Ej.: `032026` = marzo 2026 |
| **Planilla** | Documento calculado con el 80/20 y la clasificación gravable por empleado |
| **Causación** | Registro contable del gasto de medicina prepagada en el período |
| **Pensionado con prepagada** | Ex-empleado en pensión que conserva el beneficio activo |
| **Auxilio externo** | Reconocimiento de prepagada contratada fuera del convenio corporativo |
| **Política 80/20** | Configuración de porcentajes y parámetros tributarios vigentes para el cálculo |
| **EFR** | Empresa Familiarmente Responsable. Certificación que distingue empresas con políticas de conciliación vida-trabajo |

---

*Documento funcional — SIGA v2.1 · Automation Hub Finagro · Marzo 2026*
