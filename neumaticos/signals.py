# neumaticos/signals.py
from django.apps import apps
from django.db import transaction
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from vehiculos.models import Vehiculo
from .models import Neumatico, TipoNeumatico, EstadoNeumatico
from .utils import pos_to_nro
from .constants import POSICIONES_POR_EJE, KM_UMBRAL_USADO
from .services import acumular_km_vehiculo

Viaje = apps.get_model("viajes", "Viaje")

def _get_or_create_tipo(descripcion: str):
    return TipoNeumatico.objects.get_or_create(descripcion__iexact=descripcion,
                                               defaults={"descripcion": descripcion})[0]

def _get_or_create_estado(descripcion: str):
    return EstadoNeumatico.objects.get_or_create(descripcion__iexact=descripcion,
                                                 defaults={"descripcion": descripcion})[0]

@receiver(post_save, sender=Vehiculo)
def crear_neumaticos_por_ejes(sender, instance: Vehiculo, created: bool, **kwargs):
    if not created:
        return
    tipo_nuevo = _get_or_create_tipo("Nuevo")
    estado_montado = _get_or_create_estado("Montado")

    with transaction.atomic():
        for eje in range(1, instance.ejes + 1):
            for pos in range(1, POSICIONES_POR_EJE + 1):
                nro = pos_to_nro(eje, pos)
                if Neumatico.objects.filter(vehiculo=instance, nroNeumatico=nro, montado=True).exists():
                    continue
                Neumatico.objects.create(
                    vehiculo=instance, estado=estado_montado, tipo=tipo_nuevo,
                    nroNeumatico=nro, montado=True, km=0
                )

@receiver(post_save, sender=Viaje)
def sumar_km_por_viaje_nuevo(sender, instance: Viaje, created: bool, **kwargs):
    """Suma la distancia del último viaje creado a todos los neumáticos montados del vehículo."""
    if not created:
        return
    if instance.vehiculo_id and instance.distancia:
        acumular_km_vehiculo(instance.vehiculo_id, instance.distancia)

@receiver(pre_save, sender=Neumatico)
def validar_condicion_por_km(sender, instance: Neumatico, **kwargs):
    """Si el neumático llega al umbral de km, pasa a condición 'Usado' automáticamente."""
    if instance.km is None:
        return
    try:
        km = int(instance.km)
    except Exception:
        return
    if km >= KM_UMBRAL_USADO:
        instance.tipo = _get_or_create_tipo("Usado")
