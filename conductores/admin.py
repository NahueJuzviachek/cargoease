# conductores/admin.py
from django.contrib import admin
from .models import Conductor

@admin.register(Conductor)
class ConductorAdmin(admin.ModelAdmin):
    list_display = ("id", "nombreApellido", "dni", "vehiculo", "dominio", "is_active")
    list_filter = ("is_active", "vehiculo")
    search_fields = ("nombreApellido", "dni", "dominio")