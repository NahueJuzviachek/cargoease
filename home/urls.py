# home/urls.py
from django.contrib.auth.decorators import login_required
from django.urls import path
from . import views

urlpatterns = [
    path("", login_required(views.home), name="home"),

    # Endpoints JSON del dashboard
    path("dashboard/data/clientes-top-mensual/", login_required(views.data_clientes_top_mensual), name="data_clientes_top_mensual"),
    path("dashboard/data/ranking-km/", login_required(views.data_ranking_km), name="data_ranking_km"),
    path("dashboard/data/aceite-top5/", login_required(views.data_aceite_top5), name="data_aceite_top5"),
    path("dashboard/data/neumaticos-estado/", login_required(views.data_neumaticos_estado), name="data_neumaticos_estado"),
]
