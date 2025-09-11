from django.urls import path
from .views import (
    VehiculoListView, VehiculoCreateView,
    VehiculoUpdateView, VehiculoDeleteView
)
from viajes.views import (
    ViajeListView, VehiculoViajeCreateView, VehiculoViajeUpdateView, VehiculoViajeDeleteView
)

urlpatterns = [
    path("", VehiculoListView.as_view(), name="vehiculos_list"),
    path("crear/", VehiculoCreateView.as_view(), name="vehiculo_crear"),
    path("<int:pk>/editar/", VehiculoUpdateView.as_view(), name="vehiculo_editar"),
    path("<int:pk>/eliminar/", VehiculoDeleteView.as_view(), name="vehiculo_eliminar"),

    # Gestión de viajes por vehículo:
    path("<int:vehiculo_pk>/viajes/", ViajeListView.as_view(), name="vehiculo_viajes_list"),
    path("<int:vehiculo_pk>/viajes/crear/", VehiculoViajeCreateView.as_view(), name="vehiculo_viaje_crear"),
    path("<int:vehiculo_pk>/viajes/<int:pk>/editar/", VehiculoViajeUpdateView.as_view(), name="vehiculo_viaje_editar"),
    path("<int:vehiculo_pk>/viajes/<int:pk>/eliminar/", VehiculoViajeDeleteView.as_view(), name="vehiculo_viaje_eliminar"),
]