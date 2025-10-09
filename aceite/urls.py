# aceite/urls.py
from django.urls import path
from .views import AceitePanelView, confirmar_cambio_view

urlpatterns = [
    path("<int:vehiculo_pk>/", AceitePanelView.as_view(), name="aceite_panel"),
    path("<int:vehiculo_pk>/<str:tipo>/cambiar/", confirmar_cambio_view, name="aceite_cambiar"),

    # 👇 Alias opcionales (ajusta a cómo los llamabas antes)
    path("panel/<int:vehiculo_pk>/", AceitePanelView.as_view(), name="aceite_panel_legacy"),
    path("confirmar/<int:vehiculo_pk>/<str:tipo>/", confirmar_cambio_view, name="aceite_confirmar_legacy"),
]
