# conductores/views.py
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib import messages
from django.shortcuts import redirect, get_object_or_404
from .models import Conductor
from .forms import ConductorForm

class ConductorListView(ListView):
    """
    Lista todos los conductores activos con posibilidad de búsqueda por nombre.
    """
    model = Conductor
    template_name = "conductores/conductores_list.html"
    context_object_name = "conductores"

    def get_queryset(self):
        q = self.request.GET.get("q")
        qs = Conductor.objects  # devuelve sólo activos gracias al manager
        if q:
            return qs.filter(nombreApellido__icontains=q)
        return qs.all()

class ConductorCreateView(CreateView):
    """
    Crea un nuevo conductor y muestra mensaje de éxito.
    """
    model = Conductor
    form_class = ConductorForm
    template_name = "conductores/conductores_form.html"
    success_url = reverse_lazy("conductores_list")

    def form_valid(self, form):
        messages.success(self.request, "Conductor creado correctamente.")
        return super().form_valid(form)

class ConductorUpdateView(UpdateView):
    """
    Edita un conductor existente y muestra mensaje de éxito.
    """
    model = Conductor
    form_class = ConductorForm
    template_name = "conductores/conductores_form.html"
    success_url = reverse_lazy("conductores_list")

    def form_valid(self, form):
        messages.success(self.request, "Conductor actualizado correctamente.")
        return super().form_valid(form)

class ConductorDeleteView(DeleteView):
    """
    Baja lógica: marca el conductor como inactivo en vez de eliminarlo de la base.
    Mantiene la confirmación visual (GET muestra confirm page; POST realiza la baja lógica).
    """
    model = Conductor
    template_name = "conductores/conductores_confirm_delete.html"
    success_url = reverse_lazy("conductores_list")

    def post(self, request, *args, **kwargs):
        """
        Al hacer POST en la vista de confirmación, no borramos el registro: lo marcamos como inactivo.
        """
        self.object = self.get_object()
        # baja lógica
        self.object.is_active = False
        self.object.save(update_fields=["is_active"])
        messages.success(request, "Conductor dado de baja correctamente.")
        return redirect(self.success_url)

    # opcional: proteger el método delete por si alguien lo llama
    def delete(self, request, *args, **kwargs):
        """
        Si por alguna razón se llama a delete(), redirigimos al post que hace baja lógica.
        """
        return self.post(request, *args, **kwargs)