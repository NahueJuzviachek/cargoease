(function () {
    const $ = (sel, ctx = document) => ctx.querySelector(sel);
    const endpointsEl = $('#dashboard-endpoints');
    const URLS = {
        clientes: endpointsEl?.dataset?.clientesUrl,
        ranking: endpointsEl?.dataset?.rankingkmUrl,
        aceite: endpointsEl?.dataset?.aceiteUrl,
        neumaticos: endpointsEl?.dataset?.neumaticosUrl,
    };

    function showEmpty(id) { const el = $(id); if (el) el.classList.remove('d-none'); }
    function hideEmpty(id) { const el = $(id); if (el) el.classList.add('d-none'); }
    function showError(id) { const el = $(id); if (el) el.classList.remove('d-none'); }
    function hideError(id) { const el = $(id); if (el) el.classList.add('d-none'); }

    // ---------- Clientes top mensual ----------
    let chartClientes;
    function setMesInputsDefault() {
        const hoy = new Date();
        const hasta = hoy.toISOString().slice(0, 7);
        const d = new Date(hoy);
        d.setMonth(d.getMonth() - 5);
        const desde = d.toISOString().slice(0, 7);
        const desdeEl = $('#cliDesde'), hastaEl = $('#cliHasta');
        if (desdeEl) desdeEl.value = desde;
        if (hastaEl) hastaEl.value = hasta;
    }

    async function cargarClientesTopMensual() {
        hideEmpty('#emptyClientes'); hideError('#errorClientes');
        const d = $('#cliDesde')?.value;
        const h = $('#cliHasta')?.value;

        if (!URLS.clientes) { console.error('Endpoint clientes no definido'); showError('#errorClientes'); return; }

        const url = new URL(URLS.clientes, window.location.origin);
        if (d) url.searchParams.set('desde', d);
        if (h) url.searchParams.set('hasta', h);

        try {
            const res = await fetch(url);
            if (!res.ok) throw new Error('HTTP ' + res.status);
            const json = await res.json();
            console.log('[clientes-top-mensual] payload:', json);

            const labels = json.labels || [];
            const series = json.series || [];
            const datasets = series.map(s => ({
                label: s.label, data: s.data, borderWidth: 2, tension: 0.2, fill: false
            }));

            const ctx = $('#chartClientesTopMensual');
            if (!ctx) return;
            if (chartClientes) chartClientes.destroy();

            if (!labels.length || !datasets.length) { showEmpty('#emptyClientes'); return; } // ⬅️ cortar acá

            chartClientes = new Chart(ctx, {
                type: 'line',
                data: { labels, datasets },
                options: {
                    responsive: true, maintainAspectRatio: false,
                    plugins: {
                        legend: { position: 'bottom' },
                        tooltip: { callbacks: { label: (c) => `${c.dataset.label}: ${c.parsed.y} viajes` } }
                    },
                    scales: { y: { beginAtZero: true, ticks: { precision: 0 } } }
                }
            });
        } catch (e) {
            console.error('clientes-top-mensual:', e);
            showError('#errorClientes');
        }
    }

    // ---------- Ranking km por vehículo ----------
    let chartRanking;
    function rangoDefaultInput() {
        const hoy = new Date();
        const desde = new Date(hoy);
        desde.setDate(hoy.getDate() - 30);
        const dEl = $('#rkDesde'), hEl = $('#rkHasta');
        if (dEl) dEl.value = desde.toISOString().slice(0, 10);
        if (hEl) hEl.value = hoy.toISOString().slice(0, 10);
    }

    async function cargarRankingKm() {
        hideEmpty('#emptyRanking'); hideError('#errorRanking');
        const d = $('#rkDesde')?.value;
        const h = $('#rkHasta')?.value;

        if (!URLS.ranking) { console.error('Endpoint ranking no definido'); showError('#errorRanking'); return; }

        const url = new URL(URLS.ranking, window.location.origin);
        if (d) url.searchParams.set('desde', d);
        if (h) url.searchParams.set('hasta', h);

        try {
            const res = await fetch(url);
            if (!res.ok) throw new Error('HTTP ' + res.status);
            const json = await res.json();
            console.log('[ranking-km] payload:', json);

            const labels = (json.items || []).map(x => x.vehiculo);
            const data = (json.items || []).map(x => x.km);

            const ctx = $('#chartRankingKm');
            if (!ctx) return;
            if (chartRanking) chartRanking.destroy();

            if (!labels.length) { showEmpty('#emptyRanking'); return; } // ⬅️ cortar acá

            chartRanking = new Chart(ctx, {
                type: 'bar',
                data: { labels, datasets: [{ label: 'Km recorridos', data, borderWidth: 1 }] },
                options: {
                    responsive: true, maintainAspectRatio: false,
                    scales: { y: { beginAtZero: true } },
                    plugins: {
                        tooltip: { callbacks: { label: (c) => `${c.dataset.label}: ${Number(c.parsed.y).toLocaleString('es-AR')} km` } },
                        legend: { display: false }
                    }
                }
            });
        } catch (e) {
            console.error('ranking-km:', e);
            showError('#errorRanking');
        }
    }

    // ---------- Aceite Top 5 ----------
    let chartAceite;
    async function cargarAceiteTop5() {
        hideEmpty('#emptyAceite'); hideError('#errorAceite');
        if (!URLS.aceite) { console.error('Endpoint aceite no definido'); showError('#errorAceite'); return; }

        try {
            const res = await fetch(URLS.aceite, { method: 'GET' });
            if (!res.ok) throw new Error('HTTP ' + res.status);
            const json = await res.json();
            console.log('[aceite-top5] payload:', json);

            const items = json.items || [];
            const labels = items.map(x => `${x.vehiculo} (${x.tipo})`);
            const data = items.map(x => x.km_restantes);

            const ctx = $('#chartAceiteTop5');
            if (!ctx) return;
            if (chartAceite) chartAceite.destroy();

            if (!labels.length) { showEmpty('#emptyAceite'); return; } // ⬅️ cortar acá

            chartAceite = new Chart(ctx, {
                type: 'bar',
                data: { labels, datasets: [{ label: 'Km restantes', data, borderWidth: 1 }] },
                options: {
                    indexAxis: 'y',
                    responsive: true, maintainAspectRatio: false,
                    scales: { x: { beginAtZero: true } },
                    plugins: {
                        tooltip: { callbacks: { label: (c) => `${c.dataset.label}: ${Number(c.parsed.x).toLocaleString('es-AR')} km` } },
                        legend: { display: false }
                    }
                }
            });
        } catch (e) {
            console.error('aceite-top5:', e);
            showError('#errorAceite');
        }
    }

    // ---------- Neumáticos estado global ----------
    let chartNeum;
    async function cargarNeumaticosEstado() {
        hideEmpty('#emptyNeum'); hideError('#errorNeum');
        if (!URLS.neumaticos) { console.error('Endpoint neumaticos no definido'); showError('#errorNeum'); return; }

        try {
            const res = await fetch(URLS.neumaticos, { method: 'GET' });
            if (!res.ok) throw new Error('HTTP ' + res.status);
            const json = await res.json();
            console.log('[neumaticos-estado] payload:', json);

            const labels = json.labels || [];
            const values = json.values || [];

            const ctx = $('#chartNeumaticosEstado');
            if (!ctx) return;
            if (chartNeum) chartNeum.destroy();

            if (!labels.length) { showEmpty('#emptyNeum'); return; } // ⬅️ cortar acá

            chartNeum = new Chart(ctx, {
                type: 'doughnut',
                data: { labels, datasets: [{ label: 'Cantidad', data: values }] },
                options: {
                    responsive: true, maintainAspectRatio: false,
                    plugins: { legend: { position: 'bottom' } }
                }
            });
        } catch (e) {
            console.error('neumaticos-estado:', e);
            showError('#errorNeum');
        }
    }

    // ---------- Init ----------
    document.addEventListener('DOMContentLoaded', async () => {
        setMesInputsDefault();
        rangoDefaultInput();

        await Promise.all([
            cargarClientesTopMensual(),
            cargarRankingKm(),
            cargarAceiteTop5(),
            cargarNeumaticosEstado()
        ]);

        $('#cliAplicar')?.addEventListener('click', cargarClientesTopMensual);
        $('#rkAplicar')?.addEventListener('click', cargarRankingKm);
    });
})();
