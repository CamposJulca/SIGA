from django.contrib import admin
from .models import ArchivoRecibido, BeneficioSalud, ErrorProcesamiento


@admin.register(ArchivoRecibido)
class ArchivoRecibidoAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'nombre_archivo',
        'proveedor',
        'fecha_recepcion',
        'estado_procesamiento',
        'total_registros',
        'registros_procesados',
        'registros_con_error',
        'numero_contrato',
        'periodo_facturacion',
        'usuario_carga',
    ]
    list_filter = ['proveedor', 'estado_procesamiento']
    search_fields = ['nombre_archivo', 'numero_contrato', 'usuario_carga', 'hash_archivo']
    readonly_fields = [
        'fecha_recepcion',
        'hash_archivo',
        'total_registros',
        'registros_procesados',
        'registros_con_error',
    ]
    ordering = ['-fecha_recepcion']


@admin.register(BeneficioSalud)
class BeneficioSaludAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'cedula',
        'nombre',
        'proveedor',
        'parentesco',
        'sub_contrato',
        'valor_base',
        'descuento',
        'iva',
        'valor_total',
        'estado_validacion',
        'fecha_procesamiento',
        'archivo',
    ]
    list_filter = ['proveedor', 'estado_validacion', 'parentesco']
    search_fields = ['cedula', 'nombre', 'sub_contrato', 'numero_contrato']
    readonly_fields = ['fecha_procesamiento']
    raw_id_fields = ['archivo']
    ordering = ['archivo', 'cedula']


@admin.register(ErrorProcesamiento)
class ErrorProcesamientoAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'archivo',
        'fila_origen',
        'tipo_error',
        'descripcion',
        'valor_encontrado',
        'timestamp',
    ]
    list_filter = ['tipo_error']
    search_fields = ['tipo_error', 'descripcion', 'valor_encontrado']
    readonly_fields = ['timestamp']
    raw_id_fields = ['archivo']
    ordering = ['archivo', 'fila_origen']
