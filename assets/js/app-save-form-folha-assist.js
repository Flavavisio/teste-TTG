/* Total Gest — integração Assist da gravação da folha. */
(function () {
  'use strict';

  function prepare(options) {
    const opts = options || {};
    const documentRef = opts.document;
    const dados = opts.data || {};
    const servicoId = opts.serviceOrderId || null;
    const showAlert = opts.showAlert;

    let assistance = null;
    let newState = null;

    if (servicoId) {
      const serviceOrder = dados.servicos?.find(function (item) { return item.id === servicoId; });
      if (serviceOrder?.origem === 'assistencia') {
        newState = documentRef.getElementById('fo_estado_assistencia')?.value || '';
        if (!newState) {
          showAlert('Indica o estado da assistência — é obrigatório para OS geradas a partir do Total Gest Assist.');
          return { ok: false, assistance: null, newState: null };
        }
        assistance = (dados.assistencias || []).find(function (item) {
          return item.id === serviceOrder.assistenciaId || item.osGeradaId === serviceOrder.id;
        }) || null;
      }
    }

    return { ok: true, assistance: assistance, newState: newState };
  }

  function apply(options) {
    const opts = options || {};
    if (opts.assistance && opts.newState) {
      opts.assistance.estado = opts.newState;
      opts.assistance.dataModificacao = Date.now();
    }
  }

  window.TotalGestSaveFormFolhaAssist = {
    prepare: prepare,
    apply: apply
  };
})();
