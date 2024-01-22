# Generated by Django 4.2.6 on 2024-01-20 13:40

from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Clientes",
            fields=[
                (
                    "cedula",
                    models.CharField(max_length=10, primary_key=True, serialize=False),
                ),
                ("nombre", models.CharField(max_length=50)),
                ("correo", models.EmailField(max_length=254)),
                ("direccion", models.CharField(max_length=50)),
                ("ciudad", models.CharField(max_length=20)),
            ],
        ),
    ]
