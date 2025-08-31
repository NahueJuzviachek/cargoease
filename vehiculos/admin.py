from django.contrib import admin
from .models import Vehiculo

@admin.register(Vehiculo)
class VehiculoAdmin(admin.ModelAdmin):
    list_display = ("marca", "modelo", "anio", "dominio", "dominio_remolque")
    search_fields = ("marca", "modelo", "dominio", "dominio_remolque")
    list_filter = ("anio",)  # útil para filtrar por año


