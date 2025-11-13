// static/js/i18n.js  — carga traducciones mediante fetch y no necesita i18nextHttpBackend
(function () {
  console.log('[i18n] cargando i18n.js (fetch-based)');

  // helper para fetch de json con manejo simple
  async function loadLocaleJson(lang) {
    const url = (typeof window.STATIC_URL === 'string' ? window.STATIC_URL : '/static/') + `locales/${lang}/translation.json`;
    try {
      const res = await fetch(url, {cache: 'no-cache'});
      if (!res.ok) throw new Error('HTTP ' + res.status);
      return await res.json();
    } catch (err) {
      console.error('[i18n] fallo al cargar', url, err);
      return null;
    }
  }

  function applyTranslations() {
    document.querySelectorAll('[data-i18n]').forEach(el => {
      const key = el.getAttribute('data-i18n');
      try {
        if (el.tagName === 'INPUT' || el.tagName === 'TEXTAREA') {
          if (el.hasAttribute('placeholder')) el.setAttribute('placeholder', i18next.t(key));
          else el.value = i18next.t(key);
        } else {
          el.innerHTML = i18next.t(key);
        }
      } catch (e) {}
    });
    document.querySelectorAll('[data-i18n-attr]').forEach(el => {
      const mappings = el.getAttribute('data-i18n-attr').split(';');
      mappings.forEach(map => {
        if (!map) return;
        const [attr, k] = map.split(':').map(s => s.trim());
        if (attr && k) el.setAttribute(attr, i18next.t(k));
      });
    });
  }

  async function init() {
    // detect language: prefer localStorage -> navigator
    const saved = (function(){ try { return localStorage.getItem('language'); } catch(e) { return null; } })();
    const navigatorLang = (navigator.language || navigator.userLanguage || 'es').split('-')[0];
    const lang = saved || navigatorLang || 'es';

    // Cargamos los JSON que vayamos a usar (al menos 'es' y la seleccionada)
    const languagesToLoad = new Set(['es', 'en', lang]);
    const resources = {};
    await Promise.all(Array.from(languagesToLoad).map(async l => {
      const json = await loadLocaleJson(l);
      if (json) resources[l] = { translation: json };
    }));

    // inicializa i18next con recursos inline
    if (!window.i18next) {
      console.error('[i18n] i18next no está cargado. Asegurate de incluir su CDN antes de i18n.js');
      return;
    }

    i18next.init({
      lng: lang,
      fallbackLng: 'es',
      debug: false,
      resources: resources,
      interpolation: { escapeValue: false },
    }, function(err, t) {
      if (err) console.error('[i18n] init error', err);
      else console.log('[i18n] inicializado con lang=', i18next.language);
      applyTranslations();

      // aplicar intención pendiente
      try {
        const pending = localStorage.getItem('language_intent');
        if (pending) {
          localStorage.removeItem('language_intent');
          changeLanguage(pending);
        }
      } catch (e) {}
    });
  }

  // expose changeLanguage
  window.changeLanguage = function(lang) {
    if (!window.i18next) {
      try { localStorage.setItem('language_intent', lang); } catch(e){}
      console.warn('[i18n] changeLanguage solicitado pero i18next no está listo. Guardado intent.');
      return;
    }
    // si el recurso ya está cargado no hace fetch otro; si no, lo carga y actualiza
    (async function() {
      if (!i18next.hasResourceBundle || !i18next.hasResourceBundle(lang, 'translation')) {
        const json = await loadLocaleJson(lang);
        if (json) {
          i18next.addResourceBundle(lang, 'translation', json, true, true);
        }
      }
      i18next.changeLanguage(lang, function() {
        applyTranslations();
      });
      try { localStorage.setItem('language', lang); } catch(e){}
    })();
  };

  // delegación de clicks (si tus botones usan .lang-btn)
  document.addEventListener('click', function(e) {
    const btn = e.target.closest && e.target.closest('.lang-btn');
    if (!btn) return;
    e.preventDefault();
    const lang = btn.getAttribute('data-lang');
    if (lang) window.changeLanguage(lang);
  });

  // iniciar
  init();
})();
