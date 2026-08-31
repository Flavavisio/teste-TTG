/* Total Gest — finalização da sincronização
 * Atualiza estados/cache e propaga falhas confirmadas ao chamador.
 */
(function () {
  'use strict';

  function run(options) {
    const opts = options || {};
    const errors = Number(opts.errors || 0);
    const firstError = opts.firstError || '';
    const showSyncStatus = opts.showSyncStatus;
    const saveCache = opts.saveCache;
    const showOfflineStatus = opts.showOfflineStatus;

    if (typeof showSyncStatus !== 'function' || typeof saveCache !== 'function' || typeof showOfflineStatus !== 'function') {
      throw new Error('TotalGestSyncFinalize: dependencias invalidas');
    }

    showSyncStatus(errors, firstError);
    saveCache();
    showOfflineStatus(errors > 0);

    if (errors > 0) {
      throw new Error(firstError || 'Não foi possível confirmar a gravação no servidor.');
    }
  }

  window.TotalGestSyncFinalize = { run: run };
})();
