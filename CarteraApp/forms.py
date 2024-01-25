from django import forms
from .models import *


class crear_cliente(forms.ModelForm):
    class Meta:
        model = Clientes
        fields = '__all__'
        labels = {
            'cedula': 'Nit/Cédula',
        }

class actualizar_cliente(forms.ModelForm):
    class Meta:
        model = Clientes
        fields = ['nombre', 'correo', 'ciudad', 'direccion']

# modificar asesesor, fecha final
class CrearContrato(forms.ModelForm):
    class Meta:
        model = Contratos
        fields = '__all__'
        labels = {
           'Numero_Contrato': '# Contrato',
           'Fecha_Inicial': 'Fecha inicial',
           'Fecha_Final': 'Fecha final',
        }
        widgets = {
            'Fecha_Inicial': forms.DateInput(attrs={'type': 'date'}),
            'Fecha_Final': forms.DateInput(attrs={'type': 'date'}),
        }

class ActualizarContrato(forms.ModelForm):
    class Meta:
        model = Contratos
        fields = ['asesor', 'Fecha_Final', 'descripcion']
        widgets = {
            'Fecha_Inicial': forms.DateInput(attrs={'type': 'date'}),
            'Fecha_Final': forms.DateInput(attrs={'type': 'date'}),
        }

class AgregarPago(forms.ModelForm):
    class Meta:
        model =  Pagos
        fields = '__all__'
        labels = {
            'numero_contrato': '# Contrato',
        }
        widgets = {
            'fecha_pago': forms.DateInput(attrs={'type': 'date'}),
            'numero_contrato': forms.HiddenInput(),

        }

class EditarPago(forms.ModelForm):
    class Meta:
        model = Pagos
        fields = ['archivo_pago']
        widgets = {
            'fecha_pago': forms.DateInput(attrs={'type': 'date'}),
        }