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
    cache: './assets/js/app-cache.js',
    connectivity: './assets/js/app-connectivity.js',
    syncStatus: './assets/js/app-sync-status.js',
    syncHelpers: './assets/js/app-sync-helpers.js',
    syncDiff: './assets/js/app-sync-diff.js',
    syncSnapshots: './assets/js/app-sync-snapshots.js',
    syncPending: './assets/js/app-sync-pending.js',
    periodLoading: './assets/js/app-period-loading.js',
    loadContext: './assets/js/app-load-context.js',
    loadQueries: './assets/js/app-load-queries.js',
    syncPrepare: './assets/js/app-sync-prepare.js',
    syncFiles: './assets/js/app-sync-files.js',
    syncCollections: './assets/js/app-sync-collections.js',
    syncOrchestrator: './assets/js/app-sync-orchestrator.js',
    syncFinalize: './assets/js/app-sync-finalize.js',
    syncUpsert: './assets/js/app-sync-upsert.js',
    syncLicenses: './assets/js/app-sync-licenses.js',
    syncEncarregados: './assets/js/app-sync-encarregados.js',
    syncDelete: './assets/js/app-sync-delete.js',
    saveQueue: './assets/js/app-save-queue.js',
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
    if (options.cache === true) pedidos.push(MODULOS.cache);
    if (options.connectivity === true) pedidos.push(MODULOS.connectivity);
    if (options.syncStatus === true) pedidos.push(MODULOS.syncStatus);
    if (options.syncHelpers === true) pedidos.push(MODULOS.syncHelpers);
    if (options.syncDiff === true) pedidos.push(MODULOS.syncDiff);
    if (options.syncSnapshots === true) pedidos.push(MODULOS.syncSnapshots);
    if (options.syncPending === true) pedidos.push(MODULOS.syncPending);
    if (options.periodLoading === true) pedidos.push(MODULOS.periodLoading);
    if (options.loadContext === true) pedidos.push(MODULOS.loadContext);
    if (options.loadQueries === true) pedidos.push(MODULOS.loadQueries);
    if (options.syncPrepare === true) pedidos.push(MODULOS.syncPrepare);
    if (options.syncFiles === true) pedidos.push(MODULOS.syncFiles);
    if (options.syncCollections === true) pedidos.push(MODULOS.syncCollections);
    if (options.syncOrchestrator === true) pedidos.push(MODULOS.syncOrchestrator);
    if (options.syncFinalize === true) pedidos.push(MODULOS.syncFinalize);
    if (options.syncUpsert === true) pedidos.push(MODULOS.syncUpsert);
    if (options.syncLicenses === true) pedidos.push(MODULOS.syncLicenses);
    if (options.syncEncarregados === true) pedidos.push(MODULOS.syncEncarregados);
    if (options.syncDelete === true) pedidos.push(MODULOS.syncDelete);
    if (options.saveQueue === true) pedidos.push(MODULOS.saveQueue);
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
