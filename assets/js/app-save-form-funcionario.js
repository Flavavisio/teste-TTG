/* Total Gest — preparação e validação do formulário de funcionário. */
(function () {
  'use strict';

  async function prepare(options) {
    const opts = options || {};
    const doc = opts.document || document;
    const data = opts.data || {};
    const user = opts.user || {};
    const isEdit = opts.isEdit === true;
    const editingId = opts.editingId || null;
    const roleType = opts.roleType || 'funcionario';
    const showAlert = opts.showAlert || alert;

    const obj = {
      nome: doc.getElementById('f_nome').value.trim(),
      foto: doc.getElementById('f_foto_data')?.value || null,
      cargo: doc.getElementById('f_cargo').value.trim(),
      telefone: doc.getElementById('f_telefone').value.trim(),
      email: doc.getElementById('f_email').value.trim(),
      morada: doc.getElementById('f_morada').value.trim(),
      codigoPostal: doc.getElementById('f_cp').value.trim(),
      dataNascimento: doc.getElementById('f_nasc').value,
      horasSemanais: parseInt(doc.getElementById('f_horas').value) || 40,
      role: (!isEdit && roleType === 'subadmin') ? 'subadmin' : (!isEdit && roleType === 'vendedor') ? 'vendedor' : (!isEdit && roleType === 'vigilante') ? 'vigilante' : (!isEdit && roleType === 'supervisor_vigilantes') ? 'supervisor_vigilantes' : (isEdit ? undefined : 'funcionario'),
      adminId: (user.role === 'admin' ? user.id : user.adminId)
    };

    if (obj.role === undefined) delete obj.role;
    if (!isEdit && roleType === 'vigilante') {
      const supervisor = doc.getElementById('f_vigilante_supervisor_id');
      obj.vigilanteSupervisorId = supervisor && supervisor.value ? supervisor.value : null;
    }
    const supervisorEdit = doc.getElementById('f_vigilante_supervisor_id_edit');
    if (isEdit && supervisorEdit) obj.vigilanteSupervisorId = supervisorEdit.value || null;

    const senha = doc.getElementById('f_senha').value;
    if (senha) obj.senha = senha;
    if (!isEdit) obj.mudarSenha = true;

    const ordenado = doc.getElementById('f_ordenado');
    if (ordenado) obj.ordenadoBruto = ordenado.value;
    const apoliceNumero = doc.getElementById('f_apolice_numero');
    if (apoliceNumero) obj.apoliceNumero = apoliceNumero.value || null;
    const apoliceSeguradora = doc.getElementById('f_apolice_seguradora');
    if (apoliceSeguradora) obj.apoliceSeguradora = apoliceSeguradora.value || null;
    const apoliceValidade = doc.getElementById('f_apolice_validade');
    if (apoliceValidade) obj.apoliceValidade = apoliceValidade.value || null;
    const saudeNumero = doc.getElementById('f_saude_numero');
    if (saudeNumero) obj.saudeApoliceNumero = saudeNumero.value || null;
    const saudeSeguradora = doc.getElementById('f_saude_seguradora');
    if (saudeSeguradora) obj.saudeApoliceSeguradora = saudeSeguradora.value || null;
    const saudeValidade = doc.getElementById('f_saude_validade');
    if (saudeValidade) obj.saudeApoliceValidade = saudeValidade.value || null;
    const shst = doc.getElementById('f_shst_ultima_consulta');
    if (shst) obj.shstUltimaConsulta = shst.value || null;
    const veiculo = doc.getElementById('f_veiculo');
    if (veiculo) obj.veiculoId = veiculo.value || null;
    const gps = doc.getElementById('f_gps_ponto');
    if (gps) obj.gpsPonto = gps.checked;
    const podeAssinar = doc.getElementById('f_pode_assinar_relatorios');
    if (podeAssinar) obj.podeAssinarRelatorios = podeAssinar.checked;

    const diasFerias = doc.getElementById('f_dias_ferias');
    if (diasFerias && diasFerias.value !== '') obj.diasFerias = parseInt(diasFerias.value) || 0;
    else if (isEdit) {
      const existente = data.funcionarios?.find(x => x.id === editingId);
      if (existente && existente.diasFerias != null) obj.diasFerias = existente.diasFerias;
    }

    if (obj.veiculoId) {
      const ocupado = opts.vehicleAssigned(obj.veiculoId, 'func', isEdit ? editingId : null);
      if (ocupado) {
        showAlert('Esse carro já está atribuído a ' + ocupado + '. Um carro só pode ser atribuído a uma pessoa.');
        return { ok: false };
      }
    }

    if (!obj.nome || !obj.cargo || !obj.email || (!isEdit && !obj.senha) || !obj.morada || !obj.codigoPostal || !doc.getElementById('f_horas').value) {
      showAlert('Preencha os campos obrigatórios: Nome, Cargo, Email, Senha, Morada, Código Postal e Horas Semanais.');
      return { ok: false };
    }

    if (await opts.emailRegistered(obj.email, isEdit ? editingId : null)) {
      showAlert('Já existe um utilizador com este email (' + obj.email + '). Use um email diferente.');
      return { ok: false };
    }

    return { ok: true, value: obj };
  }

  window.TotalGestSaveFormFuncionario = { prepare: prepare };
})();
