// static/js/i18n.js
(function () {
  console.log('[i18n] cargando i18n.js');
  if (!window.i18next) {
    console.warn('[i18n] i18next no estaba disponible aún — esperando...');
  }

  // Helper para aplicar traducciones
  function applyTranslations() {
    document.querySelectorAll('[data-i18n]').forEach(el => {
      const key = el.getAttribute('data-i18n');
      try {
        if (el.tagName === 'INPUT' || el.tagName === 'TEXTAREA') {
          if (el.hasAttribute('placeholder')) {
            el.setAttribute('placeholder', i18next.t(key));
          } else {
            el.value = i18next.t(key);
          }
        } else {
          el.innerHTML = i18next.t(key);
        }
      } catch (e) {
        // si falla, no rompemos la ejecución
      }
    });

    document.querySelectorAll('[data-i18n-attr]').forEach(el => {
      const mappings = el.getAttribute('data-i18n-attr').split(';');
      mappings.forEach(map => {
        if (!map) return;
        const parts = map.split(':').map(s => s.trim());
        if (parts.length === 2) {
          el.setAttribute(parts[0], i18next.t(parts[1]));
        }
      });
    });
  }

  // path seguro usando window.STATIC_URL si está definido
  const staticBase = (typeof window.STATIC_URL === 'string' && window.STATIC_URL) ? window.STATIC_URL : '/static/';
  const loadPath = staticBase + 'locales/{{lng}}/{{ns}}.json';
  console.log('[i18n] loadPath:', loadPath);

  // Inicializar i18next
  i18next
    .use(i18nextBrowserLanguageDetector)
    .use(i18nextHttpBackend)
    .init({
      fallbackLng: 'es',
      debug: false,
      ns: ['translation'],
      defaultNS: 'translation',
      backend: {
        loadPath: loadPath
      },
      detection: {
        order: ['localStorage', 'cookie', 'navigator'],
        caches: ['localStorage']
      }
    }, function (err, t) {
      if (err) {
        console.error('[i18n] error inicializando i18next:', err);
      } else {
        console.log('[i18n] inicializado — idioma actual:', i18next.language);
      }
      applyTranslations();

      // Si había una intención pendiente (click antes de init), aplicarla
      try {
        const pending = localStorage.getItem('language_intent');
        if (pending) {
          console.log('[i18n] aplicando idioma pendiente:', pending);
          localStorage.removeItem('language_intent');
          i18next.changeLanguage(pending, applyTranslations);
        }
      } catch (e) {}
    });

  // función expuesta para botones antiguos que usan onclick
  window.changeLanguage = function (lang) {
    console.log('[i18n] changeLanguage llamado ->', lang);
    i18next.changeLanguage(lang, function () {
      applyTranslations();
    });
    try { localStorage.setItem('language', lang); } catch (e) {}
  };

  // delegación de eventos: botones con .lang-btn y data-lang
  document.addEventListener('click', function (e) {
    const btn = e.target.closest('.lang-btn');
    if (!btn) return;
    e.preventDefault();
    const lang = btn.getAttribute('data-lang');
    if (!lang) return;
    if (window.changeLanguage) {
      window.changeLanguage(lang);
    } else {
      try { localStorage.setItem('language_intent', lang); } catch (e) {}
      console.warn('[i18n] idioma solicitado antes de inicializar:', lang);
    }
  });
})();
