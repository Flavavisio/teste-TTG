/* Total Gest — métricas de superadmin para Relatórios. */
(function () {
  'use strict';

  function calculate(options) {
    const opts = options || {};
    const admins = opts.admins || [];
    const data = opts.data || {};
    const empresas = admins.filter(a => a.id !== 'superadmin');
    const now = Date.now();
    const ativo = a => !!(a.licenca && a.ativo !== false && a.licenca.dataExpiracao && a.licenca.dataExpiracao > now);
    const empresasAtivas = empresas.filter(ativo).length;
    const expiramEm10Dias = empresas.filter(a => a.licenca && a.licenca.dataExpiracao > now && (a.licenca.dataExpiracao - now) <= 10 * 86400000).length;
    const totalFuncionarios = (data.funcionarios || []).filter(f => f.role !== 'admin' && f.role !== 'superadmin').length;
    const totalEncarregados = (data.encarregados || []).length;
    const addonsAtivos = empresas.filter(a => opts.contractsActive(a)).length
      + empresas.filter(a => opts.fleetActive(a)).length
      + empresas.filter(a => opts.warehouseActive(a)).length
      + empresas.filter(a => opts.crmActive(a)).length
      + empresas.filter(a => opts.erpActive(a)).length;
    let receitaRecorrente = 0;
    empresas.forEach(a => {
      if (ativo(a)) receitaRecorrente += opts.baseValueCharged(a);
      if (opts.contractsActive(a)) receitaRecorrente += (a.contratosPlano === 'anual' ? opts.contractsAnnualPrice : opts.contractsMonthlyPrice);
      if (opts.fleetActive(a)) receitaRecorrente += (a.frotaPlano === 'anual' ? opts.fleetAnnualPrice : opts.fleetMonthlyPrice);
      if (opts.warehouseActive(a)) receitaRecorrente += (a.armazemPlano === 'anual' ? opts.warehouseAnnualPrice : opts.warehouseMonthlyPrice);
      if (opts.crmActive(a)) receitaRecorrente += (a.crmPlano === 'anual' ? opts.crmAnnualPrice : opts.crmMonthlyPrice);
      /* Assist incluído no CRM — não soma à parte. */
      if (opts.erpActive(a)) receitaRecorrente += (a.erpPlano === 'anual' ? opts.erpAnnualPrice : opts.erpMonthlyPrice);
    });

    return {
      empresas: empresas,
      empresasAtivas: empresasAtivas,
      expiramEm10Dias: expiramEm10Dias,
      totalFuncionarios: totalFuncionarios,
      totalEncarregados: totalEncarregados,
      addonsAtivos: addonsAtivos,
      receitaRecorrente: receitaRecorrente
    };
  }


  function calculateCompany(options) {
    const opts = options || {};
    const admin = opts.admin || {};
    const data = opts.data || {};
    const funcionarios = data.funcionarios ? data.funcionarios.filter(f => f.adminId === admin.id && f.role !== 'admin' && f.role !== 'superadmin').length : 0;
    const encarregados = data.encarregados ? data.encarregados.filter(e => e.adminId === admin.id).length : 0;
    const valorBase = admin.licenca && admin.ativo ? opts.baseValueCharged(admin) : 0;
    const temContratos = opts.contractsActive(admin);
    const temFrota = opts.fleetActive(admin);
    const temArmazem = opts.warehouseActive(admin);
    const temCrm = opts.crmActive(admin);
    const temErp = opts.erpActive(admin);
    const temRondas = opts.roundsActive(admin);
    const valorContratos = temContratos ? (admin.contratosPlano === 'anual' ? opts.contractsAnnualPrice : opts.contractsMonthlyPrice) : 0;
    const valorFrota = temFrota ? (admin.frotaPlano === 'anual' ? opts.fleetAnnualPrice : opts.fleetMonthlyPrice) : 0;
    const valorArmazem = temArmazem ? (admin.armazemPlano === 'anual' ? opts.warehouseAnnualPrice : opts.warehouseMonthlyPrice) : 0;
    const valorCrm = temCrm ? (admin.crmPlano === 'anual' ? opts.crmAnnualPrice : opts.crmMonthlyPrice) : 0;
    const valorErp = temErp ? (admin.erpPlano === 'anual' ? opts.erpAnnualPrice : opts.erpMonthlyPrice) : 0;
    /* Rondas: grátis por agora; cálculo preservado para quando tiver preço. */
    const valorRondas = temRondas ? (admin.rondasPlano === 'anual' ? opts.roundsAnnualPrice : opts.roundsMonthlyPrice) : 0;
    return {
      funcionarios: funcionarios,
      encarregados: encarregados,
      temContratos: temContratos,
      temFrota: temFrota,
      temArmazem: temArmazem,
      temCrm: temCrm,
      temErp: temErp,
      temRondas: temRondas,
      valorEmpresa: valorBase + valorContratos + valorFrota + valorArmazem + valorCrm + valorErp + valorRondas
    };
  }


  function calculateRevenueSummary(options) {
    const opts = options || {};
    const admins = (opts.admins || []).filter(a => a.id !== 'superadmin');
    let baseRevenue = 0;
    admins.forEach(a => {
      if (a.licenca && a.ativo !== false && a.licenca.dataExpiracao > Date.now()) baseRevenue += opts.baseValueCharged(a);
    });
    const modules = [
      { l: 'Licenças base', v: baseRevenue, c: '#2563eb' },
      { l: 'Contratos', v: opts.contractsRevenue, c: '#16a34a' },
      { l: 'Frota', v: opts.fleetRevenue, c: '#0ea5e9' },
      { l: 'Armazém', v: opts.warehouseRevenue, c: '#b45309' },
      { l: 'Notificações', v: opts.notificationsRevenue, c: '#e11d48' },
      { l: 'CRM + Assist', v: opts.crmRevenue, c: '#7c3aed' }
    ];
    return {
      modules: modules,
      maxModuleRevenue: Math.max(1, ...modules.map(m => m.v)),
      totalRevenue: baseRevenue + opts.contractsRevenue + opts.fleetRevenue + opts.warehouseRevenue + opts.notificationsRevenue + opts.crmRevenue
    };
  }

  window.TotalGestReportsSuperadminMetrics = { calculate: calculate, calculateCompany: calculateCompany, calculateRevenueSummary: calculateRevenueSummary };
})();
