// viajes/static/viajes/viajes.js
(function () {
    // Selector rápido por CSS
    const $ = (sel) => document.querySelector(sel);

    // Obtener elemento de configuración con URLs y API keys
    const cfgEl = $("#viajes-config");
    if (!cfgEl) {
        console.error("[viajes.js] No se encontró #viajes-config en el DOM");
        return;
    }

    // Configuración extraída de data-* attributes
    const CFG = {
        orsKey: cfgEl.dataset.orsKey || "",
        urlLocalidadCoords: cfgEl.dataset.urlLocalidadCoords || "",
        urlClienteUbic: cfgEl.dataset.urlClienteUbic || "",
        urlCargarProvincias: cfgEl.dataset.urlCargarProvincias || "",
        urlCargarLocalidades: cfgEl.dataset.urlCargarLocalidades || "",
    };

    // Exponer variables globales para otros scripts que las requieran
    window.ORS_API_KEY = CFG.orsKey;
    window.URL_LOCALIDAD_COORDS = CFG.urlLocalidadCoords;
    window.URL_CLIENTE_UBIC = CFG.urlClienteUbic;

    // Advertencias si faltan configuraciones importantes
    if (!CFG.urlCargarProvincias) console.warn("[viajes.js] Falta data-url-cargar-provincias en #viajes-config");
    if (!CFG.urlCargarLocalidades) console.warn("[viajes.js] Falta data-url-cargar-localidades en #viajes-config");
    if (!CFG.urlClienteUbic) console.warn("[viajes.js] Falta data-url-cliente-ubic en #viajes-config");

    // Referencias a los selects de salida, destino y cliente
    const sPais = $("#id_salida_pais"),
        sProv = $("#id_salida_provincia"),
        sLoc = $("#id_salida_localidad");

    const dPais = $("#id_destino_pais"),
        dProv = $("#id_destino_provincia"),
        dLoc = $("#id_destino_localidad");

    const selCliente = $("#id_cliente");

    // Función para limpiar un select y dejar un placeholder
    function resetSelect(el, placeholder) {
        if (!el) return;
        el.innerHTML = "";
        const option = document.createElement("option");
        option.value = "";
        option.textContent = placeholder;
        el.appendChild(option);
    }

    // Función para cargar provincias según el país seleccionado
    async function cargarProvincias(paisId, selectProvincia, selectedId = null) {
        if (!paisId) {
            resetSelect(selectProvincia, "— Seleccionar provincia —");
            return;
        }
        try {
            const url = `${CFG.urlCargarProvincias}?pais=${paisId}`;
            const res = await fetch(url);
            if (!res.ok) {
                console.error("[viajes.js] Error al cargar provincias:", res.status, url);
                resetSelect(selectProvincia, "— Seleccionar provincia —");
                return;
            }
            const data = await res.json();
            resetSelect(selectProvincia, "— Seleccionar provincia —");
            data.forEach((p) => {
                const o = document.createElement("option");
                o.value = String(p.id);
                o.textContent = p.nombre;
                selectProvincia.appendChild(o);
            });
            if (selectedId != null) {
                selectProvincia.value = String(selectedId);
            }
        } catch (e) {
            console.error("[viajes.js] Excepción cargarProvincias:", e);
            resetSelect(selectProvincia, "— Seleccionar provincia —");
        }
    }

    // Función para cargar localidades según la provincia seleccionada
    async function cargarLocalidades(provId, selectLocalidad, selectedId = null) {
        if (!provId) {
            resetSelect(selectLocalidad, "— Seleccionar localidad —");
            return;
        }
        try {
            const url = `${CFG.urlCargarLocalidades}?provincia=${provId}`;
            const res = await fetch(url);
            if (!res.ok) {
                console.error("[viajes.js] Error al cargar localidades:", res.status, url);
                resetSelect(selectLocalidad, "— Seleccionar localidad —");
                return;
            }
            const data = await res.json();
            resetSelect(selectLocalidad, "— Seleccionar localidad —");
            data.forEach((l) => {
                const o = document.createElement("option");
                o.value = String(l.id);
                o.textContent = l.nombre;
                selectLocalidad.appendChild(o);
            });
            if (selectedId != null) {
                selectLocalidad.value = String(selectedId);
            }
        } catch (e) {
            console.error("[viajes.js] Excepción cargarLocalidades:", e);
            resetSelect(selectLocalidad, "— Seleccionar localidad —");
        }
    }

    // Eventos para la cascada de selects de salida
    sPais?.addEventListener("change", async function () {
        await cargarProvincias(this.value, sProv);
        resetSelect(sLoc, "— Seleccionar localidad —");
    });
    sProv?.addEventListener("change", async function () {
        await cargarLocalidades(this.value, sLoc);
    });

    // Eventos para la cascada de selects de destino
    dPais?.addEventListener("change", async function () {
        await cargarProvincias(this.value, dProv);
        resetSelect(dLoc, "— Seleccionar localidad —");
    });
    dProv?.addEventListener("change", async function () {
        await cargarLocalidades(this.value, dLoc);
    });

    // Autocompletar destino según la ubicación del cliente seleccionado
    selCliente?.addEventListener("change", async function () {
        const id = this.value;
        if (!id) return;

        try {
            const url = `${CFG.urlClienteUbic}?cliente=${id}`;
            const res = await fetch(url);
            if (!res.ok) {
                console.warn("[viajes.js] Cliente sin ubicación o error:", res.status);
                return;
            }

            const { pais_id, provincia_id, localidad_id } = await res.json();
            if (!pais_id || !provincia_id || !localidad_id) {
                console.warn("[viajes.js] Ubicación incompleta en el cliente");
                return;
            }

            // Asignar país de destino
            dPais.value = String(pais_id);

            // Cargar provincias y preseleccionar
            await cargarProvincias(pais_id, dProv, provincia_id);

            // Cargar localidades y preseleccionar
            await cargarLocalidades(provincia_id, dLoc, localidad_id);

            // Nota: no se dispara 'change' de dPais/dProv para no sobrescribir manualmente seleccionado
        } catch (e) {
            console.error("[viajes.js] Error cargando ubicación del cliente:", e);
        }
    });

    // Si el form carga con cliente seleccionado y destino vacío, autocompletar
    document.addEventListener("DOMContentLoaded", () => {
        const destinoVacio = !dPais?.value && !dProv?.value && !dLoc?.value;
        if (selCliente?.value && destinoVacio) {
            selCliente.dispatchEvent(new Event("change"));
        }
    });
})();
