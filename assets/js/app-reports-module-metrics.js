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

  function calculateWarehouse(options) {
    const opts = options || {};
    const admins = opts.admins || [];
    const isActive = opts.isActive;
    const active = admins.filter(a => a.id !== 'superadmin' && isActive(a));
    const monthly = active.filter(a => a.armazemPlano === 'mensal').length;
    const annual = active.filter(a => a.armazemPlano === 'anual').length;
    const demos = active.filter(a => a.armazemPlano === 'demo').length;
    return {
      active: active,
      monthly: monthly,
      annual: annual,
      demos: demos,
      revenue: monthly * opts.monthlyPrice + annual * opts.annualPrice
    };
  }

  function calculateNotifications(options) {
    const opts = options || {};
    const admins = opts.admins || [];
    const isActive = opts.isActive;
    const active = admins.filter(a => a.id !== 'superadmin' && isActive(a));
    const monthly = active.filter(a => a.notificacoesPlano === 'mensal').length;
    const annual = active.filter(a => a.notificacoesPlano === 'anual').length;
    const demos = active.filter(a => a.notificacoesPlano === 'demo').length;
    return {
      active: active,
      monthly: monthly,
      annual: annual,
      demos: demos,
      revenue: monthly * opts.monthlyPrice + annual * opts.annualPrice
    };
  }

  function calculateCrm(options) {
    const opts = options || {};
    const admins = opts.admins || [];
    const isActive = opts.isActive;
    const active = admins.filter(a => a.id !== 'superadmin' && isActive(a));
    const monthly = active.filter(a => a.crmPlano === 'mensal').length;
    const annual = active.filter(a => a.crmPlano === 'anual').length;
    const demos = active.filter(a => a.crmPlano === 'demo').length;
    return {
      active: active,
      monthly: monthly,
      annual: annual,
      demos: demos,
      revenue: monthly * opts.monthlyPrice + annual * opts.annualPrice
    };
  }

  function card(icon, title, metrics) {
    return {
      icon: icon,
      title: title,
      activeCount: metrics.active.length,
      monthly: metrics.monthly,
      annual: metrics.annual,
      demos: metrics.demos,
      revenue: metrics.revenue
    };
  }

  function calculateOverview(options) {
    const opts = options || {};
    const admins = opts.admins || [];
    const contracts = calculateContracts({
      admins: admins,
      monthlyPrice: opts.contractsMonthlyPrice,
      annualPrice: opts.contractsAnnualPrice
    });
    const fleet = calculateFleet({
      admins: admins,
      monthlyPrice: opts.fleetMonthlyPrice,
      annualPrice: opts.fleetAnnualPrice
    });
    const warehouse = calculateWarehouse({
      admins: admins,
      isActive: opts.warehouseActive,
      monthlyPrice: opts.warehouseMonthlyPrice,
      annualPrice: opts.warehouseAnnualPrice
    });
    const notifications = calculateNotifications({
      admins: admins,
      isActive: opts.notificationsActive,
      monthlyPrice: opts.notificationsMonthlyPrice,
      annualPrice: opts.notificationsAnnualPrice
    });
    const crm = calculateCrm({
      admins: admins,
      isActive: opts.crmActive,
      monthlyPrice: opts.crmMonthlyPrice,
      annualPrice: opts.crmAnnualPrice
    });

    return {
      cards: [
        card('fa-file-signature', 'Licenças de Contratos de Manutenção', contracts),
        card('fa-car', 'Licenças de Frota', fleet),
        card('fa-boxes', 'Licenças de Armazém', warehouse),
        card('fa-bell', 'Licenças de Notificações', notifications),
        card('fa-bullseye', 'Licenças de CRM Comercial + Assist', crm)
      ],
      revenues: {
        contracts: contracts.revenue,
        fleet: fleet.revenue,
        warehouse: warehouse.revenue,
        notifications: notifications.revenue,
        crm: crm.revenue
      }
    };
  }

  window.TotalGestReportsModuleMetrics = {
    calculateContracts: calculateContracts,
    calculateFleet: calculateFleet,
    calculateWarehouse: calculateWarehouse,
    calculateNotifications: calculateNotifications,
    calculateCrm: calculateCrm,
    calculateOverview: calculateOverview
  };
})();
