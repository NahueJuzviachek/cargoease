from django.urls import path
from django.contrib.auth.decorators import login_required
from .views import soporte_view  

app_name = "soporte"

urlpatterns = [
    path("", login_required(soporte_view), name="form"),
]
