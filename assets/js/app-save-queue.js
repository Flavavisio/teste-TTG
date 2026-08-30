/* Total Gest — fila de gravacao/sincronizacao
 * Serializa tentativas de gravacao sem conhecer o modelo de dados nem o Supabase.
 */
(function () {
  'use strict';

  function create(options) {
    const opts = options || {};
    if (typeof opts.saveCache !== 'function' ||
        typeof opts.isOnline !== 'function' ||
        typeof opts.showOffline !== 'function' ||
        typeof opts.sync !== 'function' ||
        typeof opts.reportError !== 'function') {
      throw new Error('TotalGestSaveQueue: dependencias invalidas');
    }

    let chain = Promise.resolve();

    function save() {
      // Mantem a ordem legada: cache primeiro, feedback offline, depois sincronizacao.
      opts.saveCache();
      if (!opts.isOnline()) opts.showOffline();

      const attempt = chain.then(opts.sync);
      // A fila interna recupera para permitir a proxima gravacao; a Promise devolvida
      // por save() continua a refletir o sucesso/erro real desta tentativa.
      chain = attempt.catch(opts.reportError);
      return attempt;
    }

    function waitForIdle() {
      return chain;
    }

    return { save, waitForIdle };
  }

  window.TotalGestSaveQueue = { create };
})();
