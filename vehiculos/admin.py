from django.contrib import admin
from .models import Vehiculo

@admin.register(Vehiculo)
class VehiculoAdmin(admin.ModelAdmin):
    list_display = ("id", "marca", "modelo", "anio_fabricacion", "dominio", "dominio_remolque")
    search_fields = ("marca", "modelo", "dominio", "dominio_remolque")
    list_filter = ("anio_fabricacion", "marca")
