from django.shortcuts import render, redirect
from .forms import *
from django.contrib import messages
from .Funciones import *
from django_datatables_view.base_datatable_view import BaseDatatableView
from django.http import JsonResponse
from django.db.models import Q
import locale
import datetime
from django.utils.translation import gettext as _


class ContratosListJson(BaseDatatableView):
    model = Contratos

    def dispatch(self, request, *args, **kwargs):
        try:
            return super(ContratosListJson, self).dispatch(request, *args, **kwargs)
        except Exception as e:
            return JsonResponse({'error': str(e)})

    def render_column(self, row, column):
        if column in ['fecha_inicial', 'fecha_final']:
            return getattr(row, column).strftime('%Y-%m-%d') if getattr(row, column) else ''
        else:
            return super(ContratosListJson, self).render_column(row, column)

    def filter_queryset(self, qs):
        # Obtén el valor de búsqueda proporcionado por el usuario
        search = self.request.GET.get('search[value]', None)
        search_contrato = self.request.GET.get('search_contrato', None)

        filtros = [search, search_contrato]

        hay_datos = False
        for elemento in filtros:
            if elemento != '':
                hay_datos = True
                break  # Si se encuentra al menos un dato, podemos detener la iteración

        if hay_datos:
            qs = qs.filter(
                Q(numero_contrato=search_contrato)
            )
        else:
            qs = qs.all()
        return qs

    def prepare_results(self, qs):
        locale.setlocale(locale.LC_ALL, 'es_CO.UTF-8')
        prueba = []
        today = datetime.date.today()

        for item in qs:
            try:
                archivo = item.archivo_contrato.url
            except:
                archivo = ''

            dias_restantes = (item.fecha_final - today).days if item.fecha_final else None
            prueba.append({
                'numero_contrato': item.numero_contrato,
                'asesor': item.asesor,
                'cliente_id': item.cliente.nombre,
                'valor': locale.format_string("%.0f", item.valor, grouping=True),
                'saldo': locale.format_string("%.0f", saldo_pagos(item.numero_contrato)[2], grouping=True),
                'dias_restantes': dias_restantes,
                'fecha_inicial': item.fecha_inicial.strftime(
                    '%d de %B del %Y') if item.fecha_inicial else item.fecha_inicial,
                'fecha_final': item.fecha_final.strftime('%d de %B del %Y') if item.fecha_final else item.fecha_final,
                'archivo_contrato': archivo
            })
        return prueba


def home(request):
    return render(request, "proyectoCartera/contratos/Home.html")


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
    return render(request, "proyectoCartera/clientes/Clientes.html")


def agregar_contrato_vista(request):
    data = {
        'form': CrearContrato()
    }
    if request.method == 'POST':
        formulario = CrearContrato(data=request.POST, files=request.FILES)
        if formulario.is_valid():
            formulario.save()
            messages.success(request, "Contrato agregado exitosamente")
            return redirect('carteraApp_home')
        else:
            data["form"] = formulario

    return render(request, "proyectoCartera/contratos/CrearContrato.html", data)


def editar_contrato_vista(request, numero_contrato):
    try:

        contrato = Contratos.objects.get(numero_contrato=numero_contrato)
        data = {
            'form': ActualizarContrato(instance=contrato),
        }
        if request.method == 'POST':
            formulario = ActualizarContrato(data=request.POST, instance=contrato, files=request.FILES)
            if formulario.is_valid():
                formulario.save()
                messages.success(request, "Se actualizo el contrato coreectamente!")
                return redirect('carteraApp_home')
            else:
                data["form"] = formulario

        return render(request, "proyectoCartera/contratos/EditarContrato.html", data)
    except:
        return render(request, "proyectoCartera/error.html", {'mensaje': "Este contrato "})


def agregar_cliente_vista(request):
    data = {
        'form': crear_cliente()
    }

    if request.method == 'POST':
        formulario = crear_cliente(data=request.POST)
        if formulario.is_valid():
            formulario.save()
            messages.success(request, "Cliente agregado correctamente!")
            return redirect('carteraApp_clientes')
        else:
            data["form"] = formulario
    return render(request, "proyectoCartera/clientes/CrearCliente.html", data)


def eliminar_cliente(request, cedula):
    cliente = Clientes.objects.get(cedula=cedula)
    try:
        cliente.delete()
        messages.success(request, "Cliente eliminado exitosamente")
    except:
        messages.error(request, "El cliente no se puede eliminar porque tiene contratos registrados.")
    return redirect('carteraApp_clientes')


def editar_cliente_vista(request, cedula):
    cliente = Clientes.objects.get(cedula=cedula)
    data = {
        'form': actualizar_cliente(instance=cliente)
    }
    if request.method == 'POST':
        formulario = actualizar_cliente(data=request.POST, instance=cliente)
        if formulario.is_valid():
            formulario.save()
            messages.success(request, "Cliente actualizado correctamente!")
            return redirect('carteraApp_clientes')
        else:
            data["form"] = formulario

    return render(request, "proyectoCartera/clientes/EditarCliente.html", data)


# class PagosListJson(BaseDatatableView):
#     model = Pagos
#     columns = ['numero_contrato', 'tipo_pago', 'cliente', 'valor_pago', 'fecha_pago', 'archivo_pago']
#
#     def dispatch(self, request, *args, **kwargs):
#         try:
#             return super(PagosListJson, self).dispatch(request, *args, **kwargs)
#
#         except Exception as e:
#             return JsonResponse({'error': str(e)})
#
#     def render_column(self, row, column):
#         if column in ['fecha_pago']:
#             return getattr(row, column).strftime('%Y-%m-%d') if getattr(row, column) else ''
#         else:
#             return super(PagosListJson, self).render_column(row, column)
#
#     def prepare_results(self, qs):
#         data = []
#
#         for item in qs:
#             try:
#                 archivo = item.archivo_pago.url
#             except:
#                 archivo = ''
#
#             data.append({
#                 'numero_contrato': item.numero_contrato.numero_contrato,
#                 'tipo_pago': item.tipo_pago,
#                 'cliente': 'nose',
#                 'valor_pago': item.valor_pago,
#                 'fecha_pago': item.fecha_pago.strftime('%Y-%m-%d') if item.fecha_pago else '',
#                 'archivo_pago': archivo
#             })
#         return data


def pagos(request, numero_contrato):
    # Configurar locale para formatear el número con separadores de miles
    locale.setlocale(locale.LC_ALL, '')

    datos = saldo_pagos(numero_contrato)
    pagos = list(Pagos.objects.filter(contrato__numero_contrato=numero_contrato).values())

    Pagos_lista = [
        [infoPagos['id'],
         infoPagos['contrato_id'],
         infoPagos['tipo_pago'],
         locale.format_string("%.0f", infoPagos['valor_pago'], grouping=True),  # Formatear el valor_pago
         infoPagos['fecha_pago'].strftime('%Y-%m-%d') if infoPagos['fecha_pago'] else '',
         infoPagos['archivo_pago'],
         ""
         ]
        for infoPagos in pagos
    ]
    # Reemplazar el valor de 'tipo_pago' con el texto descriptivo
    for infoPagos in Pagos_lista:
        infoPagos[2] = dict(Pagos.tipo_pago_opciones)[infoPagos[2]]

    return render(request, "proyectoCartera/pagos/Pagos.html",
                  {'datos': datos, 'contrato': numero_contrato, 'datos_pagos': Pagos_lista})


def agregar_pago_vista(request, numero_contrato):
    data = {
        'formu': AgregarPago(initial={'contrato': numero_contrato})
    }
    datos = saldo_pagos(numero_contrato)
    if request.method == 'POST':
        formulario = AgregarPago(data=request.POST, files=request.FILES)
        if formulario.is_valid():
            valor_pago = formulario.cleaned_data['valor_pago']
            valor_contrato = datos[4]

            if valor_pago > valor_contrato or valor_pago > datos[2]:
                messages.error(request, "El valor de pago supera el valor del saldo")
                return render(request, "proyectoCartera/pagos/CrearPago.html", data)
            else:
                formulario.save()
                messages.success(request, "Pago agregado correctamente!")
                return redirect('carteraApp_ver_contrato', str(numero_contrato))
                # return redirect('/pagos/' + str(numero_contrato))
        else:
            data["form"] = formulario
    return render(request, "proyectoCartera/pagos/CrearPago.html", data)


def editar_pago_vista(request, id):
    pago = Pagos.objects.get(id=id)
    data = {
        'form': EditarPago(instance=pago),
    }
    if request.method == 'POST':
        formulario = EditarPago(data=request.POST, instance=pago, files=request.FILES)
        if formulario.is_valid():
            formulario.save()
            messages.success(request, "Actualizado el pago correctamente!")
            return redirect('carteraApp_ver_contrato', str(pago.contrato.numero_contrato))
            # return redirect('/pagos/' + str(pago.numero_contrato.numero_contrato))
        else:
            data["form"] = formulario

    return render(request, "proyectoCartera/pagos/EditarPago.html", data)


class PagosListJson(BaseDatatableView):
    model = Pagos

    # columns = ['numero_contrato', 'asesor', 'cliente_id', 'valor', 'descripcion', 'fecha_inicial', 'fecha_final',
    #            'archivo_contrato']

    def __init__(self):
        super().__init__()
        self.parametros = {}

    def get_initial_queryset(self):
        if not self.model:
            raise NotImplementedError(
                "Need to provide a model or implement get_initial_queryset!"
            )
        return self.model.objects.filter(contrato=self.parametros.get('numero_contrato'))

    def dispatch(self, request, *args, **kwargs):
        try:
            self.parametros = kwargs
            print('pagos :', kwargs)
            return super(PagosListJson, self).dispatch(request, *args, **kwargs)
        except Exception as e:
            return JsonResponse({'error': str(e)})

    def render_column(self, row, column):

        return super(PagosListJson, self).render_column(row, column)

    def filter_queryset(self, qs):
        # Obtén el valor de búsqueda proporcionado por el usuario
        search = self.request.GET.get('search[value]', None)
        # Aplica el filtro solo si hay un valor de búsqueda
        if search:
            # Verifica si el valor de búsqueda es numérico
            if search.isdigit():
                # Aplica el filtro a la queryset utilizando filter directamente
                qs = qs.filter(
                    Q(numero_contrato__icontains=search) |
                    Q(cliente__cedula__icontains=search)
                )
            else:
                qs = qs.filter(Q(asesor__icontains=search))
        # Devuelve la queryset filtrada
        return qs

    def prepare_results(self, qs):
        locale.setlocale(locale.LC_ALL, 'es_CO.UTF-8')
        data = []
        today = datetime.date.today()

        for item in qs:
            data.append({
                'id': item.id,
                'contrato': item.contrato.numero_contrato,
                'tipo_pago': item.get_tipo_pago_display(),
                'valor_pago': locale.format_string("%.0f", item.valor_pago, grouping=True),
                'fecha_pago': item.fecha_pago.strftime('%d de %B del %Y') if item.fecha_pago else item.fecha_pago,
                'archivo_pago': item.archivo_pago.url

            })

        return data


class SubContratosListJson(BaseDatatableView):
    model = AdicionContrato

    # columns = ['numero_contrato', 'asesor', 'cliente_id', 'valor', 'descripcion', 'fecha_inicial', 'fecha_final',
    #            'archivo_contrato']

    def __init__(self):
        super().__init__()
        self.parametros = {}

    def get_initial_queryset(self):
        if not self.model:
            raise NotImplementedError(
                "Need to provide a model or implement get_initial_queryset!"
            )
        return self.model.objects.filter(contrato=self.parametros.get('numero_contrato'))

    def dispatch(self, request, *args, **kwargs):
        try:
            self.parametros = kwargs

            return super(SubContratosListJson, self).dispatch(request, *args, **kwargs)
        except Exception as e:
            return JsonResponse({'error': str(e)})

    def render_column(self, row, column):

        return super(SubContratosListJson, self).render_column(row, column)

    def filter_queryset(self, qs):
        # Obtén el valor de búsqueda proporcionado por el usuario
        search = self.request.GET.get('search[value]', None)
        # Aplica el filtro solo si hay un valor de búsqueda
        if search:
            # Verifica si el valor de búsqueda es numérico
            if search.isdigit():
                # Aplica el filtro a la queryset utilizando filter directamente
                qs = qs.filter(
                    Q(numero_contrato__icontains=search) |
                    Q(cliente__cedula__icontains=search)
                )
            else:
                qs = qs.filter(Q(asesor__icontains=search))
        # Devuelve la queryset filtrada
        return qs

    def prepare_results(self, qs):
        locale.setlocale(locale.LC_ALL, 'es_CO.UTF-8')
        data = []
        today = datetime.date.today()

        for item in qs:
            data.append({
                'id': item.id,
                'contrato': item.contrato.numero_contrato,
                'nuevo_valor': locale.format_string("%.0f", item.nuevo_valor,
                                                    grouping=True) if item.nuevo_valor else 'No especificado',
                'nueva_fecha': item.nueva_fecha.strftime('%d de %B del %Y') if item.nueva_fecha else 'No especificado',
                'archivo_nuevo': item.archivo_nuevo.url

            })

        return data


def agregar_subcontrato(request, numero_contrato):
    contrato = Contratos.objects.get(numero_contrato=numero_contrato)

    if contrato.fecha_final < datetime.date.today():
        inicio_fecha = datetime.date.today()
    else:
        inicio_fecha = contrato.fecha_final
    data = {
        'formu': AgregarSubContrato(initial={'contrato': numero_contrato}, fecha_minima=inicio_fecha)
    }

    if request.method == 'POST':
        formulario = AgregarSubContrato(data=request.POST, files=request.FILES)
        if formulario.is_valid():

            formulario.save()
            ultimo_subcontrato = AdicionContrato.objects.filter(contrato__numero_contrato=numero_contrato).last()
            print('mirar:', ultimo_subcontrato.nueva_fecha)

            if ultimo_subcontrato.nueva_fecha:
                contrato.fecha_final = ultimo_subcontrato.nueva_fecha
                contrato.save()
            if ultimo_subcontrato.nuevo_valor:
                contrato.valor_subcontratos = ultimo_subcontrato.nuevo_valor + contrato.valor_subcontratos
                contrato.save()
            messages.success(request, "Sub-contrato agregado correctamente!")
            return redirect('carteraApp_ver_contrato', str(numero_contrato))
            # return redirect('/pagos/' + str(numero_contrato))
        else:
            data["formu"] = formulario
    return render(request, "proyectoCartera/contratos/agregar-subcontrato.html", data)


def ver_contrato(request, numero_contrato):
    locale.setlocale(locale.LC_ALL, 'es_CO.UTF-8')
    try:

        contrato = Contratos.objects.get(numero_contrato=numero_contrato)
        contrato.valor = str(locale.format_string("%.0f", contrato.valor, grouping=True))
        contrato.valor_subcontratos = str(locale.format_string("%.0f", contrato.valor_subcontratos, grouping=True))
        contrato.fecha_inicial = contrato.fecha_inicial.strftime(
            '%d de %B del %Y') if contrato.fecha_inicial else contrato.fecha_inicial
        contrato.fecha_final = contrato.fecha_final.strftime(
            '%d de %B del %Y') if contrato.fecha_final else contrato.fecha_final

        info_pagos = saldo_pagos(numero_contrato)
        info_pagos[1] = str(locale.format_string("%.0f", info_pagos[1], grouping=True))
        info_pagos[2] = str(locale.format_string("%.0f", info_pagos[2], grouping=True))
        info_pagos[4] = str(locale.format_string("%.0f", info_pagos[4], grouping=True))

        context = {
            'informacion_contrato': contrato,
            'informacion_pagos': info_pagos,
        }

        return render(request, "proyectoCartera/contratos/ver-contrato.html", context)
    except:
        return render(request, "proyectoCartera/contratos/error.html", )


def filtro_contratos(request):
    claves_contratos = ['cliente__nombre', 'asesor']
    dato_cliente = set()
    dato_asesor = set()

    for k in claves_contratos:
        contratos = Contratos.objects.all().values_list(k, flat=True)
        for item in contratos:
            if k == 'cliente__nombre':
                dato_cliente.add(item)
            elif k == 'asesor':
                dato_asesor.add(item)

    data = {
        'Cliente': list(dato_cliente),
        'Asesor': list(dato_asesor)

    }
    return JsonResponse(data)


def obtener_opciones_filtros(request, tabla):
    opciones = {
        "results": [],
    }

    try:
        modelos = get_all_models()
        modelo = modelos[tabla]

        variable = request.GET.get('variable')
        search = request.GET.get('search')

        if search:
            datos = modelo.objects.filter(**{f'{variable}__icontains': search})
        else:
            datos = modelo.objects.all()  # TODO: Evaluar que hacer cuando no haya filtro, si no cargar nada, cargar todo o carga parcial

        for opcion in datos:
            opciones['results'].append(
                {
                    "id": getattr(opcion, variable),
                    "text": getattr(opcion, variable)
                }
            )
    except Exception as e:
        print(e)

    return JsonResponse(opciones)
