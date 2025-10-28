from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.db.models import Q
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from .models import Cliente
from .forms import ClienteForm
from ubicaciones.models import Provincia, Localidad

class ClienteListView(ListView):
    """
    Lista paginada de clientes con búsqueda por nombre.
    """
    model = Cliente
    template_name = "clientes/clientes_list.html"
    context_object_name = "clientes"
    paginate_by = 10

    def get_queryset(self):
        """
        Aplica filtro de búsqueda por nombre y evita consultas N+1 usando select_related.
        """
        qs = super().get_queryset().select_related("pais", "provincia", "localidad").order_by("id")
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
    Vista para eliminar un cliente.
    """
    model = Cliente
    template_name = "clientes/clientes_confirm_delete.html"
    success_url = reverse_lazy("clientes_list")


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
