/* Total Gest — DELETE genérico da sincronização
 * Executa remoções na ordem inversa das FKs e só limpa snapshots após confirmação do servidor.
 */
(function () {
  'use strict';

  async function run(options) {
    const opts = options || {};
    const supabase = opts.supabase;
    const order = opts.order || [];
    const metadata = opts.metadata || {};
    const data = opts.data || {};
    const snapshots = opts.snapshots || {};
    const licenseSnapshot = opts.licenseSnapshot;
    const junctionSnapshot = opts.junctionSnapshot;
    const deletedIds = opts.deletedIds;
    const missingTable = opts.missingTable;
    let errors = 0;
    let firstError = '';

    if (!supabase || typeof deletedIds !== 'function' || typeof missingTable !== 'function') {
      throw new Error('TotalGestSyncDelete: dependencias invalidas');
    }

    for (let i = order.length - 1; i >= 0; i--) {
      const collection = order[i];
      const meta = metadata[collection];
      const snapshot = snapshots[collection];
      if (!meta || !snapshot) continue;

      const removed = deletedIds(data[collection] || [], snapshot);
      if (!removed.length) continue;

      const result = await supabase.from(meta.tabela).delete().in('id', removed);
      const error = result.error;
      if (error) {
        console.error('delete ' + meta.tabela + ':', error.message);
        if (!missingTable(error)) {
          errors++;
          if (!firstError) firstError = 'apagar ' + meta.tabela + ' — ' + (error.message || error.code || 'erro');
        }
        // Mantém snapshots para voltar a tentar na próxima sincronização.
        continue;
      }

      for (const id of removed) {
        snapshot.delete(id);
        if (licenseSnapshot) licenseSnapshot.delete(id);
        if (junctionSnapshot) junctionSnapshot.delete(id);
      }
    }

    return { errors: errors, firstError: firstError };
  }

  window.TotalGestSyncDelete = { run: run };
})();
