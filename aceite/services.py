# aceite/services.py
from datetime import timedelta
from decimal import Decimal

from django.db.models import Sum
from django.db.models.functions import Coalesce
from django.utils import timezone

from .models import AceiteMotor, AceiteCaja


def _sumar_km_despues_de(vehiculo, fecha_excl=None) -> Decimal:
    """
    Suma km de viajes del vehículo.
    Si fecha_excl está dada, suma viajes con fecha > fecha_excl (mismo día NO cuenta).
    """
    qs = vehiculo.viajes.all()
    if fecha_excl:
        qs = qs.filter(fecha__gt=fecha_excl)
    # Coalesce evita None y siempre devuelve Decimal("0") si no hay viajes
    return qs.aggregate(s=Coalesce(Sum("distancia"), Decimal("0")))["s"]


def _fecha_base_para_ciclo(vehiculo):
    """
    Si hay viajes: base = (mínima fecha de viaje) - 1 día, así cuentan TODOS los viajes existentes.
    Si no hay viajes: base = hoy.
    """
    min_fecha = (
        vehiculo.viajes.order_by("fecha")
        .values_list("fecha", flat=True)
        .first()
    )
    if min_fecha:
        return min_fecha - timedelta(days=1)
    return timezone.localdate()


# ---------------- MOTOR ----------------
def asegurar_ciclo_motor(vehiculo) -> AceiteMotor:
    """
    Devuelve el ciclo 'abierto' (más reciente). Si no existe, lo crea con:
    - fecha base = min fecha viaje - 1 día (o hoy)
    - km = suma de viajes posteriores a esa base (puede ser 0 si no hay viajes)
    """
    ciclo = (
        AceiteMotor.objects.filter(vehiculo=vehiculo)
        .order_by("-fecha", "-id")
        .first()
    )
    if ciclo:
        return ciclo
    base = _fecha_base_para_ciclo(vehiculo)
    km = _sumar_km_despues_de(vehiculo, base)
    return AceiteMotor.objects.create(
        vehiculo=vehiculo,
        fecha=base,
        filtros=False,
        km=km,
    )


def recalc_km_motor(vehiculo) -> AceiteMotor:
    """
    Recalcula y PERSISTE km del ciclo actual de motor.
    """
    ciclo = asegurar_ciclo_motor(vehiculo)
    km = _sumar_km_despues_de(vehiculo, ciclo.fecha)
    if ciclo.km != km:
        ciclo.km = km
        ciclo.save(update_fields=["km"])
    return ciclo


# ---------------- CAJA ----------------
def asegurar_ciclo_caja(vehiculo) -> AceiteCaja:
    ciclo = (
        AceiteCaja.objects.filter(vehiculo=vehiculo)
        .order_by("-fecha", "-id")
        .first()
    )
    if ciclo:
        return ciclo
    base = _fecha_base_para_ciclo(vehiculo)
    km = _sumar_km_despues_de(vehiculo, base)
    return AceiteCaja.objects.create(
        vehiculo=vehiculo,
        fecha=base,
        km=km,
    )


def recalc_km_caja(vehiculo) -> AceiteCaja:
    ciclo = asegurar_ciclo_caja(vehiculo)
    km = _sumar_km_despues_de(vehiculo, ciclo.fecha)
    if ciclo.km != km:
        ciclo.km = km
        ciclo.save(update_fields=["km"])
    return ciclo


# ---------------- FACILITADOR ----------------
def recalc_km_aceite_para_vehiculo(vehiculo):
    """
    Llamá esto cada vez que se cree/edite/borre un Viaje del vehículo.
    """
    recalc_km_motor(vehiculo)
    recalc_km_caja(vehiculo)
