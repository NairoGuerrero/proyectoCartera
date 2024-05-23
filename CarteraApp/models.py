from django.db import models
from django.utils import timezone


# Create your models here.

class Clientes(models.Model):
    cedula = models.CharField(primary_key=True, max_length=10)
    nombre = models.CharField(max_length=50)
    correo = models.EmailField(max_length=254)
    ciudad = models.CharField(max_length=20)
    direccion = models.CharField(max_length=50)

    def __str__(self):
        texto = "{0} - {1} "
        return texto.format(self.nombre, self.cedula)


class Contratos(models.Model):
    numero_contrato = models.IntegerField(primary_key=True)
    asesor = models.CharField(max_length=50)
    cliente = models.ForeignKey(Clientes, on_delete=models.PROTECT)
    valor = models.IntegerField()
    fecha_inicial = models.DateField()
    fecha_final = models.DateField()
    archivo_contrato = models.FileField(upload_to='contratos/', blank=True, null=True)
    valor_subcontratos = models.IntegerField(default=0, blank=True, null=True)
    descripcion = models.TextField(blank=True, null=True)

class AdicionContrato(models.Model):
    contrato = models.ForeignKey(Contratos, on_delete=models.PROTECT)
    nuevo_valor = models.IntegerField( blank=True, null=True)
    nueva_fecha = models.DateField( blank=True, null=True)
    archivo_nuevo = models.FileField(upload_to='contratos/')


class Pagos(models.Model):
    tipo_pago_opciones = [
        ('recibo_de_caja_efectivo', 'Recibo de caja - Efectivo'),
        ('recibo_de_caja_banco', 'Recibo de caja -  Banco'),
        ('recibo_de_caja_cruce', 'Recibo de caja -  Cruce')
    ]
    contrato = models.ForeignKey(Contratos, on_delete=models.PROTECT)
    tipo_pago = models.CharField(max_length=50, choices=tipo_pago_opciones)
    valor_pago = models.IntegerField()
    fecha_pago = models.DateField()
    archivo_pago = models.FileField(upload_to='Recibos/')
