#conductores/urls.py
from django.urls import path
from django.contrib.auth.decorators import login_required
from .views import (
    ConductorListView, ConductorCreateView,
    ConductorUpdateView, ConductorDeleteView
)

urlpatterns = [
    path("", login_required(ConductorListView.as_view()), name="conductores_list"),
    path("crear/", login_required(ConductorCreateView.as_view()), name="conductor_crear"),
    path("<int:pk>/editar/", login_required(ConductorUpdateView.as_view()), name="conductor_editar"),
    path("<int:pk>/eliminar/", login_required(ConductorDeleteView.as_view()), name="conductor_eliminar"),
]
