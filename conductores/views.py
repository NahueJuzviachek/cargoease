from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from .models import Conductor
from .forms import ConductorForm
from vehiculos.models import Vehiculo
from django.db.models import Q

class ConductorListView(ListView):
    model = Conductor
    template_name = "conductores/conductores_list.html"
    context_object_name = "conductores"
    paginate_by = 10

    def get_queryset(self):
        qs = super().get_queryset().select_related("vehiculo").order_by("id")
        q = self.request.GET.get("q", "").strip()
        if q:
            qs = qs.filter(
                Q(nombreApellido__icontains=q) |
                Q(dni__icontains=q) |
                Q(vehiculo__marca__icontains=q) |
                Q(vehiculo__modelo__icontains=q) |
                Q(dominio__icontains=q)
            )
        return qs

class ConductorCreateView(CreateView):
    model = Conductor
    form_class = ConductorForm
    template_name = "conductores/conductores_form.html"
    success_url = reverse_lazy("conductores_list")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        # Mapeo id -> dominio para autorrellenar vía JS
        ctx["vehiculo_dominios"] = list(Vehiculo.objects.values("id", "dominio"))
        return ctx

class ConductorUpdateView(UpdateView):
    model = Conductor
    form_class = ConductorForm
    template_name = "conductores/conductores_form.html"
    success_url = reverse_lazy("conductores_list")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["vehiculo_dominios"] = list(Vehiculo.objects.values("id", "dominio"))
        return ctx

class ConductorDeleteView(DeleteView):
    model = Conductor
    template_name = "conductores/conductores_confirm_delete.html"
    success_url = reverse_lazy("conductores_list")

