// static/viajes/viajes_map.js
document.addEventListener("DOMContentLoaded", () => {
    const map = L.map("map").setView([-34.6037, -58.3816], 5);
    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
        attribution: "© OpenStreetMap contributors", maxZoom: 19
    }).addTo(map);

    const meta = document.getElementById("route-meta");
    const distanciaInput = document.getElementById("id_distancia");

    // Selects de tu form
    const sPais = document.getElementById("id_salida_pais");
    const sProv = document.getElementById("id_salida_provincia");
    const sLoc = document.getElementById("id_salida_localidad");
    const dPais = document.getElementById("id_destino_pais");
    const dProv = document.getElementById("id_destino_provincia");
    const dLoc = document.getElementById("id_destino_localidad");

    let rutaLayers = [];

    function selectedText(sel) { if (!sel || sel.selectedIndex < 0) return ""; return sel.options[sel.selectedIndex].text.trim(); }
    function buildQuery(locSel, provSel, paisSel) {
        return [selectedText(locSel), selectedText(provSel), selectedText(paisSel)].filter(Boolean).join(", ");
    }

    async function geocode(place) {
        const url = `https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(place)}`;
        const res = await fetch(url, { headers: { "Accept-Language": "es", "User-Agent": "CargoEase/1.0", "Referer": location.origin } });
        if (!res.ok) return null;
        const data = await res.json();
        if (!data || data.length === 0) return null;
        return [parseFloat(data[0].lat), parseFloat(data[0].lon)];
    }

    function clearRoutes() {
        rutaLayers.forEach(l => map.removeLayer(l));
        rutaLayers = [];
        if (meta) meta.textContent = "";
    }

    function formatKm(m) { return (m / 1000).toFixed(2); }
    function formatMin(s) { return Math.round(s / 60); }

    async function calcularRutaORS(coordOrigen, coordDestino) {
        const key = window.ORS_API_KEY || "";
        if (!key) {
            if (meta) meta.textContent = "Falta ORS_API_KEY. Configúrala en settings.py y pásala en el contexto.";
            return null;
        }
        const start = `${coordOrigen[1]},${coordOrigen[0]}`;
        const end = `${coordDestino[1]},${coordDestino[0]}`;
        const url = `https://api.openrouteservice.org/v2/directions/driving-car?api_key=${encodeURIComponent(key)}&start=${start}&end=${end}&alternative_routes[target_count]=3&alternative_routes[share_factor]=0.6`;

        const res = await fetch(url);
        if (!res.ok) return null;
        const data = await res.json();
        if (!data || !data.features) return null;
        return data.features; // rutas alternativas
    }

    function dibujarRutas(rutas) {
        clearRoutes();
        rutas.forEach((ruta, idx) => {
            const coords = ruta.geometry.coordinates.map(c => [c[1], c[0]]);
            const color = idx === 0 ? "blue" : "gray";
            const poly = L.polyline(coords, { color, weight: 4, opacity: 0.8 }).addTo(map);
            rutaLayers.push(poly);

            const seg = ruta.properties.segments?.[0];
            if (idx === 0) {
                map.fitBounds(poly.getBounds());
                if (seg) {
                    if (distanciaInput) distanciaInput.value = formatKm(seg.distance);
                    if (meta) meta.textContent = `Ruta principal → ${formatKm(seg.distance)} km · ${formatMin(seg.duration)} min`;
                }
            }

            poly.on("click", () => {
                rutaLayers.forEach(l => l.setStyle({ color: "gray" }));
                poly.setStyle({ color: "red" });
                if (seg) {
                    if (distanciaInput) distanciaInput.value = formatKm(seg.distance);
                    if (meta) meta.textContent = `Ruta seleccionada → ${formatKm(seg.distance)} km · ${formatMin(seg.duration)} min`;
                }
            });
        });
    }

    async function update() {
        const origenQ = buildQuery(sLoc, sProv, sPais);
        const destinoQ = buildQuery(dLoc, dProv, dPais);
        if (!origenQ || !destinoQ) { clearRoutes(); return; }

        if (meta) meta.textContent = "Calculando ruta...";
        try {
            const [coordOrigen, coordDestino] = await Promise.all([geocode(origenQ), geocode(destinoQ)]);
            if (!coordOrigen || !coordDestino) { clearRoutes(); if (meta) meta.textContent = "No se pudo geocodificar salida/destino."; return; }

            const rutas = await calcularRutaORS(coordOrigen, coordDestino);
            if (!rutas || rutas.length === 0) { clearRoutes(); if (meta) meta.textContent = "No se encontraron rutas."; return; }

            dibujarRutas(rutas);
        } catch (e) {
            clearRoutes();
            if (meta) meta.textContent = "Error calculando ruta (ver consola).";
            console.error(e);
        }
    }

    function debounce(fn, d = 600) { let t; return (...a) => { clearTimeout(t); t = setTimeout(() => fn(...a), d); }; }
    const deb = debounce(update, 600);

    [sPais, sProv, sLoc, dPais, dProv, dLoc].forEach(el => {
        if (!el) return;
        el.addEventListener("change", deb);
        el.addEventListener("keyup", deb);
    });

    // Intento inicial (modo edición)
    deb();
});
