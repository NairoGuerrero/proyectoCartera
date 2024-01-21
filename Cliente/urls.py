from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('AgregarClienteVista/', views.AgregarClienteVista, name='agregar_cliente'),
    path('EliminacionCliente/<cedula>', views.EliminarCliente),
    path('editarClienteVista/<cedula>', views.EditarClienteVista),
]