/* Total Gest — reconstrução dos snapshots locais de sincronização
 * Reconstrói o último estado confirmado sem efetuar qualquer chamada de rede.
 */
(function () {
  'use strict';

  function rebuild(options) {
    const opts = options || {};
    const data = opts.data || {};
    const order = opts.order || [];
    const metadata = opts.metadata || {};
    const licenseToRow = opts.licenseToRow;
    const setSnapshots = opts.setSnapshots;
    const setLicenseSnapshot = opts.setLicenseSnapshot;
    const setJunctionSnapshot = opts.setJunctionSnapshot;

    if (typeof licenseToRow !== 'function' || typeof setSnapshots !== 'function' ||
        typeof setLicenseSnapshot !== 'function' || typeof setJunctionSnapshot !== 'function') {
      throw new Error('TotalGestSyncSnapshots: dependencias invalidas');
    }

    const snapshots = {};
    setSnapshots(snapshots);
    for (const collection of order) {
      const snapshot = new Map();
      for (const item of (data[collection] || [])) {
        snapshot.set(item.id, JSON.stringify(metadata[collection].to(item)));
      }
      snapshots[collection] = snapshot;
    }

    const licenseSnapshot = new Map();
    setLicenseSnapshot(licenseSnapshot);
    for (const admin of (data.administradores || [])) {
      if (admin.licenca) {
        licenseSnapshot.set(admin.id, JSON.stringify(licenseToRow(admin.id, admin.licenca)));
      }
    }

    const junctionSnapshot = new Map();
    setJunctionSnapshot(junctionSnapshot);
    for (const encarregado of (data.encarregados || [])) {
      junctionSnapshot.set(encarregado.id, JSON.stringify((encarregado.funcionariosIds || []).slice().sort()));
    }
  }

  window.TotalGestSyncSnapshots = { rebuild: rebuild };
})();
