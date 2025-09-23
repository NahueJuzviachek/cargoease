// static/viajes/viajes_map.js
(function () {
    // --- Config ---
    // Cambiá el perfil si usás camiones: 'driving-car' | 'driving-hgv'
    const ORS_PROFILE = 'driving-hgv'; // o 'driving-car'

    // --- Helpers DOM ---
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

    let polylines = [];     // capas dibujadas
    let segmentsCache = []; // info de segmentos paralela a polylines

    function formatKm(m) { return (m / 1000).toFixed(2); }
    function formatMin(s) { return Math.round(s / 60); }

    function clearRoutes() {
        polylines.forEach(pl => map.removeLayer(pl));
        polylines = [];
        segmentsCache = [];
        if (meta) meta.textContent = '';
    }

    // --- Obtener coords de Localidad por AJAX (evita Nominatim) ---
    async function localidadCoords(localidadId) {
        if (!localidadId) return null;
        if (!window.URL_LOCALIDAD_COORDS) {
            console.error('[CE] Falta window.URL_LOCALIDAD_COORDS en el template');
            return null;
        }
        try {
            const res = await fetch(`${window.URL_LOCALIDAD_COORDS}?localidad=${encodeURIComponent(localidadId)}`);
            if (!res.ok) {
                console.error('[CE] AJAX localidad coords HTTP', res.status);
                return null;
            }
            const data = await res.json();
            if (typeof data.lat === 'number' && typeof data.lng === 'number') {
                return [data.lat, data.lng]; // [lat, lng]
            }
        } catch (e) {
            console.error('[CE] AJAX localidad coords error', e);
        }
        return null;
    }

    // --- ORS por POST con alternative_routes + fallback shortest ---
    async function orsRutasAlternativas(coordOrigen, coordDestino) {
        const key = window.ORS_API_KEY || '';
        if (!key) {
            meta && (meta.textContent = 'Falta ORS_API_KEY en settings.py / contexto.');
            console.error('[CE] Falta ORS_API_KEY');
            return null;
        }

        const endpoint = `https://api.openrouteservice.org/v2/directions/${ORS_PROFILE}/geojson`;
        const baseBody = {
            coordinates: [
                [coordOrigen[1], coordOrigen[0]], // ORS espera [lng, lat]
                [coordDestino[1], coordDestino[0]]
            ],
            // Más agresivo: acepta rutas menos parecidas y algo más “caras”
            alternative_routes: { target_count: 3, share_factor: 0.5, weight_factor: 1.9 },
            instructions: false
            // preference: 'fastest' // implícito
        };

        // 1) POST principal (fastest)
        let features = [];
        try {
            const r1 = await fetch(endpoint, {
                method: 'POST',
                headers: { 'Authorization': key, 'Content-Type': 'application/json' },
                body: JSON.stringify(baseBody)
            });
            if (!r1.ok) {
                console.error('[CE][ORS fastest] HTTP', r1.status, await r1.text().catch(() => '-'));
                return null;
            }
            const d1 = await r1.json();
            features = Array.isArray(d1.features) ? d1.features.slice(0) : [];
            console.log('[CE][ORS] fastest features:', features.length);
        } catch (e) {
            console.error('[CE][ORS fastest] error de red:', e);
            return null;
        }

        // 2) Fallback: si falta alternativa, pedimos shortest y agregamos si difiere
        if (features.length < 2) {
            const bodyShortest = { ...baseBody, preference: 'shortest' };
            try {
                const r2 = await fetch(endpoint, {
                    method: 'POST',
                    headers: { 'Authorization': key, 'Content-Type': 'application/json' },
                    body: JSON.stringify(bodyShortest)
                });
                if (r2.ok) {
                    const d2 = await r2.json();
                    const alt = Array.isArray(d2.features) ? d2.features[0] : null;
                    if (alt) {
                        const d0 = features[0]?.properties?.segments?.[0]?.distance ?? null;
                        const dAlt = alt?.properties?.segments?.[0]?.distance ?? null;
                        const distinta = (d0 && dAlt) ? (Math.abs(d0 - dAlt) / d0 > 0.03) : true; // tolerancia 3%
                        if (distinta) {
                            features.push(alt);
                            console.log('[CE][ORS] se agregó shortest como alternativa');
                        } else {
                            console.log('[CE][ORS] shortest ~igual a fastest; no se agrega');
                        }
                    }
                } else {
                    console.warn('[CE][ORS shortest] HTTP', r2.status, await r2.text().catch(() => '-'));
                }
            } catch (e2) {
                console.warn('[CE][ORS shortest] error de red:', e2);
            }
        }

        return features.length ? features : null;
    }

    function dibujarRutas(rutas) {
        clearRoutes();

        rutas.forEach((ruta, idx) => {
            // GeoJSON: LineString con coordinates [lng,lat]
            const coords = ruta.geometry.coordinates.map(c => [c[1], c[0]]);
            const color = idx === 0 ? 'blue' : 'gray';
            const seg = ruta.properties?.segments?.[0] || null;

            const poly = L.polyline(coords, { color, weight: 4, opacity: 0.9 }).addTo(map);
            polylines.push(poly);
            segmentsCache.push(seg);

            if (idx === 0) {
                map.fitBounds(poly.getBounds(), { padding: [20, 20] });
                if (seg) {
                    distanciaInput && (distanciaInput.value = formatKm(seg.distance));
                    meta && (meta.textContent = `Ruta principal → ${formatKm(seg.distance)} km · ${formatMin(seg.duration)} min`);
                }
            }

            poly.on('click', () => {
                polylines.forEach(l => l.setStyle({ color: 'gray' }));
                poly.setStyle({ color: 'red' });
                if (seg) {
                    distanciaInput && (distanciaInput.value = formatKm(seg.distance));
                    meta && (meta.textContent = `Ruta seleccionada → ${formatKm(seg.distance)} km · ${formatMin(seg.duration)} min`);
                }
            });
        });

        if (rutas.length === 1 && meta) {
            meta.textContent += ' · No hay rutas alternativas para este tramo';
        }
    }

    async function update() {
        const salidaId = sLoc?.value;
        const destinoId = dLoc?.value;
        if (!salidaId || !destinoId) { clearRoutes(); return; }

        meta && (meta.textContent = 'Calculando ruta...');
        try {
            // Coordenadas DIRECTAS desde tus Localidades (sin Nominatim)
            const [coordOrigen, coordDestino] = await Promise.all([
                localidadCoords(salidaId),
                localidadCoords(destinoId)
            ]);

            if (!coordOrigen || !coordDestino) {
                clearRoutes();
                meta && (meta.textContent = 'No se pudieron obtener coordenadas de salida/destino.');
                return;
            }

            const rutas = await orsRutasAlternativas(coordOrigen, coordDestino);
            if (!rutas || rutas.length === 0) {
                clearRoutes();
                meta && (meta.textContent = 'No se encontraron rutas para este recorrido.');
                return;
            }
            dibujarRutas(rutas);
        } catch (e) {
            clearRoutes();
            meta && (meta.textContent = 'Error calculando ruta (ver consola).');
            console.error(e);
        }
    }

    // Disparadores (cuando cambian localidades)
    sLoc?.addEventListener('change', update);
    dLoc?.addEventListener('change', update);

    // Intento inicial (modo edición)
    update();
})();
