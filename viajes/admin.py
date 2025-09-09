from django.contrib import admin
from .models import Divisa, Viaje

# Register your models here.
@admin.register(Divisa)
class DivisaAdmin(admin.ModelAdmin):
    list_display = ("codigo", "nombre", "simbolo")
    search_fields = ("codigo", "nombre")

@admin.register(Viaje)
class ViajeAdmin(admin.ModelAdmin):
    list_display = ("id", "fecha", "vehiculo", "salida", "destino",
                    "valor_flete", "viaticos", "gasto", "ganancia_total", "divisa")
    list_filter = ("fecha", "divisa", "vehiculo", "salida", "destino")
    search_fields = ("vehiculo__patente", "salida__nombre", "destino__nombre")
    date_hierarchy = "fecha"  # navegación rápida por años/meses/días