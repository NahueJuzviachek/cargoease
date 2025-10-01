# aceite/signals.py
from decimal import Decimal
from django.db.models import Sum
from .models import Aceite

def _suma_km_desde_instalacion(aceite: Aceite) -> Decimal:
    try:
        from viajes.models import Viaje
    except Exception:
        return Decimal("0")
    agg = (
        Viaje.objects
        .filter(vehiculo_id=aceite.vehiculo_id, fecha__gte=aceite.fecha_instalacion)
        .aggregate(s=Sum("distancia"))
    )
    return Decimal(agg["s"] or 0)

def _recalcular_km_aceites(vehiculo_id: int) -> None:
    if not vehiculo_id:
        return
    for a in Aceite.objects.filter(vehiculo_id=vehiculo_id):
        a.km_acumulados = _suma_km_desde_instalacion(a)
        a.save(update_fields=["km_acumulados"])

def aceite_recalc_on_viaje_save(sender, instance, created, **kwargs):
    vehiculo_id = getattr(instance, "vehiculo_id", None)
    _recalcular_km_aceites(vehiculo_id)

def aceite_recalc_on_viaje_delete(sender, instance, **kwargs):
    vehiculo_id = getattr(instance, "vehiculo_id", None)
    _recalcular_km_aceites(vehiculo_id)
