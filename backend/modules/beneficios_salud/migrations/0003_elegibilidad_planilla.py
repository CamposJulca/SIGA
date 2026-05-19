from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('beneficios_salud', '0002_prepagada_modules'),
    ]

    operations = [
        migrations.AlterField(
            model_name='politicaprepagada',
            name='porcentaje_empresa_pensionado',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=5),
        ),
        migrations.AddField(
            model_name='detallecalculo',
            name='tipo_persona',
            field=models.CharField(default='EMPLEADO', max_length=30),
        ),
        migrations.AddField(
            model_name='detallecalculo',
            name='estado_elegibilidad',
            field=models.CharField(default='ELEGIBLE_80_20', max_length=40),
        ),
        migrations.AddField(
            model_name='detallecalculo',
            name='motivo_elegibilidad',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='detallecalculo',
            name='porcentaje_empresa_aplicado',
            field=models.DecimalField(decimal_places=2, default=80, max_digits=5),
        ),
        migrations.AddField(
            model_name='detallecalculo',
            name='porcentaje_empleado_aplicado',
            field=models.DecimalField(decimal_places=2, default=20, max_digits=5),
        ),
        migrations.AddField(
            model_name='detallecalculo',
            name='valor_no_cubierto',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=14),
        ),
    ]
