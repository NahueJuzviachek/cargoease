from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.db.models import Q
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from .models import Cliente
from .forms import ClienteForm
from ubicaciones.models import Provincia, Localidad


class ClienteListView(ListView):
    model = Cliente
    template_name = "clientes/clientes_list.html"
    context_object_name = "clientes"
    paginate_by = 10  # opcional

    def get_queryset(self):
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
    model = Cliente
    form_class = ClienteForm
    template_name = "clientes/clientes_form.html"
    success_url = reverse_lazy("clientes_list")


class ClienteUpdateView(UpdateView):
    model = Cliente
    form_class = ClienteForm
    template_name = "clientes/clientes_form.html"
    success_url = reverse_lazy("clientes_list")


class ClienteDeleteView(DeleteView):
    model = Cliente
    template_name = "clientes/clientes_confirm_delete.html"
    success_url = reverse_lazy("clientes_list")


# --------------------
# Endpoints AJAX
# --------------------
@require_GET
def ajax_cargar_provincias(request):
    pais_id = request.GET.get("pais")
    provincias = (
        Provincia.objects.filter(pais_id=pais_id)
        .values("id", "nombre")
        .order_by("nombre")
    )
    return JsonResponse(list(provincias), safe=False)


@require_GET
def ajax_cargar_localidades(request):
    provincia_id = request.GET.get("provincia")
    localidades = (
        Localidad.objects.filter(provincia_id=provincia_id)
        .values("id", "nombre")
        .order_by("nombre")
    )
    return JsonResponse(list(localidades), safe=False)
