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
    cliente = models.ForeignKey(Clientes, on_delete=models.CASCADE)
    valor = models.IntegerField()
    descripcion = models.CharField(max_length=255)
    Fecha_Inicial = models.DateField()
    Fecha_Final = models.DateField(blank=True, null=True)

    def __str__(self):
        texto = "{0} {1} {2} {3} {4} {5} {6}"
        return texto.format(self.Numero_Contrato, self.asesor, self.cliente.cedula, self.valor, self.descripcion, self.Fecha_Inicial, self.Fecha_Final)