from decimal import Decimal
from django.db.models import Sum
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import GastoExtra, Viaje


def _sumar_gastos_extra(viaje: Viaje) -> Decimal:
    total = viaje.gastos_extra.aggregate(s=Sum("monto"))["s"] or Decimal("0")
    return total


@receiver(post_save, sender=Viaje)
def viaje_post_save(sender, instance: Viaje, **kwargs):
    print(f"[viajes.signals] post_save Viaje #{instance.pk} vehiculo={instance.vehiculo_id}")
    try:
        from aceite.services import recalc_km_aceite_para_vehiculo
        recalc_km_aceite_para_vehiculo(instance.vehiculo)
        print(f"[viajes.signals] recalc OK para vehiculo={instance.vehiculo_id}")
    except Exception as e:
        print("[viajes.signals] Error recalc post_save:", e)


@receiver(post_delete, sender=Viaje)
def viaje_post_delete(sender, instance: Viaje, **kwargs):
    print(f"[viajes.signals] post_delete Viaje #{instance.pk} vehiculo={instance.vehiculo_id}")
    try:
        from aceite.services import recalc_km_aceite_para_vehiculo
        recalc_km_aceite_para_vehiculo(instance.vehiculo)
        print(f"[viajes.signals] recalc OK para vehiculo={instance.vehiculo_id}")
    except Exception as e:
        print("[viajes.signals] Error recalc post_delete:", e)


@receiver(post_save, sender=GastoExtra)
def gastoextra_post_save(sender, instance: GastoExtra, **kwargs):
    print(f"[viajes.signals] post_save GastoExtra viaje={instance.viaje_id}")
    viaje = instance.viaje
    total_extras = _sumar_gastos_extra(viaje)
    viaje.gasto = total_extras
    viaje.ganancia_total = viaje.calcular_ganancia()
    viaje.save(update_fields=["gasto", "ganancia_total", "actualizado_en"])


@receiver(post_delete, sender=GastoExtra)
def gastoextra_post_delete(sender, instance: GastoExtra, **kwargs):
    print(f"[viajes.signals] post_delete GastoExtra viaje={instance.viaje_id}")
    viaje = instance.viaje
    # Si el viaje ya no existe (borrado en cascada), salir
    if not Viaje.objects.filter(pk=viaje.pk).exists():
        return
    total_extras = _sumar_gastos_extra(viaje)
    viaje.gasto = total_extras
    viaje.ganancia_total = viaje.calcular_ganancia()
    viaje.save(update_fields=["gasto", "ganancia_total", "actualizado_en"])
