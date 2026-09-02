/* Total Gest — preparação e validação do formulário de cliente. */
(function () {
  'use strict';

  function prepare(options) {
    const opts = options || {};
    const doc = opts.document || document;
    const data = opts.data || {};
    const user = opts.user || {};
    const showAlert = opts.showAlert || alert;

    const obj = {
      nome: doc.getElementById('c_nome').value.trim(),
      numeroCliente: doc.getElementById('c_numero_cliente').value.trim(),
      morada: doc.getElementById('c_morada').value.trim(),
      numeroPorta: doc.getElementById('c_numero_porta').value.trim(),
      codigoPostal: doc.getElementById('c_cp').value.trim(),
      cidade: doc.getElementById('c_cidade').value.trim(),
      freguesia: doc.getElementById('c_freguesia').value.trim(),
      pinMapa: doc.getElementById('c_pin_mapa').value.trim() || null,
      nif: doc.getElementById('c_nif').value.trim(),
      telefone: doc.getElementById('c_telefone').value.trim(),
      email: doc.getElementById('c_email').value.trim(),
      pessoaContacto: doc.getElementById('c_contacto').value.trim(),
      adminId: user.role === 'admin' ? user.id : user.adminId
    };

    obj.portalAtivo = doc.getElementById('c_portal_ativo')?.checked || false;
    const senha = doc.getElementById('c_senha')?.value || '';
    if (senha) obj.senha = senha;

    if (!obj.nif) {
      showAlert('Preenche pelo menos o NIF do cliente.');
      return { ok: false };
    }
    if (!/^\d{1,9}$/.test(obj.nif)) {
      showAlert('O NIF deve ter só números, até 9 dígitos no máximo.');
      return { ok: false };
    }

    const NIF_CONSUMIDOR_FINAL = '999999990';
    const outroComMesmoNif = obj.nif !== NIF_CONSUMIDOR_FINAL
      ? (data.clientes || []).find(function (cliente) {
          return cliente.adminId === obj.adminId && cliente.nif === obj.nif && cliente.id !== opts.editingId;
        })
      : null;
    if (outroComMesmoNif) {
      showAlert(`Já existe um cliente com este NIF: "${outroComMesmoNif.nome}". Cada cliente precisa de um NIF diferente — é o que identifica o login no Portal.`);
      return { ok: false };
    }

    if (!obj.nome) obj.nome = 'Cliente ' + obj.nif;
    if (obj.numeroCliente && !/^\d{1,8}$/.test(obj.numeroCliente)) {
      showAlert('O número de cliente deve ter só dígitos, até 8 no máximo.');
      return { ok: false };
    }
    if (obj.portalAtivo && obj.nif === NIF_CONSUMIDOR_FINAL) {
      showAlert('⚠️ Este cliente tem o NIF de "Consumidor Final" (999999990) — como esse NIF pode estar repetido em vários clientes, não é possível ativar o Portal para ele. Define um NIF próprio a este cliente se precisares de lhe dar acesso ao Portal.');
      return { ok: false };
    }
    if (obj.portalAtivo && !obj.nif) {
      showAlert('Para ativar o Portal do Cliente é preciso um NIF (é com ele que o cliente entra).');
      return { ok: false };
    }

    return { ok: true, value: obj };
  }

  window.TotalGestSaveFormCliente = { prepare: prepare };
})();
