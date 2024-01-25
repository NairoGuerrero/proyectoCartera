# Generated by Django 4.2.6 on 2024-01-25 16:01

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("CarteraApp", "0016_alter_contratos_descripcion"),
    ]

    operations = [
        migrations.AlterField(
            model_name="contratos",
            name="cliente",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT, to="CarteraApp.clientes"
            ),
        ),
        migrations.AlterField(
            model_name="pagos",
            name="numero_contrato",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT, to="CarteraApp.contratos"
            ),
        ),
    ]
