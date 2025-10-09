from django.urls import path
from django.contrib.auth.decorators import login_required

from aceite.views import (
    aceite_dashboard, cambiar_aceite_motor, cambiar_aceite_caja,
    confirmar_cambio_motor, confirmar_cambio_caja, aceite_cambiar
)

from .views import (
    VehiculoListView, VehiculoCreateView,
    VehiculoUpdateView, VehiculoDeleteView
)
from viajes.views import (
    ViajeListView, VehiculoViajeCreateView,
    VehiculoViajeUpdateView, VehiculoViajeDeleteView
)

urlpatterns = [
    # Vehículos
    path("", login_required(VehiculoListView.as_view()), name="vehiculos_list"),
    path("crear/", login_required(VehiculoCreateView.as_view()), name="vehiculo_crear"),
    path("<int:pk>/editar/", login_required(VehiculoUpdateView.as_view()), name="vehiculo_editar"),
    path("<int:pk>/eliminar/", login_required(VehiculoDeleteView.as_view()), name="vehiculo_eliminar"),

    # Viajes por vehículo
    path("<int:vehiculo_pk>/viajes/", login_required(ViajeListView.as_view()), name="vehiculo_viajes_list"),
    path("<int:vehiculo_pk>/viajes/crear/", login_required(VehiculoViajeCreateView.as_view()), name="vehiculo_viaje_crear"),
    path("<int:vehiculo_pk>/viajes/<int:pk>/editar/", login_required(VehiculoViajeUpdateView.as_view()), name="vehiculo_viaje_editar"),
    path("<int:vehiculo_pk>/viajes/<int:pk>/eliminar/", login_required(VehiculoViajeDeleteView.as_view()), name="vehiculo_viaje_eliminar"),

    # Aceite (motor/caja)
    path("<int:vehiculo_pk>/aceite/", login_required(aceite_dashboard), name="vehiculo_aceite"),
    path("<int:vehiculo_pk>/aceite/motor/cambiar/", login_required(cambiar_aceite_motor), name="vehiculo_aceite_motor_cambiar"),
    path("<int:vehiculo_pk>/aceite/caja/cambiar/", login_required(cambiar_aceite_caja), name="vehiculo_aceite_caja_cambiar"),
    path("<int:vehiculo_pk>/aceite/motor/confirmar/", login_required(confirmar_cambio_motor), name="vehiculo_aceite_motor_confirmar"),
    path("<int:vehiculo_pk>/aceite/caja/confirmar/", login_required(confirmar_cambio_caja), name="vehiculo_aceite_caja_confirmar"),

    # Cambio de aceite 
    path("<int:vehiculo_pk>/aceite/<str:tipo>/cambiar/", login_required(aceite_cambiar), name="aceite_cambiar"),
]
