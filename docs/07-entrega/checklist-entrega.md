# Checklist de Entrega

| Campo        | Valor                                                              |
|--------------|---------------------------------------------------------------------|
| Versión      | 1.0                                                                 |
| Fecha        | 2026-05-13                                                          |
| Fuente       | Esqueleto — no documentado en fuentes                                |
| Responsable  | Líder técnico / PMO                                                  |
| Estado       | **Borrador — cobertura BAJA**, ver `gaps.md` Top 10 #10              |

---

> ⚠️ PENDIENTE: las fuentes no incluyen un checklist formal de entrega al cliente ni criterios de aceptación. Esta versión es un punto de partida para el equipo. Cada ítem debe validarse antes de declarar una entrega como "Aprobada".

## 1. Aceptación funcional

| Ítem                                                                                | Evidencia esperada                                                                  | Estado |
|-------------------------------------------------------------------------------------|--------------------------------------------------------------------------------------|--------|
| Carga de archivos AXA Colpatria sin errores en archivos representativos              | Captura/log de `POST /upload/` y `GET /archivos/<id>/`.                                | `PENDIENTE` |
| Carga de archivos Colsanitas (`.xls` y `.xlsx`) sin errores                          | Idem.                                                                                | `PENDIENTE` |
| Detección automática de proveedor por nombre y por columnas                           | Pruebas con archivos sin `AXA/COLSANITAS` en el nombre.                              | `PENDIENTE` |
| Detección de fila de encabezado en archivos con metadatos previos                     | Archivo con cabecera no en fila 1.                                                   | `PENDIENTE` |
| Validación fila a fila genera errores y advertencias correctos                        | Listado de `ErrorProcesamiento` con `fila_origen`.                                   | `PENDIENTE` |
| Exportación consolidada Excel con tres hojas                                          | Archivo descargado.                                                                  | `PENDIENTE` |
| Cálculo de planilla 80/20 con política vigente                                        | Comparación con cálculo manual del mes anterior.                                     | `PENDIENTE` |
| Clasificación correcta de apoyo gravable y no gravable                                | Validación tributaria sobre periodos con casos > 16 UVT.                              | `PENDIENTE` |
| Causación por EPS coherente con planilla                                              | Reporte `/causacion/` cuadra con la planilla.                                         | `PENDIENTE` |
| Conciliación entre dos periodos                                                       | Reporte `/conciliacion/`.                                                            | `PENDIENTE` |
| Informe EFR mensual generado                                                          | Reporte `/informe-efr/`.                                                              | `PENDIENTE` |
| Gestión CRUD de Pensionados y Auxilio Externo                                          | Pruebas manuales.                                                                    | `PENDIENTE` |

## 2. Aceptación técnica

| Ítem                                                                | Estado       |
|---------------------------------------------------------------------|--------------|
| Ambientes Dev/QA/Prod definidos y promovidos                         | `PENDIENTE`  |
| Estrategia de despliegue documentada                                  | Borrador (`../04-operacion/despliegue.md`) |
| Estrategia de backups y restore documentada                           | `PENDIENTE`  |
| Migraciones reproducibles desde cero                                   | Sí (`python manage.py migrate`) |
| Variables de entorno productivas en vault                              | `PENDIENTE`  |
| TLS / HTTPS en producción                                              | `PENDIENTE`  |
| Permisos DRF endurecidos (no `AllowAny`)                                | `PENDIENTE`  |
| `DEBUG=0` y `SECRET_KEY` único en producción                            | `PENDIENTE`  |
| Logs centralizados y retención definida                                | `PENDIENTE`  |
| Alertas operativas (archivo en `ERROR`, `prepagada.db` no accesible)    | `PENDIENTE`  |

## 3. Aceptación de cumplimiento

| Ítem                                                                | Estado       |
|---------------------------------------------------------------------|--------------|
| Política de tratamiento de datos personales (Ley 1581)                | `PENDIENTE`  |
| Inventario de datos personales y finalidades documentado               | Parcial (`../05-seguridad/manejo-de-datos-sensibles.md`) |
| Procedimiento para derechos del titular                                 | `PENDIENTE`  |
| Auditoría de acciones críticas (política, planilla, pensionados)        | `PENDIENTE`  |
| Trazabilidad documental: archivo ↔ fila ↔ error                          | Soportado    |
| Trazabilidad documental: planilla ↔ política aplicada                   | Soportado    |
| Auditoría de cumplimiento EFR                                            | Salida soportada (`/informe-efr/`); auditoría externa `PENDIENTE` |

## 4. Documentación

| Ítem                                                                | Estado       |
|---------------------------------------------------------------------|--------------|
| Documentación consolidada en `siga/docs/`                              | Generada (este set) |
| Gaps documentados                                                       | [`../00-overview/gaps.md`](../00-overview/gaps.md) |
| Matriz de trazabilidad                                                  | Parcial (`matriz-trazabilidad.md`) |
| Glosario aprobado                                                      | Borrador (`../00-overview/glosario.md`) |
| ADRs aprobados                                                          | Borrador (`../02-arquitectura/decisiones/README.md`) |

## 5. Reglas pendientes de implementación

Las reglas del manual THU-DOC-002 que están **`No soportado`** o **`Por definir`** en [`../01-funcional/reglas-de-negocio.md`](../01-funcional/reglas-de-negocio.md) deben quedar declaradas como **fuera del alcance entregable** o ingresar a un release siguiente.

> ⚠️ La aceptación del cliente debe ser explícita sobre qué reglas entran y cuáles no en cada entrega.

## 6. Sign-off

| Rol                              | Nombre         | Fecha       | Firma  |
|----------------------------------|----------------|-------------|---------|
| Sponsor / Cliente                | `PENDIENTE`    | `PENDIENTE` | `PENDIENTE` |
| Líder técnico SIGA               | `PENDIENTE`    | `PENDIENTE` | `PENDIENTE` |
| Responsable de prepagada         | `PENDIENTE`    | `PENDIENTE` | `PENDIENTE` |
| Contabilidad                      | `PENDIENTE`    | `PENDIENTE` | `PENDIENTE` |
| Auditoría interna                 | `PENDIENTE`    | `PENDIENTE` | `PENDIENTE` |

---

**Fuente:** esqueleto construido por la consolidación. Las fuentes no incluyen un checklist formal de entrega.
