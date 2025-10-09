from django.contrib import admin
from .models import Aceite, AceiteCambio

@admin.register(Aceite)
class AceiteAdmin(admin.ModelAdmin):
    list_display = ("vehiculo", "tipo", "km_acumulados", "vida_util_km", "ciclos", "fecha_instalacion")
    list_filter = ("tipo", "vehiculo")
    search_fields = ("vehiculo__dominio", "vehiculo__modelo", "vehiculo__marca")

@admin.register(AceiteCambio)
class AceiteCambioAdmin(admin.ModelAdmin):
    list_display = ("aceite", "fecha", "km_acumulados_al_cambio", "filtros_cambiados")
    list_filter = ("aceite__tipo", "filtros_cambiados")
    search_fields = ("aceite__vehiculo__dominio",)

