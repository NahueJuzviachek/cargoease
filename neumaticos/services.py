# neumaticos/services.py
from decimal import Decimal, ROUND_HALF_UP

from django.db import transaction
from django.db.models import F, Value, IntegerField
from django.db.models.functions import Greatest
from django.shortcuts import get_object_or_404

from vehiculos.models import Vehiculo
from .models import Neumatico, AlmacenNeumaticos, EstadoNeumatico, TipoNeumatico
from .constants import POSICIONES_POR_EJE, KM_UMBRAL_USADO
from .utils import pos_to_nro


# ---------------- Helpers ----------------

def _tipo_str(neum: Neumatico) -> str:
    """Devuelve 'nuevo'/'recapado'/'usado' (lower) o ''."""
    return (getattr(getattr(neum, "tipo", None), "descripcion", "") or "").strip().lower()

def _get_estado(nombre: str) -> EstadoNeumatico:
    """Busca estado por descripción (case-insensitive)."""
    return EstadoNeumatico.objects.get(descripcion__iexact=nombre)

def _get_tipo_from_slug(slug: str | None) -> TipoNeumatico | None:
    """Mapea 'nuevo'/'recapado'/'usado' a TipoNeumatico."""
    if not slug:
        return None
    mapping = {"nuevo": "Nuevo", "recapado": "Recapado", "usado": "Usado"}
    desc = mapping.get(slug.lower())
    if not desc:
        return None
    return TipoNeumatico.objects.get(descripcion__iexact=desc)

def _km_int(value) -> int:
    """Convierte Decimal/float/int a entero con redondeo clásico (0.5 → 1)."""
    if value is None:
        return 0
    d = Decimal(value)
    return int(d.quantize(Decimal("1"), rounding=ROUND_HALF_UP))


# ---------------- Acciones de almacén / montaje ----------------

@transaction.atomic
def enviar_a_almacen(neumatico_ids: list[int], tipo_slug: str | None = None) -> int:
    """
    Mueve neumáticos al almacén. Si se pasa tipo_slug:
      - asigna ese tipo; si es 'nuevo' resetea km a 0.
    """
    estado_almacen = _get_estado("Almacén")
    tipo = _get_tipo_from_slug(tipo_slug)
    moved = 0
    for nid in neumatico_ids:
        neum = get_object_or_404(Neumatico, pk=nid)
        if tipo:
            neum.tipo = tipo
            if tipo_slug == "nuevo":
                neum.km = 0
        neum.vehiculo = None
        neum.montado = False
        neum.estado = estado_almacen
        neum.nroNeumatico = 0
        neum.save(update_fields=["vehiculo", "montado", "estado", "tipo", "km", "nroNeumatico"])
        AlmacenNeumaticos.objects.get_or_create(idNeumatico=neum)
        moved += 1
    return moved


@transaction.atomic
def montar_en_vehiculo(
    neumatico_ids: list[int],
    vehiculo_id: int,
    eje: int | None,
    pos: int | None,
    auto_asignar: bool,
    tipo_slug: str | None = None,
) -> int:
    """
    Monta neumáticos en un vehículo. Si la posición está ocupada, el anterior va a almacén.
    Si se define tipo_slug: cambia condición; si es 'nuevo', km -> 0.
    """
    vehiculo = get_object_or_404(Vehiculo, pk=vehiculo_id)
    estado_montado = _get_estado("Montado")
    tipo = _get_tipo_from_slug(tipo_slug)

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

        # Resolver posición
        if nro_destino is not None:
            # Si hay otro montado en el mismo lugar, bajarlo primero
            ocupado = (
                Neumatico.objects.select_for_update()
                .filter(vehiculo=vehiculo, nroNeumatico=nro_destino, montado=True)
                .first()
            )
            if ocupado and ocupado.pk != neum.pk:
                ocupado.vehiculo = None
                ocupado.montado = False
                ocupado.estado = _get_estado("Almacén")
                ocupado.nroNeumatico = 0
                ocupado.save(update_fields=["vehiculo", "montado", "estado", "nroNeumatico"])
                AlmacenNeumaticos.objects.get_or_create(idNeumatico=ocupado)
            neum.nroNeumatico = nro_destino
        else:
            # Autoasignar primer número libre (1..ejes*POSICIONES_POR_EJE)
            usados = set(
                Neumatico.objects.filter(vehiculo=vehiculo, montado=True).values_list("nroNeumatico", flat=True)
            )
            max_nro = vehiculo.ejes * POSICIONES_POR_EJE
            nro_libre = next((c for c in range(1, max_nro + 1) if c not in usados), None)
            neum.nroNeumatico = nro_libre if nro_libre is not None else (max(usados) + 1 if usados else 1)

        # Aplicar condición elegida
        if tipo:
            neum.tipo = tipo
            if tipo_slug == "nuevo":
                neum.km = 0

        # Montar
        neum.vehiculo = vehiculo
        neum.montado = True
        neum.estado = estado_montado

        # Si no eligió condición y ya era "nuevo", al montar reseteamos km
        if not tipo and _tipo_str(neum) == "nuevo":
            neum.km = 0

        neum.save(update_fields=["vehiculo", "montado", "estado", "nroNeumatico", "km", "tipo"])
        # Quitar del almacén si estaba
        AlmacenNeumaticos.objects.filter(idNeumatico=neum).delete()
        moved += 1

    return moved


@transaction.atomic
def crear_neumatico_en_almacen(tipo_slug: str) -> Neumatico:
    """
    Crea un neumático en almacén con la condición elegida (Nuevo/Recapado/Usado).
    Km inicial = 0.
    """
    estado_almacen = _get_estado("Almacén")
    tipo = _get_tipo_from_slug(tipo_slug) or _get_tipo_from_slug("nuevo")

    neum = Neumatico.objects.create(
        vehiculo=None,
        estado=estado_almacen,
        tipo=tipo,
        nroNeumatico=0,   # en almacén no tiene posición
        montado=False,
        km=0,
    )
    AlmacenNeumaticos.objects.get_or_create(idNeumatico=neum)
    return neum


@transaction.atomic
def eliminar_neumaticos_del_almacen(ids: list[int]) -> int:
    """Elimina solo neumáticos que están en almacén (vehiculo=None y montado=False)."""
    qs = Neumatico.objects.filter(pk__in=ids, vehiculo__isnull=True, montado=False)
    deleted_count, _ = qs.delete()
    return deleted_count


@transaction.atomic
def recapar_neumaticos(ids: list[int]) -> int:
    """Cambia condición a 'Recapado' y resetea km a 0."""
    tipo_recap = _get_tipo_from_slug("recapado")
    updated = 0
    for nid in ids:
        neum = get_object_or_404(Neumatico, pk=nid)
        neum.tipo = tipo_recap
        neum.km = 0
        neum.save(update_fields=["tipo", "km"])
        updated += 1
    return updated


# ---------------- Kilometraje (usado por signals.py) ----------------

@transaction.atomic
def acumular_km_vehiculo(vehiculo_id: int, delta_km) -> int:
    """
    Suma (o resta) delta_km a todos los neumáticos montados del vehículo.
    - Nunca baja de 0.
    - Si km >= KM_UMBRAL_USADO => condición pasa a 'Usado'.
    Devuelve la cantidad de neumáticos actualizados.
    """
    if vehiculo_id is None:
        return 0
    delta = _km_int(delta_km)
    if delta == 0:
        return 0

    qs = Neumatico.objects.select_for_update().filter(vehiculo_id=vehiculo_id, montado=True)
    updated = qs.update(km=Greatest(Value(0), F("km") + Value(delta, output_field=IntegerField())))

    # Marcar 'Usado' cuando km supera umbral
    tipo_usado = _get_tipo_from_slug("usado")
    qs.filter(km__gte=KM_UMBRAL_USADO).exclude(tipo=tipo_usado).update(tipo=tipo_usado)
    return updated


# ---------------- Reubicación (swap de 2 neumáticos, seguro con UNIQUE) ----------------

@transaction.atomic
def reubicar_neumaticos(a_id: int, b_id: int) -> str:
    """
    Intercambia la ubicación de dos neumáticos cumpliendo la UNIQUE(vehiculo, nroNeumatico).
      - montado <-> montado: swap vehiculo y nroNeumatico (en 3 pasos).
      - montado <-> almacén: el de almacén toma la posición y el montado baja a almacén.
      - almacén <-> almacén: sin cambios.
    Si un neumático 'Nuevo' se monta, se resetea km a 0.
    """
    if a_id == b_id:
        raise ValueError("Seleccionaste el mismo neumático dos veces.")

    # Bloqueo consistente de ambos
    neums = list(Neumatico.objects.select_for_update().filter(pk__in=[a_id, b_id]))
    if len(neums) != 2:
        raise ValueError("No se encontraron ambos neumáticos.")

    # Conservar el orden de entrada a_id, b_id
    neums.sort(key=lambda n: 0 if n.pk == a_id else 1)
    a, b = neums[0], neums[1]

    estado_montado = _get_estado("Montado")
    estado_almacen = _get_estado("Almacén")

    def _tipo_is_nuevo(n: Neumatico) -> bool:
        return _tipo_str(n) == "nuevo"

    # --- Caso 1: montado <-> montado
    if a.montado and b.montado:
        a_veh_id, a_nro = a.vehiculo_id, a.nroNeumatico
        b_veh_id, b_nro = b.vehiculo_id, b.nroNeumatico

        # Paso 1: liberar lugar de 'a'
        Neumatico.objects.filter(pk=a.pk).update(vehiculo=None, montado=False, nroNeumatico=0)

        # Paso 2: mover 'b' al lugar de 'a'
        Neumatico.objects.filter(pk=b.pk).update(
            vehiculo_id=a_veh_id, nroNeumatico=a_nro, montado=True, estado=estado_montado
        )

        # Paso 3: mover 'a' al lugar de 'b'
        Neumatico.objects.filter(pk=a.pk).update(
            vehiculo_id=b_veh_id, nroNeumatico=b_nro, montado=True, estado=estado_montado
        )

        # No deberían existir en almacén, pero limpiamos por las dudas
        AlmacenNeumaticos.objects.filter(idNeumatico__in=[a, b]).delete()
        return f"Reubicados entre vehículos: #{a.pk} ↔ #{b.pk}"

    # --- Caso 2: montado (a) <-> almacén (b)
    if a.montado and not b.montado:
        a_veh_id, a_nro = a.vehiculo_id, a.nroNeumatico

        # Paso 1: liberar lugar (a baja primero)
        Neumatico.objects.filter(pk=a.pk).update(
            vehiculo=None, montado=False, nroNeumatico=0, estado=estado_almacen
        )

        # Paso 2: subir b a la posición liberada
        updates = dict(vehiculo_id=a_veh_id, nroNeumatico=a_nro, montado=True, estado=estado_montado)
        if _tipo_is_nuevo(b):
            updates["km"] = 0
        Neumatico.objects.filter(pk=b.pk).update(**updates)

        # Actualizar registros de almacén
        AlmacenNeumaticos.objects.get_or_create(idNeumatico=a)
        AlmacenNeumaticos.objects.filter(idNeumatico=b).delete()
        return f"Reubicado: #{b.pk} montado y #{a.pk} a almacén"

    # --- Caso 3: almacén (a) <-> montado (b)
    if not a.montado and b.montado:
        b_veh_id, b_nro = b.vehiculo_id, b.nroNeumatico

        # Paso 1: liberar lugar (b baja primero)
        Neumatico.objects.filter(pk=b.pk).update(
            vehiculo=None, montado=False, nroNeumatico=0, estado=estado_almacen
        )

        # Paso 2: subir a a la posición liberada
        updates = dict(vehiculo_id=b_veh_id, nroNeumatico=b_nro, montado=True, estado=estado_montado)
        if _tipo_is_nuevo(a):
            updates["km"] = 0
        Neumatico.objects.filter(pk=a.pk).update(**updates)

        # Actualizar registros de almacén
        AlmacenNeumaticos.objects.get_or_create(idNeumatico=b)
        AlmacenNeumaticos.objects.filter(idNeumatico=a).delete()
        return f"Reubicado: #{a.pk} montado y #{b.pk} a almacén"

    # --- Caso 4: ambos en almacén
    return "Ambos neumáticos ya están en almacén (no hay cambios)."
