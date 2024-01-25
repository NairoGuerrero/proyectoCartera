from django.db import models

# Create your models here.

class Clientes(models.Model):
    cedula = models.CharField(primary_key=True, max_length=10)
    nombre = models.CharField(max_length=50)
    correo = models.EmailField(max_length=254)
    ciudad = models.CharField(max_length=20)
    direccion = models.CharField(max_length=50)

    def __str__(self):
        texto = "{0} - {1} "
        return texto.format( self.nombre, self.cedula)


class Contratos(models.Model):
    Numero_Contrato = models.IntegerField(primary_key=True)
    asesor = models.CharField(max_length=50)
    cliente = models.ForeignKey(Clientes, on_delete=models.PROTECT)
    valor = models.IntegerField()
    Fecha_Inicial = models.DateField()
    Fecha_Final = models.DateField(blank=True, null=True)
    archivo_contrato = models.FileField(upload_to='Contratos/')
    descripcion = models.TextField(blank=True, null=True)

    def __str__(self):
        texto = "{0} - {1}"
        return texto.format(self.Numero_Contrato, self.asesor)

class Pagos(models.Model):
    tipo_pago_opciones = [
        ('recibo_de_caja', 'Recibo de Caja'),
        ('factura', 'Factura'),
    ]
    numero_contrato = models.ForeignKey(Contratos, on_delete=models.PROTECT)
    tipo_pago = models.CharField(max_length=20, choices=tipo_pago_opciones)
    valor_pago = models.IntegerField()
    fecha_pago = models.DateField()
    archivo_pago = models.FileField(upload_to='Recibos/', blank=True, null=True)

    def __str__(self):
        texto = "{0} - {1}"
        return texto.format(self.numero_contrato, self.tipo_pago, self.valor_pago, self.fecha_pago)