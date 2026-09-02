/* Total Gest — gravação do formulário de obra. */
(function () {
  'use strict';

  function run(options) {
    const opts = options || {};
    const documentRef = opts.document;
    const dados = opts.data || {};
    const usuarioLogado = opts.user || null;
    const isEdit = opts.isEdit === true;
    const idEditando = opts.editingId || null;
    const gerarId = opts.generateId;
    const mostrarErro = opts.showError;
    const showAlert = opts.showAlert;
    const guardarArmazem = opts.saveWarehouse;
    const confirmar = opts.confirm;
    const criarOSdaObra = opts.createServiceOrder;

    const nome = documentRef.getElementById('ob_nome').value.trim();
    if (!nome) { showAlert('Indique o nome da obra.'); return; }

    const descricao = documentRef.getElementById('ob_obs')?.value.trim();
    if (!descricao || descricao.length < 3) {
      mostrarErro('Descreve a obra (pelo menos 3 caracteres).');
      documentRef.getElementById('ob_obs')?.focus();
      return;
    }

    const novoEstado = documentRef.getElementById('ob_estado').value;
    let estadoAnterior = null;
    if (isEdit) {
      const existente = dados.obras?.find(obra => obra.id === idEditando);
      estadoAnterior = existente ? existente.estado : null;
    }

    const obraId = idEditando;
    const clienteId = documentRef.getElementById('ob_cliente').value || null;
    const cliente = clienteId ? dados.clientes?.find(item => item.id === clienteId) : null;
    const adminId = usuarioLogado.role === 'admin' ? usuarioLogado.id : usuarioLogado.adminId;
    let localId = documentRef.getElementById('ob_local')?.value || '';
    let morada = '', codigoPostal = '', cidade = '', numeroPorta = '', freguesia = '';

    if (localId === '__novo__') {
      const nomeNovoLocal = (documentRef.getElementById('ob_local_nome')?.value || '').trim();
      if (!nomeNovoLocal) { showAlert('Indique o nome do novo local.'); return; }
      morada = documentRef.getElementById('ob_morada')?.value.trim() || '';
      numeroPorta = documentRef.getElementById('ob_local_numero')?.value.trim() || '';
      codigoPostal = documentRef.getElementById('ob_cp')?.value.trim() || '';
      cidade = documentRef.getElementById('ob_cidade')?.value.trim() || '';
      freguesia = documentRef.getElementById('ob_local_freguesia')?.value.trim() || '';
      localId = gerarId();
      dados.locais = dados.locais || [];
      dados.locais.push({
        id: localId,
        adminId: adminId,
        clienteId: clienteId,
        nome: nomeNovoLocal,
        morada: morada,
        numeroPorta: numeroPorta,
        codigoPostal: codigoPostal,
        cidade: cidade,
        freguesia: freguesia,
        pinMapa: documentRef.getElementById('ob_local_pin_mapa')?.value.trim() || null,
        dataCriacao: Date.now()
      });
    } else if (localId) {
      const localSelecionado = dados.locais?.find(item => item.id === localId);
      morada = localSelecionado?.morada || '';
      codigoPostal = localSelecionado?.codigoPostal || '';
      cidade = localSelecionado?.cidade || '';
    } else {
      localId = null;
      morada = cliente?.morada || cliente?.endereco || '';
      codigoPostal = cliente?.codigoPostal || '';
      cidade = cliente?.cidade || '';
    }

    const responsaveisIds = [...documentRef.querySelectorAll('.ob-func-check:checked')].map(item => item.value);
    const obj = {
      nome: nome,
      clienteId: clienteId,
      localId: localId,
      morada: morada,
      codigoPostal: codigoPostal || null,
      cidade: cidade || null,
      estado: novoEstado,
      observacoes: documentRef.getElementById('ob_obs').value.trim(),
      longaDuracao: documentRef.getElementById('ob_longa_duracao')?.checked === true,
      responsavelId: responsaveisIds[0] || null,
      responsaveisIds: responsaveisIds,
      relatorioResponsavelId: documentRef.getElementById('ob_relatorio_responsavel') ? (documentRef.getElementById('ob_relatorio_responsavel').value || null) : null,
      dataInicioPrevista: documentRef.getElementById('ob_data_inicio_prevista')?.value || null,
      dataFimPrevista: documentRef.getElementById('ob_data_fim_prevista')?.value || null,
      valor: documentRef.getElementById('ob_valor')?.value !== '' ? parseFloat(documentRef.getElementById('ob_valor').value) : null,
      custoHora: documentRef.getElementById('ob_custo_hora')?.value !== '' ? parseFloat(documentRef.getElementById('ob_custo_hora').value) : null,
      temAutosMedicao: documentRef.getElementById('ob_tem_autos_medicao')?.checked === true,
      adminId: adminId
    };

    guardarArmazem('obras', obj, isEdit);

    if (isEdit && estadoAnterior === 'preparacao' && novoEstado === 'ativa') {
      setTimeout(function () {
        confirmar('A obra passou a Ativa. Criar uma Ordem de Serviço com os materiais necessários?', { titulo: 'Obra ativada', tipo: 'sucesso', icone: 'fa-hard-hat', textoOk: 'Criar OS' })
          .then(function (sim) { if (sim) criarOSdaObra(obraId); });
      }, 120);
    } else if (!isEdit && novoEstado === 'ativa') {
      const novoObraId = obj.id;
      setTimeout(function () {
        confirmar('A obra foi criada já como Ativa. Criar uma Ordem de Serviço com os materiais necessários?', { titulo: 'Obra ativada', tipo: 'sucesso', icone: 'fa-hard-hat', textoOk: 'Criar OS' })
          .then(function (sim) { if (sim) criarOSdaObra(novoObraId, true); });
      }, 120);
    }
  }

  window.TotalGestSaveFormObra = { run: run };
})();
