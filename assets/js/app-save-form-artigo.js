/* Total Gest — gravação do formulário de artigo. */
(function () {
  'use strict';

  function run(options) {
    const opts = options || {};
    const doc = opts.document || document;
    const user = opts.user || {};
    const nome = doc.getElementById('ar_nome').value.trim();
    if (!nome) {
      opts.showAlert('Indique o nome do artigo.');
      return;
    }

    const categoria = doc.getElementById('ar_categoria').value;
    const temNumeroSerie = doc.getElementById('ar_temserie') ? doc.getElementById('ar_temserie').checked : false;
    const obj = {
      nome: nome,
      marca: doc.getElementById('ar_marca').value.trim(),
      categoria: categoria === '__nova' ? '' : categoria,
      referencia: doc.getElementById('ar_ref').value.trim(),
      codigoBarras: (temNumeroSerie || !doc.getElementById('ar_codbarras')) ? '' : doc.getElementById('ar_codbarras').value.trim(),
      temNumeroSerie: temNumeroSerie,
      unidade: doc.getElementById('ar_unidade').value,
      stockMinimo: doc.getElementById('ar_stockmin').value === '' ? '' : opts.intVal('ar_stockmin', ''),
      alertaStock: doc.getElementById('ar_alerta') ? doc.getElementById('ar_alerta').checked : false,
      precoVenda: doc.getElementById('ar_preco').value,
      precoCompra: doc.getElementById('ar_preco_compra') ? doc.getElementById('ar_preco_compra').value : '',
      observacoes: doc.getElementById('ar_obs').value.trim(),
      adminId: user.role === 'admin' ? user.id : user.adminId
    };

    if (!opts.isEdit) obj.stockInicial = opts.intVal('ar_stockini', 0);
    opts.saveWarehouse('artigos', obj, opts.isEdit);
  }

  window.TotalGestSaveFormArtigo = { run: run };
})();
