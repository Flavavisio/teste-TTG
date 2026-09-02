/* Total Gest — aplicação de consumos e marcação de picagens usadas por uma folha. */
(function () {
  'use strict';

  function apply(options) {
    const opts = options || {};
    const data = opts.data || {};
    const value = opts.value || {};
    const isEdit = opts.isEdit === true;

    const sheetId = isEdit ? opts.editingId : value.id;
    opts.applyConsumption(sheetId, value.obraId || null, opts.pendingConsumption || []);

    if (!isEdit && value.servicoId) {
      (data.ponto || []).forEach(function (point) {
        if (
          point.servicoId === value.servicoId &&
          point.entrada &&
          point.saida &&
          !point.pausaAlmoco &&
          !point.usadoEmFolha
        ) {
          point.usadoEmFolha = true;
        }
      });
    }

    const pendingWork = opts.pendingWork || null;
    if (!isEdit && value.obraId && pendingWork && pendingWork.obraId === value.obraId) {
      (data.obraPontoLonga || []).forEach(function (point) {
        if (
          point.obraId === value.obraId &&
          point.entrada &&
          point.saida &&
          !point.pausaAlmoco &&
          !point.usadoEmFolha
        ) {
          point.usadoEmFolha = true;
        }
      });
    }
  }

  window.TotalGestSaveFormFolhaUsage = { apply: apply };
})();
