# Generated by Django 4.2.11 on 2024-06-14 21:10

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("CarteraApp", "0027_contratos_valor_subcontratos"),
    ]

    operations = [
        migrations.AddField(
            model_name="pagos",
            name="descripcion_pago",
            field=models.CharField(default="", max_length=20),
        ),
    ]
