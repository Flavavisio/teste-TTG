/* Total Gest — finalização comum da gravação de formulários. */
(function () {
  'use strict';

  async function run(options) {
    const opts = options || {};
    const value = opts.value || {};

    try {
      await opts.saveData(opts.data);
    } catch (err) {
      opts.showAlert(`⚠️ Ficou no ecrã, mas ainda não foi possível confirmar a gravação no servidor (${err && err.message ? err.message : err}).\n\nVerifica a ligação à internet — se o erro persistir, este registo pode desaparecer ao recarregar a página. Tenta guardar de novo.`);
    }

    opts.audit(
      opts.isEdit ? 'editar' : 'criar',
      opts.entity,
      opts.isEdit ? opts.editingId : value.id,
      (value.nome || value.descricao || value.numero || value.obraDescricao || '')
    );

    if (opts.entity === 'servico' && opts.newWorkId) opts.markServiceWorkCreated();

    opts.closeModal();
    opts.renderAll();
  }

  window.TotalGestSaveFormFinalize = { run: run };
})();
