/* Total Gest — seleção de ordens de serviço visíveis por perfil */
(function () {
  'use strict';

  function assignedIds(service) {
    if (service && service.funcionariosIds && service.funcionariosIds.length) {
      return service.funcionariosIds;
    }
    return service && service.funcionarioId ? [service.funcionarioId] : [];
  }

  function selectVisibleServices(options) {
    options = options || {};
    const user = options.user || null;
    const encarregados = options.encarregados || [];
    const funcionarios = options.funcionarios || [];
    let services = options.services || [];

    if (user && (user.role === 'admin' || user.role === 'subadmin')) {
      const tenantId = user.role === 'admin' ? user.id : user.adminId;
      services = services.filter(service => service.adminId === tenantId);
    } else if (user && user.role === 'encarregado') {
      const encarregado = encarregados.find(item => item.id === user.id);
      if (encarregado) {
        services = services.filter(service => {
          const ids = assignedIds(service);
          return service.adminId === encarregado.adminId &&
            (service.funcionarioId === null ||
              ids.includes(user.id) ||
              ids.some(id => encarregado.funcionariosIds?.includes(id)));
        });
      } else {
        services = [];
      }
    } else if (user && user.role === 'funcionario') {
      const funcionario = funcionarios.find(item => item.id === user.id);
      const adminId = funcionario?.adminId;
      if (adminId) {
        services = services.filter(service => {
          const ids = assignedIds(service);
          return service.adminId === adminId &&
            (service.funcionarioId === null || ids.includes(user.id));
        });
      } else {
        services = [];
      }
    }

    if (user?.role === 'superadmin') {
      services = [];
    }

    return services;
  }

  window.TotalGestServicesSelection = {
    selectVisibleServices: selectVisibleServices
  };
})();
