from django.urls import path
from . import views

urlpatterns = [
    # Vista principal (lista global de neumáticos)
    path("", views.neumaticos_list, name="neumaticos_list"),

    # Acción para reubicar o cambiar neumáticos (desde el modal)
    path("cambiar/", views.neumaticos_cambiar_global, name="neumaticos_cambiar_global"),
]