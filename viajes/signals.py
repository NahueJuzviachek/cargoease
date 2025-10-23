# viajes/signals.py
from decimal import Decimal
from django.db.models import Sum
from django.db.models.signals import pre_save, post_save, post_delete
from django.dispatch import receiver

from .models import GastoExtra, Viaje


# ---------------------------
# Utilidades locales
# ---------------------------
def _sumar_gastos_extra(viaje: Viaje) -> Decimal:
    total = viaje.gastos_extra.aggregate(s=Sum("monto"))["s"] or Decimal("0")
    return total

def _to_int_km(val) -> int:
    """Convierte Decimal/float/int/str a entero de km (seguro)."""
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
# (igual que tenías)
# ---------------------------------------
@receiver(post_save, sender=Viaje)
def viaje_post_save_recalc_aceite(sender, instance: Viaje, **kwargs):
    print(f"[viajes.signals] post_save Viaje #{instance.pk} vehiculo={instance.vehiculo_id}")
    try:
        from aceite.services import recalc_km_aceite_para_vehiculo
        recalc_km_aceite_para_vehiculo(instance.vehiculo)
        print(f"[viajes.signals] recalc OK para vehiculo={instance.vehiculo_id}")
    except Exception as e:
        print("[viajes.signals] Error recalc post_save:", e)


@receiver(post_delete, sender=Viaje)
def viaje_post_delete_recalc_aceite(sender, instance: Viaje, **kwargs):
    print(f"[viajes.signals] post_delete Viaje #{instance.pk} vehiculo={instance.vehiculo_id}")
    try:
        from aceite.services import recalc_km_aceite_para_vehiculo
        recalc_km_aceite_para_vehiculo(instance.vehiculo)
        print(f"[viajes.signals] recalc OK para vehiculo={instance.vehiculo_id}")
    except Exception as e:
        print("[viajes.signals] Error recalc post_delete:", e)


# ----------------------------------------------------
# GastoExtra: mantener totales/ganancia en save/delete
# (igual que tenías)
# ----------------------------------------------------
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


# =================================================================
# KM en NEUMÁTICOS: crear / editar / eliminar
#  - Usa el campo Viaje.distancia para los km
#  - En edición aplica delta (nuevo - anterior) y contempla cambio de vehículo
#  - En borrado resta los km del viaje
# =================================================================

@receiver(pre_save, sender=Viaje)
def viaje_pre_save_cache_old(sender, instance: Viaje, **kwargs):
    """
    Cachea los valores previos (vehiculo_id y distancia) para poder
    calcular deltas en post_save cuando se edita un viaje.
    """
    if not instance.pk:
        # Es un create: no hay valores anteriores
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
    Sincroniza kilómetros en neumáticos del vehículo:
      - CREATE: suma 'distancia' al vehículo del viaje.
      - UPDATE (mismo vehículo): aplica delta = distancia_nueva - distancia_anterior.
      - UPDATE (cambió de vehículo): resta al vehículo anterior y suma al nuevo.
    """
    try:
        from neumaticos.services import acumular_km_vehiculo  # suma/resta y clamp >= 0
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

    # UPDATE
    old_vid = getattr(instance, "_old_vehiculo_id", None)
    old_km = _to_int_km(getattr(instance, "_old_distancia", 0))

    if old_vid == new_vid:
        delta = new_km - old_km
        if delta:
            try:
                acumular_km_vehiculo(new_vid, delta)
            except Exception as e:
                print("[viajes.signals] Error aplicar delta km en update:", e)
    else:
        # Cambió de vehículo: sacar todo al viejo, sumar todo al nuevo
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
    ELIMINAR viaje: resta su distancia a los neumáticos del vehículo al que pertenecía.
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
