/* Total Gest — dispatcher dos handlers de gravação por entidade. */
(function () {
  'use strict';

  async function run(options) {
    const opts = options || {};
    const entity = opts.entity;

    if (entity === 'funcionario') {
      const result = await opts.employeeHandler.run({
        document: opts.document,
        data: opts.data,
        user: opts.user,
        isEdit: opts.isEdit,
        editingId: opts.editingId,
        showError: opts.showError,
        verifyLimit: opts.verifyEmployeeLimit,
        generateId: opts.generateId,
        saveData: opts.saveData,
        audit: opts.audit,
        closeModal: opts.closeModal,
        renderAll: opts.renderAll,
        createAuth: opts.createAuth,
        vehicleAssigned: opts.vehicleAssigned,
        emailRegistered: opts.emailRegistered,
        showAlert: opts.showAlert
      });
      if (result.stop) return { stop: true };
      return { stop: false, value: result.value };
    }

    if (entity === 'cliente') {
      const result = opts.clientHandler.prepare({
        document: opts.document,
        data: opts.data,
        user: opts.user,
        editingId: opts.editingId,
        showAlert: opts.showAlert
      });
      if (!result.ok) return { stop: true };
      return { stop: false, value: result.value };
    }

    if (entity === 'servico') {
      const result = await opts.serviceHandler.run({
        document: opts.document,
        data: opts.data,
        user: opts.user,
        isEdit: opts.isEdit,
        item: opts.item,
        editingId: opts.editingId,
        newWorkId: opts.newWorkId,
        approvingAssistanceId: opts.approvingAssistanceId,
        tenantId: opts.tenantId,
        generateId: opts.generateId,
        selectedWorkTypes: opts.selectedWorkTypes,
        blockIfAbsent: opts.blockIfAbsent,
        showAlert: opts.showAlert,
        showError: opts.showError,
        showConfirm: opts.showConfirm,
        timeToMinutes: opts.timeToMinutes,
        employeeName: opts.employeeName,
        generateRegistrationNumber: opts.generateRegistrationNumber,
        validation: opts.serviceValidation,
        context: opts.serviceContext,
        object: opts.serviceObject,
        conflicts: opts.serviceConflicts,
        registration: opts.serviceRegistration
      });
      if (!result.ok) return { stop: true };
      return { stop: false, value: result.value };
    }

    if (entity === 'folha') {
      const result = await opts.sheetHandler.run({
        document: opts.document,
        data: opts.data,
        user: opts.user,
        generateId: opts.generateId,
        showError: opts.showError,
        showAlert: opts.showAlert,
        hoursCorrectedManually: opts.hoursCorrectedManually,
        hoursForServiceOrder: opts.hoursForServiceOrder,
        hoursForWork: opts.hoursForWork,
        editingId: opts.editingId,
        captureSignature: opts.captureSignature,
        uploadImage: opts.uploadImage,
        isEdit: opts.isEdit,
        getToday: opts.getToday,
        advancePeriodicity: opts.advancePeriodicity,
        notify: opts.notify,
        extraMaterials: opts.extraMaterials
      });
      if (!result.ok) return { stop: true };
      opts.setPendingConsumption(result.pendingConsumption);
      opts.clearExtraMaterials();
      return { stop: false, value: result.value };
    }

    if (entity === 'requisicao') {
      opts.requestHandler.run({
        document: opts.document,
        data: opts.data,
        user: opts.user,
        isEdit: opts.isEdit,
        editingId: opts.editingId,
        generateId: opts.generateId,
        saveData: opts.saveData,
        closeModal: opts.closeModal,
        renderAll: opts.renderAll,
        showAlert: opts.showAlert,
        FileReader: opts.FileReader
      });
      return { stop: true };
    }

    if (entity === 'fornecedor') {
      opts.supplierHandler.run({
        document: opts.document,
        user: opts.user,
        isEdit: opts.isEdit,
        showAlert: opts.showAlert,
        saveWarehouse: opts.saveWarehouse
      });
      return { stop: true };
    }

    if (entity === 'artigo') {
      opts.articleHandler.run({
        document: opts.document,
        user: opts.user,
        isEdit: opts.isEdit,
        showAlert: opts.showAlert,
        intVal: opts.intVal,
        saveWarehouse: opts.saveWarehouse
      });
      return { stop: true };
    }

    if (entity === 'obra') {
      opts.workHandler.run({
        document: opts.document,
        data: opts.data,
        user: opts.user,
        isEdit: opts.isEdit,
        editingId: opts.editingId,
        generateId: opts.generateId,
        showError: opts.showError,
        showAlert: opts.showAlert,
        saveWarehouse: opts.saveWarehouse,
        confirm: opts.confirmDialog,
        createServiceOrder: opts.createServiceOrder
      });
      return { stop: true };
    }

    opts.closeModal();
    return { stop: true };
  }

  window.TotalGestSaveFormDispatch = { run: run };
})();
