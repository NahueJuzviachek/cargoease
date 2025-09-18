# neumaticos/signals.py
from django.apps import apps
from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch import receiver

from vehiculos.models import Vehiculo
from .models import Neumatico, TipoNeumatico, EstadoNeumatico
from .utils import pos_to_nro
from .constants import POSICIONES_POR_EJE
from .services import acumular_km_vehiculo

# Obtenemos el modelo Viaje dinámicamente (sin depender de la app 'viajes')
Viaje = apps.get_model("viajes", "Viaje")

def _get_or_create_tipo_nuevo():
    return TipoNeumatico.objects.get_or_create(descripcion__iexact="Nuevo",
                                               defaults={"descripcion": "Nuevo"})[0]

def _get_or_create_estado_montado():
    return EstadoNeumatico.objects.get_or_create(descripcion__iexact="Montado",
                                                 defaults={"descripcion": "Montado"})[0]

@receiver(post_save, sender=Vehiculo)
def crear_neumaticos_por_ejes(sender, instance: Vehiculo, created: bool, **kwargs):
    """Al crear un vehículo, generar neumáticos montados según ejes × POSICIONES_POR_EJE."""
    if not created:
        return
    tipo_nuevo = _get_or_create_tipo_nuevo()
    estado_montado = _get_or_create_estado_montado()

    with transaction.atomic():
        for eje in range(1, instance.ejes + 1):
            for pos in range(1, POSICIONES_POR_EJE + 1):
                nro = pos_to_nro(eje, pos)
                if Neumatico.objects.filter(vehiculo=instance, nroNeumatico=nro, montado=True).exists():
                    continue
                Neumatico.objects.create(
                    vehiculo=instance,
                    estado=estado_montado,
                    tipo=tipo_nuevo,
                    nroNeumatico=nro,
                    montado=True,
                    km=0,
                )

@receiver(post_save, sender=Viaje)
def sumar_km_por_viaje_nuevo(sender, instance: Viaje, created: bool, **kwargs):
    """
    Cuando se crea un Viaje nuevo, sumar su distancia a los km de
    todos los neumáticos montados del vehículo (último viaje).
    """
    if not created:
        return
    if instance.vehiculo_id and instance.distancia:
        acumular_km_vehiculo(instance.vehiculo_id, instance.distancia)
