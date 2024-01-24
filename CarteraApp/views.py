from django.shortcuts import render, redirect
from .models import *
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
        'archivo_contrato' : contrato.archivo_contrato,
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

def pagos(request, Numero_Contrato):
    pagos = Pagos.objects.filter(numero_contrato__Numero_Contrato= Numero_Contrato)
    valor_contrato = Contratos.objects.get(Numero_Contrato=Numero_Contrato).valor
    valores_pago = sum(list(pagos.values_list('valor_pago', flat=True)))
    saldo = valor_contrato - valores_pago


    return render(request, "Pagos.html", {"Pagos": pagos, 'datos': [valor_contrato, valores_pago, saldo],'contrato': Numero_Contrato })

def agregar_pago_vista(request, Numero_Contrato):

    data = {
        'formu': AgregarPago(initial={'numero_contrato': Numero_Contrato})
    }

    if request.method == 'POST':
        formulario = AgregarPago(data=request.POST, files=request.FILES)
        if formulario.is_valid():
            formulario.save()
            return redirect('/Pagos/' + str(Numero_Contrato))
        else:
            data["form"] = formulario
    return render(request, "CrearPago.html", data)