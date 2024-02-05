from django.urls import path, re_path
from django.conf import settings
from django.views.static import serve
from . import views
from .views import ContratosListJson

urlpatterns = [
    path('', views.home, name='home'),
    path('AgregarContratoVista/', views.agregar_contrato_vista, name='agregar_contrato'),
    path('editarContratoVista/<Numero_Contrato>', views.editar_contrato_vista, name='editar_contrato'),
    path('Pagos/<Numero_Contrato>', views.pagos),
    path('AgregarPagosVista/<Numero_Contrato>', views.agregar_pago_vista),
    path('EditarPagoVista/<id>', views.editar_pago_vista),
    path('Clientes/', views.clientes, name='clientes'),
    path('AgregarClienteVista/', views.agregar_cliente_vista, name='agregar_cliente'),
    path('EliminacionCliente/<cedula>', views.eliminar_cliente),
    path('editarClienteVista/<cedula>', views.editar_cliente_vista, name='editar_cliente'),
    path('contratos_data/', ContratosListJson.as_view(), name='contratos_data'),
]

urlpatterns += [
    re_path(r'^media/(?P<path>.*)$', serve,{
        'document_root': settings.MEDIA_ROOT,
    })
]