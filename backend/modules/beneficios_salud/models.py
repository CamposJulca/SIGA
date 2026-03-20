from django.db import models


class ArchivoRecibido(models.Model):
    PROVEEDOR_CHOICES = [
        ('axa', 'AXA Colpatria'),
        ('colsanitas', 'Colsanitas'),
        ('desconocido', 'Desconocido'),
    ]
    ESTADO_CHOICES = [
        ('RECIBIDO', 'Recibido'),
        ('PROCESANDO', 'Procesando'),
        ('PROCESADO', 'Procesado'),
        ('ERROR', 'Error'),
    ]

    proveedor = models.CharField(max_length=50, choices=PROVEEDOR_CHOICES, default='desconocido')
    nombre_archivo = models.CharField(max_length=300)
    ruta_archivo = models.CharField(max_length=500)
    fecha_recepcion = models.DateTimeField(auto_now_add=True)
    estado_procesamiento = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='RECIBIDO')
    hash_archivo = models.CharField(max_length=64)
    usuario_carga = models.CharField(max_length=150)
    total_registros = models.IntegerField(default=0)
    registros_procesados = models.IntegerField(default=0)
    registros_con_error = models.IntegerField(default=0)
    numero_contrato = models.CharField(max_length=50, blank=True)
    periodo_facturacion = models.CharField(max_length=50, blank=True)

    class Meta:
        db_table = 'bs_archivos_recibidos'
        ordering = ['-fecha_recepcion']
        verbose_name = 'Archivo Recibido'
        verbose_name_plural = 'Archivos Recibidos'

    def __str__(self):
        return f"{self.nombre_archivo} [{self.proveedor}] - {self.estado_procesamiento}"


class BeneficioSalud(models.Model):
    ESTADO_CHOICES = [
        ('OK', 'OK'),
        ('ERROR', 'Error'),
        ('ADVERTENCIA', 'Advertencia'),
    ]

    archivo = models.ForeignKey(
        ArchivoRecibido,
        on_delete=models.CASCADE,
        related_name='beneficios'
    )
    cedula = models.CharField(max_length=20)
    tipo_id = models.CharField(max_length=5, blank=True)
    nombre = models.CharField(max_length=200)
    parentesco = models.CharField(max_length=5, blank=True)
    sub_contrato = models.CharField(max_length=20, blank=True)
    cedula_titular = models.CharField(max_length=20, blank=True)
    proveedor = models.CharField(max_length=50)
    tipo_plan = models.CharField(max_length=100, blank=True)
    valor_base = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    descuento = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    iva = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    valor_total = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    fecha_nacimiento = models.CharField(max_length=20, blank=True)
    edad = models.IntegerField(null=True, blank=True)
    fecha_corte = models.DateField(null=True, blank=True)
    numero_contrato = models.CharField(max_length=50, blank=True)
    archivo_origen = models.CharField(max_length=300, blank=True)
    fecha_procesamiento = models.DateTimeField(auto_now_add=True)
    estado_validacion = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='OK')

    class Meta:
        db_table = 'bs_beneficios_salud'
        ordering = ['archivo', 'cedula']
        verbose_name = 'Beneficio de Salud'
        verbose_name_plural = 'Beneficios de Salud'

    def __str__(self):
        return f"{self.cedula} - {self.nombre} [{self.proveedor}]"


class ErrorProcesamiento(models.Model):
    archivo = models.ForeignKey(
        ArchivoRecibido,
        on_delete=models.CASCADE,
        related_name='errores'
    )
    fila_origen = models.IntegerField()
    tipo_error = models.CharField(max_length=50)
    descripcion = models.TextField()
    valor_encontrado = models.CharField(max_length=200, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'bs_errores_procesamiento'
        ordering = ['archivo', 'fila_origen']
        verbose_name = 'Error de Procesamiento'
        verbose_name_plural = 'Errores de Procesamiento'

    def __str__(self):
        return f"[{self.tipo_error}] fila {self.fila_origen} - {self.descripcion[:60]}"


# ---------------------------------------------------------------------------
# Medicina Prepagada
# ---------------------------------------------------------------------------

class PoliticaPrepagada(models.Model):
    porcentaje_empresa = models.DecimalField(max_digits=5, decimal_places=2, default=80)
    porcentaje_empleado = models.DecimalField(max_digits=5, decimal_places=2, default=20)
    uvt_limite = models.IntegerField(default=16)
    valor_uvt = models.DecimalField(max_digits=10, decimal_places=2, default=49799)
    porcentaje_empresa_pensionado = models.DecimalField(max_digits=5, decimal_places=2, default=80)
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

    def __str__(self):
        return f"{self.cedula} - {self.nombre} [{self.eps}]"


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


class PlanillaCalculo(models.Model):
    periodo = models.CharField(max_length=10)
    politica = models.ForeignKey(PoliticaPrepagada, on_delete=models.PROTECT)
    total_empleados = models.IntegerField(default=0)
    total_empresa = models.DecimalField(max_digits=16, decimal_places=2, default=0)
    total_empleado = models.DecimalField(max_digits=16, decimal_places=2, default=0)
    total_gravable = models.DecimalField(max_digits=16, decimal_places=2, default=0)
    total_no_gravable = models.DecimalField(max_digits=16, decimal_places=2, default=0)
    generada_en = models.DateTimeField(auto_now_add=True)
    generada_por = models.CharField(max_length=150, blank=True)

    class Meta:
        db_table = 'bs_planilla_calculo'
        ordering = ['-periodo']

    def __str__(self):
        return f"Planilla {self.periodo} (política {self.politica_id})"


class DetalleCalculo(models.Model):
    planilla = models.ForeignKey(PlanillaCalculo, on_delete=models.CASCADE, related_name='detalles')
    cedula = models.CharField(max_length=20)
    nombre_en_factura = models.CharField(max_length=200, blank=True)
    nombre_en_kactus = models.CharField(max_length=200, blank=True)
    eps = models.CharField(max_length=50)
    num_beneficiarios = models.IntegerField(default=0)
    total_familia = models.DecimalField(max_digits=14, decimal_places=2)
    valor_empresa = models.DecimalField(max_digits=14, decimal_places=2)
    valor_empleado = models.DecimalField(max_digits=14, decimal_places=2)
    apoyo_no_gravable = models.DecimalField(max_digits=14, decimal_places=2)
    apoyo_gravable = models.DecimalField(max_digits=14, decimal_places=2)
    estado_cruce = models.CharField(max_length=20)
    sue_basi = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    tip_cont = models.CharField(max_length=20, blank=True)

    class Meta:
        db_table = 'bs_detalle_calculo'

    def __str__(self):
        return f"{self.cedula} - {self.eps} [{self.planilla.periodo}]"
