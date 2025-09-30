from django.urls import path
from .views import (
    AceiteListView, AceiteCreateView, AceiteUpdateView, AceiteDeleteView, CambiarAceiteView
)

urlpatterns = [
    path("<int:vehiculo_id>/", AceiteListView.as_view(), name="aceite_list"),
    path("<int:vehiculo_id>/nuevo/", AceiteCreateView.as_view(), name="aceite_crear"),
    path("editar/<int:pk>/", AceiteUpdateView.as_view(), name="aceite_editar"),
    path("eliminar/<int:pk>/", AceiteDeleteView.as_view(), name="aceite_eliminar"),
    path("cambiar/<int:pk>/", CambiarAceiteView.as_view(), name="aceite_cambiar"),
]
