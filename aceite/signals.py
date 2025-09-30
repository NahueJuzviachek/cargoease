from decimal import Decimal
from django.db.models import Sum
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

def _suma_km_viajes(vehiculo):
    from viajes.models import Viaje
    total = Viaje.objects.filter(vehiculo=vehiculo).aggregate(s=Sum("distancia"))["s"]
    return Decimal(total or 0)

def _recalcular_km_aceites(vehiculo):
    """
    Recalcula km_acumulados para todos los aceites EN_USO del vehículo.
    """
    from .models import Aceite, EstadoAceite
    suma_actual = _suma_km_viajes(vehiculo)
    aceites = Aceite.objects.filter(vehiculo=vehiculo, estado=EstadoAceite.EN_USO)
    for a in aceites:
        a.km_acumulados = (suma_actual - (a.viajes_km_acumulados_al_instalar or Decimal("0")))
        if a.km_acumulados < 0:
            a.km_acumulados = Decimal("0")
        a.save(update_fields=["km_acumulados"])

@receiver(post_save, dispatch_uid="aceite_recalc_on_viaje_save")
def aceite_recalc_on_viaje_save(sender, instance, created, **kwargs):
    """
    Se conecta dinámicamente a Viaje en apps.py (para evitar import circular).
    """
    model_name = sender.__name__.lower()
    if model_name != "viaje":
        return
    _recalcular_km_aceites(instance.vehiculo)

@receiver(post_delete, dispatch_uid="aceite_recalc_on_viaje_delete")
def aceite_recalc_on_viaje_delete(sender, instance, **kwargs):
    model_name = sender.__name__.lower()
    if model_name != "viaje":
        return
    _recalcular_km_aceites(instance.vehiculo)
