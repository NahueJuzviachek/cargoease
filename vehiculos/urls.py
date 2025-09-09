from django.urls import path
from viajes.views import ViajesListView
from .views import (
    VehiculoListView, VehiculoCreateView,
    VehiculoUpdateView, VehiculoDeleteView
)

urlpatterns = [
    path("", VehiculoListView.as_view(), name="vehiculos_list"),
    path("crear/", VehiculoCreateView.as_view(), name="vehiculo_crear"),
    path("<int:pk>/editar/", VehiculoUpdateView.as_view(), name="vehiculo_editar"),
    path("<int:pk>/eliminar/", VehiculoDeleteView.as_view(), name="vehiculo_eliminar"),
    path("viajes/", ViajesListView, name="viajes_list"),  #Esta url lleva a la vista de viajes 
]
