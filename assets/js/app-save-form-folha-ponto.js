/* Total Gest — fecho de picagem ao gravar folha de obra. */
(function () {
  'use strict';

  function apply(options) {
    const opts = options || {};
    const data = opts.data || {};
    const sheet = opts.sheet || {};
    if (!sheet.servicoId) return;

    const openPoint = (data.ponto || []).find(function (point) {
      return point.servicoId === sheet.servicoId &&
        point.funcionarioId === sheet.funcionarioId &&
        point.entrada && !point.saida;
    });

    if (openPoint) openPoint.saida = new Date().toTimeString().slice(0, 5);
  }

  window.TotalGestSaveFormFolhaPonto = { apply: apply };
})();
