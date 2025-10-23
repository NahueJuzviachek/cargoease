# neumaticos/admin.py
from django.contrib import admin
from .models import Neumatico, EstadoNeumatico, TipoNeumatico, AlmacenNeumaticos
from django.utils import timezone

@admin.register(EstadoNeumatico)
class EstadoNeumaticoAdmin(admin.ModelAdmin):
    list_display = ("idEstadoNeumatico", "descripcion")
    search_fields = ("descripcion",)

@admin.register(TipoNeumatico)
class TipoNeumaticoAdmin(admin.ModelAdmin):
    list_display = ("idTipo", "descripcion")
    search_fields = ("descripcion",)

@admin.register(AlmacenNeumaticos)
class AlmacenAdmin(admin.ModelAdmin):
    list_display = ("idNeumatico_id", "fecha_ingreso")
    search_fields = ("idNeumatico__idNeumatico",)

@admin.register(Neumatico)
class NeumaticoAdmin(admin.ModelAdmin):
    list_display = ("idNeumatico", "vehiculo", "nroNeumatico", "estado", "montado", "km", "activo", "eliminado", "fecha_baja")
    list_filter = ("estado", "montado", "activo", "eliminado", "tipo")
    search_fields = ("idNeumatico", "vehiculo__dominio")
    actions = ["accion_soft_delete", "accion_restore"]

    @admin.action(description="Marcar como ELIMINADO (soft delete)")
    def accion_soft_delete(self, request, queryset):
        estado_elim, _ = EstadoNeumatico.objects.get_or_create(descripcion="ELIMINADO")
        updated = 0
        for n in queryset:
            n.estado = estado_elim
            n.activo = False
            n.eliminado = True
            n.fecha_baja = timezone.now()
            n.save(update_fields=["estado", "activo", "eliminado", "fecha_baja"])
            updated += 1
        self.message_user(request, f"{updated} neumático(s) marcados como ELIMINADO.")

    @admin.action(description="Restaurar (estado EN USO)")
    def accion_restore(self, request, queryset):
        from django.utils import timezone
        estado_activo, _ = EstadoNeumatico.objects.get_or_create(descripcion="EN USO")
        updated = 0
        for n in queryset:
            n.estado = estado_activo
            n.activo = True
            n.eliminado = False
            n.fecha_baja = None
            n.save(update_fields=["estado", "activo", "eliminado", "fecha_baja"])
            updated += 1
        self.message_user(request, f"{updated} neumático(s) restaurados.")
