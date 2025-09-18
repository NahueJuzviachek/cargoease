# neumaticos/utils.py
from .constants import POSICIONES_POR_EJE

def pos_to_nro(eje: int, posicion: int) -> int:
    """Convierte (eje, posición) al nroNeumatico absoluto."""
    return (int(eje) - 1) * POSICIONES_POR_EJE + int(posicion)

def nro_to_pos(nro: int) -> tuple[int, int]:
    """Convierte nroNeumatico absoluto a (eje, posición)."""
    nro = int(nro)
    eje = (nro - 1) // POSICIONES_POR_EJE + 1
    pos = (nro - 1) % POSICIONES_POR_EJE + 1
    return eje, pos
