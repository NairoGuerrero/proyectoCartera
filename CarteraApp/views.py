from django.shortcuts import render, redirect
from .models import *
from .forms import *
from django.contrib import messages
from .Funciones import *
# Create your views here.

def home(request):
    contrato=list(Contratos.objects.all().values())
    # Crear una lista de listas con los valores de cada contrato
    contrato_lista = [
        [
            infoContrato['Numero_Contrato'],
            infoContrato['asesor'],
            infoContrato['cliente_id'],
            infoContrato['valor'],
            infoContrato['descripcion'],
            infoContrato['Fecha_Inicial'].strftime('%Y-%m-%d') if infoContrato['Fecha_Inicial'] else '',
            infoContrato['Fecha_Final'].strftime('%Y-%m-%d') if infoContrato['Fecha_Final'] else '',
            infoContrato['archivo_contrato'],
            ""
        ]
        for infoContrato in contrato
    ]
    print(contrato_lista)
    return render(request, "ProyectoCartera/Contratos/Home.html", {"Contratos":contrato_lista})

def clientes(request):
    cliente = list(Clientes.objects.all().values())
    clientes_vista = [
        [
            infocliente['cedula'],
            infocliente['nombre'],
            infocliente['correo'],
            infocliente['ciudad'],
            infocliente['direccion'],
            ""
        ]
        for infocliente in cliente
    ]
    return render(request, "ProyectoCartera/Clientes/Clientes.html", {"Clientes": clientes_vista})

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

def pagos(request, Numero_Contrato):
    try:
        datos = saldo_pagos(Numero_Contrato)
        return render(request, "ProyectoCartera/Pagos/Pagos.html", {"Pagos":  datos[3], 'datos': datos , 'contrato': Numero_Contrato})
    except:
        return render(request, "ProyectoCartera/error.html", {'mensaje': "Este contrato no existe"})

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