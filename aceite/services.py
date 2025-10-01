# aceite/services.py
from decimal import Decimal
from django.db import transaction
from django.utils import timezone
from django.db.models import Sum
from .models import Aceite, AceiteCambio, TipoAceite

MAX_MOTOR = 30000
MAX_CAJA  = 100000

def _suma_km_desde_instalacion(aceite: Aceite) -> Decimal:
    """Suma de km de Viaje desde la fecha de instalación del aceite."""
    from viajes.models import Viaje  # import local para evitar circulares
    agg = (
        Viaje.objects
        .filter(vehiculo=aceite.vehiculo, fecha__gte=aceite.fecha_instalacion)
        .aggregate(s=Sum("distancia"))
    )
    return Decimal(agg["s"] or 0)

def recalc_km_aceite_para_vehiculo(vehiculo):
    """Recalcula km_acumulados para cada aceite sumando viajes desde fecha_instalacion."""
    for a in Aceite.objects.filter(vehiculo=vehiculo):
        a.km_acumulados = _suma_km_desde_instalacion(a)
        a.save(update_fields=["km_acumulados"])

@transaction.atomic
def cambiar_aceite(aceite: Aceite, filtros_cambiados: bool = False) -> Aceite:
    """Registra el cambio, resetea km y fija vida útil según tipo."""
    AceiteCambio.objects.create(
        aceite=aceite,
        fecha=timezone.now(),
        km_acumulados_al_cambio=aceite.km_acumulados,
        filtros_cambiados=filtros_cambiados if aceite.tipo == TipoAceite.MOTOR else False,
    )

    aceite.ciclos += 1
    aceite.km_acumulados = Decimal("0")
    aceite.fecha_instalacion = timezone.now().date()
    aceite.vida_util_km = MAX_MOTOR if aceite.tipo == TipoAceite.MOTOR else MAX_CAJA
    aceite.save(update_fields=["ciclos", "km_acumulados", "fecha_instalacion", "vida_util_km"])
    return aceite
