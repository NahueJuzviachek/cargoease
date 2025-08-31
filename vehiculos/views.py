from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import Vehiculo

class VehiculoListView(ListView):
    model = Vehiculo
    template_name = "vehiculos/vehiculos_list.html"
    context_object_name = "vehiculos"

class VehiculoCreateView(CreateView):
    model = Vehiculo
    fields = ["marca", "modelo", "anio_fabricacion", "dominio", "dominio_remolque"]
    template_name = "vehiculos/vehiculos_form.html"
    success_url = reverse_lazy("vehiculos_list")

class VehiculoUpdateView(UpdateView):
    model = Vehiculo
    fields = ["marca", "modelo", "anio_fabricacion", "dominio", "dominio_remolque"]
    template_name = "vehiculos/vehiculos_form.html"
    success_url = reverse_lazy("vehiculos_list")

class VehiculoDeleteView(DeleteView):
    model = Vehiculo
    template_name = "vehiculos/vehiculos_confirm_delete.html"
    success_url = reverse_lazy("vehiculos_list")

