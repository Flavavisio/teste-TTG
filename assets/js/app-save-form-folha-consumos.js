/* Total Gest — preparação dos consumos de materiais da folha. */
(function () {
  'use strict';

  function prepare(options) {
    const opts = options || {};
    const documentRef = opts.document;
    const extras = Array.isArray(opts.extraMaterials) ? opts.extraMaterials : [];

    const pending = Array.from(documentRef.querySelectorAll('#fo_plano_materiais .fo-consumo')).map(function (input) {
      return {
        artigoId: input.getAttribute('data-artigo'),
        consumido: parseInt(input.value, 10) || 0
      };
    });

    pending.push.apply(pending, extras.map(function (item) {
      return { artigoId: item.artigoId, consumido: item.qtd };
    }));

    return pending;
  }

  window.TotalGestSaveFormFolhaConsumos = { prepare: prepare };
})();
