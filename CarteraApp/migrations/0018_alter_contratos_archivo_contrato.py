# Generated by Django 4.1 on 2024-02-05 15:41

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("CarteraApp", "0017_alter_contratos_cliente_alter_pagos_numero_contrato"),
    ]

    operations = [
        migrations.AlterField(
            model_name="contratos",
            name="archivo_contrato",
            field=models.FileField(blank=True, null=True, upload_to="contratos/"),
        ),
    ]
