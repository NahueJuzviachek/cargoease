from django.urls import path
from django.contrib.auth.decorators import login_required
from . import views

urlpatterns = [
    path("", login_required(views.neumaticos_list), name="neumaticos_list"),
    path("reubicar/", login_required(views.neumaticos_reubicar), name="neumaticos_reubicar"),
    path("recapar/", login_required(views.neumaticos_recapar), name="neumaticos_recapar"),
    path("almacen/nuevo/", login_required(views.neumaticos_nuevo_almacen), name="neumaticos_nuevo_almacen"),
    path("almacen/eliminar/", login_required(views.neumaticos_eliminar_almacen), name="neumaticos_eliminar_almacen"),
]
