import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('beneficios_salud', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='PoliticaPrepagada',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('porcentaje_empresa', models.DecimalField(decimal_places=2, default=80, max_digits=5)),
                ('porcentaje_empleado', models.DecimalField(decimal_places=2, default=20, max_digits=5)),
                ('uvt_limite', models.IntegerField(default=16)),
                ('valor_uvt', models.DecimalField(decimal_places=2, default=49799, max_digits=10)),
                ('porcentaje_empresa_pensionado', models.DecimalField(decimal_places=2, default=80, max_digits=5)),
                ('cod_conc_apoyo_no_grav', models.CharField(blank=True, max_length=20)),
                ('cod_conc_apoyo_grav', models.CharField(blank=True, max_length=20)),
                ('cod_conc_dcto_empleado', models.CharField(blank=True, max_length=20)),
                ('notas', models.TextField(blank=True)),
                ('vigente_desde', models.DateField()),
                ('creada_en', models.DateTimeField(auto_now_add=True)),
                ('creada_por', models.CharField(blank=True, max_length=150)),
            ],
            options={
                'db_table': 'bs_politica_prepagada',
                'ordering': ['-vigente_desde'],
            },
        ),
        migrations.CreateModel(
            name='PensionadoPrepagada',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cedula', models.CharField(max_length=20, unique=True)),
                ('nombre', models.CharField(max_length=200)),
                ('eps', models.CharField(max_length=50)),
                ('valor_mensual', models.DecimalField(decimal_places=2, max_digits=14)),
                ('fecha_inicio', models.DateField()),
                ('fecha_fin', models.DateField(blank=True, null=True)),
                ('activo', models.BooleanField(default=True)),
                ('observaciones', models.TextField(blank=True)),
                ('creado_en', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'db_table': 'bs_pensionados_prepagada',
            },
        ),
        migrations.CreateModel(
            name='AuxilioExterno',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cedula', models.CharField(max_length=20)),
                ('nombre', models.CharField(max_length=200)),
                ('eps', models.CharField(max_length=100)),
                ('valor_mensual', models.DecimalField(decimal_places=2, max_digits=14)),
                ('fecha_inicio', models.DateField()),
                ('fecha_fin', models.DateField(blank=True, null=True)),
                ('activo', models.BooleanField(default=True)),
                ('observaciones', models.TextField(blank=True)),
                ('creado_en', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'db_table': 'bs_auxilio_externo',
            },
        ),
        migrations.CreateModel(
            name='PlanillaCalculo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('periodo', models.CharField(max_length=10)),
                ('politica', models.ForeignKey(
                    on_delete=django.db.models.deletion.PROTECT,
                    to='beneficios_salud.politicaprepagada'
                )),
                ('total_empleados', models.IntegerField(default=0)),
                ('total_empresa', models.DecimalField(decimal_places=2, default=0, max_digits=16)),
                ('total_empleado', models.DecimalField(decimal_places=2, default=0, max_digits=16)),
                ('total_gravable', models.DecimalField(decimal_places=2, default=0, max_digits=16)),
                ('total_no_gravable', models.DecimalField(decimal_places=2, default=0, max_digits=16)),
                ('generada_en', models.DateTimeField(auto_now_add=True)),
                ('generada_por', models.CharField(blank=True, max_length=150)),
            ],
            options={
                'db_table': 'bs_planilla_calculo',
                'ordering': ['-periodo'],
            },
        ),
        migrations.CreateModel(
            name='DetalleCalculo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('planilla', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='detalles',
                    to='beneficios_salud.planillacalculo'
                )),
                ('cedula', models.CharField(max_length=20)),
                ('nombre_en_factura', models.CharField(blank=True, max_length=200)),
                ('nombre_en_kactus', models.CharField(blank=True, max_length=200)),
                ('eps', models.CharField(max_length=50)),
                ('num_beneficiarios', models.IntegerField(default=0)),
                ('total_familia', models.DecimalField(decimal_places=2, max_digits=14)),
                ('valor_empresa', models.DecimalField(decimal_places=2, max_digits=14)),
                ('valor_empleado', models.DecimalField(decimal_places=2, max_digits=14)),
                ('apoyo_no_gravable', models.DecimalField(decimal_places=2, max_digits=14)),
                ('apoyo_gravable', models.DecimalField(decimal_places=2, max_digits=14)),
                ('estado_cruce', models.CharField(max_length=20)),
                ('sue_basi', models.DecimalField(blank=True, decimal_places=2, max_digits=14, null=True)),
                ('tip_cont', models.CharField(blank=True, max_length=20)),
            ],
            options={
                'db_table': 'bs_detalle_calculo',
            },
        ),
    ]
