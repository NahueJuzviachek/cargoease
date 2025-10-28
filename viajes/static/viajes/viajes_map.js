// static/viajes/viajes_map.js
(function () {
    // --- Configuración principal ---
    const PROFILE = 'driving-hgv';   // Siempre usamos perfil camión pesado (HGV)
    const ALT_MAX_KM = 100;          // Hasta este km intentamos rutas alternativas
    const LEG_MAX_KM = 90;           // Tamaño máximo de cada tramo si necesitamos waypoints

    // --- DOM shortcuts ---
    const $ = (id) => document.getElementById(id);
    const mapEl = $('map');              // div donde se renderiza el mapa
    const meta = $('route-meta');        // div donde mostramos info de ruta
    const distanciaInput = $('id_distancia'); // input de distancia del form
    const sLoc = $('id_salida_localidad');   // select salida
    const dLoc = $('id_destino_localidad');  // select destino

    if (!mapEl || !window.L) return; // Si no hay mapa o Leaflet, salimos

    // --- Inicialización Leaflet ---
    const map = L.map('map').setView([-34.6037, -58.3816], 5); // default ARG
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors', maxZoom: 19
    }).addTo(map);

    // Fix tamaño mapa tras render
    setTimeout(() => { try { map.invalidateSize(true); } catch (_) { } }, 120);

    let polylines = []; // líneas dibujadas
    let markers = [];   // marcadores de inicio/fin

    // --- Utils ---
    function formatKm(m) { return (m / 1000).toFixed(2); }
    function formatMin(s) { return Math.round(s / 60); }
    function isNumber(n) { return typeof n === 'number' && isFinite(n); }

    // Limpiar rutas y marcadores
    function clearRoutes() {
        polylines.forEach(pl => map.removeLayer(pl));
        markers.forEach(mk => map.removeLayer(mk));
        polylines = [];
        markers = [];
        if (meta) meta.textContent = '';
    }

    function addMarker(lat, lng, label) {
        const mk = L.marker([lat, lng], { title: label || '' }).addTo(map);
        markers.push(mk);
        return mk;
    }

    // Haversine para distancia aproximada entre dos coordenadas
    function haversineMeters([lat1, lng1], [lat2, lng2]) {
        const R = 6371000, toRad = d => d * Math.PI / 180;
        const dLat = toRad(lat2 - lat1), dLng = toRad(lng2 - lng1);
        const a = Math.sin(dLat / 2) ** 2 + Math.cos(toRad(lat1)) * Math.cos(toRad(lat2)) * Math.sin(dLng / 2) ** 2;
        return 2 * R * Math.asin(Math.sqrt(a));
    }

    // Segmentar línea larga en varios waypoints
    function segmentizeByDistance(start, end, maxKm = LEG_MAX_KM) {
        const totalM = haversineMeters(start, end);
        const maxM = maxKm * 1000;
        const nSegments = Math.max(1, Math.ceil(totalM / maxM));
        if (nSegments === 1) return [start, end];

        const pts = [];
        for (let i = 0; i <= nSegments; i++) {
            const t = i / nSegments;
            const lat = start[0] + (end[0] - start[0]) * t;
            const lng = start[1] + (end[1] - start[1]) * t;
            pts.push([lat, lng]);
        }
        return pts;
    }

    // Validar coordenadas
    function looksLikeLatLng(lat, lng) {
        return isNumber(lat) && isNumber(lng) && lat >= -90 && lat <= 90 && lng >= -180 && lng <= 180;
    }
    function normalizeCoords([lat, lng]) {
        if (!looksLikeLatLng(lat, lng)) return null;
        if (Math.abs(lat) > 90 || Math.abs(lng) > 180) return [lng, lat]; // swap si está mal
        return [lat, lng];
    }

    // Obtener coords desde backend
    async function localidadCoords(localidadId) {
        if (!localidadId || !window.URL_LOCALIDAD_COORDS) return null;
        try {
            const res = await fetch(`${window.URL_LOCALIDAD_COORDS}?localidad=${encodeURIComponent(localidadId)}`);
            if (!res.ok) return null;
            const data = await res.json();
            const raw = [data.lat, data.lng];
            if (!isNumber(raw[0]) || !isNumber(raw[1])) return null;
            return normalizeCoords(raw);
        } catch { return null; }
    }

    // Helpers ORS
    function coordsLngLat(a, b) { return [[a[1], a[0]], [b[1], b[0]]]; }
    function toLngLatList(latlngList) { return latlngList.map(([lat, lng]) => [lng, lat]); }

    function getDistDur(ruta) {
        const sum = ruta?.properties?.summary;
        if (sum && (isNumber(sum.distance) || isNumber(sum.duration))) {
            return { distance: sum.distance ?? null, duration: sum.duration ?? null };
        }
        const segs = ruta?.properties?.segments;
        if (Array.isArray(segs) && segs.length) {
            const distance = segs.reduce((acc, s) => acc + (s?.distance || 0), 0);
            const duration = segs.reduce((acc, s) => acc + (s?.duration || 0), 0);
            return { distance, duration };
        }
        return { distance: null, duration: null };
    }

    // --- ORS requests ---
    // 1) Corto con alternativas
    async function orsHgvAlternativas(a, b) { /* ... lógica fetch con alternativas ... */ }

    // 2) Simple HGV (sin alternativas)
    async function orsHgvSimple(a, b) { /* ... lógica fetch simple ... */ }

    // 3) Multi-waypoint HGV
    async function orsHgvMulti(latlngList) { /* ... lógica fetch multi ... */ }

    // --- Dibujo rutas ---
    function dibujarFeatures(rutas) {
        rutas.forEach((ruta, idx) => {
            const coords = ruta.geometry.coordinates.map(c => [c[1], c[0]]);
            const color = idx === 0 ? 'blue' : 'gray';

            const poly = L.polyline(coords, { color, weight: 4, opacity: 0.9 }).addTo(map);
            polylines.push(poly);

            if (idx === 0) {
                map.fitBounds(poly.getBounds(), { padding: [20, 20] });
                const { distance, duration } = getDistDur(ruta);
                if (isNumber(distance)) distanciaInput && (distanciaInput.value = formatKm(distance));
                if (meta) {
                    meta.textContent = isNumber(duration) ?
                        `Ruta principal (HGV) → ${formatKm(distance)} km · ${formatMin(duration)} min` :
                        `Ruta principal (HGV) → ${formatKm(distance)} km`;
                }
            }

            poly.on('click', () => {
                polylines.forEach(l => l.setStyle({ color: 'gray' }));
                poly.setStyle({ color: 'red' });
                const { distance, duration } = getDistDur(ruta);
                if (isNumber(distance)) distanciaInput && (distanciaInput.value = formatKm(distance));
                if (meta) {
                    meta.textContent = isNumber(duration) ?
                        `Ruta seleccionada (HGV) → ${formatKm(distance)} km · ${formatMin(duration)} min` :
                        `Ruta seleccionada (HGV) → ${formatKm(distance)} km`;
                }
            });
        });

        if (rutas.length === 1 && meta) {
            meta.textContent += ' · Sin alternativas para este tramo (HGV)';
        }
    }

    // --- Update principal ---
    async function update() {
        const salidaId = sLoc?.value;
        const destinoId = dLoc?.value;
        if (!salidaId || !destinoId) { clearRoutes(); return; }

        meta && (meta.textContent = 'Calculando ruta (HGV)...');
        try {
            const [a, b] = await Promise.all([localidadCoords(salidaId), localidadCoords(destinoId)]);
            if (!a || !b) { clearRoutes(); meta && (meta.textContent = 'No se pudieron obtener coordenadas.'); return; }

            clearRoutes();
            addMarker(a[0], a[1], 'Salida');
            addMarker(b[0], b[1], 'Destino');

            const approxKm = haversineMeters(a, b) / 1000;

            if (approxKm <= ALT_MAX_KM) {
                let rutas = await orsHgvAlternativas(a, b);
                if (rutas?.length) { dibujarFeatures(rutas); return; }
                rutas = await orsHgvSimple(a, b);
                if (rutas?.length) { dibujarFeatures(rutas); return; }
                rutas = await orsHgvMulti(segmentizeByDistance(a, b, LEG_MAX_KM));
                if (rutas?.length) { dibujarFeatures(rutas); return; }
                meta && (meta.textContent = 'No se pudo obtener la ruta por carretera (HGV) para este tramo corto.');
                return;
            }

            // tramo largo
            let rutas = await orsHgvSimple(a, b);
            if (rutas?.length) { dibujarFeatures(rutas); return; }

            rutas = await orsHgvMulti(segmentizeByDistance(a, b, LEG_MAX_KM));
            if (rutas?.length) { dibujarFeatures(rutas); return; }

            meta && (meta.textContent = 'No se pudo obtener la ruta por carretera (HGV) para este tramo largo.');
        } catch (e) {
            clearRoutes();
            meta && (meta.textContent = 'Error calculando ruta (ver consola).');
            console.error(e);
        }
    }

    // --- Eventos ---
    sLoc?.addEventListener('change', update);
    dLoc?.addEventListener('change', update);

    // --- Inicialización ---
    update();
})();
