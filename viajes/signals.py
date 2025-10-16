# viajes/signals.py
from decimal import Decimal
from django.db.models import Sum
from django.db.models.signals import pre_save, post_save, post_delete
from django.dispatch import receiver

from .models import GastoExtra, Viaje


# ---------------------------
# Utilidades (gastos extra)
# ---------------------------
def _sumar_gastos_extra(viaje: Viaje) -> Decimal:
    total = viaje.gastos_extra.aggregate(s=Sum("monto"))["s"] or Decimal("0")
    return total


# ---------------------------------------
# Aceite: recalcular km en save / delete
# (se mantiene igual que tenías)
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
# (se mantiene igual que tenías)
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
# NUEVO: Sincronización de KM en NEUMÁTICOS al EDITAR / ELIMINAR
# - La CREACIÓN del viaje ya la maneja neumaticos/signals.py (created=True).
#   (sumar_km_por_viaje_nuevo)  :contentReference[oaicite:2]{index=2}
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
        instance._old_distancia = None
        return

    old = (
        Viaje.objects.filter(pk=instance.pk)
        .values("vehiculo_id", "distancia")
        .first()
    ) or {}
    instance._old_vehiculo_id = old.get("vehiculo_id")
    instance._old_distancia = old.get("distancia") or 0


@receiver(post_save, sender=Viaje)
def viaje_post_save_sync_neumaticos(sender, instance: Viaje, created: bool, **kwargs):
    """
    EDITAR viaje:
      - Si NO cambió de vehículo: aplica delta = nueva_distancia - distancia_anterior.
      - Si SÍ cambió de vehículo: resta al vehículo anterior y suma al vehículo nuevo.
    La creación ya está cubierta en neumaticos/signals.py (created=True).
    """
    if created:
        return  # creación: ya suma km a neumáticos en neumaticos/signals.py

    try:
        from neumaticos.services import acumular_km_vehiculo  # suma/resta y clamp >= 0  :contentReference[oaicite:3]{index=3}

        old_vid = getattr(instance, "_old_vehiculo_id", None)
        old_km = getattr(instance, "_old_distancia", 0) or 0
        new_vid = instance.vehiculo_id
        new_km = instance.distancia or 0

        if old_vid == new_vid:
            delta = (new_km or 0) - (old_km or 0)
            if delta:
                acumular_km_vehiculo(new_vid, delta)
        else:
            # Cambió de vehículo: sacar todo al viejo, sumar todo al nuevo
            if old_vid:
                acumular_km_vehiculo(old_vid, -(old_km or 0))
            if new_vid:
                acumular_km_vehiculo(new_vid, (new_km or 0))

    except Exception as e:
        print("[viajes.signals] Error sync neumáticos post_save:", e)


@receiver(post_delete, sender=Viaje)
def viaje_post_delete_sync_neumaticos(sender, instance: Viaje, **kwargs):
    """
    ELIMINAR viaje:
      - Resta su distancia a los neumáticos del vehículo al que pertenecía.
    """
    try:
        from neumaticos.services import acumular_km_vehiculo  #  :contentReference[oaicite:4]{index=4}
        if instance.vehiculo_id and instance.distancia:
            acumular_km_vehiculo(instance.vehiculo_id, -(instance.distancia or 0))
    except Exception as e:
        print("[viajes.signals] Error sync neumáticos post_delete:", e)
