from django.contrib import admin
from .models import Conductor

@admin.register(Conductor)
class ConductorAdmin(admin.ModelAdmin):
    list_display = ("nombreApellido", "dni", "vehiculo", "dominio")
    search_fields = ("nombreApellido", "dni", "dominio", "vehiculo__marca", "vehiculo__modelo")
    list_filter = ("vehiculo__marca",)

