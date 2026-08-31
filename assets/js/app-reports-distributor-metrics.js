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

  function calculateAdminOverview(options) {
    const opts = options || {}, data = opts.data || {}, adminId = opts.adminId;
    const totalFunc = data.funcionarios ? data.funcionarios.filter(f => f.adminId === adminId && f.role !== 'admin').length : 0;
    const totalCli = data.clientes ? data.clientes.filter(c => c.adminId === adminId).length : 0;
    const totalOS = data.servicos ? data.servicos.filter(s => s.adminId === adminId).length : 0;
    const osPend = data.servicos ? data.servicos.filter(s => s.adminId === adminId && s.status === 'pendente').length : 0;
    const totalPonto = data.ponto ? data.ponto.filter(p => p.adminId === adminId).length : 0;
    const totalPedidos = data.pedidos ? data.pedidos.filter(p => p.adminId === adminId).length : 0;
    const pedPend = data.pedidos ? data.pedidos.filter(p => p.adminId === adminId && p.status === 'pendente_aprov').length : 0;
    const totalFolhas = data.folhasObra ? data.folhasObra.filter(f => f.adminId === adminId).length : 0;
    const totalReqs = data.requisicoes ? data.requisicoes.filter(r => r.adminId === adminId).length : 0;
    const reqPend = data.requisicoes ? data.requisicoes.filter(r => r.adminId === adminId && r.status === 'pendente_aprov').length : 0;
    const totalEncarregados = data.encarregados ? data.encarregados.filter(e => e.adminId === adminId).length : 0;
    const numOrd = v => (v === '' || v == null) ? 0 : (Number(v) || 0);
    const gastoFunc = (data.funcionarios || []).filter(f => f.adminId === adminId && f.role === 'funcionario').reduce((s,f) => s + numOrd(f.ordenadoBruto),0);
    const gastoEnc = (data.encarregados || []).filter(e => e.adminId === adminId).reduce((s,e) => s + numOrd(e.ordenadoBruto),0);
    const osList = (data.servicos || []).filter(s => s.adminId === adminId);
    return { totalFunc,totalCli,totalOS,osPend,totalPonto,totalPedidos,pedPend,totalFolhas,totalReqs,reqPend,totalEncarregados,numOrd,gastoFunc,gastoEnc,gastoTotal:gastoFunc+gastoEnc,osList,osPendentes:osList.filter(s=>s.status==='pendente').length,osAndamento:osList.filter(s=>s.status==='em andamento'||s.status==='em_andamento').length,osConcluidas:osList.filter(s=>(s.status||'').toLowerCase().includes('conclu')).length };
  }

  window.TotalGestReportsDistributorMetrics = {
    calculateOverview: calculateOverview,
    calculateClient: calculateClient,
    calculateAdminOverview: calculateAdminOverview
  };
})();
