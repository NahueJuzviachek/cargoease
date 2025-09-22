from decimal import Decimal
from django.db.models import Sum
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import GastoExtra, Viaje


def _sumar_gastos_extra(viaje: Viaje) -> Decimal:
    total = viaje.gastos_extra.aggregate(s=Sum("monto"))["s"] or Decimal("0")
    return total


@receiver(post_save, sender=GastoExtra)
@receiver(post_delete, sender=GastoExtra)
def actualizar_gastos_y_ganancia(sender, instance: GastoExtra, **kwargs):
    viaje = instance.viaje

    # Si el viaje ya no existe (p. ej. se borró en cascada con el vehículo), salir
    if not Viaje.objects.filter(pk=viaje.pk).exists():
        return

    total_extras = _sumar_gastos_extra(viaje)
    viaje.gasto = total_extras
    viaje.ganancia_total = viaje.calcular_ganancia()
    viaje.save(update_fields=["gasto", "ganancia_total", "actualizado_en"])
