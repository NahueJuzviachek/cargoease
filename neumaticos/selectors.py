# neumaticos/selectors.py
from vehiculos.models import Vehiculo
from .models import Neumatico

def listar_vehiculos_con_neumaticos():
    return (Vehiculo.objects
            .order_by("id")
            .prefetch_related("neumaticos__tipo", "neumaticos__estado"))

def listar_almacen():
    # En almacén = sin vehículo asignado
    return (Neumatico.objects
            .select_related("tipo")
            .filter(vehiculo__isnull=True)
            .order_by("idNeumatico"))

def mapear_neumaticos_por_eje(vehiculos, nro_to_pos):
    """
    Devuelve: { veh_id: { 'ejes': v.ejes, 'por_eje': [(eje, [neums]), ...] } }
    Sólo incluye neumáticos montados del vehículo.
    """
    mapa = {}
    for v in vehiculos:
        montados = (v.neumaticos
                    .select_related("tipo")
                    .filter(montado=True)
                    .order_by("nroNeumatico"))

        ejes = {}
        for n in montados:
            eje, _ = nro_to_pos(n.nroNeumatico or 1)
            ejes.setdefault(eje, []).append(n)

        por_eje = [(e, sorted(lst, key=lambda x: x.nroNeumatico or 0))
                   for e, lst in sorted(ejes.items())]
        mapa[v.id] = {"ejes": v.ejes, "por_eje": por_eje}
    return mapa
