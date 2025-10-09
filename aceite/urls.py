# aceite/urls.py
from django.urls import path
from .views import AceitePanelView, confirmar_cambio_view
from django.contrib.auth.decorators import login_required


urlpatterns = [
    # Panel principal (vista basada en clase)
    path("<int:vehiculo_pk>/", login_required(AceitePanelView.as_view()), name="aceite_panel"),

    # Confirmación o cambio 
    path("<int:vehiculo_pk>/<str:tipo>/cambiar/", login_required(confirmar_cambio_view), name="aceite_cambiar"),
    path("panel/<int:vehiculo_pk>/", login_required(AceitePanelView.as_view()), name="aceite_panel_legacy"),
    path("confirmar/<int:vehiculo_pk>/<str:tipo>/", login_required(confirmar_cambio_view), name="aceite_confirmar_legacy"),
]