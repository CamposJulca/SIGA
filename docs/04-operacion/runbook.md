# Runbook — Operación Día a Día

| Campo        | Valor                                                                           |
|--------------|----------------------------------------------------------------------------------|
| Versión      | 1.0                                                                              |
| Fecha        | 2026-05-13                                                                       |
| Fuente       | Documento Funcional Beneficios de Salud (Manejo de errores); Reglas TH; Arquitectura §10 |
| Responsable  | Equipo SIGA / Operación                                                          |
| Estado       | Borrador                                                                         |

---

## 1. Operación funcional mensual

El runbook funcional principal se describe en [`../01-funcional/procesos-de-negocio.md`](../01-funcional/procesos-de-negocio.md). Se replica aquí en formato corto a modo de **checklist mensual**:

| ✔ | Paso                                                                              |
|---|------------------------------------------------------------------------------------|
|   | Verificar política 80/20 vigente del periodo (cambio de UVT en enero).             |
|   | Confirmar disponibilidad de `prepagada.db` y `v_cruce` para el periodo.            |
|   | Recibir Excel de AXA Colpatria → cargar en `/upload/`.                              |
|   | Recibir Excel de Colsanitas → cargar en `/upload/`.                                 |
|   | Revisar archivos en estado `ERROR`; corregir y reintentar.                          |
|   | Revisar advertencias por archivo (cédula duplicada, diferencia aritmética).         |
|   | Ejecutar `/novedades` contra el periodo anterior.                                     |
|   | Calcular planilla 80/20 (`POST /planilla/calcular/`).                                 |
|   | Revisar empleados con `apoyo_gravable > 0` y coordinar con tributaria.                |
|   | Exportar `/planilla/<id>/exportar/`.                                                  |
|   | Generar `/causacion/` y compartir con contabilidad.                                    |
|   | Generar `/informe-efr/` para el cierre EFR del mes.                                    |

## 2. Atención a incidentes técnicos

> ⚠️ PENDIENTE: severidades, on-call, comunicación y postmortem no documentados. Esta sección recoge sólo los **escenarios técnicos descritos** en F2 (Manejo de errores) y A1 §13 (Riesgos).

### 2.1 Archivo en estado `ERROR`

| Síntoma                          | Comportamiento del sistema                                                                                  | Acción recomendada                                                                          |
|----------------------------------|-------------------------------------------------------------------------------------------------------------|----------------------------------------------------------------------------------------------|
| Archivo queda en estado `ERROR`  | El archivo Excel original queda preservado en `storage/landing/{proveedor}/`. La transacción de carga abortó.| Revisar el log del request. Volver a cargar luego de corregir la causa raíz.                  |
| Cabecera no detectada             | El lector escaneó hasta la fila 16/21 sin encontrar marcadores del proveedor.                                | Verificar formato del archivo. Si la plantilla cambió, evaluar ajuste en `reader_excel.py`.   |
| Proveedor `desconocido`           | Ni el nombre ni las columnas permitieron identificar el proveedor.                                          | Renombrar el archivo incluyendo `AXA` o `COLSANITAS`. Reintentar.                              |

### 2.2 Errores fila a fila

| Tipo de error            | Comportamiento del sistema                                            | Acción recomendada                                                              |
|---------------------------|------------------------------------------------------------------------|---------------------------------------------------------------------------------|
| `CEDULA_INVALIDA`         | Registro guardado en `ErrorProcesamiento`. No inserta beneficio.       | Reportar a la EPS. Si es masivo, revisar plantilla del proveedor.                |
| `VALOR_INVALIDO`          | Idem.                                                                  | Idem.                                                                            |
| `CEDULA_DUPLICADA`         | Registro insertado como `ADVERTENCIA`.                                 | Verificar si es duplicado real o un beneficiario válido con núcleo distinto.     |
| Diferencia aritmética > 1 | Registro insertado como `ADVERTENCIA`.                                  | Revisar el cálculo del proveedor; documentar si es ajuste contable conocido.      |

### 2.3 `prepagada.db` no disponible

| Síntoma                                | Comportamiento                                                                  | Acción recomendada                                                       |
|----------------------------------------|----------------------------------------------------------------------------------|---------------------------------------------------------------------------|
| `/cruce` o `/planilla/calcular` retornan 503/500 | El servicio reporta error de conexión a la base externa.                          | Verificar existencia de `PREPAGADA_DB_PATH` y que contenga `v_cruce`.     |
| `v_cruce` vacía o sin el periodo solicitado | El cálculo no produce resultados.                                                  | Verificar que Kactus haya sincronizado el periodo en cuestión.            |

### 2.4 Archivo duplicado (mismo SHA256)

> ⚠️ Inconsistencia entre fuentes (ver `gaps.md` §5):
> - F2 declara que el archivo duplicado es **rechazado** antes de procesar.
> - T1 §14 y A1 §13 declaran que el hash se almacena pero **no se rechaza** automáticamente.
> Verificar el comportamiento real con código y ajustar este runbook.

### 2.5 Fallo de `bulk_create`

| Síntoma                                          | Acción recomendada                                                          |
|---------------------------------------------------|-----------------------------------------------------------------------------|
| `ArchivoRecibido` pasa a `ERROR` durante inserción | Revisar logs del worker. Verificar conexión a BD principal. El Excel original sigue disponible para reproceso. |

## 3. Operación de la política 80/20

| Evento                                                 | Acción                                                                                                |
|--------------------------------------------------------|--------------------------------------------------------------------------------------------------------|
| Inicio de año / publicación nueva UVT por la DIAN      | Crear nueva `PoliticaPrepagada` con la fecha de vigencia del 1 de enero y el `valor_uvt` nuevo.        |
| Cambio interno de porcentajes empresa/empleado          | Crear nueva política con la fecha de vigencia y comunicar a contabilidad/tributaria.                    |
| Confirmar códigos contables                             | Validar `cod_conc_apoyo_no_grav`, `cod_conc_apoyo_grav`, `cod_conc_dcto_empleado` con contabilidad.    |

> ⚠️ MP-032: el cálculo actual toma la política más reciente y no la vigente al periodo. Hasta resolver esta regla, verificar manualmente la coherencia de fechas.

## 4. Gestión de pensionados y auxilios externos

| Caso                                                                | Acción                                                                                  |
|----------------------------------------------------------------------|------------------------------------------------------------------------------------------|
| Cédula aparece en factura pero el cruce queda `NO ENCONTRADO`         | Verificar con Talento Humano si corresponde a pensionado o retiro.                       |
| Pensionado confirmado                                                | Registrar en `/pensionados/`. La planilla lo clasificará como `PENSIONADO_100`.           |
| Empleado con prepagada fuera del convenio                            | Registrar en `/auxilio-externo/`. Recordar que MP-019..MP-025 están **no implementadas**. |

## 5. Auditoría

| Acción                                          | Fuente                                                                                |
|-------------------------------------------------|----------------------------------------------------------------------------------------|
| ¿Qué se procesó en el periodo X?                | `GET /archivos/?periodo_facturacion=YYYYMM`.                                            |
| ¿Qué se calculó en el periodo X?                | `GET /planilla/?periodo=YYYYMM`.                                                        |
| ¿Por qué se rechazó el registro de la cédula X? | `GET /archivos/<id>/` muestra los `ErrorProcesamiento` con su `fila_origen`.            |
| ¿Qué política se usó en el cálculo del periodo X? | Campo `politica` de `PlanillaCalculo` (cabecera).                                       |

## 6. Procedimientos administrativos

| Tarea                            | Comando / Ruta                                                              |
|----------------------------------|------------------------------------------------------------------------------|
| Crear superusuario admin          | `docker compose exec siga python manage.py createsuperuser`                  |
| Reiniciar contenedor              | `docker compose restart siga`                                                |
| Ver logs del contenedor           | `docker compose logs -f siga`                                                |
| Acceder al admin Django           | `http://<host>:9010/admin/`                                                  |

## 7. Pendientes operativos

| Tema                          | Estado                                                                                  |
|-------------------------------|-----------------------------------------------------------------------------------------|
| On-call / Severidades         | `PENDIENTE`                                                                              |
| Plantillas de incidente        | `PENDIENTE`                                                                              |
| Postmortem                     | `PENDIENTE`                                                                              |
| Procedimiento de restore       | `PENDIENTE` (depende de la estrategia de backups, ver `despliegue.md`)                    |
| Política de rotación de claves | `PENDIENTE`                                                                              |

---

**Fuente:** `siga/DOCUMENTO_FUNCIONAL_BENEFICIOS_SALUD.md` (Manejo de Errores y Resiliencia), `siga/DOCUMENTACION_TECNICA.md` (§14 Consideraciones), `siga/ARQUITECTURA_SOFTWARE.md` (§10 Observabilidad, §13 Riesgos).
