/* Total Gest — orquestração do conteúdo do modal de perfil. */
(function () {
  'use strict';

  function render(options) {
    const opts = options || {};
    const user = opts.user || null;
    if (!user) return null;

    if (user.role === 'superadmin') {
      return window.TotalGestProfileModalSuperadmin.render({
        config: opts.getConfig(),
        bankData: opts.getBankData() || {},
        getConfig: opts.getConfig
      });
    }

    if (user.role === 'admin' && opts.getAdmin()?.ehDistribuidor) {
      return window.TotalGestProfileModalDistributor.render({
        admin: opts.getAdmin(),
        employee: (opts.employees || []).find(function (employee) { return employee.id === user.id; }) || null
      });
    }

    if (user.role === 'admin' || user.role === 'subadmin') {
      return window.TotalGestProfileModalAdmin.render({
        admin: opts.getAdmin(),
        employee: (opts.employees || []).find(function (employee) { return employee.id === user.id; }) || null,
        municipalHolidays: opts.municipalHolidays,
        contractsModuleEnabled: opts.contractsModuleEnabled
      });
    }

    return window.TotalGestProfileModalWorker.render({
      employee: (opts.employees || []).find(function (employee) { return employee.id === user.id; }) ||
        (opts.foremen || []).find(function (foreman) { return foreman.id === user.id; }) || null,
      role: user.role
    });
  }

  window.TotalGestProfileModal = { render: render };
})();
