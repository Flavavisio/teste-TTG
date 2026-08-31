/* Total Gest — orquestração do carregamento inicial
 * Coordena cache offline, contexto, queries, transformação, snapshots e cache final.
 */
(function () {
  'use strict';

  async function run(options) {
    const opts = options || {};
    await opts.waitForIdle();

    if (!opts.isOnline()) {
      const cached = opts.loadCache();
      if (cached) {
        opts.setData(cached);
        opts.restoreSnapshot();
        opts.showOffline();
        return cached;
      }
    }

    const target = opts.emptyData();
    const tables = opts.order.map(function (collection) { return opts.metadata[collection].tabela; })
      .concat(['licencas', 'encarregado_funcionarios']);

    const pointSince = opts.cutoffMonths(6);
    const servicesSince = opts.cutoffMonths(3);
    const sheetsSince = opts.cutoffMonths(3);
    const auditSince = opts.cutoffMonths(6);
    opts.setPointSince(pointSince);
    opts.setServicesSince(servicesSince);
    opts.setSheetsSince(sheetsSince);

    const context = opts.resolveContext({
      tenantIdParam: opts.tenantIdParam,
      superAdminParam: opts.superAdminParam,
      clienteIdParam: opts.clienteIdParam,
      user: opts.user
    });

    let results;
    try {
      results = await opts.fetchAll({
        supabase: opts.supabase,
        tables: tables,
        tenantId: context.tenantId,
        superAdmin: context.superAdmin,
        clienteId: context.clienteId,
        pontoSince: pointSince,
        servicesSince: servicesSince,
        sheetsSince: sheetsSince,
        auditSince: auditSince
      });
    } catch (error) {
      const cached = opts.loadCache();
      if (cached) {
        opts.setData(cached);
        opts.restoreSnapshot();
        opts.showOffline();
        return cached;
      }
      throw error;
    }

    opts.transform({
      tables: tables,
      results: results,
      order: opts.order,
      metadata: opts.metadata,
      target: target,
      licenseFromRow: opts.licenseFromRow
    });

    opts.setData(target);
    opts.rebuildSnapshots();
    opts.saveCache();
    return target;
  }

  window.TotalGestLoadOrchestrator = { run: run };
})();
