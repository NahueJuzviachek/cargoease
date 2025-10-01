// static/aceite/aceite.js
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

// Elegimos un step para que el eje Y tenga más valores (ticks)
function niceStep(maxTarget) {
    const candidates = [500, 1000, 2000, 5000, 10000, 20000, 25000, 50000, 100000, 200000];
    for (let s of candidates) {
        // buscamos que el número de ticks no sea exagerado (≈6–8)
        if (maxTarget / s <= 8) return s;
    }
    // fallback: potencia de 10 inferior
    const p = Math.pow(10, Math.floor(Math.log10(maxTarget)) - 1);
    return Math.max(1000, p);
}

// Extiende el eje Y un 20% por encima del mayor valor (km actual o máximo del ciclo)
function extendedAxis(maxLimit, current) {
    const base = Math.max(Number(maxLimit) || 0, Number(current) || 0);
    const step = niceStep(base);
    const extended = base * 1.2; // 20% de “headroom”
    const maxAxis = Math.ceil(extended / step) * step;
    return { step, maxAxis };
}

function initAceiteCharts() {
    const motorCanvas = document.getElementById("chartMotor");
    const cajaCanvas = document.getElementById("chartCaja");

    // Datos desde el template (json_script)
    const kmMotor = readJSON("km_motor", 0);
    const kmCaja = readJSON("km_caja", 0);
    const maxMotor = readJSON("max_motor", 30000);   // Motor: 30.000
    const maxCaja = readJSON("max_caja", 100000);   // Caja: 100.000

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
                        max: yMaxMotor,                 // ⬅ más alto que el máximo del ciclo
                        ticks: { stepSize: stepMotor }  // ⬅ más valores (más marcas)
                    }
                }
            }
        });
    }

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
                        max: yMaxCaja,                 // ⬅ más alto que el máximo del ciclo
                        ticks: { stepSize: stepCaja }  // ⬅ más valores (más marcas)
                    }
                }
            }
        });
    }
}

document.addEventListener("DOMContentLoaded", initAceiteCharts);
