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

  window.TotalGestReportsSuperadminMetrics = { calculate: calculate };
})();
