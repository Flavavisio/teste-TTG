/* Total Gest — orquestração da gravação do formulário de funcionário. */
(function () {
  'use strict';

  async function run(options) {
    const opts = options || {};
    const doc = opts.document || document;
    const data = opts.data || {};
    const user = opts.user || {};
    const isEdit = opts.isEdit === true;
    const editingId = opts.editingId || null;

    const emailNovo = (doc.getElementById('f_email')?.value || '').trim().toLowerCase();
    if (emailNovo) {
      const emailJaUsado = (data.funcionarios || []).some(f => f.id !== editingId && (f.email || '').trim().toLowerCase() === emailNovo)
        || (data.encarregados || []).some(e => e.id !== editingId && (e.email || '').trim().toLowerCase() === emailNovo);
      if (emailJaUsado) {
        opts.showError(`Já existe uma conta com o email "${emailNovo}". Usa outro email para este funcionário.`);
        return { ok: false, stop: true };
      }
    }

    if (!isEdit) {
      const verificacao = opts.verifyLimit(user.role === 'admin' ? user.id : user.adminId);
      if (!verificacao.permitido) {
        opts.showError(verificacao.mensagem);
        return { ok: false, stop: true };
      }
    }

    const roleTypeElement = doc.getElementById('f_role_tipo');
    const roleType = roleTypeElement ? roleTypeElement.value : 'funcionario';

    const encarregado = await window.TotalGestSaveFormFuncionarioEncarregado.run({
      document: doc,
      data: data,
      user: user,
      isEdit: isEdit,
      roleType: roleType,
      generateId: opts.generateId,
      saveData: opts.saveData,
      audit: opts.audit,
      closeModal: opts.closeModal,
      renderAll: opts.renderAll,
      createAuth: opts.createAuth,
      showAlert: opts.showAlert
    });
    if (encarregado.handled) return { ok: true, stop: true };

    const funcionario = await window.TotalGestSaveFormFuncionario.prepare({
      document: doc,
      data: data,
      user: user,
      isEdit: isEdit,
      editingId: editingId,
      roleType: roleType,
      vehicleAssigned: opts.vehicleAssigned,
      emailRegistered: opts.emailRegistered,
      showAlert: opts.showAlert
    });
    if (!funcionario.ok) return { ok: false, stop: true };

    return { ok: true, stop: false, value: funcionario.value };
  }

  window.TotalGestSaveFormFuncionarioOrchestrator = { run: run };
})();
