from django.contrib import admin
from .models import (
    ArchivoRecibido, BeneficioSalud, ErrorProcesamiento,
    PoliticaPrepagada, PensionadoPrepagada, AuxilioExterno,
    PlanillaCalculo, DetalleCalculo,
)


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


# ---------------------------------------------------------------------------
# Medicina Prepagada admin
# ---------------------------------------------------------------------------

@admin.register(PoliticaPrepagada)
class PoliticaPrepagadaAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'vigente_desde',
        'porcentaje_empresa',
        'porcentaje_empleado',
        'uvt_limite',
        'valor_uvt',
        'creada_por',
        'creada_en',
    ]
    list_filter = ['vigente_desde']
    search_fields = ['creada_por', 'notas']
    readonly_fields = ['creada_en']
    ordering = ['-vigente_desde']


@admin.register(PensionadoPrepagada)
class PensionadoPrepagadaAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'cedula',
        'nombre',
        'eps',
        'valor_mensual',
        'fecha_inicio',
        'fecha_fin',
        'activo',
        'creado_en',
    ]
    list_filter = ['activo', 'eps']
    search_fields = ['cedula', 'nombre']
    readonly_fields = ['creado_en']
    ordering = ['nombre']


@admin.register(AuxilioExterno)
class AuxilioExternoAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'cedula',
        'nombre',
        'eps',
        'valor_mensual',
        'fecha_inicio',
        'fecha_fin',
        'activo',
        'creado_en',
    ]
    list_filter = ['activo', 'eps']
    search_fields = ['cedula', 'nombre']
    readonly_fields = ['creado_en']
    ordering = ['nombre']


class DetalleCalculoInline(admin.TabularInline):
    model = DetalleCalculo
    extra = 0
    readonly_fields = [
        'cedula', 'nombre_en_factura', 'nombre_en_kactus', 'eps',
        'num_beneficiarios', 'total_familia', 'valor_empresa', 'valor_empleado',
        'apoyo_no_gravable', 'apoyo_gravable', 'estado_cruce', 'sue_basi', 'tip_cont',
    ]
    can_delete = False
    show_change_link = False


@admin.register(PlanillaCalculo)
class PlanillaCalculoAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'periodo',
        'politica',
        'total_empleados',
        'total_empresa',
        'total_empleado',
        'total_gravable',
        'total_no_gravable',
        'generada_por',
        'generada_en',
    ]
    list_filter = ['periodo']
    search_fields = ['periodo', 'generada_por']
    readonly_fields = ['generada_en']
    raw_id_fields = ['politica']
    ordering = ['-periodo', '-generada_en']
    inlines = [DetalleCalculoInline]


@admin.register(DetalleCalculo)
class DetalleCalculoAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'planilla',
        'cedula',
        'nombre_en_kactus',
        'eps',
        'total_familia',
        'valor_empresa',
        'valor_empleado',
        'apoyo_no_gravable',
        'apoyo_gravable',
        'estado_cruce',
    ]
    list_filter = ['estado_cruce', 'eps']
    search_fields = ['cedula', 'nombre_en_kactus', 'nombre_en_factura']
    raw_id_fields = ['planilla']
    ordering = ['planilla', 'eps', 'cedula']
