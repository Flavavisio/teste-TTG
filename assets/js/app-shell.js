/* Total Gest — shell modular da aplicação
 * Ponto de entrada para os módulos extraídos de app.html.
 * Enquanto o bootstrap inline legado existir, este shell não inicia automaticamente a aplicação.
 */
(function () {
  'use strict';

  const MODULOS = [
    './assets/js/app-pwa.js',
    './assets/js/app-dialogs.js',
    './assets/js/app-bootstrap.js'
  ];

  function carregarScript(src) {
    return new Promise(function (resolve, reject) {
      if (document.querySelector('script[data-tg-module="' + src + '"]')) {
        resolve();
        return;
      }

      const script = document.createElement('script');
      script.src = src;
      script.defer = true;
      script.dataset.tgModule = src;
      script.onload = resolve;
      script.onerror = reject;
      document.head.appendChild(script);
    });
  }

  async function carregarModulos() {
    for (const modulo of MODULOS) {
      await carregarScript(modulo);
    }
  }

  async function iniciar(options) {
    options = options || {};
    await carregarModulos();

    if (options.pwa !== false && window.TotalGestPwa && typeof window.TotalGestPwa.init === 'function') {
      window.TotalGestPwa.init();
    }

    // O bootstrap é opt-in durante a migração para impedir um segundo arranque
    // enquanto o DOMContentLoaded legado continuar dentro de app.html.
    if (options.bootstrap === true && window.TotalGestBootstrap && typeof window.TotalGestBootstrap.init === 'function') {
      await window.TotalGestBootstrap.init();
    }
  }

  window.TotalGestApp = {
    init: iniciar,
    loadModules: carregarModulos,
    modules: MODULOS.slice()
  };
})();
