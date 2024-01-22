from django.shortcuts import render, redirect
from .models import Clientes, Contratos
from .forms import *
# Create your views here.

def home(request):
    contrato=Contratos.objects.all()
    return render(request, "Home.html", {"Contratos":contrato})

def clientes(request):
    cliente = Clientes.objects.all()
    return render(request, "Clientes.html", {"Clientes": cliente})

def agregar_contrato_vista(request):
    data = {
        'form': CrearContrato()
    }
    if request.method == 'POST':
        formulario = CrearContrato(data=request.POST, files=request.FILES)
        if formulario.is_valid():
            formulario.save()
            return redirect('home')
        else:
            data["form"] = formulario

    return render(request, "CrearContrato.html", data)

def editar_contrato_vista(request, Numero_Contrato):

    contrato = Contratos.objects.get(Numero_Contrato=Numero_Contrato)
    data = {
        'Numero_Contrato': Numero_Contrato,
        'cliente': contrato.cliente.cedula,
        'valor': contrato.valor,
        'descripcion': contrato.descripcion,
        'Fecha_Inicial': contrato.Fecha_Inicial,
        'form': ActualizarContrato(instance=contrato),
    }
    if request.method == 'POST':
        formulario = ActualizarContrato(data=request.POST, instance=contrato, files=request.FILES)
        if formulario.is_valid():
            formulario.save()
            return redirect('home')
        else:
            data["form"] = formulario

    return render(request, "EditarContrato.html", data)

def agregar_cliente_vista(request):

    data = {
        'form': crear_cliente()
    }

    if request.method == 'POST':
        formulario = crear_cliente(data=request.POST)
        if formulario.is_valid():
            formulario.save()
            return redirect('clientes')
        else:
            data["form"] = formulario
    return render(request, "CrearCliente.html", data)

def eliminar_cliente(request, cedula):
    cliente = Clientes.objects.get(cedula=cedula)
    cliente.delete()
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
            return redirect('clientes')
        else:
            data["form"] = formulario

    return render(request, "EditarCliente.html", data)