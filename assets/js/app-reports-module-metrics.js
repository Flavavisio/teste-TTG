/* Total Gest — métricas dos módulos para Relatórios. */
(function () {
  'use strict';

  function calculateContracts(options) {
    const opts = options || {};
    const admins = opts.admins || [];
    const now = Date.now();
    const active = admins.filter(a => a.contratosPlano && a.contratosExpiracao && a.contratosExpiracao > now);
    const monthly = active.filter(a => a.contratosPlano === 'mensal').length;
    const annual = active.filter(a => a.contratosPlano === 'anual').length;
    return {
      active: active,
      monthly: monthly,
      annual: annual,
      revenue: monthly * opts.monthlyPrice + annual * opts.annualPrice
    };
  }


  function calculateFleet(options) {
    const opts = options || {};
    const admins = opts.admins || [];
    const now = Date.now();
    const active = admins.filter(a => a.frotaPlano && a.frotaExpiracao && a.frotaExpiracao > now);
    const monthly = active.filter(a => a.frotaPlano === 'mensal').length;
    const annual = active.filter(a => a.frotaPlano === 'anual').length;
    return {
      active: active,
      monthly: monthly,
      annual: annual,
      revenue: monthly * opts.monthlyPrice + annual * opts.annualPrice
    };
  }

  window.TotalGestReportsModuleMetrics = {
    calculateContracts: calculateContracts,
    calculateFleet: calculateFleet
  };
})();
