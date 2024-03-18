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
        fields = '__all__'
        widgets = {
            'cedula': forms.TextInput(attrs={'readonly': 'readonly', 'style': 'background-color: #f2f2f2'}),
        }


# modificar asesesor, fecha final
class CrearContrato(forms.ModelForm):
    class Meta:
        model = Contratos
        fields = '__all__'
        labels = {
            'numero_contrato': '# Contrato',
            'fecha_inicial': 'Fecha inicial',
            'fecha_final': 'Fecha final',
        }
        widgets = {
            'fecha_inicial': forms.DateInput(attrs={'type': 'date'}),
            'fecha_final': forms.DateInput(attrs={'type': 'date'}),
        }


class ActualizarContrato(forms.ModelForm):
    class Meta:
        model = Contratos
        fields = '__all__'
        widgets = {
            'fecha_inicial': forms.DateInput(attrs={'type': 'date','readonly': 'readonly', 'style': 'background-color: #f2f2f2'}),
            'fecha_final': forms.DateInput(attrs={'type': 'date'}),
            'numero_contrato': forms.TextInput(attrs={'readonly': 'readonly', 'style': 'background-color: #f2f2f2'}),
            'cliente': forms.TextInput(attrs={'readonly': 'readonly', 'style': 'background-color: #f2f2f2'}),
            'valor': forms.TextInput(attrs={'readonly': 'readonly', 'style': 'background-color: #f2f2f2'}),
            'fecha_inicial': forms.TextInput(attrs={'readonly': 'readonly', 'style': 'background-color: #f2f2f2'})
        }


class AgregarPago(forms.ModelForm):
    class Meta:
        model = Pagos
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
        fields = '__all__'
        widgets = {
            'fecha_pago': forms.DateInput(attrs={'type': 'date','readonly': 'readonly', 'style': 'background-color: #f2f2f2'}),
            'numero_contrato': forms.TextInput(attrs={'readonly': 'readonly', 'style': 'background-color: #f2f2f2'}),
            'tipo_pago': forms.TextInput(attrs={'readonly': 'readonly', 'style': 'background-color: #f2f2f2'}),
            'valor_pago': forms.TextInput(attrs={'readonly': 'readonly', 'style': 'background-color: #f2f2f2'}),
        }
