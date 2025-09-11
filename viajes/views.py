from django.urls import reverse
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.db.models import Q
from django.shortcuts import get_object_or_404

from .models import Viaje
from .forms import ViajeForm
from vehiculos.models import Vehiculo


class ViajeListView(ListView):
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


class VehiculoViajeCreateView(CreateView):
    model = Viaje
    form_class = ViajeForm
    template_name = "viajes/viajes_form.html"

    def dispatch(self, request, *args, **kwargs):
        self.vehiculo = get_object_or_404(Vehiculo, pk=kwargs["vehiculo_pk"])
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.vehiculo = self.vehiculo  # ✅ lo fijamos acá
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["vehiculo"] = self.vehiculo
        return ctx

    def get_success_url(self):
        return reverse("vehiculo_viajes_list", kwargs={"vehiculo_pk": self.vehiculo.pk})


class VehiculoViajeUpdateView(UpdateView):
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
        if "vehiculo" in form.fields:
            form.fields["vehiculo"].widget.attrs["disabled"] = True
            form.fields["vehiculo"].initial = self.vehiculo
        return form

    def form_valid(self, form):
        form.instance.vehiculo = self.vehiculo  # por las dudas
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["vehiculo"] = self.vehiculo
        return ctx

    def get_success_url(self):
        return reverse("vehiculo_viajes_list", kwargs={"vehiculo_pk": self.vehiculo.pk})


class VehiculoViajeDeleteView(DeleteView):
    model = Viaje
    template_name = "viajes/viajes_confirm_delete.html"

    # Solo permite borrar viajes de ese vehículo
    def get_queryset(self):
        return Viaje.objects.filter(vehiculo_id=self.kwargs["vehiculo_pk"])

    def get_success_url(self):
        return reverse("vehiculo_viajes_list", kwargs={"vehiculo_pk": self.kwargs["vehiculo_pk"]})
