from django.urls import path
from django.contrib.auth.decorators import login_required
from .views import (
    ClienteListView, ClienteCreateView, ClienteUpdateView, ClienteDeleteView, ClienteReactivateView,
    ajax_cargar_provincias, ajax_cargar_localidades,
)

urlpatterns = [
    # Vistas principales (CBV)
    path("", login_required(ClienteListView.as_view()), name="clientes_list"),          # /clientes/
    path("crear/", login_required(ClienteCreateView.as_view()), name="cliente_crear"),  # /clientes/crear/
    path("<int:pk>/editar/", login_required(ClienteUpdateView.as_view()), name="cliente_editar"),
    path("<int:pk>/eliminar/", login_required(ClienteDeleteView.as_view()), name="cliente_eliminar"),
    path("<int:pk>/reactivar/", login_required(ClienteReactivateView.as_view()), name="cliente_reactivar"),

    # Endpoints AJAX (FBV)
    path("ajax/provincias/", login_required(ajax_cargar_provincias), name="ajax_cargar_provincias"),
    path("ajax/localidades/", login_required(ajax_cargar_localidades), name="ajax_cargar_localidades"),
]