from decimal import Decimal
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

from vehiculos.models import Vehiculo
from .models import Aceite, TipoAceite

MOTOR_VIDA_KM = 30000
CAJA_VIDA_KM = 100000

def _defaults_por_tipo(tipo: str) -> dict:
    if tipo == TipoAceite.MOTOR:
        return {"vida_util_km": MOTOR_VIDA_KM}
    return {"vida_util_km": CAJA_VIDA_KM}

@receiver(post_save, sender=Vehiculo)
def crear_aceites_por_defecto(sender, instance: Vehiculo, created, **kwargs):
    """
    Al crear un Vehículo, asegura que existan los dos aceites (motor y caja).
    No duplica gracias al UniqueConstraint (vehiculo, tipo).
    """
    if not created:
        return

    for tipo in (TipoAceite.MOTOR, TipoAceite.CAJA):
        Aceite.objects.get_or_create(
            vehiculo=instance,
            tipo=tipo,
            defaults={
                "km_acumulados": Decimal("0.00"),
                "vida_util_km": _defaults_por_tipo(tipo)["vida_util_km"],
                "ciclos": 0,
                "fecha_instalacion": timezone.now().date(),
            },
        )
