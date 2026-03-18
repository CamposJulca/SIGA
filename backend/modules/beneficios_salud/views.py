"""
Vistas REST para el módulo Beneficios de Salud (SIGA).
"""
import hashlib
import os

from django.conf import settings
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import ArchivoRecibido, BeneficioSalud, ErrorProcesamiento
from .serializers import (
    ArchivoRecibidoListSerializer,
    ArchivoRecibidoDetailSerializer,
    BeneficioSaludSerializer,
)
from .services.detector import detectar_proveedor
from .services.reader_excel import leer_excel
from .services.axa_adapter import adaptar_axa
from .services.colsanitas_adapter import adaptar_colsanitas
from .services.validator import validar_registros


def _sha256_archivo(file_obj) -> str:
    """Calcula el hash SHA256 de un objeto archivo."""
    sha256 = hashlib.sha256()
    file_obj.seek(0)
    for chunk in iter(lambda: file_obj.read(8192), b''):
        sha256.update(chunk)
    file_obj.seek(0)
    return sha256.hexdigest()


def _guardar_archivo(file_obj, proveedor: str, nombre_archivo: str) -> str:
    """
    Guarda el archivo en storage/landing/{proveedor}/{nombre_archivo}.
    Retorna la ruta absoluta donde fue guardado.
    """
    directorio_proveedor = {
        'axa': 'axa_colpatria',
        'colsanitas': 'colsanitas',
        'desconocido': 'desconocido',
    }.get(proveedor, 'desconocido')

    destino_dir = os.path.join(settings.MEDIA_ROOT, directorio_proveedor)
    os.makedirs(destino_dir, exist_ok=True)

    ruta_destino = os.path.join(destino_dir, nombre_archivo)

    file_obj.seek(0)
    with open(ruta_destino, 'wb') as f:
        for chunk in file_obj.chunks():
            f.write(chunk)

    return ruta_destino


class UploadView(APIView):
    """
    POST /api/beneficios-salud/upload/
    Recibe un archivo Excel via multipart form y lo procesa.
    """
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, *args, **kwargs):
        archivo = request.FILES.get('archivo')
        if not archivo:
            return Response(
                {'error': 'Se requiere el campo "archivo" con el archivo Excel.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        usuario = 'anonimo'
        if request.user and request.user.is_authenticated:
            usuario = request.user.username
        elif request.data.get('usuario'):
            usuario = str(request.data.get('usuario'))

        nombre_archivo = archivo.name
        hash_archivo = _sha256_archivo(archivo)

        # Detección inicial del proveedor por nombre de archivo
        proveedor = detectar_proveedor(nombre_archivo)

        # Guardar archivo en disco
        try:
            ruta_archivo = _guardar_archivo(archivo, proveedor, nombre_archivo)
        except Exception as exc:
            return Response(
                {'error': f'No se pudo guardar el archivo: {exc}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        # Crear registro ArchivoRecibido
        archivo_obj = ArchivoRecibido.objects.create(
            proveedor=proveedor,
            nombre_archivo=nombre_archivo,
            ruta_archivo=ruta_archivo,
            estado_procesamiento='RECIBIDO',
            hash_archivo=hash_archivo,
            usuario_carga=usuario,
        )

        try:
            # Marcar como PROCESANDO
            archivo_obj.estado_procesamiento = 'PROCESANDO'
            archivo_obj.save(update_fields=['estado_procesamiento'])

            # Leer Excel
            df, metadatos = leer_excel(ruta_archivo, proveedor)

            # Refinar detección por columnas si el proveedor era desconocido
            if proveedor == 'desconocido':
                proveedor = detectar_proveedor(nombre_archivo, list(df.columns))
                archivo_obj.proveedor = proveedor

            # Actualizar metadatos en el registro
            archivo_obj.numero_contrato = metadatos.get('numero_contrato', '')
            archivo_obj.periodo_facturacion = metadatos.get('periodo_facturacion', '')

            # Adaptar al esquema unificado
            if proveedor == 'axa':
                df_unificado = adaptar_axa(df, metadatos)
            elif proveedor == 'colsanitas':
                df_unificado = adaptar_colsanitas(df, metadatos)
            else:
                raise ValueError(
                    f'Proveedor no reconocido: "{proveedor}". '
                    'El nombre del archivo debe contener "AXA" o "COLSANITAS".'
                )

            # Añadir archivo_origen al dataframe
            df_unificado['archivo_origen'] = nombre_archivo

            total_registros = len(df_unificado)
            archivo_obj.total_registros = total_registros
            archivo_obj.save(update_fields=['proveedor', 'numero_contrato', 'periodo_facturacion', 'total_registros'])

            # Validar registros
            registros_ok, errores_val = validar_registros(df_unificado, archivo_obj.id)

            # Inserción bulk de beneficios
            beneficios_bulk = [BeneficioSalud(**r) for r in registros_ok]
            BeneficioSalud.objects.bulk_create(beneficios_bulk, batch_size=500)

            # Inserción bulk de errores
            errores_bulk = [ErrorProcesamiento(**e) for e in errores_val]
            ErrorProcesamiento.objects.bulk_create(errores_bulk, batch_size=500)

            registros_procesados = len(registros_ok)
            # Errores fatales = registros que no se insertaron (no incluye advertencias)
            registros_con_error = total_registros - registros_procesados

            # Actualizar estadísticas
            archivo_obj.registros_procesados = registros_procesados
            archivo_obj.registros_con_error = registros_con_error
            archivo_obj.estado_procesamiento = 'PROCESADO'
            archivo_obj.save(update_fields=[
                'registros_procesados',
                'registros_con_error',
                'estado_procesamiento',
            ])

            return Response({
                'archivo_id': archivo_obj.id,
                'proveedor': archivo_obj.proveedor,
                'total_registros': total_registros,
                'registros_procesados': registros_procesados,
                'registros_con_error': registros_con_error,
                'estado': 'PROCESADO',
            }, status=status.HTTP_201_CREATED)

        except Exception as exc:
            archivo_obj.estado_procesamiento = 'ERROR'
            archivo_obj.save(update_fields=['estado_procesamiento'])
            return Response(
                {
                    'error': str(exc),
                    'archivo_id': archivo_obj.id,
                    'estado': 'ERROR',
                },
                status=status.HTTP_422_UNPROCESSABLE_ENTITY
            )


class ArchivoListView(APIView):
    """
    GET /api/beneficios-salud/archivos/
    Lista todos los ArchivoRecibido.
    """

    def get(self, request, *args, **kwargs):
        qs = ArchivoRecibido.objects.all()

        proveedor = request.query_params.get('proveedor')
        if proveedor:
            qs = qs.filter(proveedor=proveedor)

        estado = request.query_params.get('estado')
        if estado:
            qs = qs.filter(estado_procesamiento=estado)

        serializer = ArchivoRecibidoListSerializer(qs, many=True)
        return Response(serializer.data)


class ArchivoDetailView(APIView):
    """
    GET /api/beneficios-salud/archivos/{id}/
    Detalle de un archivo con sus errores.
    """

    def get(self, request, pk, *args, **kwargs):
        try:
            archivo = ArchivoRecibido.objects.get(pk=pk)
        except ArchivoRecibido.DoesNotExist:
            return Response(
                {'error': f'Archivo con id={pk} no encontrado.'},
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = ArchivoRecibidoDetailSerializer(archivo)
        return Response(serializer.data)


class BeneficioListView(APIView):
    """
    GET /api/beneficios-salud/beneficios/
    Lista BeneficioSalud con filtros opcionales: ?archivo_id=X&proveedor=X&cedula=X
    """

    def get(self, request, *args, **kwargs):
        qs = BeneficioSalud.objects.select_related('archivo').all()

        archivo_id = request.query_params.get('archivo_id')
        if archivo_id:
            qs = qs.filter(archivo_id=archivo_id)

        proveedor = request.query_params.get('proveedor')
        if proveedor:
            qs = qs.filter(proveedor=proveedor)

        cedula = request.query_params.get('cedula')
        if cedula:
            qs = qs.filter(cedula=cedula)

        estado_validacion = request.query_params.get('estado_validacion')
        if estado_validacion:
            qs = qs.filter(estado_validacion=estado_validacion)

        serializer = BeneficioSaludSerializer(qs, many=True)
        return Response(serializer.data)


class ExportarExcelView(APIView):
    """
    GET /api/beneficios-salud/exportar/?archivo_id=X
    Exporta beneficios de salud a un archivo Excel (.xlsx) con tres hojas:
    Consolidado, AXA Colpatria, Colsanitas.
    Si se pasa archivo_id, exporta ese archivo.
    Si no, exporta el último archivo PROCESADO de cada proveedor.
    """

    COLUMNAS = [
        'cedula', 'nombre', 'parentesco', 'sub_contrato', 'cedula_titular',
        'proveedor', 'tipo_plan', 'valor_base', 'descuento', 'iva',
        'valor_total', 'fecha_corte', 'numero_contrato', 'periodo_facturacion',
        'estado_validacion',
    ]

    def get(self, request, *args, **kwargs):
        from io import BytesIO
        from datetime import date
        import openpyxl
        from openpyxl.styles import PatternFill, Font
        from django.http import HttpResponse
        from django.db.models import Max

        archivo_id = request.query_params.get('archivo_id')

        qs = BeneficioSalud.objects.select_related('archivo').filter(
            archivo__estado_procesamiento='PROCESADO'
        )

        if archivo_id:
            qs = qs.filter(archivo_id=archivo_id)
        else:
            # Obtener el max(id) de ArchivoRecibido por proveedor entre los procesados
            max_ids = (
                ArchivoRecibido.objects
                .filter(estado_procesamiento='PROCESADO')
                .values('proveedor')
                .annotate(max_id=Max('id'))
                .values_list('max_id', flat=True)
            )
            qs = qs.filter(archivo_id__in=list(max_ids))

        qs = qs.order_by('proveedor', 'nombre')

        registros_raw = list(qs.values(
            'cedula', 'nombre', 'parentesco', 'sub_contrato', 'cedula_titular',
            'proveedor', 'tipo_plan', 'valor_base', 'descuento', 'iva',
            'valor_total', 'fecha_corte', 'numero_contrato',
            'estado_validacion', 'archivo__nombre_archivo',
            'archivo__periodo_facturacion',
        ))
        # Normalizar para que el template use 'periodo_facturacion'
        registros = []
        for r in registros_raw:
            r['periodo_facturacion'] = r.pop('archivo__periodo_facturacion', '') or ''
            registros.append(r)

        wb = openpyxl.Workbook()

        header_fill = PatternFill(start_color='00853f', end_color='00853f', fill_type='solid')
        header_font = Font(color='FFFFFF', bold=True)
        warn_fill   = PatternFill(start_color='FFFDE7', end_color='FFFDE7', fill_type='solid')

        def _escribir_hoja(ws, filas, incluir_origen=False):
            cols = self.COLUMNAS + (['archivo_origen'] if incluir_origen else [])
            # Encabezado
            for col_idx, col_name in enumerate(cols, start=1):
                cell = ws.cell(row=1, column=col_idx, value=col_name)
                cell.fill = header_fill
                cell.font = header_font
            # Datos
            for row_idx, reg in enumerate(filas, start=2):
                es_advertencia = reg.get('estado_validacion') == 'ADVERTENCIA'
                for col_idx, col_name in enumerate(cols, start=1):
                    if col_name == 'archivo_origen':
                        valor = reg.get('archivo__nombre_archivo', '')
                    else:
                        valor = reg.get(col_name, '')
                    cell = ws.cell(row=row_idx, column=col_idx, value=valor)
                    if es_advertencia:
                        cell.fill = warn_fill

        # Hoja Consolidado
        ws_consolidado = wb.active
        ws_consolidado.title = 'Consolidado'
        _escribir_hoja(ws_consolidado, registros, incluir_origen=True)

        # Hoja AXA Colpatria
        ws_axa = wb.create_sheet(title='AXA Colpatria')
        filas_axa = [r for r in registros if r.get('proveedor') == 'axa']
        _escribir_hoja(ws_axa, filas_axa, incluir_origen=False)

        # Hoja Colsanitas
        ws_col = wb.create_sheet(title='Colsanitas')
        filas_col = [r for r in registros if r.get('proveedor') == 'colsanitas']
        _escribir_hoja(ws_col, filas_col, incluir_origen=False)

        buffer = BytesIO()
        wb.save(buffer)
        buffer.seek(0)

        fecha_hoy = date.today().strftime('%Y%m%d')
        nombre_archivo = f'SIGA_Beneficios_{fecha_hoy}.xlsx'

        response = HttpResponse(
            buffer.read(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        )
        response['Content-Disposition'] = f'attachment; filename="{nombre_archivo}"'
        return response


class NovedadesView(APIView):
    """
    GET /api/beneficios-salud/novedades/?archivo_nuevo=X&archivo_anterior=Y
    Compara dos archivos de BeneficioSalud y devuelve las novedades:
    nuevos afiliados, retirados y cambios de valor de cuota.
    """

    def get(self, request, *args, **kwargs):
        archivo_nuevo_id = request.query_params.get('archivo_nuevo')
        archivo_anterior_id = request.query_params.get('archivo_anterior')

        if not archivo_nuevo_id or not archivo_anterior_id:
            return Response(
                {'error': 'Se requieren los parámetros "archivo_nuevo" y "archivo_anterior".'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            archivo_nuevo = ArchivoRecibido.objects.get(pk=archivo_nuevo_id)
        except ArchivoRecibido.DoesNotExist:
            return Response(
                {'error': f'Archivo con id={archivo_nuevo_id} no encontrado.'},
                status=status.HTTP_404_NOT_FOUND,
            )

        try:
            archivo_anterior = ArchivoRecibido.objects.get(pk=archivo_anterior_id)
        except ArchivoRecibido.DoesNotExist:
            return Response(
                {'error': f'Archivo con id={archivo_anterior_id} no encontrado.'},
                status=status.HTTP_404_NOT_FOUND,
            )

        warning = None
        if archivo_nuevo.proveedor != archivo_anterior.proveedor:
            warning = (
                f'Los archivos son de distinto proveedor: '
                f'"{archivo_nuevo.proveedor}" vs "{archivo_anterior.proveedor}".'
            )

        # Cargar registros de cada archivo como dicts por cédula
        qs_nuevo = BeneficioSalud.objects.filter(archivo_id=archivo_nuevo_id).values(
            'cedula', 'nombre', 'parentesco', 'valor_total'
        )
        qs_anterior = BeneficioSalud.objects.filter(archivo_id=archivo_anterior_id).values(
            'cedula', 'nombre', 'parentesco', 'valor_total'
        )

        mapa_nuevo    = {r['cedula']: r for r in qs_nuevo}
        mapa_anterior = {r['cedula']: r for r in qs_anterior}

        cedulas_nuevo    = set(mapa_nuevo.keys())
        cedulas_anterior = set(mapa_anterior.keys())

        cedulas_nuevos    = cedulas_nuevo - cedulas_anterior
        cedulas_retirados = cedulas_anterior - cedulas_nuevo
        cedulas_comunes   = cedulas_nuevo & cedulas_anterior

        nuevos = [
            {
                'cedula':     c,
                'nombre':     mapa_nuevo[c]['nombre'],
                'parentesco': mapa_nuevo[c]['parentesco'],
                'valor_total': mapa_nuevo[c]['valor_total'],
            }
            for c in sorted(cedulas_nuevos)
        ]

        retirados = [
            {
                'cedula':     c,
                'nombre':     mapa_anterior[c]['nombre'],
                'parentesco': mapa_anterior[c]['parentesco'],
                'valor_total': mapa_anterior[c]['valor_total'],
            }
            for c in sorted(cedulas_retirados)
        ]

        cambios_valor = []
        sin_cambios_count = 0
        for c in cedulas_comunes:
            vn = mapa_nuevo[c]['valor_total'] or 0
            va = mapa_anterior[c]['valor_total'] or 0
            try:
                vn_f = float(vn)
                va_f = float(va)
            except (TypeError, ValueError):
                vn_f = 0.0
                va_f = 0.0
            if abs(vn_f - va_f) > 1.0:
                cambios_valor.append({
                    'cedula':        c,
                    'nombre':        mapa_nuevo[c]['nombre'],
                    'parentesco':    mapa_nuevo[c]['parentesco'],
                    'valor_anterior': va,
                    'valor_nuevo':    vn,
                    'diferencia':     round(vn_f - va_f, 2),
                })
            else:
                sin_cambios_count += 1

        data = {
            'archivo_nuevo': {
                'id':                  archivo_nuevo.id,
                'nombre_archivo':      archivo_nuevo.nombre_archivo,
                'proveedor':           archivo_nuevo.proveedor,
                'periodo_facturacion': archivo_nuevo.periodo_facturacion,
            },
            'archivo_anterior': {
                'id':                  archivo_anterior.id,
                'nombre_archivo':      archivo_anterior.nombre_archivo,
                'proveedor':           archivo_anterior.proveedor,
                'periodo_facturacion': archivo_anterior.periodo_facturacion,
            },
            'resumen': {
                'nuevos':        len(nuevos),
                'retirados':     len(retirados),
                'cambios_valor': len(cambios_valor),
                'sin_cambios':   sin_cambios_count,
            },
            'nuevos':        nuevos,
            'retirados':     retirados,
            'cambios_valor': cambios_valor,
        }

        if warning:
            data['warning'] = warning

        return Response(data)


class DashboardView(APIView):
    """
    GET /api/beneficios-salud/dashboard/
    Resumen ejecutivo para el dashboard visual de SIGA.
    """

    PARENTESCO_LABEL = {
        'T': 'Titular', 'CO': 'Cónyuge', 'HI': 'Hijo(a)',
        'P': 'Padres', 'OT': 'Otro', '': 'Sin especificar',
    }

    def get(self, request, *args, **kwargs):
        from django.db.models import Max, Sum, Count

        # ── Último archivo procesado por proveedor ──────────────────────────
        ultimos_ids = (
            ArchivoRecibido.objects
            .filter(estado_procesamiento='PROCESADO')
            .values('proveedor')
            .annotate(max_id=Max('id'))
            .values_list('max_id', flat=True)
        )
        ultimos_archivos = ArchivoRecibido.objects.filter(id__in=list(ultimos_ids))

        ultimos_periodos = []
        for arch in ultimos_archivos.order_by('proveedor'):
            agg = BeneficioSalud.objects.filter(archivo=arch).aggregate(
                total_beneficiarios=Count('id'),
                valor_total=Sum('valor_total'),
            )
            ultimos_periodos.append({
                'proveedor':           arch.proveedor,
                'periodo':             arch.periodo_facturacion or '—',
                'numero_contrato':     arch.numero_contrato or '—',
                'archivo_id':          arch.id,
                'nombre_archivo':      arch.nombre_archivo,
                'fecha_procesamiento': arch.fecha_recepcion.date().isoformat() if arch.fecha_recepcion else None,
                'total_beneficiarios': agg['total_beneficiarios'] or 0,
                'valor_total':         float(agg['valor_total'] or 0),
                'registros_procesados': arch.registros_procesados,
                'registros_con_error':  arch.registros_con_error,
            })

        # ── Distribución por parentesco (sobre últimos archivos) ────────────
        qs_ultimos = BeneficioSalud.objects.filter(archivo_id__in=list(ultimos_ids))

        dist_parentesco_raw = (
            qs_ultimos
            .values('parentesco')
            .annotate(count=Count('id'), valor_total=Sum('valor_total'))
            .order_by('-count')
        )
        distribucion_parentesco = []
        for row in dist_parentesco_raw:
            p = (row['parentesco'] or '').strip().upper()
            distribucion_parentesco.append({
                'parentesco':  row['parentesco'] or '',
                'label':       self.PARENTESCO_LABEL.get(p, row['parentesco'] or 'Sin especificar'),
                'count':       row['count'],
                'valor_total': float(row['valor_total'] or 0),
            })

        # ── Distribución de valor por proveedor (últimos archivos) ──────────
        dist_proveedor = []
        for row in (
            qs_ultimos
            .values('proveedor')
            .annotate(count=Count('id'), valor_total=Sum('valor_total'))
            .order_by('proveedor')
        ):
            dist_proveedor.append({
                'proveedor':   row['proveedor'],
                'count':       row['count'],
                'valor_total': float(row['valor_total'] or 0),
            })

        # ── Evolución histórica (valor_total por archivo procesado) ─────────
        evolucion = []
        for arch in (
            ArchivoRecibido.objects
            .filter(estado_procesamiento='PROCESADO')
            .order_by('id')
        ):
            agg = BeneficioSalud.objects.filter(archivo=arch).aggregate(
                valor_total=Sum('valor_total'),
                count=Count('id'),
            )
            evolucion.append({
                'archivo_id':   arch.id,
                'proveedor':    arch.proveedor,
                'periodo':      arch.periodo_facturacion or arch.nombre_archivo[:30],
                'valor_total':  float(agg['valor_total'] or 0),
                'beneficiarios': agg['count'] or 0,
                'fecha':        arch.fecha_recepcion.date().isoformat() if arch.fecha_recepcion else None,
            })

        # ── Consolidado global ───────────────────────────────────────────────
        total_archivos_procesados = ArchivoRecibido.objects.filter(
            estado_procesamiento='PROCESADO'
        ).count()

        consolidado_agg = qs_ultimos.aggregate(
            valor_total=Sum('valor_total'),
            beneficiarios=Count('id'),
        )

        return Response({
            'ultimos_periodos':       ultimos_periodos,
            'distribucion_parentesco': distribucion_parentesco,
            'distribucion_proveedor':  dist_proveedor,
            'evolucion':               evolucion,
            'consolidado': {
                'total_archivos_procesados': total_archivos_procesados,
                'beneficiarios_ultimo_periodo': consolidado_agg['beneficiarios'] or 0,
                'valor_total_ultimo_periodo':   float(consolidado_agg['valor_total'] or 0),
                'proveedores_activos':          len(ultimos_periodos),
            },
        })
