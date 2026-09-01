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

  function calculateClientSummary(options) {
    const opts = options || {};
    const clients = opts.clients || [];
    const rows = [];
    let totalCobrado = 0;

    clients.forEach(function (client) {
      const metrics = calculateClient(Object.assign({}, opts, { client: client }));
      totalCobrado += metrics.valorCliente;
      rows.push({
        empresa: client.empresa || '-',
        nome: client.nome,
        planoLabel: typeof opts.planLabel === 'function' ? opts.planLabel(client) : '',
        dataExp: typeof opts.expiryLabel === 'function' ? opts.expiryLabel(client) : '-',
        funcionarios: metrics.funcionarios,
        temContratos: metrics.temContratos,
        temFrota: metrics.temFrota,
        temArmazem: metrics.temArmazem,
        temCrm: metrics.temCrm,
        valorCliente: metrics.valorCliente
      });
    });

    return { rows: rows, totalCobrado: totalCobrado };
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

  function calculateAdminContracts(options) {
    const opts = options || {};
    const data = opts.data || {};
    const contracts = (data.contratos || []).filter(c => c.adminId === opts.adminId);
    let emDia = 0, aVencer = 0, vencidos = 0, valor = 0;
    contracts.forEach(c => {
      const chave = opts.maintenanceState(opts.nextMaintenance(c)).chave;
      if (chave === 'vencido') vencidos++;
      else if (chave === 'a_vencer') aVencer++;
      else if (chave === 'em_dia') emDia++;
      valor += opts.toNumber(c.valor);
    });
    return { contracts: contracts, emDia: emDia, aVencer: aVencer, vencidos: vencidos, valor: valor };
  }

  function calculateAdminOperations(options) {
    const opts = options || {}, data = opts.data || {}, admin = opts.admin || {}, adminId = admin.id;
    const totalLocais = (data.locais || []).filter(l => l.adminId === adminId).length;
    const totalEquip = (data.equipamentos || []).filter(e => e.adminId === adminId).length;
    const totalRegistos = (data.registosManutencao || []).filter(r => r.adminId === adminId).length;
    const moduloAtivoTxt = opts.contractsActive(admin) ? ('Ativo (' + (admin.contratosPlano === 'demo' ? 'Demo' : admin.contratosPlano === 'anual' ? 'Anual' : 'Mensal') + ')') : 'Inativo';
    const folhasOT = (data.folhasObra || []).filter(f => f.adminId === adminId && f.contratoId).length;
    const frotaStats = opts.countFleet((data.veiculos || []).filter(v => v.adminId === adminId));
    const intervencoes = (data.veiculoIntervencoes || []).filter(i => i.adminId === adminId);
    const totalIntervencoes = intervencoes.length;
    const gastoVeiculos = intervencoes.reduce((s, i) => s + (Number(i.custo) || 0), 0);
    const totalSinistros = (data.veiculoSinistros || []).filter(s => s.adminId === adminId).length;
    const ajudasAdmin = (data.ajudas || []).filter(a => a.adminId === adminId);
    return { totalLocais,totalEquip,totalRegistos,moduloAtivoTxt,folhasOT,frotaStats,totalIntervencoes,gastoVeiculos,totalSinistros,ajudasAdmin,ajPend:ajudasAdmin.filter(a=>a.status==='pendente').length,ajConcl:ajudasAdmin.filter(a=>(a.status||'').toLowerCase().includes('conclu')).length };
  }

  function calculateAdminSummary(options) {
    const opts = options || {};
    const admin = opts.admin || {};
    const overview = calculateAdminOverview({ data: opts.data, adminId: admin.id });
    const contracts = calculateAdminContracts({
      data: opts.data,
      adminId: admin.id,
      maintenanceState: opts.maintenanceState,
      nextMaintenance: opts.nextMaintenance,
      toNumber: overview.numOrd
    });
    const operations = calculateAdminOperations({
      data: opts.data,
      admin: admin,
      contractsActive: opts.contractsActive,
      countFleet: opts.countFleet
    });

    return {
      totalFunc: overview.totalFunc,
      totalEncarregados: overview.totalEncarregados,
      totalCli: overview.totalCli,
      gastoFunc: overview.gastoFunc,
      gastoEnc: overview.gastoEnc,
      gastoTotal: overview.gastoTotal,
      totalOS: overview.totalOS,
      osPendentes: overview.osPendentes,
      osAndamento: overview.osAndamento,
      osConcluidas: overview.osConcluidas,
      totalPonto: overview.totalPonto,
      totalPedidos: overview.totalPedidos,
      pedPend: overview.pedPend,
      totalFolhas: overview.totalFolhas,
      folhasOT: operations.folhasOT,
      totalReqs: overview.totalReqs,
      reqPend: overview.reqPend,
      moduloAtivoTxt: operations.moduloAtivoTxt,
      contratosCount: contracts.contracts.length,
      ctEmDia: contracts.emDia,
      ctAVencer: contracts.aVencer,
      ctVencidos: contracts.vencidos,
      totalLocais: operations.totalLocais,
      totalEquip: operations.totalEquip,
      totalRegistos: operations.totalRegistos,
      ctValor: contracts.valor,
      frotaTotal: operations.frotaStats.total,
      frotaEmDia: operations.frotaStats.emDia,
      frotaAVencer: operations.frotaStats.aVencer,
      frotaVencido: operations.frotaStats.vencido,
      totalIntervencoes: operations.totalIntervencoes,
      totalSinistros: operations.totalSinistros,
      gastoVeiculos: operations.gastoVeiculos,
      suporteTotal: operations.ajudasAdmin.length,
      ajPend: operations.ajPend,
      ajConcl: operations.ajConcl
    };
  }

  window.TotalGestReportsDistributorMetrics = {
    calculateOverview: calculateOverview,
    calculateClient: calculateClient,
    calculateClientSummary: calculateClientSummary,
    calculateAdminOverview: calculateAdminOverview,
    calculateAdminContracts: calculateAdminContracts,
    calculateAdminOperations: calculateAdminOperations,
    calculateAdminSummary: calculateAdminSummary
  };
})();
