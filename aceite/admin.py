# aceite/admin.py
from django.contrib import admin
from .models import Aceite, AceiteCambio

@admin.register(Aceite)
class AceiteAdmin(admin.ModelAdmin):
    list_display = ("vehiculo", "tipo", "km_acumulados", "vida_util_km", "ciclos", "fecha_instalacion")

@admin.register(AceiteCambio)
class AceiteCambioAdmin(admin.ModelAdmin):
    list_display = ("aceite", "fecha", "km_acumulados_al_cambio", "filtros_cambiados")
    list_filter = ("fecha", "filtros_cambiados", "aceite__tipo")
    search_fields = ("aceite__vehiculo__dominio", "aceite__vehiculo__modelo")
    ordering = ("-fecha",)
