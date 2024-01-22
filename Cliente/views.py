from django.shortcuts import render, redirect
from .models import Clientes
from .forms import CrearCliente
# Create your views here.

def home(request):
    cliente=Clientes.objects.all()
    return render(request, "principal.html", {"Clientes":cliente})

def AgregarClienteVista(request):

    data = {
        'form': CrearCliente()
    }

    if request.method == 'POST':
        formulario = CrearCliente(data=request.POST)
        if formulario.is_valid():
            formulario.save()
            return redirect('home')
        else:
            data["form"] = formulario
    return render(request, "CrearCliente.html", data)

def EliminarCliente(request, cedula):
    cliente = Clientes.objects.get(cedula=cedula)
    cliente.delete()
    return redirect('home')

def EditarClienteVista(request, cedula):
    cliente = Clientes.objects.get(cedula=cedula)
    data = {
        'form': CrearCliente(instance=cliente)
    }
    if request.method == 'POST':
        formulario = CrearCliente(data=request.POST, instance=cliente)
        if formulario.is_valid():
            formulario.save()
            print('aqui')
            return redirect('home')
        else:
            data["form"] = formulario

    return render(request, "EditarCliente.html", data)