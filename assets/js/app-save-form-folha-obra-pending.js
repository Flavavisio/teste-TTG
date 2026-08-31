/* Total Gest — tratamento da obra pendente após guardar uma folha. */
(function () {
  'use strict';

  function apply(options) {
    const opts = options || {};
    const value = opts.value || {};
    const pending = opts.pending || null;
    const data = opts.data || {};

    if (!pending || pending.obraId !== value.obraId) return;

    const obraId = pending.obraId;
    const terminou = pending.terminou;
    opts.clearPending();

    const work = data.obras?.find(function (item) { return item.id === obraId; });
    if (!work) return;

    if (terminou) {
      work.estado = 'concluida';
      work.dataConclusao = opts.getToday();
      opts.saveData(data);
      opts.renderAll();
      opts.showAlert('✅ Folha guardada e obra terminada. Obrigado!');
      return;
    }

    work.estado = 'suspensa';
    opts.saveData(data);
    opts.renderAll();
    opts.showAlert('Folha de obra guardada ✓ Obra em Stand By. Podes voltar a dar entrada quando retomares.');
  }

  window.TotalGestSaveFormFolhaObraPending = { apply: apply };
})();
