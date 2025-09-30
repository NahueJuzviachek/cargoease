# aceite/services.py
from decimal import Decimal
from django.db import transaction
from django.utils import timezone
from django.db.models import Sum
from .models import Aceite, AceiteCambio, TipoAceite

MAX_MOTOR = 30000
MAX_CAJA = 100000

def _suma_km_viajes(vehiculo):
    from viajes.models import Viaje  # import local para evitar circulares
    total = Viaje.objects.filter(vehiculo=vehiculo).aggregate(s=Sum("distancia"))["s"]
    return Decimal(total or 0)

def recalc_km_aceite_para_vehiculo(vehiculo):
    suma_actual = _suma_km_viajes(vehiculo)
    for a in Aceite.objects.filter(vehiculo=vehiculo):
        base = a.viajes_km_acumulados_al_instalar or Decimal("0")
        a.km_acumulados = max(Decimal("0"), suma_actual - base)
        a.save(update_fields=["km_acumulados"])

@transaction.atomic
def cambiar_aceite(aceite: Aceite, notas: str = "", filtros_cambiados: bool = False) -> Aceite:
    """
    Registra cambio (reset) y setea vida_util_km según tipo:
    - Motor: 30000
    - Caja:  10000
    """
    suma_actual = _suma_km_viajes(aceite.vehiculo)

    AceiteCambio.objects.create(
        aceite=aceite,
        fecha=timezone.now(),
        km_acumulados_al_cambio=aceite.km_acumulados,
        notas=notas or "",
        filtros_cambiados=filtros_cambiados if aceite.tipo == TipoAceite.MOTOR else False,
    )

    aceite.ciclos += 1
    aceite.km_acumulados = Decimal("0")
    aceite.viajes_km_acumulados_al_instalar = suma_actual
    aceite.fecha_instalacion = timezone.now().date()
    aceite.vida_util_km = MAX_MOTOR if aceite.tipo == TipoAceite.MOTOR else MAX_CAJA
    aceite.save(update_fields=[
        "ciclos", "km_acumulados", "viajes_km_acumulados_al_instalar",
        "fecha_instalacion", "vida_util_km"
    ])
    return aceite
