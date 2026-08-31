/* Total Gest — orquestração principal da sincronização
 * Coordena preparação, ficheiros, coleções, deletes e finalização sem alterar a lógica de cada módulo.
 */
(function () {
  'use strict';

  async function run(options) {
    const opts = options || {};
    const isOnline = opts.isOnline;
    const showOfflineStatus = opts.showOfflineStatus;
    const data = opts.data || {};
    const repairInvalidEquipmentLocations = opts.repairInvalidEquipmentLocations;
    const migratePending = opts.migratePending;
    const runCollections = opts.runCollections;
    const runDelete = opts.runDelete;
    const finalize = opts.finalize;

    if (typeof isOnline !== 'function' || typeof showOfflineStatus !== 'function' ||
        typeof repairInvalidEquipmentLocations !== 'function' || typeof migratePending !== 'function' ||
        typeof runCollections !== 'function' || typeof runDelete !== 'function' || typeof finalize !== 'function') {
      throw new Error('TotalGestSyncOrchestrator: dependencias invalidas');
    }

    if (!isOnline()) {
      showOfflineStatus();
      return;
    }

    repairInvalidEquipmentLocations(data);

    await migratePending({
      data: data,
      fields: opts.fields,
      uploadDataURL: opts.uploadDataURL
    });

    let errors = 0;
    let firstError = '';

    const collectionsResult = await runCollections({
      supabase: opts.supabase,
      order: opts.order,
      metadata: opts.metadata,
      data: data,
      snapshots: opts.snapshots,
      licenseSnapshot: opts.licenseSnapshot,
      junctionSnapshot: opts.junctionSnapshot,
      changedRows: opts.changedRows,
      runUpsert: opts.runUpsert,
      runLicenses: opts.runLicenses,
      runEncarregados: opts.runEncarregados,
      licenseToRow: opts.licenseToRow,
      missingColumn: opts.missingColumn,
      missingTable: opts.missingTable
    });
    errors += collectionsResult.errors;
    if (!firstError && collectionsResult.firstError) firstError = collectionsResult.firstError;

    const deleteResult = await runDelete({
      supabase: opts.supabase,
      order: opts.order,
      metadata: opts.metadata,
      data: data,
      snapshots: opts.snapshots,
      licenseSnapshot: opts.licenseSnapshot,
      junctionSnapshot: opts.junctionSnapshot,
      deletedIds: opts.deletedIds,
      missingTable: opts.missingTable
    });
    errors += deleteResult.errors;
    if (!firstError && deleteResult.firstError) firstError = deleteResult.firstError;

    finalize({
      errors: errors,
      firstError: firstError,
      showSyncStatus: opts.showSyncStatus,
      saveCache: opts.saveCache,
      showOfflineStatus: showOfflineStatus
    });
  }

  window.TotalGestSyncOrchestrator = { run: run };
})();
