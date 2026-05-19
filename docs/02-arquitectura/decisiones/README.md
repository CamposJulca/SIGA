# Decisiones Arquitectónicas (ADRs)

| Campo        | Valor                                                       |
|--------------|--------------------------------------------------------------|
| Versión      | 1.0                                                          |
| Fecha        | 2026-05-13                                                   |
| Fuente       | Arquitectura §11 (Decisiones arquitectónicas relevantes)      |
| Responsable  | Arquitectura / Líder técnico                                 |
| Estado       | Borrador — ADRs reconstruidos sin fecha ni autor              |

---

> ⚠️ PENDIENTE: las decisiones a continuación derivan de la tabla "decisión / justificación / consecuencia" del documento de Arquitectura. La fuente **no aporta fechas, autores, alternativas evaluadas ni estado**. Cada ADR queda como esqueleto a complementar por el equipo.

## ADR-0001 — Monolito Django modular

| Campo | Valor |
|-------|-------|
| Estado | Aceptada (deducido) |
| Fecha  | `PENDIENTE` |
| Decisores | `PENDIENTE` |
| Alternativas evaluadas | `PENDIENTE` |

**Contexto.** SIGA debe procesar archivos Excel y publicar una API REST con bajo costo operativo inicial.

**Decisión.** Implementar SIGA como aplicación Django monolítica con arquitectura modular, usando DRF para exponer las vistas API.

**Consecuencias.** Despliegue simple (un contenedor, dos workers Gunicorn). Para crecer a otros submódulos (vacaciones, primas, etc.) se mantiene la misma base con apps adicionales bajo `modules/`.

---

## ADR-0002 — Adaptador por proveedor

| Campo | Valor |
|-------|-------|
| Estado | Aceptada |
| Fecha  | `PENDIENTE` |

**Contexto.** Los proveedores AXA Colpatria y Colsanitas entregan Excel con estructuras de columnas, motores de Excel y filas resumen distintas.

**Decisión.** Implementar un adaptador por proveedor en `services/` que normalice cada formato al esquema unificado `BeneficioSalud`.

**Consecuencias.**
- Aísla los cambios de formato a un único archivo.
- **Tradeoff:** cada nuevo proveedor requiere un nuevo adaptador, además de ampliar `detector.py` y `UploadView`.

---

## ADR-0003 — Esquema unificado `BeneficioSalud`

| Campo | Valor |
|-------|-------|
| Estado | Aceptada |
| Fecha  | `PENDIENTE` |

**Contexto.** El consumo posterior (consultas, exportaciones, cálculos) debe ser homogéneo independiente del proveedor de origen.

**Decisión.** Modelar una tabla persistente única `bs_beneficios_salud` con todos los campos requeridos por cualquier proveedor soportado, incluso si quedan vacíos para algunos.

**Consecuencias.**
- Las consultas y reportes son multi-proveedor sin lógica especial.
- **Tradeoff:** algunos campos viajan como `NULL` o `0` cuando el proveedor no los entrega (ej. AXA con `descuento = 0`).

---

## ADR-0004 — Errores como entidad persistente

| Campo | Valor |
|-------|-------|
| Estado | Aceptada |
| Fecha  | `PENDIENTE` |

**Contexto.** Las facturas pueden traer filas con cédulas inválidas, valores no numéricos o inconsistencias aritméticas. Es necesario que el analista pueda auditarlas y corregirlas.

**Decisión.** Persistir cada error/advertencia en `bs_errores_procesamiento` con `fila_origen`, tipo y descripción, en vez de solo escribir logs.

**Consecuencias.**
- Auditoría completa por archivo.
- **Tradeoff:** aumenta el volumen de datos almacenado por cada carga.

---

## ADR-0005 — Base SQLite externa para Kactus (`prepagada.db`)

| Campo | Valor |
|-------|-------|
| Estado | Aceptada |
| Fecha  | `PENDIENTE` |

**Contexto.** El cruce con la nómina y la información laboral proviene de Kactus, sistema externo a SIGA, y no debe acoplarse a las tablas Django.

**Decisión.** Mantener `prepagada.db` como SQLite separado leído sólo desde `services/prepagada_service.py`, configurable por `PREPAGADA_DB_PATH`.

**Consecuencias.**
- Aísla la integración: Kactus puede cambiar internamente sin tocar Django.
- **Tradeoff:** se vuelve dependencia runtime crítica. Si el archivo no existe o no tiene `v_cruce`, los endpoints de cruce y planilla fallan.
- ⚠️ El **proceso de actualización** de este archivo desde Kactus no está documentado.

---

## ADR-0006 — Exportación Excel bajo demanda

| Campo | Valor |
|-------|-------|
| Estado | Aceptada |
| Fecha  | `PENDIENTE` |

**Contexto.** Los usuarios necesitan exportar consolidados y planillas a Excel. No es claro si se debería pre-generar y almacenar, o generar al vuelo.

**Decisión.** Generar el Excel en el momento del request usando openpyxl. No se almacenan archivos derivados.

**Consecuencias.**
- Sin necesidad de almacenamiento adicional ni invalidación de cachés.
- **Tradeoff:** exportaciones grandes consumen memoria durante el request. Riesgo si el volumen crece. (Ver `gaps.md` Top 10 #1 — RNF sin formalizar.)

---

## ADR-0007 — Inserción masiva (`bulk_create`)

| Campo | Valor |
|-------|-------|
| Estado | Aceptada |
| Fecha  | `PENDIENTE` |

**Contexto.** Cada archivo trae cientos de registros y la inserción uno a uno generaría latencia inaceptable.

**Decisión.** Usar `BeneficioSalud.objects.bulk_create(..., batch_size=500)` y lo mismo para `ErrorProcesamiento`.

**Consecuencias.**
- ETL completa en < 20 s para archivos típicos.
- **Tradeoff:** las validaciones deben ejecutarse **antes** de persistir (no se pueden usar `save()` hooks por registro).

---

## Plantilla para nuevos ADRs

```markdown
# ADR-XXXX — Título corto

| Campo | Valor |
|-------|-------|
| Estado | Propuesta / Aceptada / Reemplazada por ADR-YYYY |
| Fecha  | YYYY-MM-DD |
| Decisores | Nombre(s) |
| Alternativas evaluadas | ... |

## Contexto
...

## Decisión
...

## Consecuencias
- Positivas: ...
- Negativas / tradeoffs: ...

## Referencias
- ...
```

---

**Fuente:** `siga/ARQUITECTURA_SOFTWARE.md` §11 (tabla "decisión / justificación / consecuencia").
