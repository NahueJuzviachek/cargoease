# aceite/signals.py
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from viajes.models import Viaje
from .services import recalc_km_aceite_para_vehiculo


@receiver(post_save, sender=Viaje)
def aceite_recalc_after_viaje_save(sender, instance: Viaje, **kwargs):
    recalc_km_aceite_para_vehiculo(instance.vehiculo)


@receiver(post_delete, sender=Viaje)
def aceite_recalc_after_viaje_delete(sender, instance: Viaje, **kwargs):
    recalc_km_aceite_para_vehiculo(instance.vehiculo)
