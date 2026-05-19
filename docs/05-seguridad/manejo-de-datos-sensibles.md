# Manejo de Datos Sensibles

| Campo        | Valor                                                                |
|--------------|----------------------------------------------------------------------|
| Versión      | 1.0                                                                  |
| Fecha        | 2026-05-13                                                           |
| Fuente       | Arquitectura §9, §13                                                  |
| Responsable  | Oficial de protección de datos / Seguridad                            |
| Estado       | **Borrador — cobertura BAJA**, ver `gaps.md` Top 10 #3                |

---

> ⚠️ PENDIENTE: las fuentes señalan que SIGA almacena datos personales (cédulas, nombres, valores), pero **no documentan** política de tratamiento, finalidades, retención ni encargado de tratamiento. Esta sección queda como esqueleto para alinear con la Ley 1581 (Habeas Data) colombiana.

## 1. Datos personales identificados

| Categoría                           | Ubicación                                                                                          |
|--------------------------------------|-----------------------------------------------------------------------------------------------------|
| Identificación (cédula)              | `BeneficioSalud.cedula`, `BeneficioSalud.cedula_titular`, `PensionadoPrepagada.cedula`, `AuxilioExterno.cedula`, `prepagada.db.v_cruce.cedula`. |
| Nombre completo                       | `BeneficioSalud.nombre`, `PensionadoPrepagada.nombre`, `AuxilioExterno.nombre`, `prepagada.db.v_cruce.nombre_*`. |
| Parentesco y composición familiar     | `BeneficioSalud.parentesco`, `sub_contrato`.                                                          |
| Fecha de nacimiento                   | `BeneficioSalud.fecha_nacimiento` (opcional).                                                          |
| Datos laborales sensibles              | `prepagada.db.empleados_kactus`: `sue_basi` (salario básico), `tip_cont`, `estado`.                    |
| Valores económicos individuales        | `BeneficioSalud.valor_base`, `descuento`, `iva`, `valor_total`; `DetalleCalculo` (cálculo por cédula). |
| Snapshots de filas con error           | `ErrorProcesamiento.datos_fila` (puede contener cualquier campo de la fila).                            |
| Archivos físicos                       | `storage/landing/{proveedor}/*.xlsx`/`.xls`.                                                            |

## 2. Tratamiento actual

| Aspecto                          | Estado documentado                                                                          |
|----------------------------------|---------------------------------------------------------------------------------------------|
| Cifrado en reposo                 | `PENDIENTE` — no se menciona.                                                                |
| Cifrado en tránsito                | `PENDIENTE` — el `docker-compose` expone HTTP. TLS depende del proxy de borde.                |
| Control de acceso                  | Hoy `AllowAny`. Ver [`autenticacion-autorizacion.md`](autenticacion-autorizacion.md).         |
| Acceso a la base BD               | A través del backend Django. Acceso directo a la BD `PENDIENTE` definir.                       |
| Acceso a `storage/landing/`       | `PENDIENTE` — debe protegerse con permisos del sistema (recomendación A1 §9).                   |
| Acceso a `prepagada.db`           | `PENDIENTE` — el archivo es lectura runtime del backend.                                        |
| Logs                               | `PENDIENTE` — no documentado si los logs contienen datos personales.                            |

## 3. Finalidades de tratamiento (a declarar)

> ⚠️ PENDIENTE: cada finalidad debe quedar formalizada en la política de tratamiento de Finagro.

Finalidades inferibles del alcance funcional:

- Procesar la facturación mensual de medicina prepagada con los proveedores AXA y Colsanitas.
- Calcular la liquidación 80/20 entre empresa y empleado conforme a la política institucional.
- Soportar la causación contable del gasto.
- Producir el informe EFR mensual.
- Mantener trazabilidad para auditoría y reclamaciones.

## 4. Retención

> ⚠️ PENDIENTE: política de retención por categoría de dato. Recomendación mínima:

| Categoría                          | Retención sugerida                                              |
|------------------------------------|------------------------------------------------------------------|
| Archivos originales en `storage/landing/` | Indefinida hasta definir política contable; mínimo periodo de auditoría. |
| Tablas `bs_*`                       | Igual a archivos originales.                                      |
| Logs con datos personales            | Mínimo posible. Idealmente sin PII.                                |
| `prepagada.db`                      | Ciclo de sincronización con Kactus.                                |

## 5. Derechos del titular (Habeas Data)

> ⚠️ PENDIENTE: procedimientos para:
> - Solicitud de acceso a información personal almacenada.
> - Rectificación / actualización.
> - Cancelación / supresión.
> - Revocatoria de autorización.
> - Notificación a terceros (proveedores) en caso de cambio.

## 6. Transferencias / encargados externos

| Tercero                | Acceso a datos                                                                  |
|------------------------|----------------------------------------------------------------------------------|
| AXA Colpatria          | Envía datos al sistema; SIGA no exporta nada hacia AXA.                          |
| Colsanitas             | Idem.                                                                            |
| Kactus                 | Es **fuente** vía `prepagada.db`; la sincronización es responsabilidad del operador de Kactus. |
| Portal web Finagro     | Consume la API; comparte datos al usuario humano. `PENDIENTE` formalizar.        |
| Proveedor de hosting   | `PENDIENTE`.                                                                     |
| Backups externos        | `PENDIENTE`.                                                                     |

## 7. Riesgos específicos

| Riesgo                                                              | Mitigación recomendada                                                 |
|----------------------------------------------------------------------|------------------------------------------------------------------------|
| Acceso no autorizado por `AllowAny`                                  | Implementar autenticación + roles (ver `autenticacion-autorizacion.md`). |
| Datos personales en logs                                              | Definir filtros que enmascaren cédulas y nombres antes de loguear.       |
| Excel original en disco sin cifrado                                   | Restringir permisos del sistema; evaluar cifrado de volumen.             |
| `ErrorProcesamiento.datos_fila` con PII                               | Considerar truncado o tokenización.                                       |
| Backups sin cifrar                                                    | Cifrar backups y controlar accesos.                                       |
| Acceso a `prepagada.db` desde el host                                   | Restringir permisos al usuario que corre el contenedor.                    |

## 8. Plan mínimo sugerido

> ⚠️ PENDIENTE: plan formal a redactar por el oficial de protección de datos.

1. Identificar a Finagro como responsable y al equipo SIGA como encargado.
2. Declarar finalidades formales y obtener autorización del titular si aplica.
3. Definir retenciones y procedimiento de eliminación segura.
4. Documentar el flujo de derechos del titular.
5. Aplicar control de acceso por roles (`05-seguridad/autenticacion-autorizacion.md`).
6. Cifrar backups y volúmenes con datos personales.
7. Registrar la base ante la SIC si Finagro está obligada por su tamaño y actividad.

---

**Fuente:** `siga/ARQUITECTURA_SOFTWARE.md` (§9 Seguridad, §13 Riesgos: datos sensibles). El detalle de Ley 1581 y procesos asociados no figura en las fuentes y queda como gap.
