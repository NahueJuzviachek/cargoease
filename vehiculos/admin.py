# vehiculos/admin.py
from django.contrib import admin
from .models import Vehiculo

@admin.register(Vehiculo)
class VehiculoAdmin(admin.ModelAdmin):
    list_display = ("marca", "modelo", "anio_fabricacion", "dominio", "dominio_remolque")
    search_fields = ("marca", "modelo", "anio_fabricacion", "dominio", "dominio_remolque")

