from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name="home"),
    path('conductores', views.conductores, name="conductores"),
    path('vehiculos', views.vehiculos, name="vehiculos"),
    path('reportes', views.reportes, name="reportes"),
]

