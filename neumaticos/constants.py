# neumaticos/constants.py
POSICIONES_POR_EJE = 4  # 4 neumáticos por eje

# Topes para la UI (progressbar)
CAPS_POR_TIPO = {
    "nuevo": 100000,
    "recapado": 80000,
    "usado": 50000,
}

# Umbral para cambiar condición automáticamente a "Usado"
KM_UMBRAL_USADO = 2000
