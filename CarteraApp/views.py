from django.shortcuts import render, redirect
from .models import *
from .forms import *
from django.contrib import messages
from .Funciones import *
import json
from django_datatables_view.base_datatable_view import BaseDatatableView
from django.http import JsonResponse
from django.db.models import Q
import random
from faker import Faker
from datetime import datetime, timedelta



class ContratosListJson(BaseDatatableView):
    model = Contratos
    columns = ['Numero_Contrato', 'asesor', 'cliente_id', 'valor', 'descripcion', 'Fecha_Inicial', 'Fecha_Final', 'archivo_contrato']
    def dispatch(self, request, *args, **kwargs):
        try:
            return super(ContratosListJson, self).dispatch(request, *args, **kwargs)
        except Exception as e:
            return JsonResponse({'error': str(e)})
    def render_column(self, row, column):
        if column in ['Fecha_Inicial', 'Fecha_Final']:
            return getattr(row, column).strftime('%Y-%m-%d') if getattr(row, column) else ''
        else:
            return super(ContratosListJson, self).render_column(row, column)
    def filter_queryset(self, qs):
        # Obtén el valor de búsqueda proporcionado por el usuario
        search = self.request.GET.get('search[value]', None)
        # Aplica el filtro solo si hay un valor de búsqueda
        if search:
            # Verifica si el valor de búsqueda es numérico
            if search.isdigit():
                # Aplica el filtro a la queryset utilizando filter directamente
                qs = qs.filter(
                    Q(Numero_Contrato__icontains=search) |
                    Q(cliente__cedula__icontains=search)
                )
            else:
                qs = qs.filter( Q(asesor__icontains=search))
        # Devuelve la queryset filtrada
        return qs
    def prepare_results(self, qs):
        data = []
        for item in qs:
            try:
                archivo = item.archivo_contrato.url
            except:
                archivo = ''
            data.append({
                'Numero_Contrato': item.Numero_Contrato,
                'asesor': item.asesor,
                'cliente_id': item.cliente_id,
                'valor': item.valor,
                'descripcion': item.descripcion,
                'Fecha_Inicial': item.Fecha_Inicial.strftime('%Y-%m-%d') if item.Fecha_Inicial else '',
                'Fecha_Final': item.Fecha_Final.strftime('%Y-%m-%d') if item.Fecha_Final else '',
                'archivo_contrato': archivo
            })
        return data
def home(request):
    return render(request, "ProyectoCartera/Contratos/Home.html")

class ClientesListJson(BaseDatatableView):
    model = Clientes
    columns = ['cedula', 'nombre', 'correo', 'ciudad', 'direccion']

    def dispatch(self, request, *args, **kwargs):
        try:
            return super(ClientesListJson, self).dispatch(request, *args, **kwargs)
        except Exception as e:
            return JsonResponse({'error': str(e)})
    def render_column(self, row, column):
        return super(ClientesListJson, self).render_column(row, column)

    def filter_queryset(self, qs):
        # Obtén el valor de búsqueda proporcionado por el usuario
        search = self.request.GET.get('search[value]', None)
        # Aplica el filtro solo si hay un valor de búsqueda
        if search:
            qs = qs.filter(
                Q(cedula__icontains=search) |
                Q(nombre__icontains=search) |
                Q(correo__icontains=search) |
                Q(ciudad__icontains=search)
            )
        # Devuelve la queryset filtrada
        return qs
    def prepare_results(self, qs):
        data = []
        for item in qs:
            data.append({
                'cedula': item.cedula,
                'nombre': item.nombre,
                'correo': item.correo,
                'ciudad': item.ciudad,
                'direccion': item.direccion
            })
        return data

def clientes(request):
    return render(request, "ProyectoCartera/Clientes/Clientes.html")

def agregar_contrato_vista(request):
    data = {
        'form': CrearContrato()
    }
    if request.method == 'POST':
        formulario = CrearContrato(data=request.POST, files=request.FILES)
        if formulario.is_valid():
            formulario.save()
            messages.success(request, "Contrato agregado exitosamente")
            return redirect('home')
        else:
            data["form"] = formulario

    return render(request, "ProyectoCartera/Contratos/CrearContrato.html", data)

def editar_contrato_vista(request, Numero_Contrato):
    try:

        contrato = Contratos.objects.get(Numero_Contrato=Numero_Contrato)
        data = {
            'Numero_Contrato': Numero_Contrato,
            'cliente': contrato.cliente.cedula,
            'valor': contrato.valor,
            'descripcion': contrato.descripcion,
            'Fecha_Inicial': contrato.Fecha_Inicial,
            'archivo_contrato' : contrato.archivo_contrato,
            'form': ActualizarContrato(instance=contrato),
        }
        if request.method == 'POST':
            formulario = ActualizarContrato(data=request.POST, instance=contrato, files=request.FILES)
            if formulario.is_valid():
                formulario.save()
                messages.success(request, "Se actualizo el contrato coreectamente!")
                return redirect('home')
            else:
                data["form"] = formulario

        return render(request, "ProyectoCartera/Contratos/EditarContrato.html", data)
    except:
        return render(request, "ProyectoCartera/error.html", {'mensaje': "Este contrato "})

def agregar_cliente_vista(request):

    data = {
        'form': crear_cliente()
    }

    if request.method == 'POST':
        formulario = crear_cliente(data=request.POST)
        if formulario.is_valid():
            formulario.save()
            messages.success(request, "Cliente agregado correctamente!")
            return redirect('clientes')
        else:
            data["form"] = formulario
    return render(request, "ProyectoCartera/Clientes/CrearCliente.html", data)

def eliminar_cliente(request, cedula):
    cliente = Clientes.objects.get(cedula=cedula)
    try:
        cliente.delete()
        messages.success(request, "Cliente eliminado exitosamente")
    except:
        messages.error(request, "El cliente no se puede eliminar porque tiene contratos registrados.")
    return redirect('clientes')

def editar_cliente_vista(request, cedula):
    cliente = Clientes.objects.get(cedula=cedula)
    data = {
        'cedula': cedula,
        'form': actualizar_cliente(instance=cliente)
    }
    if request.method == 'POST':
        formulario = actualizar_cliente(data=request.POST, instance=cliente)
        if formulario.is_valid():
            formulario.save()
            messages.success(request, "Cliente actualizado correctamente!")
            return redirect('clientes')
        else:
            data["form"] = formulario

    return render(request, "ProyectoCartera/Clientes/EditarCliente.html", data)

class PagosListJson(BaseDatatableView):
    model = Pagos
    columns = ['numero_contrato', 'tipo_pago', 'valor_pago', 'fecha_pago', 'archivo_pago']

    # def dispatch(self, request, *args, **kwargs):
    #     try:
    #         return super(PagosListJson, self).dispatch(request, *args, **kwargs)
    #     except Exception as e:
    #         return JsonResponse({'error': str(e)})

    def render_column(self, row, column):
        if column in ['fecha_pago']:
            return getattr(row, column).strftime('%Y-%m-%d') if getattr(row, column) else ''
        else:
            return super(PagosListJson, self).render_column(row, column)

    def prepare_results(self, qs):
        data = []
        for item in qs:
            try:
                archivo = item.archivo_pago.url
            except:
                archivo = ''
            data.append({
                'numero_contrato': item.numero_contrato,
                'tipo_pago': item.tipo_pago,
                'valor_pago': item.valor_pago,
                'fecha_pago': item.fecha_pago.strftime('%Y-%m-%d') if item.fecha_pago else '',
                'archivo_pago': archivo
            })
        return data

def pagos(request, Numero_Contrato):
    datos = saldo_pagos(Numero_Contrato)
    return render(request, "ProyectoCartera/Pagos/Pagos.html", {'datos': datos , 'contrato': Numero_Contrato})
    # except:
    #     return render(request, "ProyectoCartera/error.html", {'mensaje': "Este contrato no existe"})

def agregar_pago_vista(request, Numero_Contrato):

    data = {
        'formu': AgregarPago(initial={'numero_contrato': Numero_Contrato})
    }
    datos = saldo_pagos(Numero_Contrato)
    if request.method == 'POST':
        formulario = AgregarPago(data=request.POST, files=request.FILES)
        if formulario.is_valid():
            valor_pago = formulario.cleaned_data['valor_pago']
            valor_contrato = datos[0]

            if valor_pago > valor_contrato or valor_pago > datos[2]:
                messages.error(request, "El valor de pago supera el valor del saldo")
                return render(request, "ProyectoCartera/Pagos/CrearPago.html", data)
            else:
                formulario.save()
                messages.success(request, "Pago agregado correctamente!")
                return redirect('/Pagos/' + str(Numero_Contrato))
        else:
            data["form"] = formulario
    return render(request, "ProyectoCartera/Pagos/CrearPago.html", data)

def editar_pago_vista(request, id):
    pago = Pagos.objects.get(id = id)
    data = {
        'numero_contrato' : pago.numero_contrato.Numero_Contrato,
        'tipo_pago' : pago.get_tipo_pago_display(),
        'valor_pago' : pago.valor_pago,
        'fecha_pago' : pago.fecha_pago,
        'form': EditarPago(instance=pago),
    }
    if request.method == 'POST':
        formulario = EditarPago(data=request.POST, instance=pago, files=request.FILES)
        if formulario.is_valid():
            formulario.save()
            messages.success(request, "Actualizado el pago correctamente!")
            return redirect('/Pagos/' + str(pago.numero_contrato.Numero_Contrato))
        else:
            data["form"] = formulario

    return render(request, "ProyectoCartera/Pagos/EditarPago.html", data)