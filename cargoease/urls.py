from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("vehiculos/", include("vehiculos.urls")),  
    path("clientes/", include("clientes.urls")),
    path("conductores/", include("conductores.urls")),
    path("", include("home.urls")),
]