from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.home, name="home"),
    path('reportes', views.reportes, name="reportes"),
]

