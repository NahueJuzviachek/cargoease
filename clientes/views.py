#clientes/views.py
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.db.models import Q
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from django.views import View
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages

from .models import Cliente
from .forms import ClienteForm
from ubicaciones.models import Provincia, Localidad

class ClienteListView(ListView):
    """
    Lista paginada de clientes con búsqueda por nombre.
    Usa el manager por defecto (devuelve solo activos).
    """
    model = Cliente
    template_name = "clientes/clientes_list.html"
    context_object_name = "clientes"
    paginate_by = 10

    def get_queryset(self):
        qs = Cliente.objects.select_related("pais", "provincia", "localidad").order_by("id")
        q = self.request.GET.get("q", "").strip()
        if q:
            qs = qs.filter(Q(nombre__icontains=q))
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["q"] = self.request.GET.get("q", "").strip()
        return ctx


class ClienteCreateView(CreateView):
    """
    Vista para crear un nuevo cliente usando ClienteForm.
    """
    model = Cliente
    form_class = ClienteForm
    template_name = "clientes/clientes_form.html"
    success_url = reverse_lazy("clientes_list")


class ClienteUpdateView(UpdateView):
    """
    Vista para editar un cliente existente.
    """
    model = Cliente
    form_class = ClienteForm
    template_name = "clientes/clientes_form.html"
    success_url = reverse_lazy("clientes_list")


class ClienteDeleteView(DeleteView):
    """
    Baja lógica: marca el cliente como inactivo en vez de eliminarlo.
    GET -> muestra confirmación; POST -> realiza la baja lógica.
    """
    model = Cliente
    template_name = "clientes/clientes_confirm_delete.html"
    success_url = reverse_lazy("clientes_list")

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.is_active = False
        self.object.save(update_fields=["is_active"])
        messages.success(request, "Cliente dado de baja correctamente.")
        return redirect(self.success_url)

    def delete(self, request, *args, **kwargs):
        # Por seguridad, delegamos a post()
        return self.post(request, *args, **kwargs)


class ClienteReactivateView(View):
    def post(self, request, pk):
        cliente = get_object_or_404(Cliente, pk=pk)
        cliente.is_active = True
        cliente.save(update_fields=["is_active"])
        messages.success(request, "Cliente reactivado correctamente.")
        return redirect("clientes_list")


# ----------------------------
# ENDPOINTS AJAX
# ----------------------------
@require_GET
def ajax_cargar_provincias(request):
    """
    Devuelve JSON con las provincias de un país dado (para formularios dinámicos).
    """
    pais_id = request.GET.get("pais")
    provincias = Provincia.objects.filter(pais_id=pais_id).values("id", "nombre").order_by("nombre")
    return JsonResponse(list(provincias), safe=False)


@require_GET
def ajax_cargar_localidades(request):
    """
    Devuelve JSON con las localidades de una provincia dada (para formularios dinámicos).
    """
    provincia_id = request.GET.get("provincia")
    localidades = Localidad.objects.filter(provincia_id=provincia_id).values("id", "nombre").order_by("nombre")
    return JsonResponse(list(localidades), safe=False)
