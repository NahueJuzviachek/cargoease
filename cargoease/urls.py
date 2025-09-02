from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    # 👇 usa tus rutas de login/logout
    path('', include('login.urls')),  # asumiendo que tu app se llama "login"
    path('', include('home.urls')),
    path('clientes/', include('clientes.urls')),
    path('conductores/', include('conductores.urls')),
    path("vehiculos/", include("vehiculos.urls")),
]