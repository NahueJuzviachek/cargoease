from django.conf import settings
from django.urls import reverse
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.db.models import Q
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib import messages
from django.db import transaction  # para on_commit
from django.contrib.auth.decorators import login_required 
from django.http import JsonResponse, Http404 
from ubicaciones.models import Localidad      
from clientes.models import Cliente
from .models import Viaje, GastoExtra
from .forms import ViajeForm, GastoExtraForm
from vehiculos.models import Vehiculo
from .mixins import ORSContextMixin  # Mixin para contextos de OpenRouteService

# -----------------------------
# LISTADO DE VIAJES POR VEHÍCULO
# -----------------------------
class ViajeListView(ORSContextMixin, ListView):
    """
    Muestra un listado de viajes filtrado por vehículo.
    Soporta búsqueda por salida/destino y paginación.
    """
    model = Viaje
    template_name = "viajes/viajes_list.html"
    context_object_name = "viajes"
    paginate_by = 10

    def dispatch(self, request, *args, **kwargs):
        """
        Captura el vehículo desde la URL y lo guarda para filtros/contexto.
        """
        self.vehiculo = get_object_or_404(Vehiculo, pk=kwargs["vehiculo_pk"])
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        """
        Filtra viajes del vehículo y aplica búsqueda por salida/destino.
        """
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

# -----------------------------
# CREAR VIAJE PARA UN VEHÍCULO
# -----------------------------
class VehiculoViajeCreateView(ORSContextMixin, CreateView):
    """
    Formulario para agregar un viaje a un vehículo específico.
    """
    model = Viaje
    form_class = ViajeForm
    template_name = "viajes/viajes_form.html"

    def dispatch(self, request, *args, **kwargs):
        self.vehiculo = get_object_or_404(Vehiculo, pk=kwargs["vehiculo_pk"])
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        # Asociamos el viaje al vehículo
        form.instance.vehiculo = self.vehiculo
        resp = super().form_valid(form)

        # Recalcular km de aceite después de commit (si existe app aceite)
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

# -----------------------------
# EDITAR VIAJE DE UN VEHÍCULO
# -----------------------------
class VehiculoViajeUpdateView(ORSContextMixin, UpdateView):
    """
    Edita un viaje de un vehículo, bloqueando el campo vehiculo.
    """
    model = Viaje
    form_class = ViajeForm
    template_name = "viajes/viajes_form.html"

    def dispatch(self, request, *args, **kwargs):
        self.vehiculo = get_object_or_404(Vehiculo, pk=kwargs["vehiculo_pk"])
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        # Solo viajes de este vehículo
        return Viaje.objects.filter(vehiculo_id=self.kwargs["vehiculo_pk"]).select_related("vehiculo")

    def get_form(self, form_class=None):
        # Bloquea el campo 'vehiculo' en el formulario
        form = super().get_form(form_class)
        if "vehiculo" in form.fields:
            form.fields["vehiculo"].widget.attrs["disabled"] = True
            form.fields["vehiculo"].initial = self.vehiculo
        return form

    def form_valid(self, form):
        # Asegura la relación con vehículo
        form.instance.vehiculo = self.vehiculo
        resp = super().form_valid(form)

        def _post_commit():
            try:
                from aceite.services import recalc_km_aceite_para_vehiculo
                recalc_km_aceite_para_vehiculo(self.vehiculo.id)
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

# -----------------------------
# ELIMINAR VIAJE DE UN VEHÍCULO
# -----------------------------
class VehiculoViajeDeleteView(ORSContextMixin, DeleteView):
    """
    Confirma y elimina un viaje. Recalcula km de aceite después de commit.
    """
    model = Viaje
    template_name = "viajes/viajes_confirm_delete.html"

    def get_queryset(self):
        return Viaje.objects.filter(vehiculo_id=self.kwargs["vehiculo_pk"])

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        vehiculo_id = self.object.vehiculo_id
        resp = super().delete(request, *args, **kwargs)

        # Recalcular km aceite
        def _post_commit():
            try:
                from aceite.services import recalc_km_aceite_para_vehiculo
                recalc_km_aceite_para_vehiculo(self.object.vehiculo)
            except Exception:
                pass

        transaction.on_commit(_post_commit)
        return resp

    def get_success_url(self):
        return reverse("vehiculo_viajes_list", kwargs={"vehiculo_pk": self.kwargs["vehiculo_pk"]})

# -----------------------------
# GASTOS EXTRA DE UN VIAJE
# -----------------------------
def gastos_list(request, viaje_id):
    """
    Muestra el formulario compacto para crear un GastoExtra
    y la tabla con los gastos de ese viaje.
    """
    viaje = get_object_or_404(Viaje, pk=viaje_id)
    gastos = viaje.gastos_extra.all()  # Orden según Meta

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

    ctx = {"viaje": viaje, "gastos": gastos, "form": form}
    return render(request, "viajes/gastos_list.html", ctx)

def gasto_extra_eliminar(request, viaje_id, gasto_id):
    """
    Elimina un gasto extra del viaje, previa confirmación.
    """
    viaje = get_object_or_404(Viaje, pk=viaje_id)
    gasto = get_object_or_404(GastoExtra, pk=gasto_id, viaje=viaje)

    if request.method == "POST":
        gasto.delete()
        messages.success(request, "Gasto extra eliminado.")
        return redirect(reverse("viaje_gastos_list", args=[viaje.id]))

    return render(request, "viajes/gasto_extra_confirm_delete.html", {"viaje": viaje, "gasto": gasto})

# -----------------------------
# AJAX: COORDENADAS DE LOCALIDAD
# -----------------------------
def ajax_localidad_coords(request):
    """
    Devuelve lat/lng de una Localidad vía AJAX.
    Usado por JS para dibujar rutas en mapas.
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
    Devuelve la ubicación del cliente (pais_id, provincia_id, localidad_id) vía AJAX.
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
