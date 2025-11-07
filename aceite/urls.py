# aceite/urls.py
from django.urls import path
from django.contrib.auth.decorators import login_required
from . import views

app_name = 'aceite'

urlpatterns = [
    # Panel principal de aceites
    path("<int:vehiculo_pk>/", login_required(views.aceite_dashboard), name="aceite_panel"),

    # Confirmación o cambio
    path("<int:vehiculo_pk>/motor/cambiar/", login_required(views.confirmar_cambio_motor), name="aceite_cambiar_motor"),
    path("<int:vehiculo_pk>/caja/cambiar/", login_required(views.confirmar_cambio_caja), name="aceite_cambiar_caja"),
    path("<int:vehiculo_pk>/<str:tipo>/cambiar/", login_required(views.aceite_cambiar), name="aceite_cambiar"),

    # Historial de aceites
    path('vehiculo/<int:vehiculo_pk>/aceites/historial/', login_required(views.historial_aceites), name='aceite_historial'),
]