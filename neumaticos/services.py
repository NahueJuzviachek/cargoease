# neumaticos/services.py
from decimal import Decimal, ROUND_HALF_UP
from django.db import transaction
from django.db.models import F, Value, IntegerField
from django.db.models.functions import Greatest
from django.shortcuts import get_object_or_404

from vehiculos.models import Vehiculo
from .models import Neumatico, AlmacenNeumaticos, EstadoNeumatico
from .constants import POSICIONES_POR_EJE
from .utils import pos_to_nro

def _tipo_str(neum: Neumatico) -> str:
    return (getattr(getattr(neum, "tipo", None), "descripcion", "") or "").strip().lower()

def _get_estado(nombre: str) -> EstadoNeumatico:
    return EstadoNeumatico.objects.get(descripcion__iexact=nombre)

@transaction.atomic
def enviar_a_almacen(neumatico_ids: list[int]) -> int:
    estado_almacen = _get_estado("Almacén")
    moved = 0
    for nid in neumatico_ids:
        neum = get_object_or_404(Neumatico, pk=nid)
        neum.vehiculo = None
        neum.montado = False
        neum.estado = estado_almacen
        neum.save(update_fields=["vehiculo", "montado", "estado"])
        AlmacenNeumaticos.objects.get_or_create(idNeumatico=neum)
        moved += 1
    return moved

@transaction.atomic
def montar_en_vehiculo(neumatico_ids: list[int], vehiculo_id: int,
                       eje: int | None, pos: int | None,
                       auto_asignar: bool) -> int:
    vehiculo = get_object_or_404(Vehiculo, pk=vehiculo_id)
    estado_montado = _get_estado("Montado")

    nro_destino = None
    if not auto_asignar:
        if eje is None or pos is None:
            raise ValueError("Debés indicar eje y posición.")
        if eje < 1 or eje > vehiculo.ejes:
            raise ValueError("Eje destino fuera de rango.")
        if pos < 1 or pos > POSICIONES_POR_EJE:
            raise ValueError("Posición destino fuera de rango.")
        nro_destino = pos_to_nro(eje, pos)

    moved = 0
    for nid in neumatico_ids:
        neum = get_object_or_404(Neumatico, pk=nid)

        if nro_destino is not None:
            # Si la posición está ocupada, enviar el existente a almacén
            ocupado = (Neumatico.objects.select_for_update()
                       .filter(vehiculo=vehiculo, nroNeumatico=nro_destino, montado=True)
                       .first())
            if ocupado and ocupado.id != neum.id:
                ocupado.vehiculo = None
                ocupado.montado = False
                ocupado.estado = _get_estado("Almacén")
                ocupado.save(update_fields=["vehiculo", "montado", "estado"])
                AlmacenNeumaticos.objects.get_or_create(idNeumatico=ocupado)
            neum.nroNeumatico = nro_destino
        else:
            # Autoasignación: primer hueco libre dentro de ejes * POSICIONES_POR_EJE
            usados = set(Neumatico.objects
                         .filter(vehiculo=vehiculo, montado=True)
                         .values_list("nroNeumatico", flat=True))
            max_nro = vehiculo.ejes * POSICIONES_POR_EJE
            nro_libre = next((c for c in range(1, max_nro + 1) if c not in usados), None)
            neum.nroNeumatico = nro_libre if nro_libre is not None else (max(usados) + 1 if usados else 1)

        # Montar
        neum.vehiculo = vehiculo
        neum.montado = True
        neum.estado = estado_montado

        # Si el tipo es "Nuevo", reiniciar km al montar
        if _tipo_str(neum) == "nuevo":
            neum.km = 0

        neum.save(update_fields=["vehiculo", "montado", "estado", "nroNeumatico", "km"])

        # Eliminar registro de almacén si estaba
        AlmacenNeumaticos.objects.filter(idNeumatico=neum).delete()
        moved += 1

    return moved

# ---- Acumulación de KM a partir de viajes ----

def _km_int(value) -> int:
    """Convierte Decimal/float/int a entero con redondeo clásico (0.5 → 1)."""
    if value is None:
        return 0
    d = Decimal(value)
    return int(d.quantize(Decimal("1"), rounding=ROUND_HALF_UP))

def acumular_km_vehiculo(vehiculo_id: int, delta_km) -> int:
    """
    Suma (o resta) delta_km a todos los neumáticos montados del vehículo.
    Nunca baja de 0. Devuelve la cantidad de neumáticos actualizados.
    """
    delta = _km_int(delta_km)
    if delta == 0 or vehiculo_id is None:
        return 0
    qs = Neumatico.objects.filter(vehiculo_id=vehiculo_id, montado=True)
    return qs.update(km=Greatest(Value(0), F("km") + Value(delta, output_field=IntegerField())))
