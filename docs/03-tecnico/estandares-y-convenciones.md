# Estándares y Convenciones

| Campo        | Valor                                                |
|--------------|-------------------------------------------------------|
| Versión      | 1.0                                                   |
| Fecha        | 2026-05-13                                            |
| Fuente       | No formal — esqueleto a definir                       |
| Responsable  | Líder técnico SIGA                                    |
| Estado       | **Borrador — cobertura BAJA**, ver `gaps.md` Top 10 #6 |

---

> ⚠️ PENDIENTE: ninguna de las fuentes consolidadas describe estándares de código, estrategia de branching, política de revisión, política de pruebas o cobertura. Esta sección es un esqueleto para que el equipo lo complete. Marcamos cada bloque con valores **propuestos por defecto** (sólo donde es razonable) y `PENDIENTE` donde requiere decisión del equipo.

## 1. Lenguaje y estilo

| Tema                | Estado documentado | Recomendación inicial                                   |
|---------------------|---------------------|---------------------------------------------------------|
| Lenguaje principal   | Python 3.11         | Confirmado en `requirements.txt`.                        |
| Estilo de código     | `PENDIENTE`         | Adoptar `black` + `ruff` o `flake8`. PEP 8 como base.    |
| Tipado               | `PENDIENTE`         | Usar `mypy` en `services/` y modelos. Definir nivel de tipado. |
| Docstrings           | `PENDIENTE`         | Estilo Google o NumPy, consistente en todos los servicios. |
| Idioma comentarios   | `PENDIENTE`         | Español o inglés — definir.                              |

## 2. Estructura y organización

| Tema                                                | Estado documentado                                                                                  |
|------------------------------------------------------|------------------------------------------------------------------------------------------------------|
| Organización por app Django                          | Cada submódulo bajo `backend/modules/<modulo>/` con `models/views/serializers/services`.             |
| Servicios "puros"                                   | Lógica de negocio en `services/`; las vistas orquestan, no contienen reglas.                          |
| Ubicación de validaciones                           | Centralizadas en `services/validator.py` para el ETL.                                                  |
| Convención de tablas                                | Prefijo `bs_` (beneficios de salud).                                                                   |

## 3. Modelo Git

> ⚠️ PENDIENTE: política de branching no documentada.

Recomendación inicial (a confirmar):

| Tema                            | Recomendación inicial                                                         |
|----------------------------------|-------------------------------------------------------------------------------|
| Branches                         | `main` protegida; ramas `feature/<nombre>`; `release/<x.y>` por entrega.       |
| Commits                          | Convención Conventional Commits (`feat:`, `fix:`, `chore:`, `docs:`...).        |
| Tamaño de PR                     | Una unidad lógica; ≤ 400 líneas netas idealmente.                              |
| Squash en merge                  | Sí, para mantener historia legible.                                            |

## 4. Code Review

> ⚠️ PENDIENTE: requisitos formales no documentados.

Recomendación inicial:

| Tema                                      | Recomendación inicial                                            |
|-------------------------------------------|-------------------------------------------------------------------|
| Aprobaciones requeridas                   | Al menos 1 reviewer del equipo SIGA antes de merge.                |
| Reviewers obligatorios para reglas críticas | Cambios en `validator.py`, `eligibility.py` o políticas: revisar con Responsable de prepagada. |
| Checklist de revisión                    | Tests añadidos / actualizados; migración revisada; cambios de API documentados.|

## 5. Pruebas

> ⚠️ PENDIENTE: las fuentes no mencionan tests existentes ni cobertura objetivo.

Recomendación inicial:

| Tipo                  | Cobertura recomendada                                                                |
|-----------------------|--------------------------------------------------------------------------------------|
| Unitarias              | `services/` (adaptadores, validador, elegibilidad, lector).                            |
| Integración            | Pipeline completo `POST /upload/` con archivos de muestra de cada proveedor.           |
| API                    | Endpoints CRUD de política, pensionados, planilla.                                      |
| Datos                  | `prepagada.db` mockeable o usar archivo SQLite de fixtures.                              |
| Cobertura mínima       | `PENDIENTE`. Sugerencia: 80 % en `services/`.                                            |

## 6. Migraciones de base de datos

| Tema                          | Convención                                                                  |
|-------------------------------|------------------------------------------------------------------------------|
| Generación                    | `python manage.py makemigrations beneficios_salud`.                            |
| Aplicación                    | `python manage.py migrate` (también en arranque del contenedor).               |
| Política de rollback           | `PENDIENTE`.                                                                  |
| Migraciones de datos           | Se aceptan migraciones `RunPython`; deben ser idempotentes.                    |

## 7. Manejo de errores

Comportamiento observado en las fuentes:

| Caso                                              | Patrón                                                                          |
|----------------------------------------------------|--------------------------------------------------------------------------------|
| Error en una fila del archivo                      | No bloquea la carga; se persiste en `ErrorProcesamiento`.                       |
| Error en `bulk_create`                              | Estado de `ArchivoRecibido` pasa a `ERROR`; archivo en disco preservado.        |
| `prepagada.db` ausente                              | Endpoints de cruce/planilla retornan HTTP 503 (o 500).                          |
| Cédula vacía / valor inválido                      | Error fatal por registro: `CEDULA_INVALIDA` o `VALOR_INVALIDO`.                  |

## 8. Logging

> ⚠️ PENDIENTE: no se documenta configuración de logging, formato, destinos ni niveles. Ver `04-operacion/monitoreo-y-alertas.md`.

## 9. Convenciones de nombres

| Elemento                  | Convención                                                                  |
|---------------------------|------------------------------------------------------------------------------|
| Modelos Django            | `CamelCase` (`BeneficioSalud`, `ArchivoRecibido`).                            |
| Tablas                    | `snake_case` con prefijo `bs_`.                                                |
| Campos                    | `snake_case` en español.                                                       |
| Estados de archivo        | MAYÚSCULAS: `RECIBIDO`, `PROCESANDO`, `PROCESADO`, `ERROR`.                    |
| Estados de validación     | MAYÚSCULAS: `OK`, `ADVERTENCIA`, `ERROR`.                                       |
| Códigos de error          | MAYÚSCULAS con guión bajo: `CEDULA_INVALIDA`, `CEDULA_DUPLICADA`, `VALOR_INVALIDO`. |
| Estados de elegibilidad   | MAYÚSCULAS con guión bajo: `ELEGIBLE_80_20`, `PENSIONADO_100`, `BLOQUEADO_CRUCE`. |
| Identificadores de proveedor | Minúsculas con guión bajo: `axa_colpatria`, `colsanitas`, `desconocido`.       |

## 10. Definición de "hecho" (Definition of Done)

> ⚠️ PENDIENTE.

Propuesta inicial mínima:

- [ ] Código revisado por al menos un par.
- [ ] Tests unitarios y de integración aplicables ejecutados en verde.
- [ ] Migraciones aplicables sin errores en QA.
- [ ] Cambios de API documentados en [`api.md`](api.md).
- [ ] Reglas nuevas o cambios de cálculo documentados en [`../01-funcional/reglas-de-negocio.md`](../01-funcional/reglas-de-negocio.md).
- [ ] Si afecta a la base externa `prepagada.db`, validado con Responsable de prepagada.

---

**Fuente:** ninguna fuente formal — sección reconstruida como esqueleto. Las únicas referencias específicas (estados, prefijos, comportamiento ante errores) provienen de `siga/DOCUMENTACION_TECNICA.md` y `siga/DOCUMENTO_FUNCIONAL_BENEFICIOS_SALUD.md`.
