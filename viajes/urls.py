from django.urls import path
from django.contrib.auth.decorators import login_required
from .views import gastos_list, gasto_extra_eliminar, ajax_localidad_coords

urlpatterns = [
    # Gastos del viaje
    path("viajes/<int:viaje_id>/gastos/", login_required(gastos_list), name="viaje_gastos_list"),
    path("viajes/<int:viaje_id>/gastos/<int:gasto_id>/eliminar/", login_required(gasto_extra_eliminar), name="gasto_extra_eliminar"),

    # EndPoint para coordenadas (AJAX)
    path("ajax/localidad-coords/", login_required(ajax_localidad_coords), name="ajax_localidad_coords"),
]
