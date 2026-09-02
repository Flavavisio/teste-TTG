/* Total Gest — cálculo puro das diferenças de sincronização
 * Não faz pedidos ao Supabase e não altera snapshots; apenas calcula o que mudou.
 */
(function () {
  'use strict';

  function changedRows(list, toRow, snapshot) {
    const rows = [];
    const states = [];
    const source = list || [];

    for (const item of source) {
      const row = toRow(item);
      const json = JSON.stringify(row);
      if (snapshot.get(item.id) !== json) {
        rows.push(row);
        states.push({ id: item.id, json: json });
      }
    }

    return { rows: rows, states: states };
  }

  function deletedIds(list, snapshot) {
    const currentIds = new Set((list || []).map(function (item) { return item.id; }));
    const removed = [];
    for (const id of snapshot.keys()) {
      if (!currentIds.has(id)) removed.push(id);
    }
    return removed;
  }

  window.TotalGestSyncDiff = {
    changedRows: changedRows,
    deletedIds: deletedIds
  };
})();
