# Módulo 6 — Pensionados: Investigación Técnica

| Campo            | Valor                                                                                       |
|------------------|---------------------------------------------------------------------------------------------|
| Fecha            | 2026-05-14                                                                                  |
| Generado por     | Verificación directa de código fuente                                                       |
| Archivos leídos  | `urls.py`, `views.py` (720–776, 1200–1296), `serializers.py` (118–133), `models.py` (130–145), `services/eligibility.py`, `services/prepagada_service.py`, `admin.py`, frontend `SigaPage.js` (1193–1334) |
| Verificación BD  | `bs_pensionados_prepagada` (`db.sqlite3`) y `v_cruce` (`prepagada.db`)                       |
| Apoyo previo     | Modelo `PensionadoPrepagada` con `cedula UNIQUE` (módulo 3, `models.py:131`); regla MP-006 ya cableada en `eligibility.py:38–50`; H2 confirmado (columna `NOM` no se lee). |

---

## CRUD: endpoints disponibles

Los endpoints están registrados en `urls.py:27-28`:

```python
path('pensionados/', PensionadosView.as_view()),
path('pensionados/<int:pk>/', PensionadoDetailView.as_view()),
```

Implementados en dos `APIView` simples sin paginación, sin permisos, sin autenticación explícita:

| Método | Ruta                                       | Vista                           | Líneas (`views.py`) |
|--------|--------------------------------------------|---------------------------------|---------------------|
| GET    | `/api/beneficios-salud/pensionados/`       | `PensionadosView.get`           | 726–732             |
| POST   | `/api/beneficios-salud/pensionados/`       | `PensionadosView.post`          | 734–739             |
| GET    | `/api/beneficios-salud/pensionados/<pk>/`  | `PensionadoDetailView.get`      | 755–759             |
| PUT    | `/api/beneficios-salud/pensionados/<pk>/`  | `PensionadoDetailView.put`      | 761–769             |
| DELETE | `/api/beneficios-salud/pensionados/<pk>/`  | `PensionadoDetailView.delete`   | 771–776             |

### Detalles del listado (`views.py:726–732`)

```python
def get(self, request, *args, **kwargs):
    qs = PensionadoPrepagada.objects.all()
    solo_activos = request.query_params.get('activo', '').lower()
    if solo_activos in ('1', 'true', 'yes'):
        qs = qs.filter(activo=True)
    serializer = PensionadoPrepagadaSerializer(qs, many=True)
    return Response(serializer.data)
```

- ❌ **No hay paginación.** Devuelve todos los registros en un solo array.
- ❌ **No hay búsqueda** por cédula, nombre o EPS desde el endpoint (el frontend filtra en cliente si quiere).
- ❌ **No hay filtros adicionales:** solo `?activo=1|true|yes` actúa; cualquier otro valor (`0`, `false`, ausente) **devuelve activos + inactivos mezclados**.
- ❌ **No hay endpoint dedicado de "activar/desactivar".** Se cambia mediante `PUT /pensionados/<pk>/` con `{"activo": true|false}` (gracias a `partial=True` en `views.py:765`).
- ❌ **No hay ordenamiento explícito en la API.** El `Meta` del modelo (`models.py:141–142`) **no define `ordering`**, así que SQLite devuelve por `id` ascendente — el frontend (`SigaPage.js:1306`) muestra los items tal cual.

### POST y PUT

Ambos delegan 100% al `ModelSerializer` (sin `validate_*` propios):

```python
# POST (views.py:734-739)
serializer = PensionadoPrepagadaSerializer(data=request.data)
if serializer.is_valid():
    serializer.save()
    return Response(serializer.data, status=status.HTTP_201_CREATED)
return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
```

### DELETE

Físico, sin soft-delete, sin confirmación de uso histórico (`views.py:771–776`):

```python
def delete(self, request, pk, *args, **kwargs):
    obj = self._get_object(pk)
    if obj is None:
        return Response({'error': f'Pensionado con id={pk} no encontrado.'}, status=status.HTTP_404_NOT_FOUND)
    obj.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)
```

---

## Modelo y campos: qué se guarda, qué falta

### Definición completa (`models.py:130–145`)

```python
class PensionadoPrepagada(models.Model):
    cedula = models.CharField(max_length=20, unique=True)
    nombre = models.CharField(max_length=200)
    eps = models.CharField(max_length=50)
    valor_mensual = models.DecimalField(max_digits=14, decimal_places=2)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField(null=True, blank=True)
    activo = models.BooleanField(default=True)
    observaciones = models.TextField(blank=True)
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'bs_pensionados_prepagada'
```

Verificado contra el schema real en SQLite:

```sql
CREATE TABLE "bs_pensionados_prepagada" (
    "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
    "cedula" varchar(20) NOT NULL UNIQUE,
    "nombre" varchar(200) NOT NULL,
    "eps" varchar(50) NOT NULL,
    "valor_mensual" decimal NOT NULL,
    "fecha_inicio" date NOT NULL,
    "fecha_fin" date NULL,
    "activo" bool NOT NULL,
    "observaciones" text NOT NULL,
    "creado_en" datetime NOT NULL
);
```

### Tabla por campo

| Campo            | Tipo                                 | Nullable | Default | Editable UI | Notas                                                                                          |
|------------------|--------------------------------------|----------|---------|-------------|------------------------------------------------------------------------------------------------|
| `id`             | autoincrement                        | NO       | auto    | NO          | PK                                                                                             |
| `cedula`         | varchar(20) **UNIQUE**               | NO       | —       | SÍ          | Texto, no numérico. La unicidad da el "no duplicados" gratis.                                  |
| `nombre`         | varchar(200)                         | NO       | —       | SÍ          | No hay normalización (mayúsculas, trim, sin acentos).                                          |
| `eps`            | varchar(50)                          | NO       | —       | SÍ          | **Texto libre.** No es FK ni `choices`. Cualquier string entra.                                |
| `valor_mensual`  | decimal(14,2)                        | NO       | —       | SÍ          | El motor 80/20 **no lo usa** (calcula sobre `total_familia` del cruce); solo lo lee `InformeEFRView`. |
| `fecha_inicio`   | date                                 | NO       | —       | SÍ          | Sin validaciones (puede ser futura, puede ser anterior a `fecha_fin`).                         |
| `fecha_fin`      | date                                 | SÍ       | NULL    | SÍ          | **NO se usa para nada en el motor.** El motor solo mira `activo`.                              |
| `activo`         | bool                                 | NO       | **True**| SÍ          | Lo único que el motor consulta (eligibility.py:38).                                            |
| `observaciones`  | text                                 | NO       | `''`    | SÍ          | Texto libre, sin formato.                                                                       |
| `creado_en`      | datetime (`auto_now_add=True`)       | NO       | now()   | NO          | Único campo de auditoría.                                                                       |

### Campos que NO existen (gaps detectados)

| Campo razonable                | Estado | Implicación                                                                                  |
|--------------------------------|--------|----------------------------------------------------------------------------------------------|
| `fecha_pension`                | ❌ Ausente | No se distingue *fecha en que pasó a pensionado* vs *fecha de alta del beneficio en SIGA*. `fecha_inicio` parece ocupar ambos roles. |
| `motivo` (jubilación / invalidez / supervivencia) | ❌ Ausente | No queda registro tipificado del tipo de pensión.                                            |
| `actualizado_en`               | ❌ Ausente | No se sabe cuándo fue el último cambio (toggle activo/inactivo, ajuste de valor, etc.).      |
| `creado_por`                   | ❌ Ausente | Nadie firma el alta del pensionado.                                                          |
| `actualizado_por`              | ❌ Ausente | Tampoco se firma quién desactivó / reactivó.                                                 |
| `documento_soporte` / FileField| ❌ Ausente | No se puede adjuntar acto administrativo, cédula, etc.                                       |
| `aprobado_por` / `aprobado_en` | ❌ Ausente | No hay flujo de aprobación.                                                                  |
| `revisado_en` / vigencia       | ❌ Ausente | No hay disparador de revisión periódica.                                                     |

---

## Validaciones al crear / editar

El serializer (`serializers.py:118–133`) es un `ModelSerializer` puro: declara campos y `read_only_fields = ['creado_en']`. **No tiene `validate()`, `validate_cedula()`, `validate_eps()`, ni constraints adicionales.**

```python
class PensionadoPrepagadaSerializer(serializers.ModelSerializer):
    class Meta:
        model = PensionadoPrepagada
        fields = ['id', 'cedula', 'nombre', 'eps', 'valor_mensual',
                  'fecha_inicio', 'fecha_fin', 'activo', 'observaciones', 'creado_en']
        read_only_fields = ['creado_en']
```

Las **únicas** validaciones efectivas son las heredadas del modelo:

| Pregunta                                                                          | Respuesta                                                                                                              |
|-----------------------------------------------------------------------------------|------------------------------------------------------------------------------------------------------------------------|
| ¿Valida formato de cédula (longitud mínima, solo dígitos, sin espacios)?          | ❌ NO. `CharField(max_length=20)`. Acepta `"abc"`, `"12 34"`, vacíos no — porque es `NOT NULL` y DRF exige el campo.   |
| ¿Valida unicidad de cédula?                                                       | ✅ SÍ, por la constraint `UNIQUE`. Si se duplica, DRF retorna `400` con el mensaje estándar: `"pensionado prepagada with this cedula already exists."` (en inglés, no localizado). |
| ¿Valida que el nombre no esté vacío?                                              | ⚠️ Parcial. `CharField` con `max_length=200` y sin `blank=True` requiere un valor; pero `" "` (un espacio) pasaría sin trim. |
| ¿Valida que `eps` corresponda a `axa`/`colsanitas`?                               | ❌ NO. **Texto libre.** Puede registrar `"AXA"`, `"axa"`, `"AXA Colpatria"`, `"colsanitas"`, `"Sura"` — todo entra. Esto es relevante porque el motor filtra por `eps__iexact` (ver siguiente sección). |
| ¿Valida coherencia con la BD externa (cédula existe en `BeneficioSalud`)?         | ❌ NO. Se puede registrar como pensionado a una cédula que nunca apareció en factura AXA/Colsanitas.                   |
| ¿Valida que esa cédula no esté como empleado activo en Kactus / `v_cruce`?       | ❌ NO. SIGA permite tener la misma cédula en `bs_pensionados_prepagada` (activa) **y** en `empleados_kactus` con `ind_acti != 'I'`. La regla MP-006 ganaría en el motor (corre primero), pero no hay alerta operativa. |
| ¿Valida que `fecha_fin >= fecha_inicio`?                                          | ❌ NO.                                                                                                                  |
| ¿Valida que `valor_mensual > 0`?                                                  | ❌ NO. Acepta 0 e incluso negativos.                                                                                    |

---

## Activo vs inactivo: semántica e impacto

### Valor por defecto

`activo = models.BooleanField(default=True)` (`models.py:137`). **Cualquier nuevo registro nace activo** — y, por tanto, **inmediatamente entra en la regla MP-006** desde el siguiente recálculo de planilla.

### Cómo se cambia

- Desde el frontend: un checkbox simple en `FormPersona` (`SigaPage.js:1226-1228`):
  ```jsx
  <input type="checkbox" checked={form.activo} onChange={e => set('activo', e.target.checked)} />
  ```
  El frontend envía `PUT /pensionados/<id>/` con el body completo. Como el backend usa `partial=True` (`views.py:765`), también admite `PUT` con solo `{"activo": false}`.
- ❌ **No hay endpoint dedicado** (`/pensionados/<id>/desactivar/`).
- ❌ **No hay confirmación adicional** ni registro de la operación.

### Impacto en histórico

**Las planillas pasadas NO cambian retroactivamente porque `DetalleCalculo` es persistente.** Cada vez que se calcula una planilla, los resultados de elegibilidad quedan congelados en la fila de `DetalleCalculo` (campos `tipo_persona`, `estado_elegibilidad`, `motivo_elegibilidad`, `porcentaje_*_aplicado`, `valor_empresa`, `valor_empleado`). Verificado en módulo 3.

⚠️ **Pero recalcular SÍ usa el estado actual.** En `prepagada_service.py:96`:

```python
elegibilidad = evaluar_elegibilidad(r, politica)
```

`evaluar_elegibilidad` (`eligibility.py:38`) consulta `PensionadoPrepagada.objects.filter(cedula=cedula, activo=True)` **en vivo**. Implicaciones:

- Si TH desactiva un pensionado **hoy** y mañana recalcula la planilla de marzo, ese pensionado dejará de ser PENSIONADO_100 en la planilla recalculada (pasaría a 80/20 si el cruce está OK, o a BLOQUEADO_CRUCE si no está en Kactus activo).
- La planilla anterior (`PlanillaCalculo` ya existente) NO se modifica: el motor crea una **nueva** `PlanillaCalculo` cada vez (`PlanillaCalcularView` no hace `update_or_create`, solo `create`; queda la más reciente como "vigente" para Causación). Esto coincide con lo visto en módulo 5 (`order_by('-generada_en').first()`).

### Reactivación

La constraint `cedula UNIQUE` **impide crear un nuevo registro** para una cédula ya existente — incluso si está inactivo. El error en POST sería `400` con `"pensionado prepagada with this cedula already exists."`. Para reactivar, la única vía es **editar el mismo registro** (PUT con `activo=true`). El frontend no tiene un flujo explícito de "reactivar"; el usuario tiene que entrar a editar el registro inactivo (que sigue visible porque el listado por defecto trae también inactivos).

⚠️ **Riesgo UX:** un usuario que use `?activo=1` en su listado no verá los inactivos; podría intentar crear uno nuevo, recibir error confuso y no saber que ya existía la entrada.

---

## Cómo se conecta con el motor de cálculo

### Flujo end-to-end

1. `PlanillaCalcularView` invoca `calcular_planilla(periodo, politica)` (`prepagada_service.py:67`).
2. `calcular_planilla` itera sobre `v_cruce` (filas de **facturas EPS del periodo** con LEFT JOIN a empleados_kactus).
3. Para cada fila llama `evaluar_elegibilidad(r, politica)` (`prepagada_service.py:96`).
4. Si retorna `PENSIONADO_100`, deja `valor_empresa=0`, `valor_empleado=total_familia`, apoyos en 0 (`prepagada_service.py:98–119`).

### Filtro real en `eligibility.py:33–50`

```python
def evaluar_elegibilidad(row: dict, politica) -> EligibilityResult:
    cedula = str(row.get('cedula') or '').strip()
    eps = str(row.get('eps') or '').strip()
    estado_cruce = str(row.get('estado') or '').strip().upper()

    pensionado_qs = PensionadoPrepagada.objects.filter(cedula=cedula, activo=True)
    if eps:
        pensionado_qs = pensionado_qs.filter(eps__iexact=eps)

    if pensionado_qs.exists():
        return EligibilityResult(
            tipo_persona=TIPO_PENSIONADO,
            estado_elegibilidad=PENSIONADO_100,
            ...
        )
```

Observaciones:

| Pregunta                                                                    | Respuesta                                                                                              |
|-----------------------------------------------------------------------------|--------------------------------------------------------------------------------------------------------|
| ¿Filtra por `eps` además de `cedula`?                                      | ✅ SÍ, **siempre que `row.eps` no esté vacío.** Usa `eps__iexact` (case-insensitive, exact match).      |
| ¿`cedula` es exact o iexact?                                                | Exact match (sin `__iexact`). Como `cedula` en `v_cruce.facturas_eps.cedula` es `INTEGER` y aquí es `CharField`, **el cast a string usa la representación numérica** (`str(int)`), sin ceros a la izquierda. Si TH registra `"012345"` con cero inicial pero la factura trae `12345`, **no matchea**. |
| ¿La regla MP-006 corre antes que el chequeo de cruce `OK`?                  | ✅ SÍ. Si la cédula está activa en `bs_pensionados_prepagada`, retorna `PENSIONADO_100` aunque `estado_cruce` sea `NO ENCONTRADO` o `INACTIVO` (no llega al `if estado_cruce != 'OK'`). |
| ¿Qué pasa si la persona tiene póliza AXA Y Colsanitas, registrada solo en una? | El registro coincide solo con la fila de `v_cruce` cuya `eps` matchee (case-insensitive) el `eps` guardado. La otra fila recae en 80/20 si el cruce es OK. **Resultado: MP-006 aplica solo a la EPS registrada.** |

⚠️ **Caso límite peligroso (`eps` texto libre):** TH puede escribir `"AXA Colpatria"` en el campo `eps` del pensionado, mientras la factura trae `eps='AXA'` (valor real de `facturas_eps.eps`, ver schema). `eps__iexact='AXA Colpatria'` **no matchea** `'AXA'`, así que el motor aplicaría 80/20 — silenciosamente. No hay validación que prevenga esto.

### Caso "pensionado no aparece en v_cruce del periodo"

Si un pensionado activo no tiene factura del mes (la EPS no lo cobró), simplemente **no aparece en la planilla** — el motor itera sobre filas de `v_cruce`, no sobre la tabla de pensionados. Donde sí aparece es en `InformeEFRView` (`views.py:1260–1264`), que lista los activos en `bs_pensionados_prepagada` aparte y suma su `valor_mensual` al consolidado. **Esa suma se acumula a `total_empresa`**, lo cual es un comportamiento que TH debería validar — el manual dice que el pensionado asume 100%, no que la empresa lo asume.

Ver `views.py:1292`:
```python
'total_empresa': round(total_empresa + total_pensionados, 2),
```
⚠️ **Aparente inconsistencia:** la regla MP-006 deja `valor_empresa=0` en la planilla, pero el informe EFR suma `valor_mensual` de pensionados a `total_empresa`. **Pendiente confirmar con TH si esto es intencional.**

---

## Carga masiva (¿existe?)

❌ **No existe.**

- No hay endpoint `POST /pensionados/upload/` ni `import/`.
- No hay management command bajo `siga/backend/modules/beneficios_salud/management/` (la carpeta no existe — verificado con `find`).
- El único `UploadView` del módulo (`urls.py:16`) es para archivos AXA/Colsanitas de facturación, no para pensionados.

Si TH tiene que registrar 50 pensionados (por ejemplo, un programa de retiro), **debe hacerlo uno por uno desde la UI**. Cada `POST` es una transacción independiente; si uno duplicado falla, los anteriores quedan creados sin rollback.

---

## Auditoría: ¿quién registró, cuándo, por qué?

Lo único que persiste hoy:

```python
creado_en = models.DateTimeField(auto_now_add=True)
```

❌ **No hay `creado_por`** (a diferencia de `PoliticaPrepagada`, que sí tiene `creada_por` — `models.py:120`).
❌ **No hay `actualizado_en`** ni `actualizado_por`.
❌ **No hay tabla de historial** (`PensionadoHistorial`, `LogPensionado`, etc.) — verificado con `grep -rn "PensionadoHistorial\|LogPensionado" siga/`, sin resultados.
❌ **No hay registro de quién activa/desactiva.** Un `PUT activo=false` simplemente sobrescribe la columna; no queda rastro.

### Implicación: trazabilidad imposible

Si en marzo TH duda si un pensionado estaba activo o no para el cálculo:
- ✅ La fila `DetalleCalculo` de esa planilla sí guarda `tipo_persona`, `estado_elegibilidad`, `motivo_elegibilidad` (verificado en módulo 3) — esto da evidencia *post-hoc* del estado en el momento del cálculo.
- ❌ Pero **no hay forma de saber quién activó o desactivó al pensionado**, ni cuándo fue el cambio.
- ❌ Si recalculan la planilla **el estado cambia** sin advertencia.

---

## Adjuntos documentales

❌ **No existen.**

- `PensionadoPrepagada` no tiene `FileField`, `ImageField`, ni FK a un modelo `Adjunto`.
- No hay modelo de adjuntos en `models.py` (verificado por inspección completa del archivo).
- El admin Django (`admin.py:100–116`) tampoco expone subida de archivos.

Si TH necesita conservar el acto administrativo de pensión, copia de cédula, o cualquier soporte legal, debe gestionarlo **fuera de SIGA** (drive, expediente físico, etc.).

---

## Sincronización con fuentes externas

❌ **El módulo es 100% manual.** Verificado:

- ❌ No hay job/cron de sincronización (`grep -rn "celery\|schedule\|cron" siga/backend/modules/beneficios_salud/` — sin resultados).
- ❌ No hay management command que actualice la tabla.
- ❌ La columna `NOM` (ACT/PNS) del archivo AXA **no se lee** — H2 ya confirmado. En `axa_adapter.py:13` el `COLUMN_MAP` mapea `NOMBRE → nombre`, pero **no existe entrada para `NOM`** (ni `tipo`, ni `pensionado`). Las columnas que el adapter conserva son solo `tipo_id`, `tipo_plan`, `fecha_nacimiento` (`axa_adapter.py:59`).
- ❌ No hay integración con Kactus para detectar empleados que pasan a `ind_acti = 'I'` por jubilación. La función `get_empleados_kactus()` (`prepagada_service.py:176–195`) existe pero **no se usa en este módulo** (solo aparece referenciada en comentarios — "útil para detección de pensionados y validaciones cruzadas").

Toda alta, baja o reactivación depende de que TH la haga manualmente desde la UI.

---

## Comportamientos confirmados / refutados

### Casos solicitados

| # | Caso                                                                                                                              | Resultado verificado en código                                                                                                                                                                                                                                          |
|---|-----------------------------------------------------------------------------------------------------------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 1 | Cédula con `NOM=PNS` en archivo AXA pero NO en `bs_pensionados_prepagada`                                                         | El motor le aplica **80/20** (o `BLOQUEADO_CRUCE` si Kactus la marca inactiva). H2 garantiza que la columna `NOM` no se lee. **Riesgo de negocio confirmado.**                                                                                                            |
| 2 | Cédula activa en `bs_pensionados_prepagada` pero ausente de `v_cruce` del periodo                                                  | **No aparece en la planilla** (el motor itera sobre `v_cruce`). Aparece en `InformeEFRView` como pensionado activo, con su `valor_mensual` sumado a `total_empresa` del consolidado (`views.py:1292`).                                                                    |
| 3 | Registrado con `eps='AXA'`, pero el archivo del mes la trae con cargo a Colsanitas (`eps='COLSANITAS'`)                            | `eps__iexact='AXA'` **no matchea** `'COLSANITAS'` → recae en 80/20 si cruce OK. **MP-006 NO se aplica.** Sin alerta operativa.                                                                                                                                            |
| 4 | TH registra un pensionado después de calcular la planilla del mes                                                                 | La planilla existente **no cambia** (DetalleCalculo persiste). Si recalculan, el motor crea **una nueva** `PlanillaCalculo` aplicando MP-006 al pensionado nuevo. No hay notificación automática.                                                                          |
| 5 | TH elimina (DELETE) un pensionado con `DetalleCalculo` históricos                                                                 | `DetalleCalculo` **no tiene FK** a `PensionadoPrepagada` — solo guarda la `cedula` como `CharField` (`models.py:187`). El `obj.delete()` (`views.py:775`) borra únicamente la fila maestra; **los `DetalleCalculo` quedan intactos**. No hay CASCADE, no se pierde histórico. |
| 6 | Conteo hoy en BD                                                                                                                  | `SELECT COUNT(*) FROM bs_pensionados_prepagada` = **0**. `WHERE activo=1` = **0**. La tabla está vacía en `siga/backend/db/db.sqlite3`. **Cualquier persona marcada PNS hoy en el archivo AXA está siendo tratada como empleada con 80/20.**                                |
| 7 | Cédulas con `PNS` en archivo AXA pero no registradas                                                                              | No se puede verificar desde SQLite porque la columna `NOM` no se persiste en `bs_beneficios_salud` ni en `facturas_eps`. **Pendiente: análisis directo del Excel original de AXA** (fuera del alcance de esta investigación).                                              |

### Reglas del manual THU-DOC-002 §10.4

> *"Se podrán incluir en las pólizas colectivas a los pensionados de FINAGRO, quienes asumen la totalidad del pago respectivo beneficiándose únicamente de la reducción de valor por afiliación en póliza colectiva."*

| Dimensión del manual                                | Cubierta en código                                                                                          |
|-----------------------------------------------------|-------------------------------------------------------------------------------------------------------------|
| El pensionado asume 100% del valor                  | ✅ MP-006 aplica `porcentaje_empleado=100`, `porcentaje_empresa=0`.                                          |
| Acceso a tarifa colectiva (vs individual)           | ⚠️ Implícito: si TH desactiva al pensionado, este desaparece de la planilla colectiva y debería pasar a tarifa individual; **el sistema no lo notifica ni gestiona**. |
| Quién aprueba la inclusión                          | ❌ No modelado. No hay campo `aprobado_por`, no hay workflow.                                                |
| Qué documentación se requiere                       | ❌ No modelado. No hay adjuntos.                                                                             |
| Proceso para retiro                                 | ❌ No modelado. El "retiro" es un PUT silencioso a `activo=false` o un DELETE físico.                       |
| Revisión periódica                                  | ❌ No modelado. `fecha_fin` existe pero el motor no la consulta.                                             |

---

# Resumen ejecutivo del módulo

## ✅ Lo que SÍ hace
- Tabla `bs_pensionados_prepagada` con cédula única, persistente y consultable.
- CRUD completo (GET listado, GET detalle, POST, PUT con partial, DELETE) en `PensionadosView` y `PensionadoDetailView` (`views.py:720-776`).
- Filtro opcional `?activo=1|true|yes` en el listado.
- Conexión con el motor: si una cédula está `activo=True` y la `eps` (case-insensitive) matchea la EPS de la factura, se le aplica `PENSIONADO_100` (`eligibility.py:38-50`, `prepagada_service.py:98-119`).
- La regla MP-006 **corre antes** del chequeo de cruce Kactus, por lo que un pensionado registrado **sí se acredita aunque Kactus lo marque inactivo o no lo encuentre**.
- El histórico de planillas es seguro frente a borrados: `DetalleCalculo` guarda la cédula como string y no cascadea.
- Resumen en `InformeEFRView`: lista pensionados activos y suma `valor_mensual` aparte del bloque de planilla (`views.py:1260-1264`).

## ❌ Lo que NO hace
- **No lee la columna `NOM` (ACT/PNS) del archivo AXA** → si TH no registra manualmente al pensionado, se le aplica 80/20 (H2 confirmado).
- **No valida formato de cédula** ni que coincida con la representación de `v_cruce` (ceros a la izquierda, espacios).
- **No valida la EPS contra un catálogo** → texto libre. `"AXA Colpatria"` vs `"AXA"` en factura es desajuste silencioso.
- **No tiene paginación, búsqueda ni filtros avanzados** en el listado.
- **No tiene carga masiva.** Ni endpoint, ni management command.
- **No tiene auditoría más allá de `creado_en`**: no hay `creado_por`, no hay `actualizado_en/por`, no hay log/historial.
- **No tiene adjuntos documentales.**
- **No tiene workflow de aprobación** (un usuario puede crear/borrar pensionados sin firma).
- **No tiene sincronización con fuentes externas** (Kactus, RRHH, archivos AXA). Es 100% manual.
- **No usa `fecha_fin` para autoexpirar.** Una fecha pasada no desactiva al pensionado; sigue siendo elegible hasta que TH lo cambie a mano.
- **No alerta al recalcular planillas pasadas** que un cambio actual de estado afectará la planilla recalculada.

## ⚠️ Pendiente validar con TH
- ¿Es intencional que `InformeEFRView` sume `valor_mensual` de pensionados a `total_empresa` del consolidado (`views.py:1292`), si en realidad el pensionado asume el 100%? Parece doble conteo / lectura del manual a verificar.
- ¿Cómo opera hoy operacionalmente: cuándo y por quién se registran las altas y bajas?
- ¿Quién y cómo se entera SIGA cuando un empleado se jubila? Hoy ningún job lo detecta; ¿hay un comunicado RH → equipo SIGA?
- ¿Hay registros pasados de pensionados (en Excel, en mente del equipo) que deban migrarse? La tabla está vacía hoy.
- ¿Acepta TH que un DELETE no deja rastro de quién lo hizo? ¿O hay que migrar a soft-delete + audit log?
- Caso `eps` con sinónimos (`"AXA"`, `"AXA Colpatria"`, `"Colpatria"`): ¿debemos cerrar el campo a un `choices` igual que `ArchivoRecibido.PROVEEDOR_CHOICES`?
- Caso multi-EPS (una persona con AXA Y Colsanitas registrada solo en una): ¿se espera MP-006 solo a esa EPS o a ambas?
