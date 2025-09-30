# aceite/services.py
from decimal import Decimal
from django.db import transaction
from django.utils import timezone
from django.db.models import Sum

from .models import Aceite, AceiteCambio, EstadoAceite, TipoAceite


def _suma_km_viajes(vehiculo):
    from viajes.models import Viaje
    total = Viaje.objects.filter(vehiculo=vehiculo).aggregate(s=Sum("distancia"))["s"]
    return Decimal(total or 0)


def recalc_km_aceite_para_vehiculo(vehiculo):
    """
    Recalcula km_acumulados para todos los aceites EN_USO del vehículo.
    Lo llamás desde viajes (on_commit) y también lo podés usar manualmente.
    """
    suma_actual = _suma_km_viajes(vehiculo)
    aceites = Aceite.objects.filter(vehiculo=vehiculo, estado=EstadoAceite.EN_USO)
    for a in aceites:
        base = a.viajes_km_acumulados_al_instalar or Decimal("0")
        a.km_acumulados = suma_actual - base
        if a.km_acumulados < 0:
            a.km_acumulados = Decimal("0")
        a.save(update_fields=["km_acumulados"])


@transaction.atomic
def cambiar_aceite(aceite: Aceite, notas: str = "", filtros_cambiados: bool = False) -> Aceite:
    """
    Registra un cambio (reset):
    - Guarda historial (con filtros_cambiados solo si es motor).
    - Incrementa ciclos.
    - Resetea km a 0 y actualiza snapshot al total de km de viajes actual.
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
    aceite.estado = EstadoAceite.EN_USO
    aceite.save(update_fields=[
        "ciclos", "km_acumulados", "viajes_km_acumulados_al_instalar",
        "fecha_instalacion", "estado"
    ])
    return aceite
