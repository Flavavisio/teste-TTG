/* Total Gest — orquestração da gravação do perfil. */
(function () {
  'use strict';

  function run(options) {
    const opts = options || {};
    const event = opts.event;
    if (event && typeof event.preventDefault === 'function') event.preventDefault();
    const user = opts.user;
    if (!user) return;

    const documentRef = opts.document;
    const nome = documentRef.getElementById('perf_nome').value.trim();
    const senha = documentRef.getElementById('perf_senha').value;
    if (!nome) {
      opts.alert('Nome é obrigatório.');
      return;
    }

    const common = {
      document: documentRef,
      data: opts.data,
      user: user,
      name: nome,
      password: senha,
      saveData: opts.saveData,
      closeModal: opts.closeModal,
      renderAll: opts.renderAll,
      alert: opts.alert
    };

    if (user.role === 'superadmin') {
      opts.superadmin.run(Object.assign({}, common, {
        getConfig: opts.getConfig,
        saveConfig: opts.saveConfig
      }));
      return;
    }

    if (user.role === 'admin' && opts.getAdmin()?.ehDistribuidor) {
      opts.distributor.run(Object.assign({}, common, {
        getAdmin: opts.getAdmin,
        applyHeaderConfig: opts.applyHeaderConfig
      }));
      return;
    }

    if (user.role === 'admin' || user.role === 'subadmin') {
      opts.admin.run(Object.assign({}, common, {
        getAdmin: opts.getAdmin,
        numberAlreadyUsed: opts.numberAlreadyUsed,
        applyHeaderConfig: opts.applyHeaderConfig
      }));
      return;
    }

    opts.worker.run(common);
  }

  window.TotalGestProfileSave = { run: run };
})();
