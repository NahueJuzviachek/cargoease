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
    Calcula la suma total de distancias recorridas por los viajes del vehículo
    asociados a un aceite desde su última instalación o cambio.

    El método soporta dos esquemas distintos según el tipo de campo 'fecha' en Viaje:
      A) Si 'fecha' es DateTimeField → filtra todos los viajes con fecha >= instalación.
      B) Si 'fecha' es DateField → incluye:
         - viajes con fecha posterior a la fecha de instalación, o
         - viajes el mismo día pero creados después o en el mismo instante.

    Retorna la distancia total recorrida (Decimal).
    """
    fi = aceite.fecha_instalacion
    if fi is None:
        # Si por alguna razón no hay fecha de instalación, no hay viajes válidos.
        return Decimal("0.00")

    # Se obtiene el tipo de campo 'fecha' del modelo Viaje para adaptar el filtro.
    fecha_field = Viaje._meta.get_field("fecha")

    # Filtrado según el tipo de campo de fecha.
    if isinstance(fecha_field, DateTimeField):
        # Caso A: el campo 'fecha' es DateTime → comparación directa.
        qs = (
            Viaje.objects
            .filter(vehiculo=aceite.vehiculo, fecha__gte=fi)
            .values_list("distancia", flat=True)
        )
    elif isinstance(fecha_field, DateField):
        # Caso B: el campo 'fecha' es Date → combinar condiciones con Q.
        qs = (
            Viaje.objects
            .filter(vehiculo=aceite.vehiculo)
            .filter(
                Q(fecha__gt=fi.date()) |
                Q(fecha=fi.date(), creado_en__gte=fi)
            )
            .values_list("distancia", flat=True)
        )
    else:
        # Fallback raro: trata el campo como DateField por compatibilidad.
        qs = (
            Viaje.objects
            .filter(vehiculo=aceite.vehiculo)
            .filter(
                Q(fecha__gt=fi.date()) |
                Q(fecha=fi.date(), creado_en__gte=fi)
            )
            .values_list("distancia", flat=True)
        )

    # Suma todas las distancias válidas, ignorando nulos o ceros.
    total = sum((d or Decimal("0")) for d in qs) or Decimal("0")
    return total


def recalc_km_aceite(aceite: Aceite) -> Aceite:
    """
    Recalcula los kilómetros acumulados para un solo aceite.
    - Suma las distancias de los viajes posteriores a la instalación.
    - Actualiza el campo 'km_acumulados' si cambió el valor.
    """
    total = _sumar_distancias_desde_instalacion(aceite)
    if aceite.km_acumulados != total:
        aceite.km_acumulados = total
        aceite.save(update_fields=["km_acumulados"])
    return aceite


def recalc_km_aceite_para_vehiculo(vehiculo) -> None:
    """
    Recalcula los kilómetros acumulados para todos los aceites de un vehículo.
    Utiliza la función recalc_km_aceite() sobre cada uno.
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
    Registra un cambio de aceite, asegurando consistencia mediante una transacción atómica.

    Operaciones realizadas:
      1. Crea un registro en AceiteCambio con:
         - Fecha exacta del cambio.
         - Kilómetros acumulados al momento del cambio.
         - Si se cambiaron filtros (solo para aceite de motor).
      2. Incrementa el contador de ciclos del aceite.
      3. Resetea los km acumulados a cero.
      4. Actualiza la fecha de instalación al momento exacto del cambio.

    Retorna el objeto AceiteCambio creado.
    """
    now_dt = fecha or timezone.now()

    # Registrar el evento histórico del cambio.
    cambio = AceiteCambio.objects.create(
        aceite=aceite,
        fecha=now_dt,
        km_acumulados_al_cambio=aceite.km_acumulados or Decimal("0.00"),
        filtros_cambiados=bool(filtros_cambiados)
        if aceite.tipo == TipoAceite.MOTOR
        else False,
    )

    # Actualizar el estado actual del aceite.
    aceite.ciclos = (aceite.ciclos or 0) + 1
    aceite.km_acumulados = Decimal("0.00")
    aceite.fecha_instalacion = now_dt  # Fecha/hora exacta del cambio.
    aceite.save(update_fields=["ciclos", "km_acumulados", "fecha_instalacion"])

    return cambio
