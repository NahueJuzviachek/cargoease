# viajes/urls.py
from django.urls import path
from .views import gastos_list, gasto_extra_eliminar, ajax_localidad_coords

urlpatterns = [
    path("viajes/<int:viaje_id>/gastos/", gastos_list, name="viaje_gastos_list"),
    path("viajes/<int:viaje_id>/gastos/<int:gasto_id>/eliminar/", gasto_extra_eliminar, name="gasto_extra_eliminar"),
    # End Point para las cordenadas
    path("ajax/localidad-coords/", ajax_localidad_coords, name="ajax_localidad_coords"),
]