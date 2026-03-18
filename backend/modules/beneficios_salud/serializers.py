from rest_framework import serializers
from .models import ArchivoRecibido, BeneficioSalud, ErrorProcesamiento


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
