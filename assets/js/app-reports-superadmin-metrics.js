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

  window.TotalGestReportsSuperadminMetrics = { calculate: calculate, calculateCompany: calculateCompany };
})();
