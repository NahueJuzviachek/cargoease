from django.conf import settings
from django.urls import reverse
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.db.models import Q
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib import messages
from django.db import transaction  # para on_commit
from django.contrib.auth.decorators import login_required 
from django.http import JsonResponse, Http404  # ⬅️ AJAX coords
from ubicaciones.models import Localidad       # ⬅️ AJAX coords
from clientes.models import Cliente
from .models import Viaje, GastoExtra
from .forms import ViajeForm
from .forms import GastoExtraForm  # formulario del gasto extra
from vehiculos.models import Vehiculo
from .mixins import ORSContextMixin


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
            .select_related("vehiculo", "salida", "destino", "divisa", "cliente")
            .filter(vehiculo=self.vehiculo)
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
        resp = super().form_valid(form)

        vehiculo_id = self.vehiculo.id

        def _post_commit():
            try:
                from aceite.services import recalc_km_aceite_para_vehiculo
                recalc_km_aceite_para_vehiculo(self.vehiculo) 
            except Exception:
                pass

        transaction.on_commit(_post_commit)
        return resp

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

    def get_queryset(self):
        # Solo permitimos editar viajes de ese vehículo
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
        resp = super().form_valid(form)

        vehiculo_id = self.vehiculo.id

        def _post_commit():
            try:
                from aceite.services import recalc_km_aceite_para_vehiculo
                recalc_km_aceite_para_vehiculo(vehiculo_id)
            except Exception:
                pass

        transaction.on_commit(_post_commit)
        return resp

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["vehiculo"] = self.vehiculo
        return ctx

    def get_success_url(self):
        return reverse("vehiculo_viajes_list", kwargs={"vehiculo_pk": self.vehiculo.pk})


class VehiculoViajeDeleteView(ORSContextMixin, DeleteView):
    model = Viaje
    template_name = "viajes/viajes_confirm_delete.html"

    def get_queryset(self):
        # Solo permite borrar viajes de ese vehículo
        return Viaje.objects.filter(vehiculo_id=self.kwargs["vehiculo_pk"])

    def delete(self, request, *args, **kwargs):
        # Guardamos vehiculo antes de borrar para recalcular luego
        self.object = self.get_object()
        vehiculo_id = self.object.vehiculo_id
        resp = super().delete(request, *args, **kwargs)

        vehiculo = self.object.vehiculo
        def _post_commit():
            try:
                from aceite.services import recalc_km_aceite_para_vehiculo
                recalc_km_aceite_para_vehiculo(vehiculo)  
            except Exception:
                pass

        transaction.on_commit(_post_commit)
        return resp

    def get_success_url(self):
        return reverse("vehiculo_viajes_list", kwargs={"vehiculo_pk": self.kwargs["vehiculo_pk"]})


# -----------------------------
# Gastos Extra (form arriba + tabla debajo)
# -----------------------------
def gastos_list(request, viaje_id):
    """
    Vista que muestra el formulario compacto para crear un GastoExtra
    y debajo la tabla de todos los gastos de ese viaje.
    """
    viaje = get_object_or_404(Viaje, pk=viaje_id)
    gastos = viaje.gastos_extra.all()  # ya viene ordenado por Meta en el modelo

    if request.method == "POST":
        form = GastoExtraForm(request.POST)
        if form.is_valid():
            gasto = form.save(commit=False)
            gasto.viaje = viaje
            gasto.save()
            messages.success(request, "Gasto extra registrado correctamente.")
            return redirect(reverse("viaje_gastos_list", args=[viaje.id]))
        else:
            messages.error(request, "Revisá los datos del formulario.")
    else:
        form = GastoExtraForm()

    ctx = {
        "viaje": viaje,
        "gastos": gastos,
        "form": form,
    }
    return render(request, "viajes/gastos_list.html", ctx)


def gasto_extra_eliminar(request, viaje_id, gasto_id):
    """
    Confirma y elimina un gasto extra asociado al viaje.
    """
    viaje = get_object_or_404(Viaje, pk=viaje_id)
    gasto = get_object_or_404(GastoExtra, pk=gasto_id, viaje=viaje)

    if request.method == "POST":
        gasto.delete()
        messages.success(request, "Gasto extra eliminado.")
        return redirect(reverse("viaje_gastos_list", args=[viaje.id]))

    # Plantilla de confirmación mínima (o podés usar un modal/confirm JS)
    return render(request, "viajes/gasto_extra_confirm_delete.html", {"viaje": viaje, "gasto": gasto})


# -----------------------------
# AJAX: Coordenadas de Localidad (para el mapa)
# -----------------------------
def ajax_localidad_coords(request):
    """
    Devuelve lat/lng (float) para una Localidad via ?localidad=<id>.
    Usado por static/viajes/viajes_map.js para trazar la ruta sin geocodificar por nombre.
    """
    loc_id = request.GET.get("localidad")
    if not loc_id:
        return JsonResponse({"error": "Falta parámetro 'localidad'."}, status=400)

    try:
        loc = Localidad.objects.only("lat", "lng").get(pk=loc_id)
    except Localidad.DoesNotExist:
        raise Http404("Localidad no encontrada")

    if loc.lat is None or loc.lng is None:
        return JsonResponse({"error": "Localidad sin coordenadas."}, status=422)

    return JsonResponse({"lat": float(loc.lat), "lng": float(loc.lng)})

def ajax_cliente_ubicacion(request):
    """
    /viajes/ajax/cliente-ubicacion/?cliente=<id>
    Devuelve {pais_id, provincia_id, localidad_id} de la ubicación del cliente.
    """
    cli_id = request.GET.get("cliente")
    if not cli_id:
        return JsonResponse({"error": "Falta parámetro 'cliente'."}, status=400)

    try:
        c = Cliente.objects.select_related("pais", "provincia", "localidad").get(pk=cli_id)
    except Cliente.DoesNotExist:
        raise Http404("Cliente no encontrado")

    data = {
        "pais_id": c.pais_id,
        "provincia_id": c.provincia_id,
        "localidad_id": c.localidad_id,
    }
    return JsonResponse(data)