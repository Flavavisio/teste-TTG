/* Total Gest — orquestração da gravação de Ordem de Serviço. */
(function () {
  'use strict';

  async function run(options) {
    const opts = options || {};

    const validation = opts.validation.validate({
      document: opts.document,
      data: opts.data,
      user: opts.user,
      isEdit: opts.isEdit,
      item: opts.item,
      showAlert: opts.showAlert,
      showError: opts.showError
    });
    if (!validation.ok) return { ok: false };

    const context = opts.context.prepare({
      document: opts.document,
      data: opts.data,
      user: opts.user,
      isEdit: opts.isEdit,
      editingId: opts.editingId,
      tenantId: opts.tenantId,
      generateId: opts.generateId,
      showAlert: opts.showAlert,
      showConfirm: opts.showConfirm
    });
    if (!context.ok) return { ok: false };

    let value = opts.object.prepare({
      document: opts.document,
      employeeId: context.employeeId,
      employeeIds: context.employeeIds,
      existingOrder: context.existingOrder,
      newWorkId: opts.newWorkId,
      localId: context.localId,
      adminId: context.adminId,
      selectedWorkTypes: opts.selectedWorkTypes,
      approvingAssistanceId: opts.approvingAssistanceId,
      editingId: opts.editingId
    });

    const conflicts = opts.conflicts.validate({
      value: value,
      data: opts.data,
      user: opts.user,
      isEdit: opts.isEdit,
      editingId: opts.editingId,
      blockIfAbsent: opts.blockIfAbsent,
      showAlert: opts.showAlert,
      showConfirm: opts.showConfirm,
      timeToMinutes: opts.timeToMinutes,
      employeeName: opts.employeeName
    });
    if (!conflicts.ok) return { ok: false };

    value = await opts.registration.apply({
      value: conflicts.value,
      isEdit: opts.isEdit,
      generateRegistrationNumber: opts.generateRegistrationNumber
    });

    return { ok: true, value: value };
  }

  window.TotalGestSaveFormServico = { run: run };
})();
