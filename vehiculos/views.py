from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.db.models import Q
from .models import Vehiculo
from .forms import VehiculoForm

class VehiculoListView(ListView):
    model = Vehiculo
    template_name = "vehiculos/vehiculos_list.html"
    context_object_name = "vehiculos"
    paginate_by = 10

    def get_queryset(self):
        qs = super().get_queryset().order_by("id")
        q = self.request.GET.get("q", "").strip()
        if q:
            filtros = (
                Q(marca__icontains=q) |
                Q(modelo__icontains=q) |
                Q(dominio__icontains=q) |
                Q(dominio_remolque__icontains=q)
            )
            if q.isdigit():
                filtros = filtros | Q(anio=int(q))
            qs = qs.filter(filtros)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["q"] = self.request.GET.get("q", "").strip()
        return ctx

class VehiculoCreateView(CreateView):
    model = Vehiculo
    form_class = VehiculoForm
    template_name = "vehiculos/vehiculos_form.html"
    success_url = reverse_lazy("vehiculos_list")

class VehiculoUpdateView(UpdateView):
    model = Vehiculo
    form_class = VehiculoForm
    template_name = "vehiculos/vehiculos_form.html"
    success_url = reverse_lazy("vehiculos_list")

class VehiculoDeleteView(DeleteView):
    model = Vehiculo
    template_name = "vehiculos/vehiculos_confirm_delete.html"
    success_url = reverse_lazy("vehiculos_list")


