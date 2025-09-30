// static/aceite/aceite.js
function readJSON(id, fallback = 0) {
    const el = document.getElementById(id);
    if (!el) return fallback;
    try {
        const val = JSON.parse(el.textContent);
        const num = Number(val);
        return Number.isFinite(num) ? num : fallback;
    } catch (e) {
        return fallback;
    }
}

function initAceiteCharts() {
    const motorCanvas = document.getElementById("chartMotor");
    const cajaCanvas = document.getElementById("chartCaja");

    // Datos desde el template (json_script)
    const kmMotor = readJSON("km_motor", 0);
    const kmCaja = readJSON("km_caja", 0);

    // Máximos fijos
    const maxMotor = readJSON("max_motor", 30000);
    const maxCaja = readJSON("max_caja", 100000);

    if (motorCanvas) {
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
                    y: { beginAtZero: true, max: maxMotor }
                }
            }
        });
    }

    if (cajaCanvas) {
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
                    y: { beginAtZero: true, max: maxCaja }
                }
            }
        });
    }
}

document.addEventListener("DOMContentLoaded", initAceiteCharts);
