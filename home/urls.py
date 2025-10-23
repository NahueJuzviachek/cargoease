# home/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),

    # Endpoints JSON del dashboard
    path("dashboard/data/clientes-top-mensual/", views.data_clientes_top_mensual, name="data_clientes_top_mensual"),
    path("dashboard/data/ranking-km/", views.data_ranking_km, name="data_ranking_km"),
    path("dashboard/data/aceite-top5/", views.data_aceite_top5, name="data_aceite_top5"),
    path("dashboard/data/neumaticos-estado/", views.data_neumaticos_estado, name="data_neumaticos_estado"),
]
