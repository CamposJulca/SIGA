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
