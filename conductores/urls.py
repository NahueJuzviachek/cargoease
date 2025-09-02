from django.urls import path
from .views import (
    ConductorListView, ConductorCreateView,
    ConductorUpdateView, ConductorDeleteView
)

urlpatterns = [
    path("", ConductorListView.as_view(), name="conductores_list"),
    path("crear/", ConductorCreateView.as_view(), name="conductor_crear"),
    path("<int:pk>/editar/", ConductorUpdateView.as_view(), name="conductor_editar"),
    path("<int:pk>/eliminar/", ConductorDeleteView.as_view(), name="conductor_eliminar"),
]

