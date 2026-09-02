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

  function selectVisibleServicesFromData(options) {
    options = options || {};
    const data = options.data || {};
    return selectVisibleServices({
      services: data.servicos || [],
      user: options.user || null,
      encarregados: data.encarregados || [],
      funcionarios: data.funcionarios || []
    });
  }

  function selectPendingSpecialtyServices(options) {
    options = options || {};
    const role = options.role || '';
    const services = Array.isArray(options.services) ? options.services : [];
    const getPendingTypes = typeof options.getPendingTypes === 'function' ? options.getPendingTypes : function () { return []; };
    const canSeePending = role === 'admin' || role === 'subadmin' || role === 'encarregado';
    const pendingServices = canSeePending
      ? services
          .filter(service => service.status === 'concluído')
          .map(service => ({ number: service.numeroRegisto || '', types: getPendingTypes(service.id) || [] }))
          .filter(item => item.types.length > 0)
      : [];
    return { canSeePending, pendingServices };
  }

  function selectPendingSpecialtyServicesForUser(options) {
    options = options || {};
    return selectPendingSpecialtyServices({
      services: options.services,
      role: options.user?.role || '',
      getPendingTypes: options.getPendingTypes
    });
  }

  function prepareServiceRow(options) {
    options = options || {};
    const service = options.service || {};
    const getEmployeeName = typeof options.getEmployeeName === 'function' ? options.getEmployeeName : function (id) { return id || ''; };
    const getClientName = typeof options.getClientName === 'function' ? options.getClientName : function (id) { return id || ''; };
    const generateNumber = typeof options.generateNumber === 'function' ? options.generateNumber : function () { return ''; };
    const hasMaterials = typeof options.hasMaterials === 'function' ? options.hasMaterials : function () { return false; };
    const isErpActive = typeof options.isErpActive === 'function' ? options.isErpActive : function () { return false; };
    const administrators = Array.isArray(options.administrators) ? options.administrators : [];
    const employeeIds = assignedIds(service);
    const administrator = administrators.find(item => item.id === service.adminId);

    return {
      employeeName: employeeIds.length ? employeeIds.map(getEmployeeName).join('<br>') : 'Todos',
      clientName: getClientName(service.clienteId),
      number: service.numeroRegisto || generateNumber(),
      hasMaterials: hasMaterials(service.id),
      erpActive: isErpActive(administrator),
      provider: administrator?.integracaoFaturacao?.provider || ''
    };
  }

  function createServiceRowPreparer(options) {
    options = options || {};
    return function (service) {
      return prepareServiceRow({
        service: service || {},
        administrators: options.administrators,
        getEmployeeName: options.getEmployeeName,
        getClientName: options.getClientName,
        generateNumber: options.generateNumber,
        hasMaterials: options.hasMaterials,
        isErpActive: options.isErpActive
      });
    };
  }

  function filterAndSortServices(options) {
    options = options || {};
    const services = Array.isArray(options.services) ? options.services : [];
    const applyFilterSort = typeof options.applyFilterSort === 'function' ? options.applyFilterSort : function (_, items) { return items; };
    const getTableState = typeof options.getTableState === 'function' ? options.getTableState : function () { return {}; };
    const getClientName = typeof options.getClientName === 'function' ? options.getClientName : function (id) { return id || ''; };
    let visibleServices = applyFilterSort('servicos', services,
      ['numeroRegisto', 'descricao', 'status', service => getClientName(service.clienteId)],
      {
        data: (a, b) => (a.data || '') + (a.hora || '') < (b.data || '') + (b.hora || '') ? -1 : 1,
        status: (a, b) => (a.status || '').localeCompare(b.status || '')
      });
    if (!getTableState('servicos').sortCol) {
      visibleServices.sort((a, b) => (a.data + a.hora) < (b.data + b.hora) ? 1 : -1);
    }
    return visibleServices;
  }

  window.TotalGestServicesSelection = {
    selectVisibleServices: selectVisibleServices,
    selectVisibleServicesFromData: selectVisibleServicesFromData,
    selectPendingSpecialtyServices: selectPendingSpecialtyServices,
    selectPendingSpecialtyServicesForUser: selectPendingSpecialtyServicesForUser,
    prepareServiceRow: prepareServiceRow,
    createServiceRowPreparer: createServiceRowPreparer,
    filterAndSortServices: filterAndSortServices
  };
})();
