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

  window.TotalGestReportsModuleMetrics = {
    calculateContracts: calculateContracts
  };
})();
