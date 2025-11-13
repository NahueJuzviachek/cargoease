// static/aceite/aceite.js

/**
 * Lee y convierte a número el contenido JSON de un elemento HTML <script type="application/json">.
 * Devuelve un valor por defecto si el elemento no existe o el contenido no es válido.
 *
 * @param {string} id - ID del elemento <script> con JSON embebido.
 * @param {number} [fallback=0] - Valor devuelto si el contenido no es numérico o no se encuentra.
 * @returns {number} Valor numérico parseado o el valor por defecto.
 */
function readJSON(id, fallback = 0) {
    const el = document.getElementById(id);
    if (!el) return fallback;
    try {
        const val = JSON.parse(el.textContent);
        const num = Number(val);
        return Number.isFinite(num) ? num : fallback;
    } catch {
        return fallback;
    }
}

/**
 * Calcula un tamaño de paso (step) "agradable" para el eje Y de un gráfico.
 * Busca un balance entre legibilidad y número razonable de marcas (ticks).
 *
 * @param {number} maxTarget - Valor máximo esperado en el eje.
 * @returns {number} Tamaño de paso sugerido.
 */
function niceStep(maxTarget) {
    const candidates = [500, 1000, 2000, 5000, 10000, 20000, 25000, 50000, 100000, 200000];

    // Busca el primer step donde el eje tenga menos de ~8 divisiones
    for (let s of candidates) {
        if (maxTarget / s <= 8) return s;
    }

    // Si ninguno aplica, calcula una potencia de 10 inferior al máximo
    const p = Math.pow(10, Math.floor(Math.log10(maxTarget)) - 1);
    return Math.max(1000, p);
}

/**
 * Extiende el rango máximo del eje Y un 20% por encima del mayor valor actual.
 * Esto mejora la legibilidad de los gráficos y evita que las barras toquen el borde superior.
 *
 * @param {number} maxLimit - Valor máximo teórico (por ejemplo, vida útil del aceite).
 * @param {number} current - Valor actual acumulado (km recorridos).
 * @returns {{ step: number, maxAxis: number }} Objeto con step sugerido y nuevo valor máximo del eje.
 */
function extendedAxis(maxLimit, current) {
    const base = Math.max(Number(maxLimit) || 0, Number(current) || 0);
    const step = niceStep(base);
    const extended = base * 1.2; // agrega 20% de espacio libre visual
    const maxAxis = Math.ceil(extended / step) * step;
    return { step, maxAxis };
}

/**
 * Inicializa los gráficos de aceite de motor y caja usando Chart.js.
 * Los datos (km actuales y máximos) provienen de etiquetas <script type="application/json"> 
 * renderizadas en el template.
 */
function initAceiteCharts() {
    const motorCanvas = document.getElementById("chartMotor");
    const cajaCanvas = document.getElementById("chartCaja");

    // Datos inyectados desde el template Django (ver uso de json_script)
    const kmMotor = readJSON("km_motor", 0);
    const kmCaja = readJSON("km_caja", 0);
    const maxMotor = readJSON("max_motor", 30000);   // vida útil del aceite de motor (km)
    const maxCaja = readJSON("max_caja", 100000);   // vida útil del aceite de caja (km)

    // --- Gráfico de aceite de motor ---
    if (motorCanvas) {
        const { step: stepMotor, maxAxis: yMaxMotor } = extendedAxis(maxMotor, kmMotor);

        new Chart(motorCanvas, {
            type: "bar",
            data: {
                labels: ["Acumulado", "Restante"],
                datasets: [{
                    data: [kmMotor, Math.max(maxMotor - kmMotor, 0)]
                }]
            },
            options: {
                responsive: true,
                plugins: { legend: { display: false } },
                scales: {
                    y: {
                        beginAtZero: true,
                        max: yMaxMotor,
                        ticks: { stepSize: stepMotor }
                    }
                }
            }
        });
    }

    // --- Gráfico de aceite de caja ---
    if (cajaCanvas) {
        const { step: stepCaja, maxAxis: yMaxCaja } = extendedAxis(maxCaja, kmCaja);

        new Chart(cajaCanvas, {
            type: "bar",
            data: {
                labels: ["Acumulado", "Restante"],
                datasets: [{
                    data: [kmCaja, Math.max(maxCaja - kmCaja, 0)]
                }]
            },
            options: {
                responsive: true,
                plugins: { legend: { display: false } },
                scales: {
                    y: {
                        beginAtZero: true,
                        max: yMaxCaja,
                        ticks: { stepSize: stepCaja }
                    }
                }
            }
        });
    }
}

// Espera a que el DOM esté cargado antes de inicializar los gráficos
document.addEventListener("DOMContentLoaded", initAceiteCharts);
