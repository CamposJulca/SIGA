import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='ArchivoRecibido',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('proveedor', models.CharField(
                    choices=[('axa', 'AXA Colpatria'), ('colsanitas', 'Colsanitas'), ('desconocido', 'Desconocido')],
                    default='desconocido', max_length=50
                )),
                ('nombre_archivo', models.CharField(max_length=300)),
                ('ruta_archivo', models.CharField(max_length=500)),
                ('fecha_recepcion', models.DateTimeField(auto_now_add=True)),
                ('estado_procesamiento', models.CharField(
                    choices=[('RECIBIDO', 'Recibido'), ('PROCESANDO', 'Procesando'), ('PROCESADO', 'Procesado'), ('ERROR', 'Error')],
                    default='RECIBIDO', max_length=20
                )),
                ('hash_archivo', models.CharField(max_length=64)),
                ('usuario_carga', models.CharField(max_length=150)),
                ('total_registros', models.IntegerField(default=0)),
                ('registros_procesados', models.IntegerField(default=0)),
                ('registros_con_error', models.IntegerField(default=0)),
                ('numero_contrato', models.CharField(blank=True, max_length=50)),
                ('periodo_facturacion', models.CharField(blank=True, max_length=50)),
            ],
            options={
                'verbose_name': 'Archivo Recibido',
                'verbose_name_plural': 'Archivos Recibidos',
                'db_table': 'bs_archivos_recibidos',
                'ordering': ['-fecha_recepcion'],
            },
        ),
        migrations.CreateModel(
            name='BeneficioSalud',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('archivo', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='beneficios',
                    to='beneficios_salud.archivorecibido'
                )),
                ('cedula', models.CharField(max_length=20)),
                ('tipo_id', models.CharField(blank=True, max_length=5)),
                ('nombre', models.CharField(max_length=200)),
                ('parentesco', models.CharField(blank=True, max_length=5)),
                ('sub_contrato', models.CharField(blank=True, max_length=20)),
                ('cedula_titular', models.CharField(blank=True, max_length=20)),
                ('proveedor', models.CharField(max_length=50)),
                ('tipo_plan', models.CharField(blank=True, max_length=100)),
                ('valor_base', models.DecimalField(decimal_places=2, default=0, max_digits=14)),
                ('descuento', models.DecimalField(decimal_places=2, default=0, max_digits=14)),
                ('iva', models.DecimalField(decimal_places=2, default=0, max_digits=14)),
                ('valor_total', models.DecimalField(decimal_places=2, default=0, max_digits=14)),
                ('fecha_nacimiento', models.CharField(blank=True, max_length=20)),
                ('edad', models.IntegerField(blank=True, null=True)),
                ('fecha_corte', models.DateField(blank=True, null=True)),
                ('numero_contrato', models.CharField(blank=True, max_length=50)),
                ('archivo_origen', models.CharField(blank=True, max_length=300)),
                ('fecha_procesamiento', models.DateTimeField(auto_now_add=True)),
                ('estado_validacion', models.CharField(
                    choices=[('OK', 'OK'), ('ERROR', 'Error'), ('ADVERTENCIA', 'Advertencia')],
                    default='OK', max_length=20
                )),
            ],
            options={
                'verbose_name': 'Beneficio de Salud',
                'verbose_name_plural': 'Beneficios de Salud',
                'db_table': 'bs_beneficios_salud',
                'ordering': ['archivo', 'cedula'],
            },
        ),
        migrations.CreateModel(
            name='ErrorProcesamiento',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('archivo', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='errores',
                    to='beneficios_salud.archivorecibido'
                )),
                ('fila_origen', models.IntegerField()),
                ('tipo_error', models.CharField(max_length=50)),
                ('descripcion', models.TextField()),
                ('valor_encontrado', models.CharField(blank=True, max_length=200)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name': 'Error de Procesamiento',
                'verbose_name_plural': 'Errores de Procesamiento',
                'db_table': 'bs_errores_procesamiento',
                'ordering': ['archivo', 'fila_origen'],
            },
        ),
    ]
