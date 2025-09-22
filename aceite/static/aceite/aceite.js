// static/aceite/aceite.js

// Función para decidir colores según % consumido
function coloresPorcentaje(usados, max) {
    const pct = (usados / max) * 100;
    if (pct <= 60) return ["#198754", "#E9ECEF"];      // verde
    if (pct <= 85) return ["#FFC107", "#E9ECEF"];      // amarillo
    return ["#DC3545", "#E9ECEF"];                     // rojo
}

function renderDoughnutChart(canvasId) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) return;

    const usados = parseFloat(canvas.dataset.usados);
    const restantes = parseFloat(canvas.dataset.restantes);
    const max = parseFloat(canvas.dataset.max);

    const ctx = canvas.getContext("2d");
    const colors = coloresPorcentaje(usados, max);

    new Chart(ctx, {
        type: "doughnut",
        data: {
            labels: ["Usados", "Restantes"],
            datasets: [{
                data: [usados, restantes],
                backgroundColor: colors,
                hoverOffset: 8
            }]
        },
        options: {
            cutout: "65%",
            plugins: { legend: { position: "bottom" } }
        }
    });
}

// Renderizar ambos gráficos
document.addEventListener("DOMContentLoaded", () => {
    renderDoughnutChart("chartMotor");
    renderDoughnutChart("chartCaja");
});
