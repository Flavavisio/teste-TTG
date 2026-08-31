/* Total Gest — tratamento da OS pendente após guardar uma folha. */
(function () {
  'use strict';

  function apply(options) {
    const opts = options || {};
    const value = opts.value || {};
    const pending = opts.pending || null;
    const data = opts.data || {};

    if (!pending || pending.osId !== value.servicoId) return;

    const osId = pending.osId;
    const terminou = pending.terminou;
    opts.clearPending();

    const service = data.servicos?.find(function (item) { return item.id === osId; });
    if (!service) return;

    if (terminou) {
      const pendingSpecialty = opts.pendingSpecialty(osId);
      const finalize = function () { opts.completeService(service); };
      if (pendingSpecialty.length) opts.openSpecialtyQueue(osId, pendingSpecialty, finalize);
      else finalize();
      return;
    }

    service.status = 'stand by';
    opts.saveData(data);
    opts.renderAgenda();
    if (typeof opts.renderPoint === 'function') opts.renderPoint();
    opts.showAlert('Folha de obra guardada ✓ Obra em Stand By. Podes voltar a dar entrada quando retomares.');
  }

  window.TotalGestSaveFormFolhaOsPending = { apply: apply };
})();
