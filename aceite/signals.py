# aceite/signals.py
from decimal import Decimal
from django.db.models import Sum

from .models import Aceite


def _total_km_viajes(vehiculo_id: int) -> Decimal:
    """
    Suma de km (distancia) de todos los Viaje del vehículo.
    Import local para evitar import circular.
    """
    if not vehiculo_id:
        return Decimal("0")
    try:
        from viajes.models import Viaje
    except Exception:
        return Decimal("0")
    agg = Viaje.objects.filter(vehiculo_id=vehiculo_id).aggregate(s=Sum("distancia"))
    return Decimal(agg["s"] or 0)


def _recalcular_km_aceites(vehiculo_id: int) -> None:
    """
    Recalcula km_acumulados = total_km_viajes - snapshot_instalación
    para todos los Aceite del vehículo. Tolera que no existan aceites.
    """
    if not vehiculo_id:
        return
    total = _total_km_viajes(vehiculo_id)
    for a in Aceite.objects.filter(vehiculo_id=vehiculo_id):
        base = a.viajes_km_acumulados_al_instalar or Decimal("0")
        nuevo = total - base
        if nuevo < 0:
            nuevo = Decimal("0")
        a.km_acumulados = nuevo
        a.save(update_fields=["km_acumulados"])


# Estas funciones se conectan en aceite/apps.py usando sender=Viaje.
# NO usamos decoradores @receiver aquí para evitar doble registro global.
def aceite_recalc_on_viaje_save(sender, instance, created, **kwargs):
    vehiculo_id = getattr(instance, "vehiculo_id", None)
    _recalcular_km_aceites(vehiculo_id)


def aceite_recalc_on_viaje_delete(sender, instance, **kwargs):
    vehiculo_id = getattr(instance, "vehiculo_id", None)
    _recalcular_km_aceites(vehiculo_id)
