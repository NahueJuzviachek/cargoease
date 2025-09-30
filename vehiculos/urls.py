from django.urls import path
from .views import (
    VehiculoListView, VehiculoCreateView,
    VehiculoUpdateView, VehiculoDeleteView
)
from viajes.views import (
    ViajeListView, VehiculoViajeCreateView,
    VehiculoViajeUpdateView, VehiculoViajeDeleteView
)

from aceite.views import aceite_dashboard, cambiar_aceite_motor, cambiar_aceite_caja

urlpatterns = [
    # Vehículos
    path("", VehiculoListView.as_view(), name="vehiculos_list"),
    path("crear/", VehiculoCreateView.as_view(), name="vehiculo_crear"),
    path("<int:pk>/editar/", VehiculoUpdateView.as_view(), name="vehiculo_editar"),
    path("<int:pk>/eliminar/", VehiculoDeleteView.as_view(), name="vehiculo_eliminar"),

    # Viajes por vehículo
    path("<int:vehiculo_pk>/viajes/", ViajeListView.as_view(), name="vehiculo_viajes_list"),
    path("<int:vehiculo_pk>/viajes/crear/", VehiculoViajeCreateView.as_view(), name="vehiculo_viaje_crear"),
    path("<int:vehiculo_pk>/viajes/<int:pk>/editar/", VehiculoViajeUpdateView.as_view(), name="vehiculo_viaje_editar"),
    path("<int:vehiculo_pk>/viajes/<int:pk>/eliminar/", VehiculoViajeDeleteView.as_view(), name="vehiculo_viaje_eliminar"),

    path("<int:vehiculo_pk>/aceite/", aceite_dashboard, name="vehiculo_aceite"),
    path("<int:vehiculo_pk>/aceite/motor/cambiar/", cambiar_aceite_motor, name="vehiculo_aceite_motor_cambiar"),
    path("<int:vehiculo_pk>/aceite/caja/cambiar/", cambiar_aceite_caja, name="vehiculo_aceite_caja_cambiar"),
]