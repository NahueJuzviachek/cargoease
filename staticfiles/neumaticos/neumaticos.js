(function () {
    // --------- Progressbars ----------
    const caps = { nuevo: 100000, recapado: 80000, usado: 50000 };
    const first = document.querySelector(".progress[data-cap-nuevo]");
    if (first) {
        caps.nuevo = parseInt(first.dataset.capNuevo || caps.nuevo, 10);
        caps.recapado = parseInt(first.dataset.capRecapado || caps.recapado, 10);
        caps.usado = parseInt(first.dataset.capUsado || caps.usado, 10);
    }

    const COLOR_CLASSES = ["bg-success", "bg-primary", "bg-warning", "bg-secondary"];
    const colorFor = (t) => {
        switch ((t || "").toLowerCase()) {
            case "nuevo": return "bg-success";
            case "recapado": return "bg-primary";
            case "usado": return "bg-warning";
            default: return "bg-secondary";
        }
    };

    document.querySelectorAll(".progress").forEach(p => {
        const km = parseInt(p.dataset.km || "0", 10);
        const tipo = (p.dataset.tipo || "").toLowerCase();
        const cap = caps[tipo] || caps.usado;
        const pct = Math.min(100, Math.round((km / cap) * 100));
        const bar = p.querySelector(".progress-bar");
        bar.style.width = pct + "%";
        COLOR_CLASSES.forEach(c => bar.classList.remove(c));
        bar.classList.add(colorFor(tipo));
        const lbl = bar.querySelector(".progress-label");
        if (lbl) lbl.textContent = pct + "%";
    });

    // --------- Selección (máximo 2) ----------
    const checks = document.querySelectorAll(".select-neum");
    const btnReubicar = document.getElementById("btnReubicar");
    const btnRecapar = document.getElementById("btnRecapar");
    const btnEliminarAlmacen = document.getElementById("btnEliminarAlmacen");

    const hiddenSwap = document.getElementById("neumaticos_ids_swap");
    const hiddenRecapar = document.getElementById("neumaticos_ids_recapar");
    const hiddenEliminar = document.getElementById("neumaticos_ids_eliminar");

    function selectedIds() {
        const all = [];
        const almacen = [];
        checks.forEach(c => {
            if (c.checked) {
                all.push(c.value);
                if (c.dataset.scope === "almacen") almacen.push(c.value);
            }
        });
        return { all, almacen };
    }

    function refreshSelection() {
        const { all, almacen } = selectedIds();

        // Límite máx 2: si superó, desmarcar el último marcado
        if (all.length > 2) {
            const lastChecked = Array.from(checks).reverse().find(c => c.checked);
            if (lastChecked) lastChecked.checked = false;
            alert("Solo podés seleccionar hasta 2 neumáticos.");
            return refreshSelection();
        }

        if (btnReubicar) btnReubicar.disabled = (all.length !== 2);
        if (btnRecapar) btnRecapar.disabled = (all.length === 0);
        if (btnEliminarAlmacen) btnEliminarAlmacen.disabled = (almacen.length === 0);

        if (hiddenSwap) hiddenSwap.value = all.join(",");
        if (hiddenRecapar) hiddenRecapar.value = all.join(",");
        if (hiddenEliminar) hiddenEliminar.value = almacen.join(",");
    }

    checks.forEach(c => c.addEventListener("change", refreshSelection));
    refreshSelection();

    // --------- Confirmaciones (modal Bootstrap con fallback) ----------
    const modalEl = document.getElementById("confirmModal");
    const hasBootstrap = typeof window.bootstrap !== "undefined" && window.bootstrap.Modal;
    const modal = (hasBootstrap && modalEl) ? new bootstrap.Modal(modalEl) : null;
    const modalTitle = document.getElementById("confirmModalTitle");
    const modalBody = document.getElementById("confirmModalBody");
    const modalOk = document.getElementById("confirmModalOk");

    function hookConfirm(form) {
        if (!form) return;
        form.addEventListener("submit", function (e) {
            const msg = form.getAttribute("data-confirm") || "¿Confirmar acción?";
            const hidden = form.querySelector('input[type="hidden"]');
            if (hidden && (!hidden.value || hidden.value.trim() === "")) {
                e.preventDefault();
                return;
            }

            // Si NO hay modal de Bootstrap disponible -> fallback a confirm nativo
            if (!modal) {
                if (!window.confirm(msg)) {
                    e.preventDefault();
                }
                return; // si confirmó, deja que el submit siga
            }

            // Con modal elegante
            e.preventDefault();
            if (modalTitle) modalTitle.textContent = "Confirmar acción";
            if (modalBody) modalBody.textContent = msg;
            modalOk.onclick = () => { form.submit(); };
            modal.show();
        });
    }

    hookConfirm(document.getElementById("formReubicar"));
    hookConfirm(document.getElementById("formRecapar"));
    hookConfirm(document.getElementById("formEliminarAlmacen"));
})();
