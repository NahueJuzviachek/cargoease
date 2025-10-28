from decimal import Decimal
from django.db.models import Sum
from django.db.models.signals import pre_save, post_save, post_delete
from django.dispatch import receiver

from .models import GastoExtra, Viaje

# ---------------------------
# Utilidades locales
# ---------------------------
def _sumar_gastos_extra(viaje: Viaje) -> Decimal:
    """
    Suma todos los gastos extra asociados a un viaje.
    Devuelve Decimal('0') si no hay gastos.
    """
    total = viaje.gastos_extra.aggregate(s=Sum("monto"))["s"] or Decimal("0")
    return total

def _to_int_km(val) -> int:
    """
    Convierte Decimal/float/int/str a entero de km.
    Seguro contra valores None o inválidos.
    """
    if val is None:
        return 0
    try:
        if isinstance(val, Decimal):
            return int(val)
        return int(float(val))
    except Exception:
        return 0


# ---------------------------------------
# Aceite: recalcular km en save / delete
# ---------------------------------------
@receiver(post_save, sender=Viaje)
def viaje_post_save_recalc_aceite(sender, instance: Viaje, **kwargs):
    """
    Tras guardar un viaje, recalcula los km de aceite del vehículo.
    """
    try:
        from aceite.services import recalc_km_aceite_para_vehiculo
        if instance.vehiculo_id:
            recalc_km_aceite_para_vehiculo(instance.vehiculo_id)
    except Exception as e:
        print("[viajes.signals] Error recalc aceite post_save:", e)

@receiver(post_delete, sender=Viaje)
def viaje_post_delete_recalc_aceite(sender, instance, **kwargs):
    """
    Tras eliminar un viaje, recalcula los km de aceite del vehículo.
    """
    try:
        from aceite.services import recalc_km_aceite_para_vehiculo
        if instance.vehiculo:
            recalc_km_aceite_para_vehiculo(instance.vehiculo)
    except Exception as e:
        print("[viajes.signals] Error recalc aceite post_delete:", e)


# ----------------------------------------------------
# GastoExtra: mantener totales/ganancia en save/delete
# ----------------------------------------------------
@receiver(post_save, sender=GastoExtra)
def gastoextra_post_save(sender, instance: GastoExtra, **kwargs):
    """
    Tras crear/editar un gasto extra, recalcula:
    - total de gastos del viaje
    - ganancia total
    """
    viaje = instance.viaje
    total_extras = _sumar_gastos_extra(viaje)
    viaje.gasto = total_extras
    viaje.ganancia_total = viaje.calcular_ganancia()
    viaje.save(update_fields=["gasto", "ganancia_total", "actualizado_en"])

@receiver(post_delete, sender=GastoExtra)
def gastoextra_post_delete(sender, instance: GastoExtra, **kwargs):
    """
    Tras eliminar un gasto extra, recalcula totales del viaje.
    """
    viaje = instance.viaje
    if not Viaje.objects.filter(pk=viaje.pk).exists():
        return
    total_extras = _sumar_gastos_extra(viaje)
    viaje.gasto = total_extras
    viaje.ganancia_total = viaje.calcular_ganancia()
    viaje.save(update_fields=["gasto", "ganancia_total", "actualizado_en"])


# =================================================================
# KM en NEUMÁTICOS: crear / editar / eliminar
# =================================================================
@receiver(pre_save, sender=Viaje)
def viaje_pre_save_cache_old(sender, instance: Viaje, **kwargs):
    """
    Antes de guardar un viaje:
    - si es creación, inicializa km y vehículo antiguos a 0/None
    - si es edición, guarda los valores antiguos para calcular deltas
    """
    if not instance.pk:
        instance._old_vehiculo_id = None
        instance._old_distancia = 0
        return
    old = (
        Viaje.objects.filter(pk=instance.pk)
        .values("vehiculo_id", "distancia")
        .first()
    ) or {}
    instance._old_vehiculo_id = old.get("vehiculo_id")
    instance._old_distancia = _to_int_km(old.get("distancia") or 0)

@receiver(post_save, sender=Viaje)
def viaje_post_save_sync_neumaticos(sender, instance: Viaje, created: bool, **kwargs):
    """
    Tras guardar un viaje:
    - si se creó, suma km a neumáticos del vehículo
    - si se editó, calcula delta km y actualiza neumáticos correctamente
    """
    try:
        from neumaticos.services import acumular_km_vehiculo
    except Exception as e:
        print("[viajes.signals] Error import acumular_km_vehiculo:", e)
        return

    new_vid = instance.vehiculo_id
    new_km = _to_int_km(getattr(instance, "distancia", 0))

    if created:
        if new_vid and new_km:
            try:
                acumular_km_vehiculo(new_vid, new_km)
            except Exception as e:
                print("[viajes.signals] Error sumar km en create:", e)
        return

    old_vid = getattr(instance, "_old_vehiculo_id", None)
    old_km = _to_int_km(getattr(instance, "_old_distancia", 0))

    # Mismo vehículo: aplicar delta
    if old_vid == new_vid:
        delta = new_km - old_km
        if delta:
            try:
                acumular_km_vehiculo(new_vid, delta)
            except Exception as e:
                print("[viajes.signals] Error aplicar delta km en update:", e)
    else:
        # Vehículo cambiado: restar km del viejo y sumar al nuevo
        if old_vid and old_km:
            try:
                acumular_km_vehiculo(old_vid, -old_km)
            except Exception as e:
                print("[viajes.signals] Error restar km al viejo en update:", e)
        if new_vid and new_km:
            try:
                acumular_km_vehiculo(new_vid, new_km)
            except Exception as e:
                print("[viajes.signals] Error sumar km al nuevo en update:", e)

@receiver(post_delete, sender=Viaje)
def viaje_post_delete_sync_neumaticos(sender, instance: Viaje, **kwargs):
    """
    Tras eliminar un viaje, resta los km del vehículo a los neumáticos.
    """
    try:
        from neumaticos.services import acumular_km_vehiculo
    except Exception as e:
        print("[viajes.signals] Error import acumular_km_vehiculo (delete):", e)
        return

    vid = instance.vehiculo_id
    km = _to_int_km(getattr(instance, "distancia", 0))
    if vid and km:
        try:
            acumular_km_vehiculo(vid, -km)
        except Exception as e:
            print("[viajes.signals] Error restar km en delete:", e)
