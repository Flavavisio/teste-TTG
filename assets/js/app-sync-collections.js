/* Total Gest — orquestração da sincronização das coleções
 * Mantém a ordem das FKs e delega cada responsabilidade nos módulos já extraídos.
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
    const changedRows = opts.changedRows;
    const runUpsert = opts.runUpsert;
    const runLicenses = opts.runLicenses;
    const runEncarregados = opts.runEncarregados;
    const licenseToRow = opts.licenseToRow;
    const missingColumn = opts.missingColumn;
    const missingTable = opts.missingTable;
    let errors = 0;
    let firstError = '';

    if (!supabase || typeof changedRows !== 'function' || typeof runUpsert !== 'function' ||
        typeof runLicenses !== 'function' || typeof runEncarregados !== 'function' ||
        typeof licenseToRow !== 'function' || typeof missingColumn !== 'function' ||
        typeof missingTable !== 'function') {
      throw new Error('TotalGestSyncCollections: dependencias invalidas');
    }

    for (const collection of order) {
      const meta = metadata[collection];
      const list = data[collection] || [];
      const diff = changedRows(list, meta.to, snapshots[collection]);
      const rows = diff.rows;
      const states = diff.states;

      if (collection === 'obraPontoLonga' && list.length) {
        console.log('[obraPontoLonga] a sincronizar:', rows.length, 'de', list.length, 'registo(s) local(is)');
      }

      if (rows.length) {
        const upsertResult = await runUpsert({
          supabase: supabase,
          table: meta.tabela,
          rows: rows,
          states: states,
          snapshot: snapshots[collection],
          missingColumn: missingColumn
        });
        const tableError = upsertResult.error;
        if (tableError && !missingTable(tableError) && collection !== 'auditoria') {
          errors++;
          if (!firstError) firstError = meta.tabela + ' — ' + (tableError.message || tableError.code || 'erro');
        }
      }

      if (collection === 'administradores') {
        const licenseResult = await runLicenses({
          supabase: supabase,
          admins: list,
          snapshot: licenseSnapshot,
          toRow: licenseToRow
        });
        if (licenseResult.error && !missingTable(licenseResult.error)) {
          errors++;
          if (!firstError) firstError = 'licencas — ' + (licenseResult.error.message || licenseResult.error.code || 'erro');
        }
      }

      if (collection === 'encarregados') {
        const junctionResult = await runEncarregados({
          supabase: supabase,
          encarregados: list,
          snapshot: junctionSnapshot,
          missingTable: missingTable
        });
        errors += junctionResult.errors;
        if (!firstError && junctionResult.firstError) firstError = junctionResult.firstError;
      }
    }

    return { errors: errors, firstError: firstError };
  }

  window.TotalGestSyncCollections = { run: run };
})();
