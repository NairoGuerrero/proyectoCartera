import os
from django.conf import settings
from django.core.paginator import Paginator
from django.shortcuts import render, redirect
from .forms import *
from django.contrib import messages
from .Funciones import *
from django_datatables_view.base_datatable_view import BaseDatatableView
from django.http import JsonResponse
from django.db.models import Q
import locale
import datetime
from datetime import datetime as dt
from django.utils.translation import gettext as _
import io
from django.http import FileResponse
from reportlab.pdfgen import canvas
from django.views.decorators.csrf import csrf_exempt
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from django.http import HttpResponse
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from io import BytesIO

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle
from reportlab.lib.units import inch
import io
from reportlab.pdfgen import canvas
from django.http import FileResponse
from datetime import datetime as dt
from .models import Contratos
import os
from django.conf import settings
from datetime import timedelta
from random import randint
from .models import Contratos, Clientes


def pdf_contratos(request):
    if request.method == 'POST':
        # Obtén los datos enviados en la solicitud POST
        contrato = request.POST.get('search_contrato')
        asesor = request.POST.get('search_asesor')
        search_fecha_start = request.POST.get('search_fecha_start')
        search_fecha_end = request.POST.get('search_fecha_end')

        filtro_fecha = Q()
        try:
            if search_fecha_start is not None:
                fecha_inicio = dt.strptime(search_fecha_start, '%Y-%m-%d')

                if search_fecha_end is not None:
                    fecha_fin = dt.strptime(search_fecha_end, '%Y-%m-%d')
                else:
                    fecha_fin = fecha_inicio

                fecha_fin = fecha_fin.replace(hour=23, minute=59, second=59)
                filtro_fecha = Q(fecha_inicial__range=(fecha_inicio, fecha_fin))
        except:
            print("No se pudo crear el filtro de fecha")

        filtros = [
            Q(numero_contrato=contrato),
            Q(asesor=asesor),
            filtro_fecha,
        ]

        filtros_validos = [filtro for filtro in filtros if filtro.children and filtro.children[0][1] != '']
        filtro_completo = Q()
        for filtro in filtros_validos:
            filtro_completo |= filtro
        contratos = Contratos.objects.filter(filtro_completo)

        paginator = Paginator(contratos, 20)

        data = [['# Contrato', 'Asesor', 'Cliente', 'Valor (COP)', 'saldo (COP)', 'Fecha Inicial', 'Fecha Final',
                 'Dias restantes']]
        fecha_actual = datetime.datetime.now()

        buffer = io.BytesIO()
        p = canvas.Canvas(buffer, pagesize=letter)
        p.setFont("Helvetica-Bold", 20)
        p.drawString(280, 750, "Informe Contratos")
        p.setFont("Helvetica", 10)
        p.drawString(290, 730, f"Generado el {fecha_actual.strftime('%d de %B del %Y')}")
        # Dibujar la primera imagen en la esquina superior izquierda
        image_dir = os.path.join(settings.BASE_DIR, 'static', 'img')
        image_path_left = os.path.join(image_dir, 'logo.jpg')
        p.drawImage(image_path_left, x=80, y=720, width=150,
                    height=40)  # Ajusta la posición y tamaño según tu preferencia

        for page_num in paginator.page_range:
            page_contratos = paginator.page(page_num)
            for contrato in page_contratos:
                data.append([
                    contrato.numero_contrato,
                    contrato.asesor,
                    contrato.cliente.nombre,
                    locale.format_string("%.0f", contrato.valor, grouping=True),
                    locale.format_string("%.0f", saldo_pagos(contrato.numero_contrato)[2], grouping=True),
                    contrato.fecha_inicial.strftime('%d/%m/%Y') if contrato.fecha_inicial else '',
                    contrato.fecha_final.strftime('%d/%m/%Y') if contrato.fecha_final else contrato.fecha_final,
                    (contrato.fecha_final - datetime.date.today()).days if contrato.fecha_final else None
                ])

            print('numero pagina', page_num)

            table = Table(data, rowHeights=[30] * len(data))

            # Calcular la posición horizontal para centrar la tabla
            table_width, table_height = table.wrapOn(p, 0, 0)
            x_position = (letter[0] - table_width) / 2

            style = TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),  # Alinear verticalmente al centro
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),

                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ])
            rowNumb = len(data)
            for row in range(1, rowNumb):
                if row % 2 == 0:
                    table_background = colors.lightgrey
                else:
                    table_background = colors.white

                style.add('BACKGROUND', (0, row), (-1, row), table_background)

            table.setStyle(style)
            table.wrapOn(p, 0, 0)

            p.setFont("Helvetica", 10)
            p.drawString(300, 10, f"{page_num}")

            if page_num > 1:
                table.drawOn(p, x_position, 730 - (len(data) * 30))  # Usar la posición calculada
            else:
                table.drawOn(p, x_position, 680 - (len(data) * 30))

            # Guardar página y limpiar datos para la siguiente página
            p.showPage()
            data = [['# Contrato', 'Asesor', 'Cliente', 'Valor (COP)', 'saldo (COP)', 'Fecha Inicial', 'Fecha Final',
                     'Dias restantes']]

        p.save()
        buffer.seek(0)
        print(buffer)
        return FileResponse(buffer, as_attachment=True, filename="informe_contratos.pdf")


def pdf_pagos(request):
    if request.method == 'POST':
        numero_contrato = request.POST.get('numero_contrato')
        tipo_pago = request.POST.get('tipo_pago')
        search_fecha_start = request.POST.get('search_fecha_start')
        search_fecha_end = request.POST.get('search_fecha_end')

        filtro_numero_contrato = Q(contrato__numero_contrato=numero_contrato)

        filtro_fecha = Q()
        try:
            if search_fecha_start is not None:
                fecha_inicio = dt.strptime(search_fecha_start, '%Y-%m-%d')

                if search_fecha_end is not None:
                    fecha_fin = dt.strptime(search_fecha_end, '%Y-%m-%d')
                else:
                    fecha_fin = fecha_inicio

                fecha_fin = fecha_fin.replace(hour=23, minute=59, second=59)
                filtro_fecha = Q(fecha_pago__range=(fecha_inicio, fecha_fin))
        except:
            print("No se pudo crear el filtro de fecha")

        filtros = [
            filtro_numero_contrato,
            Q(tipo_pago=tipo_pago),
            filtro_fecha,
        ]

        filtros_validos = [filtro for filtro in filtros if filtro.children and filtro.children[0][1] != '']
        filtro_completo = Q()
        for filtro in filtros_validos:
            filtro_completo &= filtro

        pagos = Pagos.objects.filter(filtro_completo)
        print(pagos)
        paginator = Paginator(pagos, 20)

        data = [['# Contrato', 'Tipo de pago', 'Valor del pago (COP)', 'Fecha de pago']]
        fecha_actual = datetime.datetime.now()

        buffer = io.BytesIO()
        p = canvas.Canvas(buffer, pagesize=letter)
        p.setFont("Helvetica-Bold", 20)
        p.drawString(280, 750, "Informe Contratos")
        p.setFont("Helvetica", 10)
        p.drawString(290, 730, f"Generado el {fecha_actual.strftime('%d de %B del %Y')}")
        # Dibujar la primera imagen en la esquina superior izquierda
        image_dir = os.path.join(settings.BASE_DIR, 'static', 'img')
        image_path_left = os.path.join(image_dir, 'logo.jpg')
        p.drawImage(image_path_left, x=80, y=720, width=150,
                    height=40)  # Ajusta la posición y tamaño según tu preferencia

        for page_num in paginator.page_range:
            page_contratos = paginator.page(page_num)
            for pago in page_contratos:
                print(pago)
                data.append([
                    numero_contrato,
                    pago.tipo_pago,
                    locale.format_string("%.0f", pago.valor_pago, grouping=True),
                    pago.fecha_pago.strftime('%d de %B del %Y') if pago.fecha_pago else 'No especificado',
                ])

            print('numero pagina', page_num)

            table = Table(data, colWidths=[140] * 3, rowHeights=[30] * len(data))

            # Calcular la posición horizontal para centrar la tabla
            table_width, table_height = table.wrapOn(p, 0, 0)
            x_position = (letter[0] - table_width) / 2

            style = TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),  # Alinear verticalmente al centro
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),

                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ])
            rowNumb = len(data)
            for row in range(1, rowNumb):
                if row % 2 == 0:
                    table_background = colors.lightgrey
                else:
                    table_background = colors.white

                style.add('BACKGROUND', (0, row), (-1, row), table_background)

            table.setStyle(style)
            table.wrapOn(p, 0, 0)

            p.setFont("Helvetica", 10)
            p.drawString(300, 10, f"{page_num}")

            if page_num > 1:
                table.drawOn(p, x_position, 730 - (len(data) * 30))  # Usar la posición calculada
            else:
                table.drawOn(p, x_position, 680 - (len(data) * 30))

            # Guardar página y limpiar datos para la siguiente página
            p.showPage()

            data = [['# Contrato', 'Tipo de pago', 'Valor del pago (COP)', 'Fecha de pago']]

        p.save()
        buffer.seek(0)
        print(buffer)
        return FileResponse(buffer, as_attachment=True, filename="informe_contratos.pdf")


def pdf_contrato_especifico(request):
    if request.method == 'POST':
        numero_contrato = request.POST.get('numero_contrato')
        print('Numero contrato ver: ', numero_contrato)
        sub_contrato = AdicionContrato.objects.filter(contrato__numero_contrato=numero_contrato)
        contrato = Contratos.objects.get(numero_contrato=numero_contrato)
        pagos = Pagos.objects.filter(contrato__numero_contrato=numero_contrato)
        print(sub_contrato)
        fecha_actual = datetime.datetime.now()

        buffer = io.BytesIO()
        p = canvas.Canvas(buffer, pagesize=letter)
        p.setFont("Helvetica-Bold", 18)
        p.drawString(260, 750, "Informe Contrato ")
        p.setFont("Helvetica-Bold", 18)
        p.drawString(415, 750, f"# {numero_contrato}")
        p.setFont("Helvetica", 10)
        p.drawString(290, 730, f"Generado el {fecha_actual.strftime('%d de %B del %Y')}")
        # Dibujar la primera imagen en la esquina superior izquierda
        image_dir = os.path.join(settings.BASE_DIR, 'static', 'img')
        image_path_left = os.path.join(image_dir, 'logo.jpg')
        p.drawImage(image_path_left, x=80, y=720, width=150,
                    height=40)  # Ajusta la posición y tamaño según tu preferencia

        p.setFont("Helvetica-Bold", 12)
        p.drawString(30, 680, '# Contrato : ')
        p.setFont("Helvetica", 12)
        p.drawString(100, 680, f"{contrato.numero_contrato}")

        p.setFont("Helvetica-Bold", 12)
        p.drawString(30, 655, 'Asesor : ')
        p.setFont("Helvetica", 12)
        p.drawString(80, 655, f"{contrato.asesor}")

        p.setFont("Helvetica-Bold", 12)
        p.drawString(30, 630, 'Cliente : ')
        p.setFont("Helvetica", 12)
        p.drawString(80, 630, f"{contrato.cliente}")

        p.setFont("Helvetica-Bold", 12)
        p.drawString(30, 605, 'Fecha inicial : ')
        p.setFont("Helvetica", 12)
        p.drawString(110, 605,
                     f"{contrato.fecha_inicial.strftime('%d de %B del %Y') if contrato.fecha_inicial else contrato.fecha_inicial}")

        p.setFont("Helvetica-Bold", 12)
        p.drawString(30, 580, 'Fecha final : ')
        p.setFont("Helvetica", 12)
        p.drawString(103, 580,
                     f"{contrato.fecha_final.strftime('%d de %B del %Y') if contrato.fecha_final else contrato.fecha_final}")

        p.setFont("Helvetica-Bold", 12)
        p.drawString(340, 680, 'Valor inicial : ')
        p.setFont("Helvetica", 12)
        p.drawString(420, 680, f"{locale.format_string('%.0f', contrato.valor, grouping=True)} (COP)")

        p.setFont("Helvetica-Bold", 12)
        p.drawString(340, 655, 'Valor sub-contratos : ')
        p.setFont("Helvetica", 12)
        p.drawString(465, 655, f"{locale.format_string('%.0f', contrato.valor_subcontratos, grouping=True)} (COP)")

        info_pagos = saldo_pagos(numero_contrato)

        p.setFont("Helvetica-Bold", 12)
        p.drawString(340, 630, 'Valor Total : ')
        p.setFont("Helvetica", 12)
        p.drawString(420, 630, f"{locale.format_string('%.0f', info_pagos[4], grouping=True)} (COP)")

        p.setFont("Helvetica-Bold", 12)
        p.drawString(340, 605, 'Pagos Realizados : ')
        p.setFont("Helvetica", 12)
        p.drawString(457, 605, f"{locale.format_string('%.0f', info_pagos[1], grouping=True)} (COP)")

        p.setFont("Helvetica-Bold", 12)
        p.drawString(340, 580, 'Saldo : ')
        p.setFont("Helvetica", 12)
        p.drawString(385, 580, f"{locale.format_string('%.0f', info_pagos[2], grouping=True)} (COP)")

        p.setFont("Helvetica-Bold", 14)
        p.drawString(35, 540, f"Tabla sub-contratos")

        paginator = Paginator(sub_contrato, 10)
        contador = None
        data = [['# Contrato', 'Valor (COP)', 'Fecha']]
        position_y = None
        for page_num in paginator.page_range:

            page_sub_contratos = paginator.page(page_num)
            for sub_contrato_item in page_sub_contratos:
                data.append([
                    sub_contrato_item.contrato.numero_contrato,
                    locale.format_string("%.0f", sub_contrato_item.nuevo_valor,
                                         grouping=True) if sub_contrato_item.nuevo_valor else 'No especificado',
                    sub_contrato_item.nueva_fecha.strftime(
                        '%d de %B del %Y') if sub_contrato_item.nueva_fecha else 'No especificado',
                ])

            table = Table(data, colWidths=[180] * 3, rowHeights=[30] * len(data))

            # Calcular la posición horizontal para centrar la tabla
            table_width, table_height = table.wrapOn(p, 0, 0)
            x_position = (letter[0] - table_width) / 2

            style = TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),  # Alinear verticalmente al centro
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ])
            rowNumb = len(data)
            for row in range(1, rowNumb):
                if row % 2 == 0:
                    table_background = colors.lightgrey
                else:
                    table_background = colors.white

                style.add('BACKGROUND', (0, row), (-1, row), table_background)

            table.setStyle(style)
            table.wrapOn(p, 0, 0)
            if page_num > 1:
                table.drawOn(p, x_position, 720 - (len(data) * 30))  # Usar la posición calculada
                position_y = 720 - (len(data) * 30)
            else:
                table.drawOn(p, x_position, 530 - (len(data) * 30))
                position_y = 530 - (len(data) * 30)

            p.setFont("Helvetica", 10)
            p.drawString(300, 10, f"{page_num}")

            data = [['# Contrato', 'Valor (COP)', 'Fecha']]
            # if page_num != paginator.page_range.stop - 1:
            #     p.showPage()
            p.showPage()
            contador = page_num

        p.setFont("Helvetica-Bold", 14)
        p.drawString(35, 730, f"Tabla Pagos")
        # desde aqui es la segunda tabla
        paginator = Paginator(pagos, 10)

        data = [['Tipo de pago', 'Valor de pago (COP)', 'Fecha de pago']]

        for page_num in paginator.page_range:
            page_sub_contratos = paginator.page(page_num)
            for sub_contrato_item in page_sub_contratos:
                data.append([
                    sub_contrato_item.get_tipo_pago_display(),
                    locale.format_string("%.0f", sub_contrato_item.valor_pago,
                                         grouping=True) if sub_contrato_item.fecha_pago else 'No especificado',
                    sub_contrato_item.fecha_pago.strftime(
                        '%d de %B del %Y') if sub_contrato_item.fecha_pago else 'No especificado',
                ])

            table = Table(data, colWidths=[180] * 3, rowHeights=[30] * len(data))

            # Calcular la posición horizontal para centrar la tabla
            table_width, table_height = table.wrapOn(p, 0, 0)
            x_position = (letter[0] - table_width) / 2

            style = TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),  # Alinear verticalmente al centro
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),

                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ])

            rowNumb = len(data)
            for row in range(1, rowNumb):
                if row % 2 == 0:
                    table_background = colors.lightgrey
                else:
                    table_background = colors.white

                style.add('BACKGROUND', (0, row), (-1, row), table_background)

            table.setStyle(style)
            table.wrapOn(p, 0, 0)

            if page_num > 1:
                table.drawOn(p, x_position, 720 - (len(data) * 30))  # Usar la posición calculada
            else:
                table.drawOn(p, x_position, 720 - (len(data) * 30))

            p.setFont("Helvetica", 10)
            p.drawString(300, 10, f"{page_num + contador}")

            data = [['Tipo de pago', 'Valor de pago (COP)', 'Fecha de pago']]

            p.showPage()

        p.save()
        buffer.seek(0)
        return FileResponse(buffer, as_attachment=True, filename="hello.pdf")


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

        # Obteniendo datos para filtrar
        sort_by = self.request.GET.get('sort_by', None)
        sorting_direction = self.request.GET.get('sorting_direction', None)
        search_contrato = self.request.GET.get('search_contrato', None)
        search_asesor = self.request.GET.get('search_asesor', None)
        search_fecha_start = self.request.GET.get('search_fecha_start', None)
        search_fecha_end = self.request.GET.get('search_fecha_end', None)

        # Creando el Query por fecha
        filtro_fecha = Q()
        try:
            if search_fecha_start is not None:
                fecha_inicio = dt.strptime(search_fecha_start, '%Y-%m-%d')

                if search_fecha_end is not None:
                    fecha_fin = dt.strptime(search_fecha_end, '%Y-%m-%d')
                else:
                    fecha_fin = fecha_inicio

                fecha_fin.replace(hour=23, minute=59, second=59)
                filtro_fecha = Q(fecha_inicial__range=(fecha_inicio, fecha_fin))
        except:
            print("No se pudo crear el filtro de fecha")

        # Creando el resto de filtros y creando una lista con ellos
        filtros = [
            Q(numero_contrato=search_contrato),
            Q(asesor=search_asesor),
            filtro_fecha,
        ]

        # Quitando los filtros que no tienen nada
        filtros_validos = [filtro for filtro in filtros if filtro.children and filtro.children[0][1] != '']

        # Creando el Query
        filtro_completo = Q()
        for filtro in filtros_validos:
            filtro_completo |= filtro  # FIXME: Determinar si se quiere que sea una OR o una AND

        # Filtrando
        # FIXME: Arreglar el ordenamiento por saldo y días restantes
        if sort_by:
            sort_by = sort_by if sorting_direction == 'desc' else f'-{sort_by}'
        if len(filtros_validos) > 0:
            qs = qs.filter(filtro_completo).order_by(sort_by) if sort_by else qs.filter(filtro_completo)
        else:
            qs = qs.all().order_by(sort_by) if sort_by else qs.all()

        return qs

    def prepare_results(self, qs):
        locale.setlocale(locale.LC_ALL, 'en_US.utf8')
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
    locale.setlocale(locale.LC_ALL, 'en_US.utf8')

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
        search_tipo_pago = self.request.GET.get('search_tipo_pago', None)
        search_fecha_start = self.request.GET.get('search_fecha_start', None)
        search_fecha_end = self.request.GET.get('search_fecha_end', None)

        # Creando el Query por fecha
        filtro_fecha = Q()
        try:
            if search_fecha_start is not None:
                fecha_inicio = dt.strptime(search_fecha_start, '%Y-%m-%d')

                if search_fecha_end is not None:
                    fecha_fin = dt.strptime(search_fecha_end, '%Y-%m-%d')
                else:
                    fecha_fin = fecha_inicio

                fecha_fin.replace(hour=23, minute=59, second=59)
                filtro_fecha = Q(fecha_pago__range=(fecha_inicio, fecha_fin))
        except:
            print("No se pudo crear el filtro de fecha pagos")

        # Creando el resto de filtros y creando una lista con ellos
        filtros = [
            Q(tipo_pago=search_tipo_pago),
            filtro_fecha,
        ]

        # Quitando los filtros que no tienen nada
        filtros_validos = [filtro for filtro in filtros if filtro.children and filtro.children[0][1] != '']

        # Creando el Query
        filtro_completo = Q()
        for filtro in filtros_validos:
            filtro_completo &= filtro  # FIXME: Determinar si se quiere que sea una OR o una AND

        # Filtrando
        # FIXME: Arreglar el ordenamiento por saldo y días restantes

        if len(filtros_validos) > 0:
            qs = qs.filter(filtro_completo)
        else:
            qs = qs.all()

        return qs

    def prepare_results(self, qs):
        locale.setlocale(locale.LC_ALL, 'en_US.utf8')
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
        locale.setlocale(locale.LC_ALL, 'en_US.utf8')
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
    locale.setlocale(locale.LC_ALL, 'en_US.utf8')
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
        choices = dict(modelo._meta.get_field(variable).flatchoices)
        if search:

            datos = modelo.objects.filter(**{f'{variable}__icontains': search})
            print(datos)
        else:
            datos = modelo.objects.all()  # FIXME: Evaluar que hacer cuando no haya filtro, si no cargar nada, cargar todo o carga parcial

        datos = datos.values(variable).distinct()

        if choices:
            for dato in datos:
                dato[f'{variable}_'] = choices[dato.get(variable)]

        print(datos)

        for opcion in datos:
            variable_txt = variable if not choices else f'{variable}_'
            opciones['results'].append(
                {
                    "id": opcion[variable] if isinstance(opcion, dict) else getattr(opcion, variable),
                    "text": opcion[variable_txt] if isinstance(opcion, dict) else getattr(opcion, variable)
                }
            )

    except Exception as e:
        print(e)

    return JsonResponse(opciones)
