from rest_framework import serializers
from .models import (
    ArchivoRecibido, BeneficioSalud, ErrorProcesamiento,
    PoliticaPrepagada, PensionadoPrepagada, AuxilioExterno,
    PlanillaCalculo, DetalleCalculo,
)


class ErrorProcesamientoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ErrorProcesamiento
        fields = [
            'id',
            'fila_origen',
            'tipo_error',
            'descripcion',
            'valor_encontrado',
            'timestamp',
        ]


class BeneficioSaludSerializer(serializers.ModelSerializer):
    class Meta:
        model = BeneficioSalud
        fields = [
            'id',
            'archivo',
            'cedula',
            'tipo_id',
            'nombre',
            'parentesco',
            'sub_contrato',
            'cedula_titular',
            'proveedor',
            'tipo_plan',
            'valor_base',
            'descuento',
            'iva',
            'valor_total',
            'fecha_nacimiento',
            'edad',
            'fecha_corte',
            'numero_contrato',
            'archivo_origen',
            'fecha_procesamiento',
            'estado_validacion',
        ]


class ArchivoRecibidoListSerializer(serializers.ModelSerializer):
    """Serializer ligero para listado."""

    class Meta:
        model = ArchivoRecibido
        fields = [
            'id',
            'proveedor',
            'nombre_archivo',
            'fecha_recepcion',
            'estado_procesamiento',
            'total_registros',
            'registros_procesados',
            'registros_con_error',
            'numero_contrato',
            'periodo_facturacion',
        ]


class ArchivoRecibidoDetailSerializer(serializers.ModelSerializer):
    """Serializer detallado con errores anidados."""
    errores = ErrorProcesamientoSerializer(many=True, read_only=True)

    class Meta:
        model = ArchivoRecibido
        fields = [
            'id',
            'proveedor',
            'nombre_archivo',
            'ruta_archivo',
            'fecha_recepcion',
            'estado_procesamiento',
            'hash_archivo',
            'usuario_carga',
            'total_registros',
            'registros_procesados',
            'registros_con_error',
            'numero_contrato',
            'periodo_facturacion',
            'errores',
        ]


# ---------------------------------------------------------------------------
# Medicina Prepagada serializers
# ---------------------------------------------------------------------------

class PoliticaPrepagadaSerializer(serializers.ModelSerializer):
    class Meta:
        model = PoliticaPrepagada
        fields = [
            'id',
            'porcentaje_empresa',
            'porcentaje_empleado',
            'uvt_limite',
            'valor_uvt',
            'porcentaje_empresa_pensionado',
            'cod_conc_apoyo_no_grav',
            'cod_conc_apoyo_grav',
            'cod_conc_dcto_empleado',
            'notas',
            'vigente_desde',
            'creada_en',
            'creada_por',
        ]
        read_only_fields = ['creada_en']


class PensionadoPrepagadaSerializer(serializers.ModelSerializer):
    class Meta:
        model = PensionadoPrepagada
        fields = [
            'id',
            'cedula',
            'nombre',
            'eps',
            'valor_mensual',
            'fecha_inicio',
            'fecha_fin',
            'activo',
            'observaciones',
            'creado_en',
        ]
        read_only_fields = ['creado_en']


class AuxilioExternoSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuxilioExterno
        fields = [
            'id',
            'cedula',
            'nombre',
            'eps',
            'valor_mensual',
            'fecha_inicio',
            'fecha_fin',
            'activo',
            'observaciones',
            'creado_en',
        ]
        read_only_fields = ['creado_en']


class DetalleCalculoSerializer(serializers.ModelSerializer):
    class Meta:
        model = DetalleCalculo
        fields = [
            'id',
            'cedula',
            'nombre_en_factura',
            'nombre_en_kactus',
            'eps',
            'num_beneficiarios',
            'total_familia',
            'valor_empresa',
            'valor_empleado',
            'apoyo_no_gravable',
            'apoyo_gravable',
            'estado_cruce',
            'tipo_persona',
            'estado_elegibilidad',
            'motivo_elegibilidad',
            'porcentaje_empresa_aplicado',
            'porcentaje_empleado_aplicado',
            'valor_no_cubierto',
            'sue_basi',
            'tip_cont',
        ]


class PlanillaCalculoListSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlanillaCalculo
        fields = [
            'id',
            'periodo',
            'politica',
            'total_empleados',
            'total_empresa',
            'total_empleado',
            'total_gravable',
            'total_no_gravable',
            'generada_en',
            'generada_por',
        ]
        read_only_fields = ['generada_en']


class PlanillaCalculoDetailSerializer(serializers.ModelSerializer):
    detalles = DetalleCalculoSerializer(many=True, read_only=True)
    politica = PoliticaPrepagadaSerializer(read_only=True)

    class Meta:
        model = PlanillaCalculo
        fields = [
            'id',
            'periodo',
            'politica',
            'total_empleados',
            'total_empresa',
            'total_empleado',
            'total_gravable',
            'total_no_gravable',
            'generada_en',
            'generada_por',
            'detalles',
        ]
        read_only_fields = ['generada_en']
