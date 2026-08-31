/* Total Gest — UPSERT genérico em lotes
 * Mantém a semântica legada de confirmação, retry por coluna em falta e snapshots.
 */
(function () {
  'use strict';

  async function run(options) {
    const opts = options || {};
    const supabase = opts.supabase;
    const table = opts.table;
    const rows = opts.rows || [];
    const states = opts.states || [];
    const snapshot = opts.snapshot;
    const missingColumn = opts.missingColumn;
    const batchSize = 200;
    let tableError = null;

    if (!supabase || !table || !snapshot || typeof missingColumn !== 'function') {
      throw new Error('TotalGestSyncUpsert: dependencias invalidas');
    }

    for (let i = 0; i < rows.length; i += batchSize) {
      const batchRows = rows.slice(i, i + batchSize);
      const batchStates = states.slice(i, i + batchSize);
      const result = await supabase.from(table).upsert(batchRows, { onConflict: 'id' }).select('id');
      const writtenRows = result.data;
      const error = result.error;

      if (error) {
        console.error('upsert ' + table + ' (lote ' + (i / batchSize + 1) + '):', error.message);
        const missing = missingColumn(error);
        if (missing) {
          console.warn('Coluna "' + missing + '" não existe em "' + table + '" — a sincronizar sem ela por agora. Corre a query SQL correspondente para isto passar a gravar completo.');
          const retryRows = batchRows.map(function (row) {
            const copy = { ...row };
            delete copy[missing];
            return copy;
          });
          const retry = await supabase.from(table).upsert(retryRows, { onConflict: 'id' }).select('id');
          if (!retry.error && retry.data && retry.data.length >= retryRows.length) {
            batchStates.forEach(function (state) { snapshot.set(state.id, state.json); });
            continue;
          }
        }
        tableError = error;
        continue;
      }

      if (!writtenRows || writtenRows.length < batchRows.length) {
        const confirmedIds = new Set((writtenRows || []).map(function (row) { return row.id; }));
        batchStates.forEach(function (state) {
          if (confirmedIds.has(state.id)) snapshot.set(state.id, state.json);
        });
        console.error('upsert ' + table + ': enviadas ' + batchRows.length + ', confirmadas ' + ((writtenRows && writtenRows.length) || 0) + ' — bloqueado por permissões (RLS)');
        tableError = { message: 'Algumas linhas de "' + table + '" foram bloqueadas pelas permissões do servidor (RLS)' };
      } else {
        batchStates.forEach(function (state) { snapshot.set(state.id, state.json); });
      }
    }

    return { error: tableError };
  }

  window.TotalGestSyncUpsert = { run: run };
})();
