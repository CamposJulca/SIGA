# Módulo 8 — Política 80/20: Investigación Técnica

| Campo            | Valor                                                                                                                                                                                                                                              |
|------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Fecha            | 2026-05-14                                                                                                                                                                                                                                          |
| Generado por     | Verificación directa de código fuente                                                                                                                                                                                                                |
| Archivos leídos  | `urls.py` (25–26), `views.py` (669–717, 838–909), `serializers.py` (97–115), `models.py` (108–127), `services/eligibility.py` (66–67), `services/prepagada_service.py` (78–81, 146–171), `admin.py` (82–97), frontend `SigaPage.js` (1336–1499)      |
| Verificación BD  | `bs_politica_prepagada` — 1 fila; `bs_planilla_calculo` — 1 planilla FK→politica_id=1                                                                                                                                                                |
| Apoyo previo     | MP-032 confirmado (`views.py:860` toma `order_by('-vigente_desde').first()`); FK PROTECT en `PlanillaCalculo.politica` (`models.py:168`); causación no expone códigos PUC (módulo 5).                                                                |

---

## ⚠️ Aclaración: divergencia entre el prompt y el código real

El prompt menciona campos `nombre`, `vigente_hasta`, `activa`, `concepto_no_gravable`, `concepto_gravable`, `concepto_descuento_empleado`. **Ninguno existe** en el modelo real. El esquema verificado (`models.py:108–127` y `sqlite .schema bs_politica_prepagada`) tiene otros nombres. Esto se reporta tal cual; ver tabla en "Modelo y campos completos".

---

## CRUD: endpoints disponibles

Registrados en `urls.py:25-26`:

```python
path('politica/', PoliticaView.as_view()),
path('politica/<int:pk>/', PoliticaDetailView.as_view()),
```

| Método | Ruta                                  | Vista                          | Líneas (`views.py`) |
|--------|---------------------------------------|--------------------------------|---------------------|
| GET    | `/api/beneficios-salud/politica/`     | `PoliticaView.get`             | 675–678             |
| POST   | `/api/beneficios-salud/politica/`     | `PoliticaView.post`            | 680–688             |
| GET    | `/api/beneficios-salud/politica/<pk>/`| `PoliticaDetailView.get`       | 703–707             |
| PUT    | `/api/beneficios-salud/politica/<pk>/`| `PoliticaDetailView.put`       | 709–717             |
| ❌ DELETE | —                                   | **No existe**                  | —                   |

### Características del listado (`views.py:675-678`)

```python
def get(self, request, *args, **kwargs):
    qs = PoliticaPrepagada.objects.all()
    serializer = PoliticaPrepagadaSerializer(qs, many=True)
    return Response(serializer.data)
```

- ❌ Sin paginación.
- ❌ Sin filtro `?activo=...` (no existe el campo).
- ❌ Sin filtro `?año=...` ni `?vigente_en=...`.
- ❌ Sin ordenamiento explícito en el endpoint. El modelo sí declara `ordering = ['-vigente_desde']` (`models.py:124`), así que SQLite las devuelve más reciente primero — **el listado del endpoint sí queda ordenado**, pero el motor de planilla NO depende de ese orden (usa `order_by('-vigente_desde').first()` explícito).

### POST (`views.py:680-688`)

```python
def post(self, request, *args, **kwargs):
    data = request.data.copy()
    if not data.get('creada_por') and request.user and request.user.is_authenticated:
        data['creada_por'] = request.user.username
    serializer = PoliticaPrepagadaSerializer(data=data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
```

⚠️ Es **el único endpoint del módulo BS que captura `creada_por` del `request.user`** — pero solo si el usuario está autenticado. Como SIGA no fuerza autenticación (todas las APIView usan defaults), en práctica casi siempre llega como string vacía (la BD actual confirma esto: `creada_por = ''`).

### PUT (`views.py:709-717`)

`PUT` con `partial=True`. **Permite editar cualquier campo, incluidos `vigente_desde`, `valor_uvt`, `porcentaje_empresa`, `porcentaje_empleado`, los códigos PUC y `creada_por`.** No hay restricción aunque la política tenga planillas asociadas.

### Endpoints especiales

❌ **No hay endpoints de**:
- `POST /politica/<pk>/clonar/` — para crear nueva política copiando de una anterior.
- `POST /politica/<pk>/activar/` o `desactivar/` — ese concepto no existe en el modelo.
- `GET /politica/vigente/?fecha=YYYY-MM-DD` — para consultar cuál política aplica a una fecha.
- `POST /politica/<pk>/simular/` — para probar antes de "activar".

---

## Modelo y campos completos

### Definición real (`models.py:108–127`)

```python
class PoliticaPrepagada(models.Model):
    porcentaje_empresa = models.DecimalField(max_digits=5, decimal_places=2, default=80)
    porcentaje_empleado = models.DecimalField(max_digits=5, decimal_places=2, default=20)
    uvt_limite = models.IntegerField(default=16)
    valor_uvt = models.DecimalField(max_digits=10, decimal_places=2, default=49799)
    porcentaje_empresa_pensionado = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    cod_conc_apoyo_no_grav = models.CharField(max_length=20, blank=True)
    cod_conc_apoyo_grav = models.CharField(max_length=20, blank=True)
    cod_conc_dcto_empleado = models.CharField(max_length=20, blank=True)
    notas = models.TextField(blank=True)
    vigente_desde = models.DateField()
    creada_en = models.DateTimeField(auto_now_add=True)
    creada_por = models.CharField(max_length=150, blank=True)

    class Meta:
        db_table = 'bs_politica_prepagada'
        ordering = ['-vigente_desde']

    def __str__(self):
        return f"Política vigente desde {self.vigente_desde} ({self.porcentaje_empresa}/{self.porcentaje_empleado})"
```

### Schema real en SQLite

```sql
CREATE TABLE "bs_politica_prepagada" (
    "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
    "porcentaje_empresa" decimal NOT NULL,
    "porcentaje_empleado" decimal NOT NULL,
    "uvt_limite" integer NOT NULL,
    "valor_uvt" decimal NOT NULL,
    "cod_conc_apoyo_no_grav" varchar(20) NOT NULL,
    "cod_conc_apoyo_grav" varchar(20) NOT NULL,
    "cod_conc_dcto_empleado" varchar(20) NOT NULL,
    "notas" text NOT NULL,
    "vigente_desde" date NOT NULL,
    "creada_en" datetime NOT NULL,
    "creada_por" varchar(150) NOT NULL,
    "porcentaje_empresa_pensionado" decimal NOT NULL
);
```

### Tabla por campo

| Campo                            | Tipo                       | Default | Editable post-creación | Notas                                                                                                                                                                       |
|----------------------------------|----------------------------|---------|------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `id`                             | autoincrement              | auto    | NO                     | PK al que apunta `PlanillaCalculo.politica` con `on_delete=PROTECT`.                                                                                                          |
| `porcentaje_empresa`             | decimal(5,2)               | 80      | SÍ                     | Lo lee `eligibility.py:66` por valor (Decimal) — **se evalúa en tiempo de cálculo**. Edita después de calcular → al recalcular cambia.                                       |
| `porcentaje_empleado`            | decimal(5,2)               | 20      | SÍ                     | Lo lee `eligibility.py:67`. Igual semántica.                                                                                                                                |
| `uvt_limite`                     | integer                    | 16      | SÍ                     | Multiplicador del límite no gravable. Usado en `prepagada_service.py:80-82`.                                                                                                |
| `valor_uvt`                      | decimal(10,2)              | 49799   | SÍ                     | Valor UVT del año. Usado en `prepagada_service.py:80-82`.                                                                                                                   |
| `porcentaje_empresa_pensionado`  | decimal(5,2)               | **0**   | SÍ                     | ⚠️ **DEFINIDO PERO NUNCA LEÍDO** por el motor. `eligibility.py:38–50` hardcodea `porcentaje_empresa=0, porcentaje_empleado=100` para pensionados. El campo es decoración.    |
| `cod_conc_apoyo_no_grav`         | varchar(20) (blank=True)   | `''`    | SÍ                     | ⚠️ **NUNCA LEÍDO** por backend. Solo se devuelve en `PoliticaPrepagadaSerializer`. Causación (módulo 5) no lo expone.                                                       |
| `cod_conc_apoyo_grav`            | varchar(20) (blank=True)   | `''`    | SÍ                     | ⚠️ Igual: nunca leído.                                                                                                                                                       |
| `cod_conc_dcto_empleado`         | varchar(20) (blank=True)   | `''`    | SÍ                     | ⚠️ Igual: nunca leído.                                                                                                                                                       |
| `notas`                          | text (blank=True)          | `''`    | SÍ                     | Texto libre, sin formato.                                                                                                                                                    |
| `vigente_desde`                  | date (NOT NULL)            | —       | SÍ                     | **Única señal temporal del modelo.** Lo lee el motor en `views.py:860` para escoger "la más reciente". No hay `vigente_hasta` ni rango cerrado.                              |
| `creada_en`                      | datetime (`auto_now_add`)  | now()   | NO                     | Auditoría: cuándo se grabó la fila.                                                                                                                                          |
| `creada_por`                     | varchar(150) (blank=True)  | `''`    | SÍ (PUT lo acepta)     | Se llena solo si `request.user.is_authenticated` al crear (`views.py:682-683`). ⚠️ **Es editable en PUT**, así que su "auditoría" se puede sobrescribir.                       |

### Campos que NO existen (gap explícito)

| Campo razonable               | Estado     | Implicación                                                                                                          |
|-------------------------------|------------|----------------------------------------------------------------------------------------------------------------------|
| `nombre` / `version`          | ❌ Ausente | No hay forma de etiquetar políticas ("Política 2026 v1", "Hotfix UVT marzo"). Solo se identifican por id y fecha.   |
| `vigente_hasta`               | ❌ Ausente | No hay cierre explícito de vigencia. Una política "queda" hasta que llegue otra más reciente — y solo si el bug MP-032 lo permite. |
| `activa: bool`                | ❌ Ausente | No hay flag manual. La semántica de "activa" es **implícita**: la última en `vigente_desde`.                         |
| `actualizado_en`              | ❌ Ausente | Si TH edita un campo, no queda rastro temporal.                                                                       |
| `actualizado_por`             | ❌ Ausente | Tampoco quién lo editó.                                                                                              |
| Snapshot en `PlanillaCalculo` | ❌ Ausente | `PlanillaCalculo` solo guarda FK a la política (`models.py:168`), no copia los valores. Editar la política altera lo que reporta el banner del módulo 4 al re-leerla. |
| Tabla de historial            | ❌ Ausente | Ningún modelo `PoliticaHistorial` ni log.                                                                            |

### ¿Qué pasa si TH edita una política con planillas asociadas?

- ✅ **Lo permite sin advertencia.** El PUT (`views.py:709-717`) no verifica si `PlanillaCalculo.objects.filter(politica=obj).exists()`.
- ⚠️ **Los `DetalleCalculo` ya creados NO cambian** — sus columnas `porcentaje_empresa_aplicado`, `porcentaje_empleado_aplicado`, `valor_empresa`, `valor_empleado`, `apoyo_no_gravable`, `apoyo_gravable` ya quedaron persistidas en el momento del cálculo (módulo 3 verificado).
- ⚠️ **Pero los valores "live" de la política SÍ cambian**: cualquier vista que serialice la política (incluyendo el banner UVT del módulo 4 y el campo `politica` en `PlanillaCalculoDetailSerializer:201`) leerá los nuevos valores.
- ❌ **Resultado**: la planilla histórica mostrará valores calculados con UVT viejo, pero el banner del UVT que ve TH dirá el UVT nuevo. **Inconsistencia visual no detectada.**
- ⚠️ **Si se recalcula** (`PlanillaCalcularView`), se crea una nueva `PlanillaCalculo` con la política editada — la anterior sigue existiendo. No es update_or_create.

---

## Validaciones al crear / editar

El serializer (`serializers.py:97-115`) es un `ModelSerializer` puro:

```python
class PoliticaPrepagadaSerializer(serializers.ModelSerializer):
    class Meta:
        model = PoliticaPrepagada
        fields = [
            'id', 'porcentaje_empresa', 'porcentaje_empleado',
            'uvt_limite', 'valor_uvt', 'porcentaje_empresa_pensionado',
            'cod_conc_apoyo_no_grav', 'cod_conc_apoyo_grav', 'cod_conc_dcto_empleado',
            'notas', 'vigente_desde', 'creada_en', 'creada_por',
        ]
        read_only_fields = ['creada_en']
```

**No define `validate()`, `validate_porcentaje_empresa()`, ni ninguna otra validación.**

| Pregunta                                                                          | Resultado                                                                                                              |
|-----------------------------------------------------------------------------------|------------------------------------------------------------------------------------------------------------------------|
| ¿Valida `porcentaje_empresa + porcentaje_empleado = 100`?                         | ❌ No. Se puede crear una política con 70/20 y el motor multiplica sin advertir el "10% perdido".                       |
| ¿Valida `uvt_limite > 0`?                                                         | ❌ No. Decimal acepta 0, negativo, o muy grande.                                                                        |
| ¿Valida `valor_uvt > 0`?                                                          | ❌ No. Acepta 0; el límite no gravable quedaría en 0 → todo el apoyo se vuelve gravable.                                |
| ¿Valida formato de códigos PUC?                                                    | ❌ No. Acepta cualquier string ≤ 20 chars, o vacío (el default es blank=True).                                          |
| ¿Valida solapamiento de vigencias?                                                | ❌ No. Se pueden crear dos políticas con la misma `vigente_desde` — el motor no detecta el empate.                       |
| ¿Valida que `vigente_desde < vigente_hasta`?                                      | n/a — `vigente_hasta` no existe.                                                                                       |
| ¿Valida unicidad?                                                                 | ❌ No. Ni constraint en BD ni en serializer. Se pueden crear N políticas idénticas.                                     |
| ¿Valida cardinalidad "solo una activa"?                                           | ❌ No — el concepto de "activa" no existe en el modelo. Lo "activo" es implícito (la última por `vigente_desde`).        |
| ¿Valida `porcentaje_empresa_pensionado` coherente con la regla MP-006?             | ❌ No. Acepta cualquier valor; el motor lo ignora, así que TH puede ver "100%" guardado y creer que aplica.              |
| ¿Permite editar `vigente_desde` después de creada?                                 | ✅ Sí. Vía PUT con `partial=True`. **Puede romper la consistencia histórica.**                                          |

### Lo único que sí pasa: `creada_por` se autocaptura en POST

```python
# views.py:682-683
if not data.get('creada_por') and request.user and request.user.is_authenticated:
    data['creada_por'] = request.user.username
```

Pero como las vistas no exigen autenticación, en práctica suele quedar en `''` (verificado: la única política en BD tiene `creada_por = ''`).

---

## Semántica de "activa" vs "vigente"

| Concepto             | Existencia                                                                                              |
|----------------------|---------------------------------------------------------------------------------------------------------|
| Campo `activa: bool` | ❌ **NO EXISTE en el modelo.** El prompt asumía que sí; el código no lo respalda.                       |
| Rango temporal       | ⚠️ Parcial: solo `vigente_desde`. No hay `vigente_hasta`.                                               |
| "Política vigente"   | Implícito: la fila con mayor `vigente_desde` (`views.py:860`).                                          |

### Implicación operativa

- **No hay forma de marcar manualmente una política como "no usar".** Si TH crea por error una política futura, queda automáticamente "vigente" desde su fecha futura — y por el bug MP-032, se toma incluso ANTES de esa fecha.
- **No hay forma de cerrar una política.** Cuando un nuevo año llega, hay que crear otra política con `vigente_desde` mayor. La anterior nunca se "apaga" — solo deja de ser la más reciente.
- **Pueden coexistir N políticas con la misma `vigente_desde`.** En empate, Django ordena por `-vigente_desde` y luego implícitamente por `id` o por algún criterio no determinístico — `views.py:860` toma `.first()` sin criterio secundario. **Indeterminismo no controlado.**
- **El frontend `TabPolitica` (línea 1460) intenta mostrar un badge `{p.vigente && <span>Vigente</span>}`** pero el campo `p.vigente` **nunca está en el response del serializer**. El badge nunca se renderiza. Frontend code muerto.

---

## Cómo se conecta con los otros módulos

Inventario completo de consultas a `PoliticaPrepagada` y a la instancia `politica`:

| # | Ubicación                                              | Qué hace                                                                                                                                                | Criterio                                          |
|---|--------------------------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------|---------------------------------------------------|
| 1 | `views.py:676` (`PoliticaView.get`)                    | Lista todas para la UI.                                                                                                                                  | `.all()` (ordering del Meta: `-vigente_desde`).   |
| 2 | `views.py:684` (`PoliticaView.post`)                   | Crea nueva política.                                                                                                                                     | n/a                                               |
| 3 | `views.py:699` (`PoliticaDetailView._get_object`)      | Obtiene una por id.                                                                                                                                      | `pk=pk`                                           |
| 4 | `views.py:713` (`PoliticaDetailView.put`)              | Edita una.                                                                                                                                               | `pk=pk`                                           |
| 5 | `views.py:853` (`PlanillaCalcularView` con override)   | Si TH envía `politica_id` en el body, lo respeta.                                                                                                       | `pk=politica_id`                                  |
| 6 | `views.py:860` (`PlanillaCalcularView` sin override)   | **MP-032**: toma la más reciente por `vigente_desde`, sin filtrar contra el `periodo`.                                                                  | `.order_by('-vigente_desde').first()`             |
| 7 | `services/eligibility.py:66-67`                        | Lee `politica.porcentaje_empresa` y `politica.porcentaje_empleado` por **valor**, no por FK.                                                            | Atributos de la instancia que recibe.             |
| 8 | `services/prepagada_service.py:80-82`                  | Calcula `limite_no_grav = uvt_limite * valor_uvt`.                                                                                                       | Atributos de la instancia que recibe.             |
| 9 | `serializers.py:201` (`PlanillaCalculoDetailSerializer`)| Anida `politica` (read-only) en la respuesta del detalle de planilla — esto es lo que alimenta el banner UVT del módulo 4.                              | Vía FK `PlanillaCalculo.politica`.                |

### Lecturas críticas

- ❌ **Ningún módulo filtra por `activa=True`** (porque el campo no existe).
- ❌ **Ningún módulo filtra por `vigente_desde <= fecha_periodo`** (este es exactamente el bug MP-032).
- ❌ **Causación (`views.py:1038-1098`) no consulta `PoliticaPrepagada` directamente.** Lee la planilla y agrupa `DetalleCalculo` por EPS — no expone los códigos PUC aunque la política los tenga. Confirmado en módulo 5.
- ❌ **`InformeEFRView` no consulta `PoliticaPrepagada`.** Solo lee la planilla.
- ❌ **`AuxilioExterno` no consulta `PoliticaPrepagada`.** Confirmado en módulo 7.

### Snapshot vs lectura "live"

- El motor **lee los valores de la política en tiempo de cálculo** y los persiste en cada `DetalleCalculo` (`porcentaje_empresa_aplicado`, `porcentaje_empleado_aplicado`, `valor_empresa`, `valor_empleado`, `apoyo_no_gravable`, `apoyo_gravable`).
- ✅ Para esos campos congelados, las planillas históricas **son inmutables** frente a ediciones posteriores de la política.
- ⚠️ Pero `valor_uvt`, `uvt_limite`, `cod_conc_*` y `porcentaje_empresa_pensionado` **NO se snapshotean** en `PlanillaCalculo` ni en `DetalleCalculo`. Cualquier UI que serialice la política asociada mostrará los valores ACTUALES, no los del momento del cálculo. Esto contamina el banner UVT del módulo 4.

---

## Versionamiento y trazabilidad

| Aspecto                                                | Estado                                                                                                          |
|--------------------------------------------------------|-----------------------------------------------------------------------------------------------------------------|
| `creada_en` (auto_now_add)                             | ✅ Sí.                                                                                                          |
| `creada_por`                                           | ⚠️ Sí, pero captura silenciosa: solo se llena si `request.user.is_authenticated`; sin auth queda vacío.         |
| `actualizado_en` / `actualizado_por`                   | ❌ No.                                                                                                          |
| Modelo de historial separado (`PoliticaHistorial`)     | ❌ No existe. `grep -rn "PoliticaHistorial\|LogPolitica"` → cero.                                                |
| Snapshot de valores en `PlanillaCalculo`               | ❌ No. Solo FK.                                                                                                  |
| Snapshot de porcentajes en `DetalleCalculo`            | ✅ Sí (`porcentaje_empresa_aplicado`, `porcentaje_empleado_aplicado`).                                          |
| Snapshot de UVT en `DetalleCalculo`                    | ❌ No. No hay columna `valor_uvt_aplicado` ni `limite_no_gravable_aplicado`.                                     |

### Caso crítico: TH cambia el UVT a mitad de año

Escenario realista — el operador captura `valor_uvt = 49.799` para 2026 y luego descubre que el decreto fijó `49.799`. Edita a `49.799` exacto, o digita `49.800` por error.

- ✅ Lo que ya está calculado en `DetalleCalculo` no cambia. Los `apoyo_no_gravable` y `apoyo_gravable` están congelados.
- ❌ Pero **no se sabe con qué UVT se calculó cada planilla**: no hay snapshot. La única forma de reconstruir el UVT histórico es:
  - Mirar `DetalleCalculo.valor_empresa` de un empleado y dividir por el porcentaje aplicado para obtener `total_familia`, luego restar `apoyo_no_gravable` y dividir por `uvt_limite` (si está disponible). Reconstrucción frágil.
  - Asumir que la política nunca se editó (no verificable).
- ❌ No hay log que diga "el campo `valor_uvt` fue cambiado de 49.799 a 49.800 el día X por usuario Y".

---

## El bug MP-032 desde el lado de la configuración

Confirmado en `views.py:860`:

```python
politica = PoliticaPrepagada.objects.order_by('-vigente_desde').first()
```

### Salvaguardas detectadas (o ausentes)

- ❌ **No hay alerta al crear una política nueva.** El POST se acepta y queda "vigente" inmediatamente.
- ❌ **No hay simulador.** No existe `POST /politica/<pk>/simular/?periodo=MMYYYY`. La única forma de "probar" es crear la planilla con `politica_id` explícito — pero eso ya crea persistencia (`PlanillaCalculo` + `DetalleCalculo`).
- ❌ **No hay vista "política vigente HOY".** El frontend (`SigaPage.js:1460`) intenta mostrarlo (`p.vigente && <span>Vigente</span>`) pero el campo no viene del backend → la UI **nunca** marca cuál es la vigente. **TH no tiene retroalimentación visual.**
- ⚠️ **El override existe pero es opcional**: `PlanillaCalcularView` acepta `politica_id` en el body (`views.py:850-858`). Si TH no lo manda (caso típico), cae al `latest()` buggy. Si lo manda, puede elegir mal igualmente.
- ❌ **No hay validación "política con `vigente_desde > periodo`"**. Si TH crea por error una política con `vigente_desde = 2027-01-01` mientras calcula la planilla de mayo 2026, esa política gana — y todas las planillas a partir de ahí usarán los porcentajes/UVT de 2027.

---

## Borrado y protección de integridad

| Aspecto                                                | Resultado                                                                                                                                  |
|--------------------------------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------|
| Endpoint DELETE                                        | ❌ **NO EXISTE.** `PoliticaDetailView` solo implementa `get` y `put` (`views.py:691-717`). Buscado: no hay `def delete` en esa clase.        |
| Frontend "Eliminar"                                    | ❌ `TabPolitica` (`SigaPage.js:1336-1499`) tampoco tiene botón de eliminar.                                                                |
| FK `PlanillaCalculo.politica`                          | `on_delete=PROTECT` (`models.py:168`). Aunque hubiera DELETE, fallaría con `ProtectedError`.                                                 |
| ¿Vía Django admin?                                     | ⚠️ Sí, posible: `@admin.register(PoliticaPrepagada)` con default acciones (`admin.py:82-97`). Allí el DELETE existe; intentar borrar una política con planillas asociadas lanza `ProtectedError` (Django se lo mostrará al usuario admin, pero no es flujo operativo). |
| Soft-delete / archivar                                 | ❌ No existe. No hay flag de archivado.                                                                                                     |
| "Mensaje legible" en API si se intentara DELETE        | n/a — no hay endpoint que probar.                                                                                                          |

**Resultado neto: una política, una vez creada vía API, es permanente.** Solo se puede editar (PUT). Esto entra en tensión con la posibilidad de errores de captura.

---

## Carga masiva / migración inicial

- ❌ No hay management command (`siga/backend/modules/beneficios_salud/management/` no existe).
- ❌ No hay fixtures (`find -name "fixtures"` → nada).
- ❌ Las migraciones (`0001_initial.py`, `0002_prepagada_modules.py`, `0003_elegibilidad_planilla.py`) solo crean schema; no hacen `RunPython` que precargue políticas (verificado: ninguna `RunPython` operación).
- La política única que existe hoy se creó vía API el `2026-05-06 13:46:09` (ver "Estado actual de la tabla en BD").

Si TH tiene políticas históricas (UVT 2024, 2025) en otro sistema, **no hay mecanismo para migrarlas en bulk**. Hay que crearlas una por una vía POST.

---

## Estado actual de la tabla en BD

`bs_politica_prepagada`:

| id | vigente_desde | valor_uvt | uvt_limite | %_empresa | %_empleado | %_emp_pens | cod_no_grav | cod_grav | cod_dcto_emp | creada_por | creada_en             |
|----|---------------|-----------|------------|-----------|------------|------------|-------------|----------|--------------|------------|-----------------------|
| 1  | 2026-01-01    | 49799     | 16         | 80        | 20         | 0          | `''`        | `''`     | `''`         | `''`       | 2026-05-06 13:46:09   |

`bs_planilla_calculo` apuntando a política:

```
politica_id | COUNT(*)
1           | 1
```

### Observaciones críticas

- ✅ **Una sola política**, no hay solapamientos. UVT y porcentajes coinciden con valores esperados (`$49.799`, `16 UVT`, `80/20`).
- ❌ **Códigos PUC vacíos.** `cod_conc_apoyo_no_grav`, `cod_conc_apoyo_grav`, `cod_conc_dcto_empleado` son `''`. Incluso si el módulo 5 (Causación) los expusiera en el response, no habría nada que mostrar.
- ❌ **`porcentaje_empresa_pensionado = 0`**, no `100`. Confusión visual: el manual dice 100% para pensionados; el motor ignora este campo y aplica 100% al empleado por código duro; pero la UI mostraría "0%" si el frontend imprimiera este campo. Verificado: el frontend solo lo muestra como badge si tiene valor (`SigaPage.js:1484`), y 0 evalúa falsy → no se muestra.
- ❌ **`creada_por` vacío** → no hay auditoría real de quién la creó.
- ⚠️ **Una planilla calculada apunta a esta política.** Si alguien edita el `valor_uvt` ahora, el banner del módulo 4 mostrará el valor nuevo aunque el cálculo histórico use el viejo.

---

## Comportamientos confirmados / refutados

### Casos solicitados

| # | Caso                                                                                                                              | Resultado verificado en código                                                                                                                                                                                                                                          |
|---|-----------------------------------------------------------------------------------------------------------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 1 | TH crea política 2027-01-01 y en diciembre 2026 calcula planilla de diciembre                                                     | ✅ **Bug MP-032 confirmado.** `views.py:860` toma la 2027 incluso si TH la creó por error o por adelantado. La planilla de diciembre 2026 calculará con porcentajes/UVT futuros. Salvación parcial: TH puede mandar `politica_id` explícito en el body.                  |
| 2 | TH crea dos políticas con la misma `vigente_desde`                                                                                | ✅ Se permite. `views.py:860` no rompe empate explícitamente — `.first()` toma la "primera" por orden de inserción interna de SQLite. **Comportamiento indeterminístico** para empates.                                                                                  |
| 3 | TH edita `valor_uvt` después de calcular planillas                                                                                | ⚠️ Mixto: los `apoyo_*` de `DetalleCalculo` quedan congelados; pero el banner UVT del módulo 4 (que lee la política via FK serializada) muestra el valor NUEVO. **Inconsistencia visual confirmada.**                                                                    |
| 4 | TH borra una política con planillas                                                                                                | ❌ No hay endpoint DELETE en la API. Vía Django admin sí, pero `on_delete=PROTECT` (`models.py:168`) lanza `ProtectedError` ⇒ el admin lo muestra como mensaje de error.                                                                                                |
| 5 | TH "desactiva" una política                                                                                                       | n/a — el concepto no existe (no hay campo `activa`). La única forma de "quitar de juego" una política es crear otra con `vigente_desde` posterior; aún así sigue persistida.                                                                                              |
| 6 | Hoy: ¿la política vigente tiene códigos PUC poblados?                                                                              | ❌ NO. Los tres campos `cod_conc_*` están en `''`. **Aunque módulo 5 expusiera el JSON con PUC, no habría datos que enviar.** Hay que poblarlos antes (decisión: contabilidad).                                                                                            |

### Reglas implícitas del manual

| Aspecto institucional                                                                  | Soporte en código                                                                                                                                                            |
|----------------------------------------------------------------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Porcentajes 80/20 fijados por política institucional, no negociables                   | ❌ El modelo los permite cambiar libremente (no hay regla `porcentaje_empresa=80 forzado`).                                                                                  |
| UVT se actualiza anualmente por decreto                                                | ❌ No hay automatización (importar UVT del DIAN). 100% manual.                                                                                                               |
| PUC es responsabilidad de contabilidad, no de TH                                       | ❌ Mismo usuario edita todo. No hay segregación de campos por rol.                                                                                                            |
| Separación de roles                                                                    | ❌ Ninguna autenticación obligatoria, ninguna restricción por permiso (`PoliticaView` y `PoliticaDetailView` no declaran `permission_classes`).                                |

---

# Resumen ejecutivo del módulo

## ✅ Lo que SÍ hace

- Modelo `PoliticaPrepagada` con porcentajes, UVT, códigos PUC, `vigente_desde`, `notas` y auditoría parcial (`creada_en` + `creada_por` opcional).
- CRUD parcial (GET listado, GET detalle, POST, PUT). PUT con `partial=True`.
- `Meta.ordering = ['-vigente_desde']` → listado más reciente primero por defecto.
- Captura `creada_por` automáticamente desde `request.user.username` cuando el usuario está autenticado (`views.py:682-683`) — único módulo BS que lo hace.
- Snapshot de porcentajes aplicados en `DetalleCalculo.porcentaje_*_aplicado` (cálculo histórico inmutable para esos campos).
- FK `PlanillaCalculo.politica` con `on_delete=PROTECT` previene borrado accidental por bd-side (aunque por API no haya DELETE de todas formas).
- Override opcional del motor: `PlanillaCalcularView` acepta `politica_id` para usar una política específica.

## ❌ Lo que NO hace

- **No tiene endpoint DELETE** — política es prácticamente inmutable post-creación (solo se puede editar).
- **No tiene snapshot de UVT/PUC** en `PlanillaCalculo` ni en `DetalleCalculo` → editar la política contamina el banner histórico del módulo 4.
- **No valida** porcentajes sumando 100, ni valores positivos, ni códigos PUC, ni solapamientos, ni unicidad.
- **No tiene `activa`, `vigente_hasta`, `nombre`, `actualizado_en`, `actualizado_por`** ni modelo de historial.
- **No tiene endpoint para identificar "política vigente"** — el frontend intenta mostrar el badge `Vigente` (`SigaPage.js:1460`) pero el campo no llega del backend; código muerto.
- **No tiene simulador** ("¿qué pasaría si aplicara esta política al período X?") ni endpoint de clonar / archivar.
- **No tiene segregación de roles** — cualquiera con permiso de PUT edita porcentajes (TH) o PUC (contabilidad) indistintamente.
- **Bug MP-032 sigue activo**: el motor toma `order_by('-vigente_desde').first()`, sin compararse con la fecha del periodo a calcular.
- **`porcentaje_empresa_pensionado` está definido pero NO se lee** por `eligibility.py` (que hardcodea 100/0). Es campo decorativo.
- **`cod_conc_*` están definidos pero NO se leen** por ninguna lógica de causación. Hoy además están vacíos en la BD real.
- **No tiene migración de datos** ni fixtures históricos.
- **Empates en `vigente_desde`** se resuelven de forma indeterminística.

## ⚠️ Pendiente validar con TH

- **Política operativa para el cambio anual de UVT**: ¿quién aprueba el cambio? ¿en qué momento del año se crea la nueva política para 2027? Hoy basta con que cualquier usuario haga POST.
- **¿Cómo prevenir el bug MP-032 desde la operación** mientras se arregla en código? Posibilidad: prohibir crear políticas con `vigente_desde > today` hasta el cierre de mes.
- **¿Quién va a poblar los códigos PUC vacíos** (`cod_conc_apoyo_no_grav`, `cod_conc_apoyo_grav`, `cod_conc_dcto_empleado`)? Hoy son `''` y no hay quien los administre.
- **¿Es aceptable que la política sea editable después de tener planillas asociadas?** En estricto rigor de auditoría, debería ser inmutable y obligar a crear una nueva versión.
- **¿`porcentaje_empresa_pensionado` debe leerlo el motor** (para que la regla MP-006 sea parametrizable) o debe **eliminarse** como campo muerto?
- **¿Quién es "el creador" cuando `request.user` no está autenticado?** Hoy queda vacío. Si se exige firma, hay que cerrar el endpoint con `IsAuthenticated`.
- **¿Aceptamos que no haya endpoint DELETE?** Si TH crea una política por error, hoy solo queda editarla — no eliminarla. ¿Suficiente?
- **Snapshot de UVT en el momento del cálculo:** ¿se acepta el riesgo actual o exigimos guardar `valor_uvt_aplicado`/`uvt_limite_aplicado` en `DetalleCalculo`?
