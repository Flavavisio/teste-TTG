/* Total Gest — sincronizacao de licencas
 * Mantem a chamada legada a tabela licencas e atualiza o snapshot apenas apos sucesso.
 */
(function () {
  'use strict';

  async function run(options) {
    const opts = options || {};
    const supabase = opts.supabase;
    const admins = opts.admins || [];
    const snapshot = opts.snapshot;
    const toRow = opts.toRow;

    if (!supabase || !snapshot || typeof toRow !== 'function') {
      throw new Error('TotalGestSyncLicenses: dependencias invalidas');
    }

    const rows = [];
    const states = [];
    for (const admin of admins) {
      if (!admin.licenca) continue;
      const row = toRow(admin.id, admin.licenca);
      const json = JSON.stringify(row);
      if (snapshot.get(admin.id) !== json) {
        rows.push(row);
        states.push({ id: admin.id, json: json });
      }
    }

    if (!rows.length) return { error: null };

    const result = await supabase.from('licencas').upsert(rows, { onConflict: 'admin_id' });
    if (result.error) {
      console.error('upsert licencas:', result.error.message);
      return { error: result.error };
    }

    states.forEach(function (state) { snapshot.set(state.id, state.json); });
    return { error: null };
  }

  window.TotalGestSyncLicenses = { run: run };
})();
