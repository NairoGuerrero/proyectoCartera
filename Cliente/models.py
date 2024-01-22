from django.db import models

# Create your models here.

class Clientes(models.Model):
    cedula=models.CharField(primary_key=True, max_length=10)
    nombre=models.CharField(max_length=50)
    correo=models.EmailField(max_length=254)
    ciudad = models.CharField(max_length=20)
    direccion=models.CharField(max_length=50)
    

    def __str__(self):
        texto = "{0} {1} {2} {3} {4}"
        return texto.format(self.cedula, self.nombre, self.correo, self.ciudad, self.direccion)