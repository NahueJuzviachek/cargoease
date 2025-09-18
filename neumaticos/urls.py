# neumaticos/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path("", views.neumaticos_list, name="neumaticos_list"),
    path("reubicar/", views.neumaticos_reubicar, name="neumaticos_reubicar"),
    path("recapar/", views.neumaticos_recapar, name="neumaticos_recapar"),
    path("almacen/nuevo/", views.neumaticos_nuevo_almacen, name="neumaticos_nuevo_almacen"),
    path("almacen/eliminar/", views.neumaticos_eliminar_almacen, name="neumaticos_eliminar_almacen"),
]
