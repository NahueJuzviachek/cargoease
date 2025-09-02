from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib import messages
from .models import Conductor
from .forms import ConductorForm


class ConductorListView(ListView):
    model = Conductor
    template_name = "conductores/conductores_list.html"
    context_object_name = "conductores"

    def get_queryset(self):
        q = self.request.GET.get("q")
        if q:
            return Conductor.objects.filter(nombreApellido__icontains=q)
        return Conductor.objects.all()


class ConductorCreateView(CreateView):
    model = Conductor
    form_class = ConductorForm
    template_name = "conductores/conductores_form.html"
    success_url = reverse_lazy("conductores_list")

    def form_valid(self, form):
        messages.success(self.request, "Conductor creado correctamente.")
        return super().form_valid(form)


class ConductorUpdateView(UpdateView):
    model = Conductor
    form_class = ConductorForm
    template_name = "conductores/conductores_form.html"
    success_url = reverse_lazy("conductores_list")

    def form_valid(self, form):
        messages.success(self.request, "Conductor actualizado correctamente.")
        return super().form_valid(form)


class ConductorDeleteView(DeleteView):
    model = Conductor
    template_name = "conductores/conductores_confirm_delete.html"
    success_url = reverse_lazy("conductores_list")

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "Conductor eliminado correctamente.")
        return super().delete(request, *args, **kwargs)



