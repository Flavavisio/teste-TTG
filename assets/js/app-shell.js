/* Total Gest — shell modular da aplicação
 * Ponto de entrada para os módulos extraídos de app.html.
 */
(function () {
  'use strict';

  const MODULOS = {
    pwa: './assets/js/app-pwa.js',
    toast: './assets/js/app-toast.js',
    ui: './assets/js/app-ui.js',
    dialogs: './assets/js/app-dialogs.js',
    cache: './assets/js/app-cache.js',
    connectivity: './assets/js/app-connectivity.js',
    syncStatus: './assets/js/app-sync-status.js',
    syncHelpers: './assets/js/app-sync-helpers.js',
    syncDiff: './assets/js/app-sync-diff.js',
    syncSnapshots: './assets/js/app-sync-snapshots.js',
    syncPending: './assets/js/app-sync-pending.js',
    periodLoading: './assets/js/app-period-loading.js',
    loadContext: './assets/js/app-load-context.js',
    loadQueries: './assets/js/app-load-queries.js',
    loadTransform: './assets/js/app-load-transform.js',
    loadOrchestrator: './assets/js/app-load-orchestrator.js',
    modalFuncionario: './assets/js/app-modal-funcionario.js',
    modalCliente: './assets/js/app-modal-cliente.js',
    modalFornecedor: './assets/js/app-modal-fornecedor.js',
    modalRequisicao: './assets/js/app-modal-requisicao.js',
    modalArtigo: './assets/js/app-modal-artigo.js',
    modalFolha: './assets/js/app-modal-folha.js',
    modalServico: './assets/js/app-modal-servico.js',
    modalObra: './assets/js/app-modal-obra.js',
    saveFormFornecedor: './assets/js/app-save-form-fornecedor.js',
    saveFormArtigo: './assets/js/app-save-form-artigo.js',
    saveFormRequisicao: './assets/js/app-save-form-requisicao.js',
    saveFormObra: './assets/js/app-save-form-obra.js',
    saveFormFolhaContext: './assets/js/app-save-form-folha-context.js',
    saveFormFolhaSignature: './assets/js/app-save-form-folha-signature.js',
    saveFormFolhaObject: './assets/js/app-save-form-folha-object.js',
    saveFormFolhaAssist: './assets/js/app-save-form-folha-assist.js',
    saveFormFolhaConsumos: './assets/js/app-save-form-folha-consumos.js',
    saveFormFolhaManutencao: './assets/js/app-save-form-folha-manutencao.js',
    saveFormFolhaPonto: './assets/js/app-save-form-folha-ponto.js',
    saveFormFolha: './assets/js/app-save-form-folha.js',
    saveFormCliente: './assets/js/app-save-form-cliente.js',
    saveFormFuncionario: './assets/js/app-save-form-funcionario.js',
    saveFormFuncionarioEncarregado: './assets/js/app-save-form-funcionario-encarregado.js',
    saveFormFuncionarioOrchestrator: './assets/js/app-save-form-funcionario-orchestrator.js',
    saveFormServicoValidation: './assets/js/app-save-form-servico-validation.js',
    saveFormServicoContext: './assets/js/app-save-form-servico-context.js',
    saveFormServicoObject: './assets/js/app-save-form-servico-object.js',
    saveFormServicoConflicts: './assets/js/app-save-form-servico-conflicts.js',
    saveFormServicoRegistration: './assets/js/app-save-form-servico-registration.js',
    saveFormServico: './assets/js/app-save-form-servico.js',
    saveFormPersist: './assets/js/app-save-form-persist.js',
    saveFormServicoNotifications: './assets/js/app-save-form-servico-notifications.js',
    saveFormFolhaUsage: './assets/js/app-save-form-folha-usage.js',
    saveFormFolhaOsPending: './assets/js/app-save-form-folha-os-pending.js',
    saveFormFolhaObraPending: './assets/js/app-save-form-folha-obra-pending.js',
    saveFormFinalize: './assets/js/app-save-form-finalize.js',
    saveFormAuth: './assets/js/app-save-form-auth.js',
    saveFormContactValidation: './assets/js/app-save-form-contact-validation.js',
    saveFormDispatch: './assets/js/app-save-form-dispatch.js',
    saveFormPostPersist: './assets/js/app-save-form-post-persist.js',
    profileModalSuperadmin: './assets/js/app-profile-modal-superadmin.js',
    profileModalDistributor: './assets/js/app-profile-modal-distributor.js',
    profileModalAdmin: './assets/js/app-profile-modal-admin.js',
    profileModalWorker: './assets/js/app-profile-modal-worker.js',
    profileModal: './assets/js/app-profile-modal.js',
    profileHelpers: './assets/js/app-profile-helpers.js',
    profileSaveSuperadmin: './assets/js/app-profile-save-superadmin.js',
    profileSaveDistributor: './assets/js/app-profile-save-distributor.js',
    profileSaveAdmin: './assets/js/app-profile-save-admin.js',
    profileSaveWorker: './assets/js/app-profile-save-worker.js',
    profileSave: './assets/js/app-profile-save.js',
    syncPrepare: './assets/js/app-sync-prepare.js',
    syncFiles: './assets/js/app-sync-files.js',
    syncCollections: './assets/js/app-sync-collections.js',
    syncOrchestrator: './assets/js/app-sync-orchestrator.js',
    syncFinalize: './assets/js/app-sync-finalize.js',
    syncUpsert: './assets/js/app-sync-upsert.js',
    syncLicenses: './assets/js/app-sync-licenses.js',
    syncEncarregados: './assets/js/app-sync-encarregados.js',
    syncDelete: './assets/js/app-sync-delete.js',
    saveQueue: './assets/js/app-save-queue.js',
    bootstrap: './assets/js/app-bootstrap.js'
  };

  function carregarScript(src) {
    return new Promise(function (resolve, reject) {
      const existente = document.querySelector('script[data-tg-module="' + src + '"]');
      if (existente) {
        if (existente.dataset.tgLoaded === '1') resolve();
        else existente.addEventListener('load', resolve, { once: true });
        return;
      }

      const script = document.createElement('script');
      script.src = src;
      script.dataset.tgModule = src;
      script.onload = function () {
        script.dataset.tgLoaded = '1';
        resolve();
      };
      script.onerror = reject;
      document.head.appendChild(script);
    });
  }

  async function carregarModulos(options) {
    options = options || {};
    const pedidos = [];

    if (options.pwa === true) pedidos.push(MODULOS.pwa);
    if (options.toast === true) pedidos.push(MODULOS.toast);
    if (options.ui === true) pedidos.push(MODULOS.ui);
    if (options.dialogs === true) pedidos.push(MODULOS.dialogs);
    if (options.cache === true) pedidos.push(MODULOS.cache);
    if (options.connectivity === true) pedidos.push(MODULOS.connectivity);
    if (options.syncStatus === true) pedidos.push(MODULOS.syncStatus);
    if (options.syncHelpers === true) pedidos.push(MODULOS.syncHelpers);
    if (options.syncDiff === true) pedidos.push(MODULOS.syncDiff);
    if (options.syncSnapshots === true) pedidos.push(MODULOS.syncSnapshots);
    if (options.syncPending === true) pedidos.push(MODULOS.syncPending);
    if (options.periodLoading === true) pedidos.push(MODULOS.periodLoading);
    if (options.loadContext === true) pedidos.push(MODULOS.loadContext);
    if (options.loadQueries === true) pedidos.push(MODULOS.loadQueries);
    if (options.loadTransform === true) pedidos.push(MODULOS.loadTransform);
    if (options.loadOrchestrator === true) pedidos.push(MODULOS.loadOrchestrator);
    if (options.modalFuncionario === true) pedidos.push(MODULOS.modalFuncionario);
    if (options.modalCliente === true) pedidos.push(MODULOS.modalCliente);
    if (options.modalFornecedor === true) pedidos.push(MODULOS.modalFornecedor);
    if (options.modalRequisicao === true) pedidos.push(MODULOS.modalRequisicao);
    if (options.modalArtigo === true) pedidos.push(MODULOS.modalArtigo);
    if (options.modalFolha === true) pedidos.push(MODULOS.modalFolha);
    if (options.modalServico === true) pedidos.push(MODULOS.modalServico);
    if (options.modalObra === true) pedidos.push(MODULOS.modalObra);
    if (options.saveFormFornecedor === true) pedidos.push(MODULOS.saveFormFornecedor);
    if (options.saveFormArtigo === true) pedidos.push(MODULOS.saveFormArtigo);
    if (options.saveFormRequisicao === true) pedidos.push(MODULOS.saveFormRequisicao);
    if (options.saveFormObra === true) pedidos.push(MODULOS.saveFormObra);
    if (options.saveFormFolhaContext === true) pedidos.push(MODULOS.saveFormFolhaContext);
    if (options.saveFormFolhaSignature === true) pedidos.push(MODULOS.saveFormFolhaSignature);
    if (options.saveFormFolhaObject === true) pedidos.push(MODULOS.saveFormFolhaObject);
    if (options.saveFormFolhaAssist === true) pedidos.push(MODULOS.saveFormFolhaAssist);
    if (options.saveFormFolhaConsumos === true) pedidos.push(MODULOS.saveFormFolhaConsumos);
    if (options.saveFormFolhaManutencao === true) pedidos.push(MODULOS.saveFormFolhaManutencao);
    if (options.saveFormFolhaPonto === true) pedidos.push(MODULOS.saveFormFolhaPonto);
    if (options.saveFormFolha === true) pedidos.push(MODULOS.saveFormFolha);
    if (options.saveFormCliente === true) pedidos.push(MODULOS.saveFormCliente);
    if (options.saveFormFuncionario === true) pedidos.push(MODULOS.saveFormFuncionario);
    if (options.saveFormFuncionarioEncarregado === true) pedidos.push(MODULOS.saveFormFuncionarioEncarregado);
    if (options.saveFormFuncionarioOrchestrator === true) pedidos.push(MODULOS.saveFormFuncionarioOrchestrator);
    if (options.saveFormServicoValidation === true) pedidos.push(MODULOS.saveFormServicoValidation);
    if (options.saveFormServicoContext === true) pedidos.push(MODULOS.saveFormServicoContext);
    if (options.saveFormServicoObject === true) pedidos.push(MODULOS.saveFormServicoObject);
    if (options.saveFormServicoConflicts === true) pedidos.push(MODULOS.saveFormServicoConflicts);
    if (options.saveFormServicoRegistration === true) pedidos.push(MODULOS.saveFormServicoRegistration);
    if (options.saveFormServico === true) pedidos.push(MODULOS.saveFormServico);
    if (options.saveFormPersist === true) pedidos.push(MODULOS.saveFormPersist);
    if (options.saveFormServicoNotifications === true) pedidos.push(MODULOS.saveFormServicoNotifications);
    if (options.saveFormFolhaUsage === true) pedidos.push(MODULOS.saveFormFolhaUsage);
    if (options.saveFormFolhaOsPending === true) pedidos.push(MODULOS.saveFormFolhaOsPending);
    if (options.saveFormFolhaObraPending === true) pedidos.push(MODULOS.saveFormFolhaObraPending);
    if (options.saveFormFinalize === true) pedidos.push(MODULOS.saveFormFinalize);
    if (options.saveFormAuth === true) pedidos.push(MODULOS.saveFormAuth);
    if (options.saveFormContactValidation === true) pedidos.push(MODULOS.saveFormContactValidation);
    if (options.saveFormDispatch === true) pedidos.push(MODULOS.saveFormDispatch);
    if (options.saveFormPostPersist === true) pedidos.push(MODULOS.saveFormPostPersist);
    if (options.profileModalSuperadmin === true) pedidos.push(MODULOS.profileModalSuperadmin);
    if (options.profileModalDistributor === true) pedidos.push(MODULOS.profileModalDistributor);
    if (options.profileModalAdmin === true) pedidos.push(MODULOS.profileModalAdmin);
    if (options.profileModalWorker === true) pedidos.push(MODULOS.profileModalWorker);
    if (options.profileModal === true) pedidos.push(MODULOS.profileModal);
    if (options.profileHelpers === true) pedidos.push(MODULOS.profileHelpers);
    if (options.profileSaveSuperadmin === true) pedidos.push(MODULOS.profileSaveSuperadmin);
    if (options.profileSaveDistributor === true) pedidos.push(MODULOS.profileSaveDistributor);
    if (options.profileSaveAdmin === true) pedidos.push(MODULOS.profileSaveAdmin);
    if (options.profileSaveWorker === true) pedidos.push(MODULOS.profileSaveWorker);
    if (options.profileSave === true) pedidos.push(MODULOS.profileSave);
    if (options.syncPrepare === true) pedidos.push(MODULOS.syncPrepare);
    if (options.syncFiles === true) pedidos.push(MODULOS.syncFiles);
    if (options.syncCollections === true) pedidos.push(MODULOS.syncCollections);
    if (options.syncOrchestrator === true) pedidos.push(MODULOS.syncOrchestrator);
    if (options.syncFinalize === true) pedidos.push(MODULOS.syncFinalize);
    if (options.syncUpsert === true) pedidos.push(MODULOS.syncUpsert);
    if (options.syncLicenses === true) pedidos.push(MODULOS.syncLicenses);
    if (options.syncEncarregados === true) pedidos.push(MODULOS.syncEncarregados);
    if (options.syncDelete === true) pedidos.push(MODULOS.syncDelete);
    if (options.saveQueue === true) pedidos.push(MODULOS.saveQueue);
    if (options.bootstrap === true) pedidos.push(MODULOS.bootstrap);

    for (const modulo of pedidos) {
      await carregarScript(modulo);
    }
  }

  async function iniciar(options) {
    options = options || {};
    await carregarModulos(options);

    if (options.pwa === true && window.TotalGestPwa && typeof window.TotalGestPwa.init === 'function') {
      window.TotalGestPwa.init();
    }

    if (options.dialogs === true && window.TotalGestDialogs && typeof window.TotalGestDialogs.init === 'function') {
      window.TotalGestDialogs.init();
    }

    if (options.connectivity === true && window.TotalGestConnectivity && typeof window.TotalGestConnectivity.init === 'function') {
      window.TotalGestConnectivity.init();
    }

    if (options.bootstrap === true && window.TotalGestBootstrap && typeof window.TotalGestBootstrap.init === 'function') {
      await window.TotalGestBootstrap.init();
    }
  }

  window.TotalGestApp = {
    init: iniciar,
    loadModules: carregarModulos,
    modules: Object.assign({}, MODULOS)
  };
})();
