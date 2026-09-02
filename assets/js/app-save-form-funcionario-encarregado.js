/* Total Gest — criação de encarregado a partir do formulário de funcionário. */
(function () {
  'use strict';

  async function run(options) {
    const opts = options || {};
    if (opts.isEdit === true || opts.roleType !== 'encarregado') return { handled: false };

    const doc = opts.document || document;
    const data = opts.data || {};
    const user = opts.user || {};
    const adminId = user.role === 'admin' ? user.id : user.adminId;
    const encObj = {
      id: opts.generateId(),
      nome: doc.getElementById('f_nome').value.trim(),
      cargo: doc.getElementById('f_cargo').value.trim(),
      telefone: doc.getElementById('f_telefone').value.trim(),
      email: doc.getElementById('f_email').value.trim(),
      senha: doc.getElementById('f_senha').value,
      morada: doc.getElementById('f_morada').value.trim(),
      codigoPostal: doc.getElementById('f_cp').value.trim(),
      dataNascimento: doc.getElementById('f_nasc').value,
      horasSemanais: parseInt(doc.getElementById('f_horas').value) || 40,
      adminId: adminId,
      funcionariosIds: Array.from(doc.querySelectorAll('.f-equipa-check:checked')).map(cb => cb.value),
      mudarSenha: true,
      gpsPonto: true,
      dataCriacao: Date.now()
    };

    data.encarregados = data.encarregados || [];
    data.encarregados.push(encObj);
    opts.saveData(data);
    opts.audit('criar', 'encarregado', encObj.id, encObj.nome);
    opts.closeModal();
    opts.renderAll();

    if (encObj.email && encObj.senha) {
      try {
        await opts.saveData(data);
      } catch (e) {
        opts.showAlert(`⚠️ O encarregado ${encObj.nome} foi criado no ecrã, mas ainda não foi possível confirmar a gravação no servidor (${e && e.message ? e.message : e}).\n\nNão foi criada a conta de login para evitar inconsistências — tenta novamente mais tarde.`);
        return { handled: true };
      }
      opts.createAuth(encObj.email, encObj.senha, 'encarregado', encObj.adminId, encObj.id, encObj.nome).then(r => {
        if (!r.ok) opts.showAlert('✅ Encarregado criado.\n⚠️ A conta de login não foi criada automaticamente: ' + r.erro + '\nSe o email já tiver sido usado antes, pede para o removerem da autenticação antes de tentares de novo.');
      });
    }

    return { handled: true };
  }

  window.TotalGestSaveFormFuncionarioEncarregado = { run: run };
})();
