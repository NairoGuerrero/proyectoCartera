from django.urls import path, re_path
from django.conf import settings
from django.views.static import serve
from . import views
from .views import *

urlpatterns = [
    path('', views.home, name='carteraApp_home'),
    path('agregar-contrato-vista/', views.agregar_contrato_vista, name='carteraApp_agregar_contrato'),
    path('editar-contrato-vista/<numero_contrato>', views.editar_contrato_vista, name='carteraApp_editar_contrato'),
    path('pagos/<numero_contrato>/', views.pagos, name="carteraApp_pagos"),
    path('agregar-pagos-vista/<numero_contrato>', views.agregar_pago_vista, name="carteraApp_agregar_pago"),
    path('editar-pago-vista/<id>', views.editar_pago_vista, name = "carteraApp_editar_pago"),
    path('clientes/', views.clientes, name='carteraApp_clientes'),
    path('agregar-cliente-vista/', views.agregar_cliente_vista, name='carteraApp_agregar_cliente'),
    path('elimininar-cliente/<cedula>', views.eliminar_cliente, name="carteraApp_eliminar_cliente"),
    path('editar-cliente-vista/<cedula>', views.editar_cliente_vista, name='carteraApp_editar_cliente'),
    path('contratos-data/', ContratosListJson.as_view(), name='carteraApp_contratos_data'),
    path('clientes-data/', ClientesListJson.as_view(), name='carteraApp_clientes_data'),
    # path('pagos-data/', PagosListJson.as_view(), name='carteraApp_pagos_data'),
]

urlpatterns += [
    re_path(r'^media/(?P<path>.*)$', serve,{
        'document_root': settings.MEDIA_ROOT,
    })
]