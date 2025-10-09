from __future__ import annotations

from decimal import Decimal
from typing import Optional

from django.db import transaction
from django.db.models import Q
from django.utils import timezone
from django.db.models.fields import DateTimeField, DateField

from .models import Aceite, AceiteCambio, TipoAceite
from viajes.models import Viaje


def _sumar_distancias_desde_instalacion(aceite: Aceite) -> Decimal:
    """
    Devuelve la suma de 'distancia' de viajes del mismo vehículo que ocurren
    DESPUÉS (o en el mismo instante o después) de 'aceite.fecha_instalacion'.

    Soporta dos esquemas:
      A) Viaje.fecha = DateTimeField  -> filtra con fecha__gte (exacto)
      B) Viaje.fecha = DateField      -> combina:
           - fecha > fecha_instalacion.date()
           - fecha == fecha_instalacion.date() AND creado_en >= fecha_instalacion
    """
    fi = aceite.fecha_instalacion
    if fi is None:
        return Decimal("0.00")

    fecha_field = Viaje._meta.get_field("fecha")

    if isinstance(fecha_field, DateTimeField):
        qs = (Viaje.objects
              .filter(vehiculo=aceite.vehiculo, fecha__gte=fi)
              .values_list("distancia", flat=True))
    elif isinstance(fecha_field, DateField):
        qs = (Viaje.objects
              .filter(vehiculo=aceite.vehiculo)
              .filter(Q(fecha__gt=fi.date()) | Q(fecha=fi.date(), creado_en__gte=fi))
              .values_list("distancia", flat=True))
    else:
        # Fallback extremadamente raro: tratamos como DateField
        qs = (Viaje.objects
              .filter(vehiculo=aceite.vehiculo)
              .filter(Q(fecha__gt=fi.date()) | Q(fecha=fi.date(), creado_en__gte=fi))
              .values_list("distancia", flat=True))

    total = sum((d or Decimal("0")) for d in qs) or Decimal("0")
    return total


def recalc_km_aceite(aceite: Aceite) -> Aceite:
    """
    Recalcula y persiste 'km_acumulados' de UN aceite a partir de los viajes
    ocurridos desde 'fecha_instalacion' (incluida).
    """
    total = _sumar_distancias_desde_instalacion(aceite)
    if aceite.km_acumulados != total:
        aceite.km_acumulados = total
        aceite.save(update_fields=["km_acumulados"])
    return aceite


def recalc_km_aceite_para_vehiculo(vehiculo) -> None:
    """
    Recalcula 'km_acumulados' para TODOS los aceites del vehículo.
    """
    for aceite in Aceite.objects.filter(vehiculo=vehiculo):
        recalc_km_aceite(aceite)


@transaction.atomic
def registrar_cambio_aceite(
    aceite: Aceite,
    *,
    filtros_cambiados: bool = False,
    fecha: Optional[timezone.datetime] = None,
) -> AceiteCambio:
    """
    Registra un cambio de aceite y realiza:
      - Guarda AceiteCambio(fecha exacta, km acumulados al cambio, filtros)
      - Incrementa ciclos
      - Resetea km_acumulados = 0
      - Actualiza fecha_instalacion con DateTime exacto del cambio
    """
    now_dt = fecha or timezone.now()

    cambio = AceiteCambio.objects.create(
        aceite=aceite,
        fecha=now_dt,
        km_acumulados_al_cambio=aceite.km_acumulados or Decimal("0.00"),
        filtros_cambiados=bool(filtros_cambiados) if aceite.tipo == TipoAceite.MOTOR else False,
    )

    aceite.ciclos = (aceite.ciclos or 0) + 1
    aceite.km_acumulados = Decimal("0.00")
    aceite.fecha_instalacion = now_dt  # << DateTime exacto
    aceite.save(update_fields=["ciclos", "km_acumulados", "fecha_instalacion"])

    return cambio
