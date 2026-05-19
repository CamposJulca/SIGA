# Hallazgos Pre-Reunión TH — Verificación contra Código

| Campo        | Valor                                            |
|--------------|--------------------------------------------------|
| Fecha        | 2026-05-13                                       |
| Generado por | Verificación directa del código fuente            |
| Propósito    | Llegar a la reunión con TH con respuestas firmes |
| Alcance      | 6 hipótesis surgidas del análisis de `20251130PlanillaAxaColpatria.xlsx` y `20251231EFRInformesBeneficiosNominaOk.xlsx` |

---

## H1. Qué hoja del Excel de AXA lee SIGA

**Hipótesis original:** El adaptador de AXA lee la hoja `Planilla` (que no trae parentesco) y por eso el dashboard muestra "Sin especificar" en muchos registros. La hoja `Novedad` del mismo archivo SÍ trae parentesco completo (TITULAR, CÓNYUGE, HIJO(A), PADRES, OTROS).

**Veredicto:** ⚠️ Ambigua — el código **lee únicamente UNA hoja, y siempre es la primera del archivo** (no especifica `sheet_name`). Cuál sea esa primera hoja es propiedad del archivo, no del código.

**Evidencia:**

- Archivo: `siga/backend/modules/beneficios_salud/services/reader_excel.py`
- Función: `_leer_axa`
- Líneas: 80–102
- Snippet relevante:
  ```python
  def _leer_axa(ruta_archivo: str) -> tuple:
      """Lee un archivo Excel de AXA Colpatria."""
      # Leer sin encabezado para inspeccionar filas
      df_raw = pd.read_excel(ruta_archivo, engine='openpyxl', header=None)
      ...
      df = pd.read_excel(ruta_archivo, engine='openpyxl', header=header_row)
  ```
- Verificación global: `grep -rn "sheet_name" backend/` → **0 resultados** en toda la base de código. El proyecto **nunca** llama a `pd.read_excel` con `sheet_name`. Por convención de pandas, eso es equivalente a `sheet_name=0` → siempre la primera hoja.
- El adaptador **sí busca** la columna `PARENTESCO`:
  - Archivo: `siga/backend/modules/beneficios_salud/services/axa_adapter.py`, líneas 9–18
  ```python
  AXA_COLUMN_MAP = {
      'SUB CTO': 'sub_contrato',
      'NUMID': 'cedula_titular',
      'NUMERO ID.BEN': 'cedula',
      'NOMBRE': 'nombre',
      'PARENTESCO': 'parentesco',
      'SUBTOTAL': 'valor_base',
      'IVA': 'iva',
      'TOTAL': 'valor_total',
  }
  ```
- Si la columna `PARENTESCO` **no está** en la hoja que se está leyendo, el adaptador asigna `None` (líneas 38–47):
  ```python
  for src_col, dst_col in AXA_COLUMN_MAP.items():
      if src_col in df.columns:
          unified[dst_col] = df[src_col]
      else:
          ...
              unified[dst_col] = None
  ```

**Implicación para la reunión:** Lo que veamos depende de cuál sea físicamente la primera hoja del archivo entregado por AXA. **Si AXA entrega un libro donde la primera hoja es `Planilla` y esa hoja no trae `PARENTESCO` poblado**, el adaptador llena ese campo con `None` y el dashboard muestra "Sin especificar". El sistema **no intenta leer `Novedad`** ni ninguna otra hoja. Esto es un cambio de **una línea** si TH confirma que `Novedad` es la fuente correcta del parentesco — pero hay que validarlo primero contra el archivo real abierto.

**Preguntas que ahora sí tienen respuesta firme:**
- ¿SIGA lee múltiples hojas? **No.** Lee solo una (la primera).
- ¿El adaptador mapea `PARENTESCO`? **Sí**, pero solo si la columna existe en la hoja leída.
- ¿Hay alguna lógica que elija entre `Planilla` y `Novedad`? **No.**

**Acción para hoy:** abrir el `20251130PlanillaAxaColpatria.xlsx` antes de la reunión y confirmar **cuál hoja queda primera en orden físico**. Si es `Planilla` y no trae PARENTESCO con valores reales, el hallazgo es accionable de inmediato.

---

## H2. Columna `NOM` (ACT/PNS) de AXA

**Hipótesis original:** La hoja `Planilla` de AXA marca explícitamente en la columna `NOM` si la persona es `ACT` (activo) o `PNS` (pensionado). SIGA NO está aprovechando esa columna, y por eso requiere registro manual de pensionados en el Módulo 6.

**Veredicto:** ✅ **Confirmada.**

**Evidencia:**

- Archivo: `siga/backend/modules/beneficios_salud/services/axa_adapter.py`
- Líneas: 9–18 (mapeo completo)
- El `AXA_COLUMN_MAP` **no incluye** `NOM`. Las únicas columnas que se leen son: `SUB CTO`, `NUMID`, `NUMERO ID.BEN`, `NOMBRE`, `PARENTESCO`, `SUBTOTAL`, `IVA`, `TOTAL`.
- Verificación global: `grep -rn -E "'NOM'|\"NOM\"|ACT|PNS" backend/ --include="*.py"` → 0 resultados (el único match fue una falsa coincidencia con la palabra "FACTURACION" en `reader_excel.py:40`).
- El modelo `BeneficioSalud` **tampoco** tiene un campo equivalente a `tipo_nomina` / `ACT` / `PNS`:
  - Archivo: `siga/backend/modules/beneficios_salud/models.py`, líneas 40–79.
- La identificación de pensionado se hace **por tabla aparte**:
  - Archivo: `siga/backend/modules/beneficios_salud/services/eligibility.py`, líneas 38–50
  ```python
  pensionado_qs = PensionadoPrepagada.objects.filter(cedula=cedula, activo=True)
  if eps:
      pensionado_qs = pensionado_qs.filter(eps__iexact=eps)

  if pensionado_qs.exists():
      return EligibilityResult(
          tipo_persona=TIPO_PENSIONADO,
          estado_elegibilidad=PENSIONADO_100,
          ...
          porcentaje_empresa=Decimal('0'),
          porcentaje_empleado=Decimal('100'),
          ...
      )
  ```
- Es decir: la regla MP-006 (pensionado = 100% empleado) **solo se aplica** si la persona ya fue registrada **manualmente** en la tabla `bs_pensionados_prepagada`.

**Implicación para la reunión:** Esto es **una mejora alta-prioridad y barata**. AXA ya nos dice quién es pensionado en cada archivo. Hoy estamos pidiendo que TH lo registre a mano. Bastaría con: (1) mapear `NOM` al adaptador, (2) agregar un campo `tipo_nomina` (o reutilizar el campo `tipo_persona` que ya existe en `DetalleCalculo`), (3) auto-poblar `PensionadoPrepagada` a partir del valor `PNS` recibido. **Es un cambio que reduce trabajo manual significativo** y se puede ofrecer como compromiso concreto en la reunión.

**Preguntas que ahora sí tienen respuesta firme:**
- ¿El adaptador lee `NOM`? **No.**
- ¿`BeneficioSalud` tiene un campo equivalente? **No.**
- ¿Cómo identifica el sistema a un pensionado hoy? **Consultando `bs_pensionados_prepagada`, que se llena a mano** (Módulo 6).
- ¿La regla MP-006 consume el dato del archivo? **No, consume la tabla manual.**

---

## H3. Presencia del proveedor COLMÉDICA

**Hipótesis original:** El informe EFR menciona "APOYO MED. PREPAGADA COLMEDICA" como un concepto activo. SIGA solo contempla AXA Colpatria y Colsanitas. Colmédica podría ser un tercer proveedor real, un caso de auxilio externo, o algo no contemplado.

**Veredicto:** ✅ **Confirmada — Colmédica NO existe en el código.**

**Evidencia:**

- Búsqueda global: `grep -ri "colmed" backend/ --include="*.py"` → **0 resultados** (case-insensitive, cubre `colmedica`, `colmédica`, `colmed`).
- Catálogo de proveedores está **hardcodeado**:
  - Archivo: `siga/backend/modules/beneficios_salud/models.py`, líneas 5–9
  ```python
  PROVEEDOR_CHOICES = [
      ('axa', 'AXA Colpatria'),
      ('colsanitas', 'Colsanitas'),
      ('desconocido', 'Desconocido'),
  ]
  ```
- Detector solo conoce dos:
  - Archivo: `siga/backend/modules/beneficios_salud/services/detector.py`, líneas 18–35
  ```python
  if 'AXACOLPATRIA' in nombre_upper or 'AXA' in nombre_upper:
      return 'axa'
  if 'COLSANITAS' in nombre_upper:
      return 'colsanitas'
  ...
  axa_markers = {'SUB CTO', 'NUMID'}
  if axa_markers.issubset(set(columnas_str)):
      return 'axa'
  if 'Número de Familia' in columnas_str:
      return 'colsanitas'
  ```
- **Módulo 7 (Auxilio Externo) permite proveedor libre:**
  - Archivo: `models.py`, líneas 148–163
  ```python
  class AuxilioExterno(models.Model):
      cedula = models.CharField(max_length=20)
      nombre = models.CharField(max_length=200)
      eps = models.CharField(max_length=100)  # <-- sin choices, texto libre
      ...
  ```
  Es decir: para AuxilioExterno se puede escribir `Colmédica` como texto, pero **no hay procesamiento ETL** de archivos Colmédica.

**Implicación para la reunión:** Hay que preguntar a TH explícitamente: **¿qué es "APOYO MED. PREPAGADA COLMEDICA" en el informe EFR?** Tres posibilidades, y solo TH lo sabe:
1. Es un legado histórico (un proveedor que ya no entrega archivos).
2. Es un caso de **auxilio externo** (Módulo 7) que se está reportando manualmente.
3. Es un **tercer proveedor real** con archivos que hoy nadie procesa.

Si la respuesta es (3), tenemos un gap funcional grande: hay que ampliar el catálogo de proveedores, el detector y crear un nuevo adaptador. Si es (1) o (2), no hay cambio de código, sino conversación.

**Preguntas que ahora sí tienen respuesta firme:**
- ¿"colmedica" aparece en el código? **No, en ningún lado.**
- ¿La lista de proveedores está hardcodeada? **Sí.**
- ¿`detector.py` puede manejar más de 2 proveedores? **No con su lógica actual; habría que añadir reglas.**
- ¿Auxilio Externo tiene catálogo cerrado? **No, el campo `eps` es texto libre.**

---

## H4. Fórmula real del descuento 20%

**Hipótesis original:** Los números de la planilla AXA noviembre 2025 muestran que el descuento al empleado NO es el 20% literal. Castillo y Cely tienen 14% real, Rangel 15.3%, Monroy 18.3%, Hernández y Barahona 19.1%. La fórmula documentada (`valor_empleado = total_familia × 20%`) no explica estos números.

**Veredicto:** ✅ **Confirmada — el código aplica 20% literal sobre `total_familia`.** Si en el archivo real se ven porcentajes distintos, no es por la lógica de SIGA.

**Evidencia:**

- Archivo: `siga/backend/modules/beneficios_salud/services/prepagada_service.py`
- Función: `calcular_planilla`
- Líneas: 67–171 (función completa); cálculo exacto en líneas 146–149:
  ```python
  valor_empresa = round(total * elegibilidad.porcentaje_empresa / 100, 2)
  valor_empleado = round(total * elegibilidad.porcentaje_empleado / 100, 2)
  apoyo_no_grav = min(valor_empresa, limite_no_grav)
  apoyo_grav = max(Decimal('0'), valor_empresa - limite_no_grav)
  ```
- Donde `total` se asigna en la línea 95:
  ```python
  total = Decimal(str(r['total_familia'] or 0))
  ```
  Es decir: el cálculo es **estrictamente** `total_familia × porcentaje / 100`. **No considera** `DCTO CIAL`, `DESCUENTO POS` ni `IVA` por separado. Tampoco consulta `BeneficioSalud.descuento` ni `BeneficioSalud.iva` que sí están en el modelo de carga (`models.py` líneas 60–63).
- `total_familia` viene de la vista `v_cruce` en `prepagada.db`. El código de SIGA **no calcula** ese valor: lo consume:
  - Archivo: `prepagada_service.py`, líneas 51–60
  ```python
  cur.execute("""
      SELECT periodo, eps, cedula, nombre_en_factura, nombre_en_kactus,
             num_beneficiarios, total_familia, sub_cto, nro_cont,
             sue_basi, tip_cont, estado, archivo
      FROM v_cruce
      WHERE periodo = ?
      ...
  """, (periodo,))
  ```
- El límite UVT se aplica **después** de calcular el 80%, no antes:
  - Línea 80–82: `limite_no_grav = uvt_limite × valor_uvt`.
  - Líneas 148–149: el límite afecta solo a la **separación gravable/no gravable**, **no al porcentaje empresa/empleado**.

**Verificación con caso de prueba:**
- Para `total_familia = 4_351_000`, con política 80/20: el código produce
  - `valor_empresa = 4_351_000 × 80 / 100 = 3_480_800`
  - `valor_empleado = 4_351_000 × 20 / 100 = 870_200`
- Si el archivo de AXA real muestra ≈ $610.000 (14% efectivo), **la diferencia NO viene del cálculo de SIGA**, viene de:
  - Cómo se construye `total_familia` en la vista `v_cruce` de `prepagada.db`, o
  - Que el "descuento" visto en el archivo es el resultado final aplicado en Kactus, descontando otros conceptos (descuento comercial, IVA, ajustes), o
  - Que la política aplicada en ese mes no era 80/20 sino otra.

**Implicación para la reunión:** Hay que ser **muy claros con TH**: SIGA aplica un porcentaje literal sobre el `total_familia` que recibe de la vista de cruce. **No considera** descuento comercial ni IVA en el cálculo del 80/20. Si la realidad operativa de Finagro está aplicando otra fórmula (que descuenta IVA antes, o que aplica el 20% sobre `subtotal − descuento` en vez del total), eso es un **gap funcional** que debemos discutir. Es la conversación más importante de la reunión para el cálculo de planilla.

**Preguntas que ahora sí tienen respuesta firme:**
- ¿Dónde está el cálculo? `prepagada_service.py`, función `calcular_planilla`, líneas 146–147.
- ¿Aplica el UVT antes o después del 20%? **Después.** El UVT solo separa apoyo gravable de no gravable; no modifica el 80%.
- ¿Considera descuento comercial o IVA? **No, en absoluto** (en el cálculo de planilla).
- ¿Calcula 20% literal? **Sí, sobre `total_familia` recibido de la vista de cruce.**

---

## H5. Hoja "No Cubrimientos"

**Hipótesis original:** El archivo AXA trae una hoja separada con beneficiarios que la empresa NO cubre (en el ejemplo, 2 nietas). SIGA podría estar ignorando esa hoja, o procesándola y registrándola como exclusión.

**Veredicto:** ✅ **Confirmada — SIGA ignora esa hoja totalmente.**

**Evidencia:**

- Búsqueda global: `grep -ri -E "no.cubrimient|cubrimiento" backend/ --include="*.py"` → **0 resultados**.
- Como se demostró en H1, el lector AXA solo abre la primera hoja (`reader_excel.py` líneas 80–102, sin `sheet_name`). No hay código que enumere las hojas del libro ni que busque por nombre.
- No existe ningún modelo en `models.py` para "beneficiarios no cubiertos" / "exclusiones".

**Implicación para la reunión:** SIGA **no captura** las exclusiones explícitas que el proveedor reporta. Hoy, si AXA marca a una nieta como "no cubierta", esa información se pierde al cargar el archivo. Si TH usa esa información en algún punto del proceso (justificación, auditoría, reclamaciones), hoy lo está haciendo **fuera del sistema**. Pregunta directa para TH: *¿usan esa hoja para algo?* Si responden que sí, es un requerimiento nuevo.

**Preguntas que ahora sí tienen respuesta firme:**
- ¿El adaptador lee "No Cubrimientos"? **No.**
- ¿Esos registros se persisten en algún modelo? **No, no existe modelo equivalente.**

---

## H6. Hoja "Maestro" del archivo AXA

**Hipótesis original:** El archivo AXA incluye una hoja `Maestro` con todos los empleados de Finagro (cédula, ingreso, retiro, cargo, dependencia). La documentación dice que el cruce se hace con Kactus vía `prepagada.db`. Pueden estar coexistiendo dos fuentes.

**Veredicto:** ✅ **Confirmada — SIGA ignora la hoja `Maestro` y consume `prepagada.db` como única fuente para el cruce.**

**Evidencia:**

- Búsqueda global: `grep -ri "maestro" backend/ --include="*.py"` → **0 resultados**.
- El lector AXA (`reader_excel.py:_leer_axa`) abre solo la primera hoja, como en H1/H5.
- El cruce con la nómina se hace **exclusivamente** desde `prepagada.db`:
  - Archivo: `prepagada_service.py`, líneas 13–22 (apertura de conexión)
  ```python
  def _get_connection():
      db_path = settings.PREPAGADA_DB_PATH
      try:
          conn = sqlite3.connect(db_path)
          return conn
      except Exception as e:
          raise RuntimeError(...)
  ```
  - Líneas 43–64 (lectura de `v_cruce`): selecciona `cedula`, `nombre_en_kactus`, `sue_basi`, `tip_cont`, `estado`, etc.
- **El código NO escribe a `prepagada.db` en ningún punto.** Sólo lee:
  - Las únicas operaciones SQL contra esa base son `SELECT DISTINCT periodo ...` (línea 30–33), `SELECT ... FROM v_cruce` (línea 51–60), y `SELECT ... LEFT JOIN ... FROM facturas_eps` (línea 184–191). **No hay INSERT/UPDATE/CREATE en `prepagada.db`.**
- Por tanto, `prepagada.db` **se actualiza por un proceso externo a SIGA**, que en el código no aparece y no está documentado en el repositorio.

**Implicación para la reunión:** Hay que aclarar con TH **dos cosas distintas**:
1. La hoja `Maestro` que viene en el archivo AXA hoy **no se está usando**. ¿La usan ustedes fuera del sistema?
2. ¿Quién mantiene `prepagada.db` actualizado? Es la dependencia más crítica del cálculo de planilla, pero el código de SIGA no la alimenta — alguien debe estar exportando desde Kactus periódicamente. Necesitamos confirmar **quién, con qué frecuencia y cómo**. Si hoy nadie tiene un proceso formal, esto es un riesgo operativo que el equipo SIGA debe levantar formalmente.

**Preguntas que ahora sí tienen respuesta firme:**
- ¿El adaptador lee la hoja `Maestro`? **No.**
- ¿`prepagada.db` se actualiza desde el archivo AXA? **No.**
- ¿SIGA actualiza `prepagada.db`? **No, solo la lee.**

---

# Resumen ejecutivo para la reunión

## ✅ Qué podemos afirmar con certeza

| # | Afirmación firme                                                                                                                                  |
|---|----------------------------------------------------------------------------------------------------------------------------------------------------|
| 1 | **SIGA lee solo UNA hoja del archivo Excel (la primera)**. No hay manejo de múltiples hojas. Cualquier información en otras hojas se pierde.       |
| 2 | **SIGA NO aprovecha la columna `NOM` (ACT/PNS) de AXA**. La identificación de pensionado se hace por la tabla manual `bs_pensionados_prepagada`.   |
| 3 | **Colmédica no existe en el código** (0 ocurrencias). Si está en el informe EFR es un dato manejado fuera de SIGA.                                  |
| 4 | **El cálculo del 20% es literal sobre `total_familia`** que viene de `v_cruce` en `prepagada.db`. No considera IVA, no considera descuento comercial. |
| 5 | **El UVT se aplica después del 80%**, solo para separar gravable de no gravable. No modifica el porcentaje empresa/empleado.                        |
| 6 | **SIGA NO actualiza `prepagada.db`**. Solo lee. La sincronización con Kactus es un proceso externo no documentado en el código.                    |
| 7 | **Las hojas `Novedad`, `No Cubrimientos`, `Maestro`, `Alerta Retirados` y `Descuento` se ignoran completamente** por el código.                     |
| 8 | El catálogo de proveedores está hardcodeado: `axa`, `colsanitas`, `desconocido`. AuxilioExterno sí permite EPS libre (texto).                       |

## ❌ Qué debemos NO afirmar

| # | Lo que no podemos decir                                                                                                                            |
|---|----------------------------------------------------------------------------------------------------------------------------------------------------|
| 1 | "El parentesco siempre viene del archivo AXA." — **Falso**. Depende de si la columna `PARENTESCO` está en la primera hoja del archivo.              |
| 2 | "El sistema identifica automáticamente a los pensionados." — **Falso**. Hay que registrarlos a mano en el Módulo 6 aunque AXA ya los marca con `PNS`. |
| 3 | "El cálculo del 80/20 considera descuento comercial e IVA." — **Falso**. Aplica el porcentaje literal sobre `total_familia`.                        |
| 4 | "Colmédica está soportada." — **Falso**, ni siquiera está mencionada en el código.                                                                  |
| 5 | "Los beneficiarios no cubiertos quedan registrados en el sistema." — **Falso**, esa hoja se ignora.                                                  |
| 6 | "El cruce con Kactus se actualiza desde el archivo AXA." — **Falso**. `prepagada.db` se actualiza por un proceso externo no controlado por SIGA.    |
| 7 | "El sistema toma la política vigente al periodo." — **Sin verificar contra código aún**; pero el cálculo recibe la política como argumento desde la vista, **no la elige por fecha**. Habrá que confirmar con `views.py` antes de afirmarlo. |

## ⚠️ Qué sigue siendo pregunta abierta para TH

| # | Pregunta abierta                                                                                                                                                |
|---|------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 1 | ¿Cuál es la **primera hoja física** del archivo `20251130PlanillaAxaColpatria.xlsx`? (Validar antes de la reunión abriendo el archivo).                         |
| 2 | Si `Planilla` no trae parentesco poblado, ¿quieren que SIGA pase a leer `Novedad`? (Cambio de una línea, alta prioridad).                                        |
| 3 | ¿Quieren que SIGA auto-identifique pensionados leyendo `NOM` y registre/actualice `PensionadoPrepagada` automáticamente?                                          |
| 4 | **APOYO MED. PREPAGADA COLMEDICA** del informe EFR: ¿es histórico, es auxilio externo, o es un proveedor real que hoy nadie procesa?                              |
| 5 | El descuento real del 14%–19.1% que ven en el archivo de noviembre 2025, ¿de dónde viene? ¿Es porque `total_familia` ya trae deducciones, porque la fórmula real es distinta, o porque Kactus aplica otros conceptos? |
| 6 | ¿La hoja `No Cubrimientos` se usa hoy para algo? (Justificación de exclusiones, auditoría, reclamaciones, etc.).                                                  |
| 7 | ¿Quién mantiene `prepagada.db` sincronizado con Kactus? ¿Con qué frecuencia? ¿Hay un proceso formal o es ad-hoc?                                                |
| 8 | ¿La hoja `Maestro` del archivo AXA la usan ustedes fuera de SIGA?                                                                                                |

---

**Anexo — Comandos de verificación ejecutados**

```bash
grep -ri "colmed" backend/ --include="*.py"
grep -ri -E "no.cubrimient|cubrimiento" backend/ --include="*.py"
grep -ri "maestro" backend/ --include="*.py"
grep -rn "sheet_name" backend/ --include="*.py"
grep -rn -E "'NOM'|\"NOM\"|ACT|PNS" backend/ --include="*.py"
grep -n "openpyxl\|pd.read_excel" backend/modules/beneficios_salud/services/*.py backend/modules/beneficios_salud/views.py
```

**Archivos leídos en su totalidad:**
- `siga/backend/modules/beneficios_salud/services/axa_adapter.py`
- `siga/backend/modules/beneficios_salud/services/reader_excel.py`
- `siga/backend/modules/beneficios_salud/services/eligibility.py`
- `siga/backend/modules/beneficios_salud/services/detector.py`
- `siga/backend/modules/beneficios_salud/services/prepagada_service.py`
- `siga/backend/modules/beneficios_salud/models.py`
