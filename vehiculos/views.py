from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.db.models import Q
from .models import Vehiculo
from .forms import VehiculoForm


# ---------------- Lista de vehículos ----------------
class VehiculoListView(ListView):
    """
    Vista de lista paginada de vehículos con búsqueda por marca, modelo,
    dominio, dominio de remolque o año de fabricación.
    """
    model = Vehiculo
    template_name = "vehiculos/vehiculos_list.html"
    context_object_name = "vehiculos"
    paginate_by = 10

    def get_queryset(self):
        """
        Permite filtrar por los campos de texto y por año si la búsqueda es numérica.
        """
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
                filtros |= Q(anio_fabricacion__exact=int(q))
            qs = qs.filter(filtros)
        return qs

    def get_context_data(self, **kwargs):
        """
        Agrega la query de búsqueda al contexto para mantener el valor en el formulario.
        """
        ctx = super().get_context_data(**kwargs)
        ctx["q"] = self.request.GET.get("q", "").strip()
        return ctx


# ---------------- Crear vehículo ----------------
class VehiculoCreateView(CreateView):
    """
    Vista para crear un nuevo vehículo usando el formulario VehiculoForm.
    Redirige a la lista de vehículos al completar.
    """
    model = Vehiculo
    form_class = VehiculoForm
    template_name = "vehiculos/vehiculos_form.html"
    success_url = reverse_lazy("vehiculos_list")


# ---------------- Editar vehículo ----------------
class VehiculoUpdateView(UpdateView):
    """
    Vista para editar un vehículo existente usando VehiculoForm.
    """
    model = Vehiculo
    form_class = VehiculoForm
    template_name = "vehiculos/vehiculos_form.html"
    success_url = reverse_lazy("vehiculos_list")


# ---------------- Eliminar vehículo ----------------
class VehiculoDeleteView(DeleteView):
    """
    Vista para eliminar un vehículo.
    """
    model = Vehiculo
    template_name = "vehiculos/vehiculos_confirm_delete.html"
    success_url = reverse_lazy("vehiculos_list")
