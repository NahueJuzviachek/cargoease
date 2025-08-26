from django.urls import path

from home import views

urlpatterns = [
    
    path('', views.home, name="home"),
    path('clientes', views.clientes, name="clientes"),
    path('conductores', views.conductores, name="conductores"),
    path('vehiculos', views.vehiculos, name="vehiculos"),
    path('reportes', views.reportes, name="reportes"),
    path('login', views.login, name="login")
]
