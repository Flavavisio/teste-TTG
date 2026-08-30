/* Total Gest — shell modular da aplicação
 * Ponto de entrada para os módulos extraídos de app.html.
 */
(function () {
  'use strict';

  const MODULOS = {
    pwa: './assets/js/app-pwa.js',
    toast: './assets/js/app-toast.js',
    ui: './assets/js/app-ui.js',
    dialogs: './assets/js/app-dialogs.js',
    connectivity: './assets/js/app-connectivity.js',
    syncStatus: './assets/js/app-sync-status.js',
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
    if (options.toast === true) pedidos.push(MODULOS.toast);
    if (options.ui === true) pedidos.push(MODULOS.ui);
    if (options.dialogs === true) pedidos.push(MODULOS.dialogs);
    if (options.connectivity === true) pedidos.push(MODULOS.connectivity);
    if (options.syncStatus === true) pedidos.push(MODULOS.syncStatus);
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

    if (options.connectivity === true && window.TotalGestConnectivity && typeof window.TotalGestConnectivity.init === 'function') {
      window.TotalGestConnectivity.init();
    }

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
