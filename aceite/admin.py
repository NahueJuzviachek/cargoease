from django.contrib import admin
from .models import AceiteMotor, AceiteCaja

@admin.register(AceiteMotor)
class AceiteMotorAdmin(admin.ModelAdmin):
    list_display = ("vehiculo", "fecha", "km", "filtros")
    list_filter = ("fecha", "filtros")
    search_fields = ("vehiculo__dominio", "vehiculo__marca", "vehiculo__modelo")

@admin.register(AceiteCaja)
class AceiteCajaAdmin(admin.ModelAdmin):
    list_display = ("vehiculo", "fecha", "km")
    list_filter = ("fecha",)
    search_fields = ("vehiculo__dominio", "vehiculo__marca", "vehiculo__modelo")
