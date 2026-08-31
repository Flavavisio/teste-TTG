/* Total Gest — gravação do formulário de fornecedor. */
(function () {
  'use strict';

  function run(options) {
    const opts = options || {};
    const doc = opts.document || document;
    const user = opts.user || {};
    const nome = doc.getElementById('fr_nome').value.trim();
    if (!nome) {
      opts.showAlert('Indique o nome do fornecedor.');
      return;
    }

    const obj = {
      nome: nome,
      nif: doc.getElementById('fr_nif').value.trim(),
      contacto: doc.getElementById('fr_contacto').value.trim(),
      email: doc.getElementById('fr_email').value.trim(),
      observacoes: doc.getElementById('fr_obs').value.trim(),
      adminId: user.role === 'admin' ? user.id : user.adminId
    };

    opts.saveWarehouse('fornecedores', obj, opts.isEdit);
  }

  window.TotalGestSaveFormFornecedor = { run: run };
})();
