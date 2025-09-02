from django.urls import path
from .views import (
    ClienteListView, ClienteCreateView, ClienteUpdateView, ClienteDeleteView,
    ajax_cargar_provincias, ajax_cargar_localidades,
)

urlpatterns = [
    path("", ClienteListView.as_view(), name="clientes_list"),          # /clientes/
    path("crear/", ClienteCreateView.as_view(), name="cliente_crear"),  # /clientes/crear/
    path("<int:pk>/editar/", ClienteUpdateView.as_view(), name="cliente_editar"),
    path("<int:pk>/eliminar/", ClienteDeleteView.as_view(), name="cliente_eliminar"),

    # Endpoints AJAX
    path("ajax/provincias/", ajax_cargar_provincias, name="ajax_cargar_provincias"),
    path("ajax/localidades/", ajax_cargar_localidades, name="ajax_cargar_localidades"),
]