from django.urls import path
from .views import aceite_dashboard, cambio_motor_hoy, cambio_caja_hoy

app_name = "aceite"

urlpatterns = [
    path("vehiculos/<int:vehiculo_pk>/aceite/", aceite_dashboard, name="dashboard"),
    path("vehiculos/<int:vehiculo_pk>/aceite/motor/hoy/", cambio_motor_hoy, name="cambio_motor_hoy"),
    path("vehiculos/<int:vehiculo_pk>/aceite/caja/hoy/", cambio_caja_hoy, name="cambio_caja_hoy"),
]
