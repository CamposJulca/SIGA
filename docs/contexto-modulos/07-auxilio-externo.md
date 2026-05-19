# Módulo 7 — Auxilio Externo: Investigación Técnica

| Campo            | Valor                                                                                                                                                                |
|------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Fecha            | 2026-05-14                                                                                                                                                           |
| Generado por     | Verificación directa de código fuente                                                                                                                                |
| Archivos leídos  | `urls.py`, `views.py` (779–836, 1200–1296), `serializers.py` (136–151), `models.py` (148–163), `services/eligibility.py`, `services/prepagada_service.py`, `admin.py` (119–135), frontend `SigaPage.js` (1193–1334, 1527, 1602) |
| Verificación BD  | `bs_auxilio_externo` (`db.sqlite3`) — `COUNT(*) = 0`                                                                                                                  |
| Apoyo previo     | Módulos 3 y 6 ya verificados: `AuxilioExterno` reutiliza el mismo patrón "tabla + CRUD plano + texto libre" que `PensionadoPrepagada`, pero sin la conexión MP-006 con `eligibility.py`. |

---

## CRUD: endpoints disponibles

Registrados en `urls.py:29-30`:

```python
path('auxilio-externo/', AuxilioExternoView.as_view()),
path('auxilio-externo/<int:pk>/', AuxilioExternoDetailView.as_view()),
```

| Método | Ruta                                            | Vista                              | Líneas (`views.py`) |
|--------|-------------------------------------------------|------------------------------------|---------------------|
| GET    | `/api/beneficios-salud/auxilio-externo/`        | `AuxilioExternoView.get`           | 785–791             |
| POST   | `/api/beneficios-salud/auxilio-externo/`        | `AuxilioExternoView.post`          | 793–798             |
| GET    | `/api/beneficios-salud/auxilio-externo/<pk>/`   | `AuxilioExternoDetailView.get`     | 814–818             |
| PUT    | `/api/beneficios-salud/auxilio-externo/<pk>/`   | `AuxilioExternoDetailView.put`     | 820–828             |
| DELETE | `/api/beneficios-salud/auxilio-externo/<pk>/`   | `AuxilioExternoDetailView.delete`  | 830–835             |

**Es una copia byte-por-byte del CRUD de Pensionados.** Mismas mismas características:

- ❌ No hay paginación.
- ❌ No hay búsqueda por cédula, nombre, EPS.
- ❌ No hay ordenamiento explícito (`Meta` no define `ordering` — `models.py:159-160`).
- ❌ No hay filtros adicionales: solo `?activo=1|true|yes` (`views.py:787-789`).
- ❌ No hay endpoint dedicado para "calcular", "recalcular", "validar tope", "ver promedio Finagro", "subir recibos", "subir acto administrativo". **Ningún endpoint del módulo hace cálculo.**

### Listado real

```python
# views.py:785-791
def get(self, request, *args, **kwargs):
    qs = AuxilioExterno.objects.all()
    solo_activos = request.query_params.get('activo', '').lower()
    if solo_activos in ('1', 'true', 'yes'):
        qs = qs.filter(activo=True)
    serializer = AuxilioExternoSerializer(qs, many=True)
    return Response(serializer.data)
```

### POST / PUT / DELETE

`POST` (`views.py:793-798`) y `PUT` (`views.py:820-828`) delegan al `ModelSerializer`. `PUT` usa `partial=True`. `DELETE` (`views.py:830-835`) es físico, sin soft-delete, sin verificación de uso.

### Frontend

El frontend (`SigaPage.js:1602`) reutiliza el componente `TabPersonas` que también sirve a Pensionados (`SigaPage.js:1241`):

```jsx
{activeTab === 'auxilio' && <TabPersonas endpoint="auxilio-externo" nombreSingular="auxilio externo" nombrePlural="auxilios externos" />}
```

Mismos campos en el formulario (`FormPersona`, `SigaPage.js:1193-1238`): cédula, nombre, EPS, valor_mensual, fecha_inicio, fecha_fin, activo, observaciones. **No hay UI para cargar recibos, certificación, acto administrativo, ni para visualizar el auxilio calculado.**

---

## Modelo y campos

### Definición completa (`models.py:148–163`)

```python
class AuxilioExterno(models.Model):
    cedula = models.CharField(max_length=20)
    nombre = models.CharField(max_length=200)
    eps = models.CharField(max_length=100)
    valor_mensual = models.DecimalField(max_digits=14, decimal_places=2)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField(null=True, blank=True)
    activo = models.BooleanField(default=True)
    observaciones = models.TextField(blank=True)
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'bs_auxilio_externo'

    def __str__(self):
        return f"{self.cedula} - {self.nombre} [{self.eps}]"
```

Verificado contra el schema real:

```sql
CREATE TABLE "bs_auxilio_externo" (
    "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
    "cedula" varchar(20) NOT NULL,            -- ⚠️ SIN UNIQUE
    "nombre" varchar(200) NOT NULL,
    "eps" varchar(100) NOT NULL,
    "valor_mensual" decimal NOT NULL,
    "fecha_inicio" date NOT NULL,
    "fecha_fin" date NULL,
    "activo" bool NOT NULL,
    "observaciones" text NOT NULL,
    "creado_en" datetime NOT NULL
);
```

### Tabla por campo

| Campo            | Tipo                                | Nullable | Default | Notas                                                                                                                                                                |
|------------------|-------------------------------------|----------|---------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `id`             | autoincrement                       | NO       | auto    | PK                                                                                                                                                                   |
| `cedula`         | varchar(20)                         | NO       | —       | ⚠️ **NO es UNIQUE** (a diferencia de `PensionadoPrepagada.cedula`). Una misma persona puede tener N registros simultáneos sin alerta.                                |
| `nombre`         | varchar(200)                        | NO       | —       | Texto libre, sin normalización.                                                                                                                                      |
| `eps`            | varchar(100) **(más ancho)**        | NO       | —       | Texto libre. No es FK ni `choices`. Aquí cabe `"Colmédica"`, `"Sura"`, `"Sanitas"`, `"Medplus"`, lo que sea.                                                          |
| `valor_mensual`  | decimal(14,2)                       | NO       | —       | Lo que TH digita como "valor del auxilio". No es el certificado, ni el promedio, ni el resultado de un cálculo: es lo que el operador escribe en el form.            |
| `fecha_inicio`   | date                                | NO       | —       | Sin validaciones (futura, pasada > 3 meses, todo entra).                                                                                                              |
| `fecha_fin`      | date                                | SÍ       | NULL    | No la usa nadie excepto la UI para mostrar. El `InformeEFRView` filtra solo por `activo=True`.                                                                       |
| `activo`         | bool                                | NO       | True    | Único campo que filtran las vistas.                                                                                                                                  |
| `observaciones`  | text                                | NO       | `''`    | Texto libre.                                                                                                                                                          |
| `creado_en`      | datetime (`auto_now_add=True`)      | NO       | now()   | Único campo de auditoría.                                                                                                                                            |

### Campos que NO existen (gap explícito contra el manual)

| Campo razonable                       | Estado     | Regla del manual asociada |
|---------------------------------------|------------|---------------------------|
| `valor_certificado_anual` (lo que el empleado paga a su póliza externa)    | ❌ Ausente | MP-019, MP-023            |
| `valor_pagado_efectivo_mes`           | ❌ Ausente | MP-019                    |
| `fecha_certificacion`                 | ❌ Ausente | MP-020                    |
| `vigencia_desde` / `vigencia_hasta` (de la póliza externa) | ❌ Ausente (`fecha_inicio`/`fecha_fin` son del auxilio, no de la póliza) | MP-020 |
| `recibo_mes` (FileField o modelo `ReciboAuxilio`) | ❌ Ausente | MP-021                    |
| `acto_administrativo` (FileField)     | ❌ Ausente | MP-025                    |
| `numero_acto_administrativo`          | ❌ Ausente | MP-025                    |
| `fecha_solicitud` (para validar retroactividad ≤ 3 meses) | ❌ Ausente | MP-022                    |
| `promedio_finagro_aplicado`           | ❌ Ausente | MP-019, MP-024            |
| `auxilio_calculado`                   | ❌ Ausente | MP-019, MP-023            |
| `tope_aplicado` (cuál tope ganó)      | ❌ Ausente | MP-019, MP-023            |
| `creado_por`, `actualizado_en`, `actualizado_por` | ❌ Ausentes | (auditoría general)       |

El modelo **no distingue** entre los conceptos *"lo que el empleado paga a su póliza"* y *"lo que Finagro le reembolsa"*. Solo existe un único `valor_mensual` cuyo significado funcional **no está documentado en el código** ni inferible: depende de qué interprete el usuario que digita.

---

## Validaciones al crear / editar

El serializer (`serializers.py:136–151`) es un `ModelSerializer` puro: declara campos y `read_only_fields = ['creado_en']`. **No tiene `validate()`, `validate_cedula()`, `validate_eps()`, ni `UniqueTogether`.**

```python
class AuxilioExternoSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuxilioExterno
        fields = ['id', 'cedula', 'nombre', 'eps', 'valor_mensual',
                  'fecha_inicio', 'fecha_fin', 'activo', 'observaciones', 'creado_en']
        read_only_fields = ['creado_en']
```

| Pregunta                                                                                | Resultado                                                                                                                            |
|-----------------------------------------------------------------------------------------|--------------------------------------------------------------------------------------------------------------------------------------|
| ¿Valida formato de cédula?                                                              | ❌ No.                                                                                                                                |
| ¿Valida cédula única?                                                                   | ❌ **NO.** `cedula` carece de `unique=True`. La misma cédula puede tener varios auxilios simultáneamente sin error.                  |
| ¿Valida que la cédula NO esté en `BeneficioSalud` (AXA/Colsanitas) del periodo?         | ❌ No. Permite registrar auxilio para una persona que **también** factura por póliza colectiva.                                       |
| ¿Valida que la cédula NO esté en `bs_pensionados_prepagada` activo?                     | ❌ No. Una misma persona puede ser "pensionado MP-006" y "auxilio externo MP-019" al mismo tiempo, sin alerta.                       |
| ¿Valida la EPS contra catálogo?                                                         | ❌ No. Texto libre. Una persona puede tener `eps='Colmedica'`, otra `eps='Colmédica'`, otra `eps='COLMEDICA SA'` — son grupos distintos para el sistema. |
| ¿Valida `fecha_fin >= fecha_inicio`?                                                    | ❌ No.                                                                                                                                |
| ¿Valida `valor_mensual > 0`?                                                            | ❌ No.                                                                                                                                |
| ¿Valida retroactividad ≤ 3 meses (MP-022)?                                              | ❌ No. `fecha_inicio` acepta cualquier fecha.                                                                                         |
| ¿Exige adjuntar certificación / recibos / acto administrativo?                          | ❌ No. No hay campos de adjunto.                                                                                                      |

---

## Motor de cálculo: ¿existe o no?

### Veredicto: ❌ **NO EXISTE.**

Búsquedas realizadas (todas con cero resultados útiles fuera de los puntos abajo):

```bash
$ grep -rn "AuxilioExterno\|auxilio_externo" siga/backend/modules/beneficios_salud/services/
# (vacío)
$ grep -rni "promedio\|reembolso\|recibo\|certificad\|retroact\|acto_admin\|colmedica" siga/backend/
# (vacío)
$ ls siga/backend/modules/beneficios_salud/services/
axa_adapter.py  colsanitas_adapter.py  detector.py  eligibility.py
prepagada_service.py  reader_excel.py  validator.py
```

Evidencias específicas:

1. **`services/eligibility.py` NO consulta `AuxilioExterno`.** Solo importa `PensionadoPrepagada` (`eligibility.py:12`). El árbol de elegibilidad solo conoce dos estados: `PENSIONADO_100`, `ELEGIBLE_80_20`, `BLOQUEADO_CRUCE`. No hay rama "AUXILIO_EXTERNO".
2. **`services/prepagada_service.calcular_planilla` NO consulta `AuxilioExterno`.** Itera sobre `v_cruce` (facturas AXA/Colsanitas), no sobre la tabla de auxilios.
3. **No existe `auxilio_externo_service.py`**, ni función `calcular_auxilio`, ni `promedio_finagro`, ni queries de promedio en ningún módulo.
4. **No hay endpoint de "calcular"** (a diferencia de planilla, que tiene `PlanillaCalcularView`).
5. **El campo `valor_mensual` es completamente manual**: TH lo digita, SIGA lo guarda; no se valida, no se topa, no se compara con un promedio, no se cruza contra `valor_certificado_anual` (que tampoco existe).

### Lo único que SIGA hace con `AuxilioExterno`

- `InformeEFRView` (`views.py:1266-1289`):
  ```python
  auxilio_qs = AuxilioExterno.objects.filter(activo=True)
  auxilio_externo = AuxilioExternoSerializer(auxilio_qs, many=True).data
  total_auxilio = float(auxilio_qs.aggregate(total=Sum('valor_mensual'))['total'] or 0)
  ```
  Lista los activos y suma su `valor_mensual` en el consolidado.

- El consolidado se construye en `views.py:1291-1295`:
  ```python
  'consolidado': {
      'total_empresa': round(total_empresa + total_pensionados, 2),     # ← auxilio NO se suma aquí
      'total_empleado': round(total_empleado, 2),
      'total_general': round(total_empresa + total_empleado + total_pensionados + total_auxilio, 2),
  },
  ```
  ⚠️ **Asimetría detectada:** el auxilio externo **no se suma a `total_empresa`**, pero sí a `total_general`. Pensionados sí se suma a ambos. No queda claro qué intenta representar.

---

## Conexión con planilla / causación / EFR

| Proceso                              | ¿Considera `AuxilioExterno`? | Cómo                                                                                                                                                                            |
|--------------------------------------|------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Cálculo planilla 80/20               | ❌ No                        | `calcular_planilla` itera `v_cruce` (`prepagada_service.py:78`). Una cédula que está en `AuxilioExterno` pero no en `v_cruce` no aparece en la planilla.                        |
| `DetalleCalculo` (filas planilla)    | ❌ No                        | El motor no crea filas por auxilio. No hay `estado_elegibilidad='AUXILIO_EXTERNO_*'` (verificado: no aparece en `eligibility.py` ni en ningún `default=` del modelo).            |
| Causación (`CausacionView`)          | ❌ No                        | Causación agrupa `DetalleCalculo` por EPS (módulo 5 ya verificado). Como los auxilios no generan `DetalleCalculo`, **no figuran en la causación**.                              |
| Conciliación (`ConciliacionView`)    | ❌ No                        | Mismo origen: compara `DetalleCalculo` entre periodos.                                                                                                                          |
| Informe EFR (`InformeEFRView`)       | ✅ Parcial                   | Solo lista los activos y suma `valor_mensual` (líneas 1266-1289). **No filtra por periodo de fecha_inicio/fecha_fin del auxilio.** Sigue sumando incluso si el periodo consultado es anterior al `fecha_inicio` del auxilio o posterior al `fecha_fin`. |
| Exportación de planilla              | ❌ No                        | `PlanillaExportarView` exporta `DetalleCalculo` (sin auxilios).                                                                                                                  |

### Caso real "APOYO MED. PREPAGADA COLMEDICA"

El informe EFR del manual cita el concepto `1037 - I - APOYO MED. PREPAGADA COLMEDICA`. Buscado en código:

```bash
$ grep -rni "colmedica\|1037\|APOYO MED" siga/backend/modules/beneficios_salud/
# (vacío)
```

❌ **SIGA no tiene ni un concepto contable mapeado para auxilios externos** (a diferencia de `cod_conc_apoyo_no_grav`, `cod_conc_apoyo_grav`, `cod_conc_dcto_empleado` que sí existen en `PoliticaPrepagada` para la planilla 80/20 — `models.py:114-116`). Si Colmédica aparece en el EFR oficial, ese reporte se está produciendo **fuera de SIGA** (Excel manual, otro sistema, o causación contable directa).

---

## Las 7 reglas del manual (MP-019..MP-025) — verificación punto por punto

| Regla MP | Texto sintetizado del manual                                                              | Estado en SIGA              | Evidencia                                                                                                                                  |
|----------|-------------------------------------------------------------------------------------------|-----------------------------|--------------------------------------------------------------------------------------------------------------------------------------------|
| MP-019   | Auxilio = MIN(valor pagado por empleado, promedio pólizas Finagro)                        | ❌ **No soportado**         | No existe función de cálculo. `valor_mensual` es texto libre digitado. `grep "min(" services/` no devuelve nada relacionado.               |
| MP-020   | Certificación anual de póliza externa                                                     | ❌ **No soportado**         | No existe campo `fecha_certificacion`, ni `vigencia_*` de póliza, ni adjunto de certificación. Nadie valida vigencia.                       |
| MP-021   | Recibos mensuales para verificar pago                                                     | ❌ **No soportado**         | No existe modelo `ReciboAuxilio` ni `FileField`. `grep -rni "recibo"` retorna cero resultados en el módulo.                                |
| MP-022   | Retroactividad máxima 3 meses                                                              | ❌ **No soportado**         | `fecha_inicio` acepta cualquier fecha. No hay `fecha_solicitud` ni validación temporal.                                                    |
| MP-023   | Tope: el auxilio nunca puede exceder lo pagado                                            | ❌ **No soportado**         | No hay campo `valor_certificado`/`valor_pagado_efectivo`. Sin ese dato, comparar contra `valor_mensual` es imposible.                       |
| MP-024   | Cálculo del promedio de pólizas Finagro                                                   | ❌ **No soportado** + ⚠️ **decisión funcional abierta** | No hay query, función, ni endpoint que calcule el promedio. La definición misma (general / por proveedor / por plan / por grupo familiar) sigue sin decidir. |
| MP-025   | Acto administrativo de autorización                                                       | ❌ **No soportado**         | No hay campo `acto_administrativo`, ni FileField, ni número de acto. No hay flujo de aprobación.                                            |

**Estado neto: 0 de 7 reglas implementadas.** Coincide con la documentación previa de presentación a TH (`docs/presentacion-th/07-auxilio-externo.md`).

---

## Carga masiva (¿existe?)

❌ **No existe.**

- No hay endpoint `POST /auxilio-externo/upload/`.
- No hay management command (`siga/backend/modules/beneficios_salud/management/` no existe).
- El frontend solo expone el formulario uno-a-uno (`SigaPage.js:1193-1238`, `FormPersona`).

---

## Auditoría y adjuntos

| Aspecto                                    | Estado                                                                                                                                |
|--------------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------|
| `creado_en`                                | ✅ Sí (`auto_now_add=True`).                                                                                                          |
| `creado_por`                               | ❌ No.                                                                                                                                 |
| `actualizado_en`                           | ❌ No.                                                                                                                                 |
| `actualizado_por`                          | ❌ No.                                                                                                                                 |
| Log/historial separado                     | ❌ No existe modelo `AuxilioHistorial` ni `LogAuxilio`.                                                                               |
| Trazabilidad de activación/desactivación   | ❌ Ninguna. PUT silencioso a `activo=false` sin rastro.                                                                                |
| Adjuntos (`FileField` / modelo `Adjunto`)  | ❌ Ninguno. Imposible adjuntar certificación, recibos o acto administrativo.                                                          |
| Caída por DELETE                           | ⚠️ DELETE físico (`views.py:834`). Como ningún otro modelo apunta a `AuxilioExterno` por FK, no hay cascada — pero tampoco hay histórico que conservar (no se generan `DetalleCalculo`). |

---

## Comportamientos confirmados / refutados

### Casos solicitados

| # | Caso                                                                                                                                  | Resultado verificado en código                                                                                                                                                                                                                  |
|---|---------------------------------------------------------------------------------------------------------------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 1 | TH registra un auxilio externo de $500.000 mensual                                                                                    | SIGA lo guarda como dato suelto. **No aparece en la planilla** (el motor no lo consulta). Solo aparece en `InformeEFRView` listado y sumado al `total_general` consolidado.                                                                     |
| 2 | Una cédula está en `AuxilioExterno` activo Y también aparece en archivo AXA del mes                                                   | ⚠️ **El sistema NO detecta el conflicto.** Generaría doble beneficio: (a) en planilla con 80/20 vía AXA y (b) en EFR como auxilio externo sumando su `valor_mensual` al consolidado. No hay alerta ni regla que lo prevenga.                     |
| 3 | El EFR oficial menciona `APOYO MED. PREPAGADA COLMEDICA`                                                                              | ❌ Hoy la tabla está vacía (`COUNT(*)=0`). Si en algún momento se llena, SIGA solo lo expondría en `InformeEFRView` con la etiqueta de texto libre que TH escriba. **No hay concepto contable mapeado** (a diferencia de la planilla 80/20).      |
| 4 | TH registra un auxilio sin adjuntar recibos                                                                                            | ✅ **Lo permite sin ninguna fricción.** No hay forma técnica de adjuntar nada; MP-021 está fuera del modelo de datos.                                                                                                                            |
| 5 | Un auxilio termina su vigencia (acto administrativo expira)                                                                            | ⚠️ **No hay automatización.** `fecha_fin` se guarda pero ningún proceso la consulta. El auxilio sigue activo en informes hasta que TH cambie manualmente `activo=False`. No hay alerta ni email.                                                |

### Discrepancias contra la documentación previa (`docs/presentacion-th/07-auxilio-externo.md`)

La presentación previa marcó este módulo como "alto riesgo / motor no implementado". **El código confirma íntegramente esa lectura.** No se detectaron implementaciones parciales no documentadas. Sin embargo:

- ⚠️ Hay **un riesgo no señalado antes**: `AuxilioExterno.cedula` no tiene `unique=True`. Una persona puede tener N auxilios activos simultáneos y el `InformeEFRView` los sumaría todos. En `PensionadoPrepagada` la unicidad sí está garantizada.
- ⚠️ Hay **una asimetría no señalada antes** entre cómo se suma `total_pensionados` (a `total_empresa` Y a `total_general`) y cómo se suma `total_auxilio` (solo a `total_general`). No hay comentario que explique el criterio.

---

## Estado actual de la tabla en BD

Ejecutado contra `siga/backend/db/db.sqlite3`:

```sql
SELECT COUNT(*) FROM bs_auxilio_externo;
-- 0

SELECT COUNT(*), SUM(CASE WHEN activo=1 THEN 1 ELSE 0 END) FROM bs_auxilio_externo;
-- 0 | 0
```

✅ **Tabla vacía.** Cero registros totales, cero activos. Confirma que el módulo está en versión de prueba / espera funcional, igual que `bs_pensionados_prepagada`.

No es posible analizar distribución por EPS porque no hay datos. Si TH usa Colmédica hoy, ese registro **no está en SIGA** — se lleva por otro mecanismo (Excel, causación directa, etc.).

---

# Resumen ejecutivo del módulo

## ✅ Lo que SÍ hace

- Persistencia de altas, ediciones, bajas y borrados físicos vía CRUD plano (`AuxilioExternoView`, `AuxilioExternoDetailView`).
- Filtro opcional por `?activo=1|true|yes` en el listado.
- Reúso del mismo formulario del módulo Pensionados en la UI (`TabPersonas` + `FormPersona`).
- Inclusión de auxilios activos en `InformeEFRView` con suma de `valor_mensual` al consolidado (`total_general`).
- Campo `eps` con texto libre y ancho mayor (100 chars vs 50 en Pensionados) — el único soporte real para "tercer proveedor" tipo Colmédica/Sura/Sanitas.

## ❌ Lo que NO hace

- **No tiene motor de cálculo.** `valor_mensual` es 100% manual. Ninguna de las 7 reglas MP-019..MP-025 está implementada.
- **No calcula promedio Finagro** ni hay decisión técnica sobre cómo calcularlo.
- **No valida tope contra valor pagado** (porque ni siquiera tiene campo "valor pagado").
- **No exige ni almacena**: certificación anual, recibos mensuales, acto administrativo.
- **No valida retroactividad** ≤ 3 meses ni cualquier otra restricción temporal.
- **No valida unicidad de cédula** (a diferencia de Pensionados).
- **No valida coherencia** con la planilla AXA/Colsanitas ni con `bs_pensionados_prepagada` — permite doble beneficio sin alerta.
- **No conecta con causación** ni con `DetalleCalculo`. Los auxilios viven en una silos paralela.
- **No tiene auditoría real** más allá de `creado_en`.
- **No tiene adjuntos** ni `FileField` ni modelo `AdjuntoAuxilio`.
- **No tiene workflow de aprobación**.
- **No tiene carga masiva**.
- **No filtra por periodo** en `InformeEFRView`: una vigencia caduca (`fecha_fin` pasada) sigue sumando si `activo=True`.
- **No mapea un concepto contable** propio (no hay `cod_conc_auxilio_externo` en `PoliticaPrepagada`).
- **No expone el "auxilio calculado"** porque no hay cálculo: lo que la UI muestra es lo mismo que se digita.

## ⚠️ Pendiente validar con TH

- **Decisión funcional bloqueante:** definición operativa del "promedio Finagro" para MP-019. Cuatro hipótesis sin resolver (general / por proveedor / por plan / por grupo familiar). Sin esto, ni siquiera podemos diseñar el motor.
- ¿Hoy quién registra/maneja los auxilios externos en la práctica? ¿Excel propio? ¿Bolt-on al EFR final? ¿Causación directa por contabilidad?
- ¿`valor_mensual` lo digita TH como (a) lo que paga el empleado a su póliza, (b) el auxilio que Finagro reembolsa, o (c) ambos confundidos? **El código no lo aclara**; depende de cómo lo use el usuario hoy.
- ¿Es aceptable que una cédula pueda tener N auxilios externos simultáneos? Si no, hay que poner `unique=True` (con o sin compuesta con `fecha_inicio`).
- ¿Es aceptable que un auxilio se acumule al EFR consolidado incluso si su `fecha_fin` ya pasó? ¿O debe filtrarse por periodo?
- ¿Los recibos mensuales (MP-021) realmente se exigen hoy en papel/Drive, o también en la práctica se omiten? La respuesta orienta si SIGA debe forzarlos o solo "permitirlos".
- ¿El concepto contable que debería usar SIGA al causar auxilios externos (equivalente al `cod_conc_apoyo_no_grav` de 80/20) es uniforme o depende del proveedor (`1037 COLMEDICA`, `1038 SURA`, etc.)?
- ¿Existe hoy un acto administrativo formal para cada auxilio? Si sí, ¿debe SIGA guardarlo como adjunto o solo como número de referencia?
