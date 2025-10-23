from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from django.utils import timezone
from django.db import transaction

from vehiculos.models import Vehiculo
from .models import Neumatico, EstadoNeumatico, TipoNeumatico, AlmacenNeumaticos

# Fallback si constants no está disponible
try:
    from .constants import POSICIONES_POR_EJE
except Exception:
    POSICIONES_POR_EJE = 2


def _get_estado(descripcion: str):
    estado, _ = EstadoNeumatico.objects.get_or_create(descripcion=descripcion)
    return estado


def _get_tipo_default():
    try:
        tipo, _ = TipoNeumatico.objects.get_or_create(descripcion="EN USO")
        return tipo
    except Exception:
        return None


@receiver(post_save, sender=Vehiculo)
def crear_neumaticos_base_al_crear_vehiculo(sender, instance: Vehiculo, created, **kwargs):
    """
    Al crear un vehículo nuevo, si no tiene neumáticos asociados, crear posiciones base
    YA MONTADAS en el vehículo, con estado 'Montado' y nroNeumatico 1..(ejes*POSICIONES_POR_EJE).
    """
    if not created:
        return

    if Neumatico.objects.filter(vehiculo=instance).exists():
        return

    try:
        ejes = int(getattr(instance, "ejes", 2) or 2)
    except Exception:
        ejes = 2

    total_posiciones = max(1, ejes * POSICIONES_POR_EJE)
    estado_montado = _get_estado("Montado")
    tipo_default = _get_tipo_default()

    objs = []
    for i in range(1, total_posiciones + 1):
        objs.append(
            Neumatico(
                vehiculo=instance,
                estado=estado_montado,
                tipo=tipo_default,
                nroNeumatico=i,
                montado=True,         # 👈 YA montados
                km=0,
                activo=True,
                eliminado=False,
                fecha_baja=None,
            )
        )

    with transaction.atomic():
        creados = Neumatico.objects.bulk_create(objs, ignore_conflicts=True)
        # Limpieza defensiva: por si algún flujo externo generara registro en almacén
        pks = [n.pk for n in creados if n.pk]
        if pks:
            AlmacenNeumaticos.objects.filter(idNeumatico_id__in=pks).delete()


@receiver(pre_delete, sender=Vehiculo)
def soft_delete_neumaticos_on_vehicle_delete(sender, instance: Vehiculo, **kwargs):
    """
    Antes de borrar un Vehículo, marcamos 'ELIMINADO' todos sus neumáticos.
    """
    estado_elim = _get_estado("ELIMINADO")
    now = timezone.now()
    Neumatico.objects.filter(vehiculo=instance).update(
        estado=estado_elim, activo=False, eliminado=True, fecha_baja=now
    )
