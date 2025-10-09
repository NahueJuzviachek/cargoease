from django.urls import path
from .views import soporte_view  

app_name = "soporte"

urlpatterns = [
    path("", soporte_view, name="form"),  
]