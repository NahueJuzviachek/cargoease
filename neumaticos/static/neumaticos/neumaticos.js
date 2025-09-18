(function () {
    // Topes por tipo (valores por defecto)
    const caps = {
        nuevo: 100000,
        recapado: 80000,
        usado: 50000,
    };

    // Si la vista envía caps_por_tipo en data-attributes, sobreescribir
    const first = document.querySelector(".progress[data-cap-nuevo]");
    if (first) {
        caps.nuevo = parseInt(first.dataset.capNuevo || caps.nuevo, 10);
        caps.recapado = parseInt(first.dataset.capRecapado || caps.recapado, 10);
        caps.usado = parseInt(first.dataset.capUsado || caps.usado, 10);
    }

    // Función para elegir color según tipo
    const colorFor = (tipo) => {
        switch ((tipo || "").toLowerCase()) {
            case "nuevo":
                return "bg-success";
            case "recapado":
                return "bg-primary";
            case "usado":
                return "bg-warning";
            default:
                return "bg-secondary";
        }
    };

    // Renderizar progressbars
    document.querySelectorAll(".progress").forEach((p) => {
        const km = parseInt(p.dataset.km || "0", 10);
        const tipo = (p.dataset.tipo || "").toLowerCase();
        const cap = caps[tipo] || caps.usado;
        const pct = Math.min(100, Math.round((km / cap) * 100));

        const bar = p.querySelector(".progress-bar");
        bar.style.width = pct + "%";
        bar.classList.add(colorFor(tipo));

        const lbl = bar.querySelector(".progress-label");
        if (lbl) lbl.textContent = pct + "%";
    });

    // Selección de neumáticos y habilitar modal
    const checks = document.querySelectorAll(".select-neum");
    const btn = document.getElementById("btnAbrirModal");
    const hidden = document.getElementById("neumaticos_ids");
    const destinoSelect = document.getElementById("destinoSelect");
    const grupoVehiculo = document.getElementById("grupoVehiculo");

    function refreshSelection() {
        const ids = Array.from(checks)
            .filter((c) => c.checked)
            .map((c) => c.value);
        btn.disabled = ids.length === 0;
        if (hidden) hidden.value = ids.join(",");
    }

    checks.forEach((c) => c.addEventListener("change", refreshSelection));
    refreshSelection();

    destinoSelect?.addEventListener("change", function () {
        const value = this.value || "";
        grupoVehiculo.classList.toggle("d-none", !value.startsWith("vehiculo:"));
    });
})();
