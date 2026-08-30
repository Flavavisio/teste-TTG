/* Total Gest — shell modular da aplicação
 * Ponto de entrada para os módulos extraídos de app.html.
 * Enquanto o bootstrap inline legado existir, este shell só inicia os módulos explicitamente pedidos.
 */
(function () {
  'use strict';

  const MODULOS = {
    pwa: './assets/js/app-pwa.js',
    dialogs: './assets/js/app-dialogs.js',
    bootstrap: './assets/js/app-bootstrap.js'
  };

  function carregarScript(src) {
    return new Promise(function (resolve, reject) {
      const existente = document.querySelector('script[data-tg-module="' + src + '"]');
      if (existente) {
        if (existente.dataset.tgLoaded === '1') resolve();
        else existente.addEventListener('load', resolve, { once: true });
        return;
      }

      const script = document.createElement('script');
      script.src = src;
      script.dataset.tgModule = src;
      script.onload = function () {
        script.dataset.tgLoaded = '1';
        resolve();
      };
      script.onerror = reject;
      document.head.appendChild(script);
    });
  }

  async function carregarModulos(options) {
    options = options || {};
    const pedidos = [];

    if (options.pwa === true) pedidos.push(MODULOS.pwa);
    if (options.dialogs === true) pedidos.push(MODULOS.dialogs);
    if (options.bootstrap === true) pedidos.push(MODULOS.bootstrap);

    for (const modulo of pedidos) {
      await carregarScript(modulo);
    }
  }

  async function iniciar(options) {
    options = options || {};
    await carregarModulos(options);

    if (options.pwa === true && window.TotalGestPwa && typeof window.TotalGestPwa.init === 'function') {
      window.TotalGestPwa.init();
    }

    if (options.dialogs === true && window.TotalGestDialogs && typeof window.TotalGestDialogs.init === 'function') {
      window.TotalGestDialogs.init();
    }

    // O bootstrap continua opt-in durante a migração para impedir um segundo arranque
    // enquanto o DOMContentLoaded legado continuar dentro de app.html.
    if (options.bootstrap === true && window.TotalGestBootstrap && typeof window.TotalGestBootstrap.init === 'function') {
      await window.TotalGestBootstrap.init();
    }
  }

  window.TotalGestApp = {
    init: iniciar,
    loadModules: carregarModulos,
    modules: Object.assign({}, MODULOS)
  };
})();
