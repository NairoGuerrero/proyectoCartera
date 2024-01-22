from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('AgregarContratoVista/', views.agregar_contrato_vista, name='agregar_contrato'),
    path('editarContratoVista/<Numero_Contrato>', views.editar_contrato_vista, name='editar_contrato'),
    path('Clientes/', views.clientes, name='clientes'),
    path('AgregarClienteVista/', views.agregar_cliente_vista, name='agregar_cliente'),
    path('EliminacionCliente/<cedula>', views.eliminar_cliente),
    path('editarClienteVista/<cedula>', views.editar_cliente_vista, name='editar_cliente'),
]