/* Total Gest — pós-persistência dos formulários comuns. */
(function () {
  'use strict';

  async function run(options) {
    const opts = options || {};
    let value = opts.value;

    const persistence = opts.persist.apply({
      entity: opts.entity,
      data: opts.data,
      value: value,
      isEdit: opts.isEdit,
      editingId: opts.editingId,
      generateId: opts.generateId
    });
    if (!persistence.ok) return { ok: false };

    value = persistence.value;
    const list = persistence.list;
    const oldService = persistence.oldService;
    const oldEmployee = persistence.oldEmployee;

    if (opts.entity === 'funcionario') opts.data.funcionarios = list;
    else if (opts.entity === 'cliente') opts.data.clientes = list;
    else if (opts.entity === 'servico') {
      opts.data.servicos = list;
      opts.serviceNotifications.run({
        value: value,
        oldService: oldService,
        data: opts.data,
        isEdit: opts.isEdit,
        clientName: opts.clientName,
        notify: opts.notify,
        formatEuro: opts.formatEuro
      });
    } else if (opts.entity === 'folha') {
      opts.data.folhasObra = list;
    }

    if (opts.entity === 'folha') {
      opts.sheetUsage.apply({
        data: opts.data,
        value: value,
        isEdit: opts.isEdit,
        editingId: opts.editingId,
        pendingConsumption: opts.getPendingConsumption(),
        pendingWork: opts.getPendingWork(),
        applyConsumption: opts.applyConsumption
      });
      opts.clearPendingConsumption();

      opts.sheetOsPending.apply({
        value: value,
        pending: opts.getPendingServiceOrder(),
        data: opts.data,
        clearPending: opts.clearPendingServiceOrder,
        pendingSpecialty: opts.pendingSpecialty,
        completeService: opts.completeService,
        openSpecialtyQueue: opts.openSpecialtyQueue,
        saveData: opts.saveData,
        renderAgenda: opts.renderAgenda,
        renderPoint: opts.renderPoint,
        showAlert: opts.showAlert
      });

      opts.sheetWorkPending.apply({
        value: value,
        pending: opts.getPendingWork(),
        data: opts.data,
        clearPending: opts.clearPendingWork,
        getToday: opts.getToday,
        saveData: opts.saveData,
        renderAll: opts.renderAll,
        showAlert: opts.showAlert
      });
    }

    await opts.finalize.run({
      data: opts.data,
      value: value,
      entity: opts.entity,
      isEdit: opts.isEdit,
      editingId: opts.editingId,
      newWorkId: opts.newWorkId,
      saveData: opts.saveData,
      showAlert: opts.showAlert,
      audit: opts.audit,
      markServiceWorkCreated: opts.markServiceWorkCreated,
      closeModal: opts.closeModal,
      renderAll: opts.renderAll
    });

    await opts.auth.run({
      entity: opts.entity,
      data: opts.data,
      value: value,
      isEdit: opts.isEdit,
      oldEmployee: oldEmployee,
      saveData: opts.saveData,
      showAlert: opts.showAlert,
      createAuth: opts.createAuth,
      clientTechnicalEmail: opts.clientTechnicalEmail
    });

    return { ok: true, value: value };
  }

  window.TotalGestSaveFormPostPersist = { run: run };
})();
