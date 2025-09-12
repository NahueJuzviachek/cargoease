# viajes/views.py
from django.conf import settings
from django.urls import reverse
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.db.models import Q
from django.shortcuts import get_object_or_404

from .models import Viaje
from .forms import ViajeForm
from vehiculos.models import Vehiculo


class ORSContextMixin:
    """
    Mixin para inyectar en el template la API key de OpenRouteService (ORS_API_KEY),
    que usa el JS del mapa para calcular rutas alternativas.
    """
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["ORS_API_KEY"] = getattr(settings, "ORS_API_KEY", "")  # <- clave para el front
        return ctx


class ViajeListView(ORSContextMixin, ListView):
    model = Viaje
    template_name = "viajes/viajes_list.html"
    context_object_name = "viajes"
    paginate_by = 10

    def dispatch(self, request, *args, **kwargs):
        # Vehículo obligatorio
        self.vehiculo = get_object_or_404(Vehiculo, pk=kwargs["vehiculo_pk"])
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        qs = (
            super()
            .get_queryset()
            .select_related("vehiculo", "salida", "destino", "divisa")
            .filter(vehiculo=self.vehiculo)  # Solo este vehículo
            .order_by("-fecha", "-creado_en")
        )
        q = self.request.GET.get("q", "").strip()
        if q:
            qs = qs.filter(
                Q(salida__nombre__icontains=q) |
                Q(destino__nombre__icontains=q)
            )
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["q"] = self.request.GET.get("q", "").strip()
        ctx["vehiculo"] = self.vehiculo
        return ctx


class VehiculoViajeCreateView(ORSContextMixin, CreateView):
    model = Viaje
    form_class = ViajeForm
    template_name = "viajes/viajes_form.html"

    def dispatch(self, request, *args, **kwargs):
        self.vehiculo = get_object_or_404(Vehiculo, pk=kwargs["vehiculo_pk"])
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        # Asociamos el viaje al vehículo del URL
        form.instance.vehiculo = self.vehiculo
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["vehiculo"] = self.vehiculo
        return ctx

    def get_success_url(self):
        return reverse("vehiculo_viajes_list", kwargs={"vehiculo_pk": self.vehiculo.pk})


class VehiculoViajeUpdateView(ORSContextMixin, UpdateView):
    model = Viaje
    form_class = ViajeForm
    template_name = "viajes/viajes_form.html"

    def dispatch(self, request, *args, **kwargs):
        self.vehiculo = get_object_or_404(Vehiculo, pk=kwargs["vehiculo_pk"])
        return super().dispatch(request, *args, **kwargs)

    # Solo permitimos editar viajes de ese vehículo
    def get_queryset(self):
        return (
            Viaje.objects
            .filter(vehiculo_id=self.kwargs["vehiculo_pk"])
            .select_related("vehiculo")
        )

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        # Si por algún motivo el form trae el campo 'vehiculo', lo bloqueamos visualmente
        if "vehiculo" in form.fields:
            form.fields["vehiculo"].widget.attrs["disabled"] = True
            form.fields["vehiculo"].initial = self.vehiculo
        return form

    def form_valid(self, form):
        # Aseguramos la relación aunque el campo esté disabled
        form.instance.vehiculo = self.vehiculo
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["vehiculo"] = self.vehiculo
        return ctx

    def get_success_url(self):
        return reverse("vehiculo_viajes_list", kwargs={"vehiculo_pk": self.vehiculo.pk})


class VehiculoViajeDeleteView(ORSContextMixin, DeleteView):
    model = Viaje
    template_name = "viajes/viajes_confirm_delete.html"

    # Solo permite borrar viajes de ese vehículo
    def get_queryset(self):
        return Viaje.objects.filter(vehiculo_id=self.kwargs["vehiculo_pk"])

    def get_success_url(self):
        return reverse("vehiculo_viajes_list", kwargs={"vehiculo_pk": self.kwargs["vehiculo_pk"]})
