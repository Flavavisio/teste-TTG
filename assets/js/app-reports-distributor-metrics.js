/* Total Gest — métricas do distribuidor para Relatórios. */
(function () {
  'use strict';

  function calculateOverview(options) {
    const opts = options || {};
    const admins = opts.admins || [];
    const distributorId = opts.distributorId;
    const clients = admins.filter(a => a.distribuidorId === distributorId);
    const active = clients.filter(c => c.licenca && c.ativo !== false && opts.isLicenseValid(c.licenca.dataExpiracao));
    return {
      clients: clients,
      active: active
    };
  }

  function calculateClient(options) {
    const opts = options || {};
    const client = opts.client || {};
    const data = opts.data || {};
    const funcionarios = (data.funcionarios || []).filter(f => f.adminId === client.id && f.role !== 'admin' && f.role !== 'superadmin').length;
    const temContratos = opts.contractsActive(client);
    const temFrota = opts.fleetActive(client);
    const temArmazem = opts.warehouseActive(client);
    const temCrm = opts.crmActive(client);
    const valorBase = client.precoDistribuidorCobrado != null
      ? client.precoDistribuidorCobrado
      : (client.licenca ? parseFloat(opts.getPlanValue(client.licenca.plano)) : 0);
    const valorAddons =
      (temContratos ? (client.contratosPlano === 'anual' ? opts.contractsAnnualPrice / 12 : opts.contractsMonthlyPrice) : 0)
      + (temFrota ? (client.frotaPlano === 'anual' ? opts.fleetAnnualPrice / 12 : opts.fleetMonthlyPrice) : 0)
      + (temArmazem ? (client.armazemPlano === 'anual' ? opts.warehouseAnnualPrice / 12 : opts.warehouseMonthlyPrice) : 0)
      + (temCrm ? (client.crmPlano === 'anual' ? opts.crmAnnualPrice / 12 : opts.crmMonthlyPrice) : 0);
    return {
      funcionarios: funcionarios,
      temContratos: temContratos,
      temFrota: temFrota,
      temArmazem: temArmazem,
      temCrm: temCrm,
      valorCliente: valorBase + valorAddons
    };
  }

  window.TotalGestReportsDistributorMetrics = {
    calculateOverview: calculateOverview,
    calculateClient: calculateClient
  };
})();
