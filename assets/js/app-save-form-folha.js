/* Total Gest — orquestração da gravação do formulário de folha de obra. */
(function () {
  'use strict';

  async function run(options) {
    const opts = options || {};

    const context = window.TotalGestSaveFormFolhaContext.prepare({
      document: opts.document,
      data: opts.data,
      user: opts.user,
      generateId: opts.generateId,
      showError: opts.showError,
      showAlert: opts.showAlert,
      hoursCorrectedManually: opts.hoursCorrectedManually,
      hoursForServiceOrder: opts.hoursForServiceOrder,
      hoursForWork: opts.hoursForWork
    });
    if (!context.ok) return { ok: false };

    const signature = await window.TotalGestSaveFormFolhaSignature.prepare({
      adminId: context.adminId,
      editingId: opts.editingId,
      captureSignature: opts.captureSignature,
      generateId: opts.generateId,
      uploadImage: opts.uploadImage
    });

    const preparedObject = window.TotalGestSaveFormFolhaObject.prepare({
      document: opts.document,
      clientId: context.clientId,
      localId: context.localId,
      workDescription: context.workDescription,
      hours: context.hours,
      employeeId: context.employeeId,
      signatureBase64: signature.base64,
      signaturePath: signature.path,
      adminId: context.adminId,
      sheetId: signature.id,
      isEdit: opts.isEdit,
      showAlert: opts.showAlert
    });
    if (!preparedObject.ok) return { ok: false };

    const sheet = preparedObject.value;
    const assist = window.TotalGestSaveFormFolhaAssist.prepare({
      document: opts.document,
      data: opts.data,
      serviceOrderId: sheet.servicoId,
      showAlert: opts.showAlert
    });
    if (!assist.ok) return { ok: false };

    const pendingConsumption = window.TotalGestSaveFormFolhaConsumos.prepare({
      document: opts.document,
      extraMaterials: opts.extraMaterials
    });

    window.TotalGestSaveFormFolhaManutencao.apply({
      data: opts.data,
      sheet: sheet,
      isEdit: opts.isEdit,
      generateId: opts.generateId,
      getToday: opts.getToday,
      advancePeriodicity: opts.advancePeriodicity,
      notify: opts.notify
    });

    window.TotalGestSaveFormFolhaAssist.apply({
      assistance: assist.assistance,
      newState: assist.newState
    });

    window.TotalGestSaveFormFolhaPonto.apply({
      data: opts.data,
      sheet: sheet
    });

    return {
      ok: true,
      value: sheet,
      pendingConsumption: pendingConsumption
    };
  }

  window.TotalGestSaveFormFolha = { run: run };
})();
