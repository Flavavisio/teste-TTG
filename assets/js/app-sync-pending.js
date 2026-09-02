/* Total Gest — contagem de alterações locais pendentes
 * Compara os dados atuais com os snapshots confirmados sem efetuar chamadas de rede.
 */
(function () {
  'use strict';

  function count(options) {
    const opts = options || {};
    const order = opts.order || [];
    const data = opts.data || {};
    const metadata = opts.metadata || {};
    const snapshots = opts.snapshots || {};
    let total = 0;

    for (const collection of order) {
      const list = data[collection] || [];
      for (const item of list) {
        const json = JSON.stringify(metadata[collection].to(item));
        if (snapshots[collection].get(item.id) !== json) total++;
      }
      for (const id of snapshots[collection].keys()) {
        if (!list.some(item => item.id === id)) total++;
      }
    }

    return total;
  }

  window.TotalGestSyncPending = { count: count };
})();
