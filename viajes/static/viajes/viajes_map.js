// static/viajes/viajes_map.js
(function () {
    // --- Config ---
    const PROFILE = 'driving-hgv';   // SIEMPRE HGV
    const ALT_MAX_KM = 100;          // hasta aquí intentamos alternativas
    const LEG_MAX_KM = 90;           // tamaño de cada leg si necesitamos waypoints

    // --- DOM ---
    const $ = (id) => document.getElementById(id);
    const mapEl = $('map');
    const meta = $('route-meta');
    const distanciaInput = $('id_distancia');
    const sLoc = $('id_salida_localidad');
    const dLoc = $('id_destino_localidad');

    if (!mapEl || !window.L) return;

    // --- Mapa ---
    const map = L.map('map').setView([-34.6037, -58.3816], 5);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors', maxZoom: 19
    }).addTo(map);
    setTimeout(() => { try { map.invalidateSize(true); } catch (_) { } }, 120);

    let polylines = [];
    let markers = [];

    // --- Utils ---
    function formatKm(m) { return (m / 1000).toFixed(2); }
    function formatMin(s) { return Math.round(s / 60); }
    function isNumber(n) { return typeof n === 'number' && isFinite(n); }

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

    // Haversine (solo para estimar largo/corto y segmentar)
    function haversineMeters([lat1, lng1], [lat2, lng2]) {
        const R = 6371000, toRad = d => d * Math.PI / 180;
        const dLat = toRad(lat2 - lat1), dLng = toRad(lng2 - lng1);
        const a = Math.sin(dLat / 2) ** 2 + Math.cos(toRad(lat1)) * Math.cos(toRad(lat2)) * Math.sin(dLng / 2) ** 2;
        return 2 * R * Math.asin(Math.sqrt(a));
    }

    // Segmentación en puntos cada ~LEG_MAX_KM
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

    // Normalización coords backend
    function looksLikeLatLng(lat, lng) {
        return isNumber(lat) && isNumber(lng) && lat >= -90 && lat <= 90 && lng >= -180 && lng <= 180;
    }
    function normalizeCoords([lat, lng]) {
        if (!looksLikeLatLng(lat, lng)) return null;
        if (Math.abs(lat) > 90 || Math.abs(lng) > 180) return [lng, lat];
        return [lat, lng];
    }
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

    // ORS helpers
    function coordsLngLat(a, b) {
        return [
            [a[1], a[0]], // [lng, lat]
            [b[1], b[0]]
        ];
    }
    function toLngLatList(latlngList) {
        return latlngList.map(([lat, lng]) => [lng, lat]);
    }
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

    // 1) Cortas: HGV con alternativas (si 2004, devolvemos null)
    async function orsHgvAlternativas(a, b) {
        const key = window.ORS_API_KEY || '';
        if (!key) return null;

        const endpoint = `https://api.openrouteservice.org/v2/directions/${PROFILE}/geojson`;
        const baseBody = {
            coordinates: coordsLngLat(a, b),
            alternative_routes: { target_count: 3, share_factor: 0.5, weight_factor: 1.9 },
            instructions: false
        };

        // fastest
        let feats = [];
        const r1 = await fetch(endpoint, {
            method: 'POST',
            headers: { 'Authorization': key, 'Content-Type': 'application/json' },
            body: JSON.stringify(baseBody)
        });
        const raw1 = await r1.text();
        if (!r1.ok) {
            // Si code 2004 (límite 150 km o similar), devolvemos null para que el caller use simple/waypoints
            if (r1.status === 400 && raw1.includes('"code":2004')) return null;
            return null;
        }
        let d1; try { d1 = JSON.parse(raw1); } catch { return null; }
        feats = Array.isArray(d1.features) ? d1.features.slice(0) : [];
        if (feats.length >= 2) return feats;

        // shortest como posible alternativa
        const bodyShortest = { ...baseBody, preference: 'shortest' };
        const r2 = await fetch(endpoint, {
            method: 'POST',
            headers: { 'Authorization': key, 'Content-Type': 'application/json' },
            body: JSON.stringify(bodyShortest)
        });
        const raw2 = await r2.text();
        if (!r2.ok) return feats.length ? feats : null;

        let d2; try { d2 = JSON.parse(raw2); } catch { return feats.length ? feats : null; }
        const alt = d2 && Array.isArray(d2.features) ? d2.features[0] : null;
        if (!alt) return feats.length ? feats : null;

        const { distance: d0 } = getDistDur(feats[0]);
        const { distance: dAlt } = getDistDur(alt);
        const distinta = (isNumber(d0) && isNumber(dAlt)) ? (Math.abs(d0 - dAlt) / d0 > 0.03) : true;
        if (distinta) feats.push(alt);

        return feats.length ? feats : null;
    }

    // 2) Simple HGV (SIN alternativas)
    async function orsHgvSimple(a, b) {
        const key = window.ORS_API_KEY || '';
        if (!key) return null;

        const endpoint = `https://api.openrouteservice.org/v2/directions/${PROFILE}/geojson`;
        const body = { coordinates: coordsLngLat(a, b), instructions: false };

        const r = await fetch(endpoint, {
            method: 'POST',
            headers: { 'Authorization': key, 'Content-Type': 'application/json' },
            body: JSON.stringify(body)
        });
        const raw = await r.text();
        if (!r.ok) {
            // si acá igual viniera 2004 (raro sin alternativas), devolver null para intentar multi-waypoint
            return null;
        }
        let j; try { j = JSON.parse(raw); } catch { return null; }
        const feats = Array.isArray(j.features) ? j.features : [];
        return feats.length ? feats : null;
    }

    // 3) HGV Multi-waypoint (1 sola request, pasando por puntos intermedios)
    async function orsHgvMulti(latlngList) {
        const key = window.ORS_API_KEY || '';
        if (!key) return null;

        if (!Array.isArray(latlngList) || latlngList.length < 2) return null;

        const endpoint = `https://api.openrouteservice.org/v2/directions/${PROFILE}/geojson`;
        const coords = toLngLatList(latlngList);
        const body = { coordinates: coords, instructions: false };

        const r = await fetch(endpoint, {
            method: 'POST',
            headers: { 'Authorization': key, 'Content-Type': 'application/json' },
            body: JSON.stringify(body)
        });
        const raw = await r.text();
        if (!r.ok) {
            return null;
        }
        let j; try { j = JSON.parse(raw); } catch { return null; }
        const feats = Array.isArray(j.features) ? j.features : [];
        return feats.length ? feats : null;
    }

    // --- Dibujo ---
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
                    if (isNumber(distance) && isNumber(duration)) {
                        meta.textContent = `Ruta principal (HGV) → ${formatKm(distance)} km · ${formatMin(duration)} min`;
                    } else if (isNumber(distance)) {
                        meta.textContent = `Ruta principal (HGV) → ${formatKm(distance)} km`;
                    } else {
                        meta.textContent = 'Ruta principal (HGV) cargada';
                    }
                }
            }

            poly.on('click', () => {
                polylines.forEach(l => l.setStyle({ color: 'gray' }));
                poly.setStyle({ color: 'red' });
                const { distance, duration } = getDistDur(ruta);
                if (isNumber(distance)) distanciaInput && (distanciaInput.value = formatKm(distance));
                if (meta) {
                    if (isNumber(distance) && isNumber(duration)) {
                        meta.textContent = `Ruta seleccionada (HGV) → ${formatKm(distance)} km · ${formatMin(duration)} min`;
                    } else if (isNumber(distance)) {
                        meta.textContent = `Ruta seleccionada (HGV) → ${formatKm(distance)} km`;
                    } else {
                        meta.textContent = 'Ruta seleccionada (HGV)';
                    }
                }
            });
        });

        if (rutas.length === 1 && meta) {
            meta.textContent += ' · Sin alternativas para este tramo (HGV)';
        }
    }

    // --- Update principal (SIEMPRE HGV) ---
    async function update() {
        const salidaId = sLoc?.value;
        const destinoId = dLoc?.value;
        if (!salidaId || !destinoId) { clearRoutes(); return; }

        meta && (meta.textContent = 'Calculando ruta (HGV)...');
        try {
            const [a, b] = await Promise.all([
                localidadCoords(salidaId),
                localidadCoords(destinoId)
            ]);
            if (!a || !b) {
                clearRoutes();
                meta && (meta.textContent = 'No se pudieron obtener coordenadas de salida/destino.');
                return;
            }

            clearRoutes();
            addMarker(a[0], a[1], 'Salida');
            addMarker(b[0], b[1], 'Destino');

            const approxKm = haversineMeters(a, b) / 1000;

            // 1) Corto → intento con alternativas (HGV)
            if (approxKm <= ALT_MAX_KM) {
                let rutas = await orsHgvAlternativas(a, b);
                if (rutas && rutas.length) { dibujarFeatures(rutas); return; }
                // 2) Fallback corto → simple HGV
                rutas = await orsHgvSimple(a, b);
                if (rutas && rutas.length) { dibujarFeatures(rutas); return; }
                // 3) último recurso corto → multi HGV (raro que haga falta)
                const ptsC = segmentizeByDistance(a, b, LEG_MAX_KM);
                rutas = await orsHgvMulti(ptsC);
                if (rutas && rutas.length) { dibujarFeatures(rutas); return; }
                meta && (meta.textContent = 'No se pudo obtener la ruta por carretera (HGV) para este tramo corto.');
                return;
            }

            // Largo:
            // 1) Simple HGV (sin alternativas)
            let rutas = await orsHgvSimple(a, b);
            if (rutas && rutas.length) { dibujarFeatures(rutas); return; }

            // 2) Si el servidor devuelve 2004 u otro límite, probamos una sola request con WAYPOINTS (HGV)
            const pts = segmentizeByDistance(a, b, LEG_MAX_KM);
            rutas = await orsHgvMulti(pts);
            if (rutas && rutas.length) { dibujarFeatures(rutas); return; }

            // 3) No dibujamos línea recta (pediste siempre carretera)
            meta && (meta.textContent = 'No se pudo obtener la ruta por carretera (HGV) para este tramo largo.');
        } catch (e) {
            clearRoutes();
            meta && (meta.textContent = 'Error calculando ruta (ver consola).');
            console.error(e);
        }
    }

    // eventos
    sLoc?.addEventListener('change', update);
    dLoc?.addEventListener('change', update);

    // inicial
    update();
})();
