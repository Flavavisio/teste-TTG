/* Total Gest — preparação do formulário de folha de obra. */
(function () {
  'use strict';

  function prepare(options) {
    const opts = options || {};
    const documentRef = opts.document;
    const dados = opts.data || {};
    const usuarioLogado = opts.user || null;
    const gerarId = opts.generateId;
    const mostrarErro = opts.showError;
    const showAlert = opts.showAlert;
    const horasCorrigidasManualmente = opts.hoursCorrectedManually === true;
    const horasPicadasOS = opts.hoursForServiceOrder;
    const horasPicadasObra = opts.hoursForWork;

    const descricao = documentRef.getElementById('fo_descricao').value.trim();
    if (!descricao || descricao.length < 3) {
      mostrarErro('Descreve o trabalho realizado (pelo menos 3 caracteres).');
      documentRef.getElementById('fo_descricao')?.focus();
      return { ok: false };
    }

    const servicoIdCampo = documentRef.getElementById('fo_servico_id')?.value || '';
    const obraIdCampo = documentRef.getElementById('fo_obra')?.value || '';
    let horas = parseFloat(documentRef.getElementById('fo_horas').value) || 0;
    if (!horasCorrigidasManualmente) {
      if (servicoIdCampo) horas = horasPicadasOS(servicoIdCampo);
      else if (obraIdCampo) horas = horasPicadasObra(obraIdCampo);
    }
    if (horas < 0) {
      showAlert('Horas não podem ser negativas.');
      return { ok: false };
    }

    const funcionarioId = documentRef.getElementById('fo_funcionario')?.value || usuarioLogado?.id || '';
    const adminId = usuarioLogado?.role === 'admin' ? usuarioLogado.id : (usuarioLogado?.role === 'encarregado' ?
      usuarioLogado.adminId : usuarioLogado?.adminId);

    const temCampoCliente = !!documentRef.getElementById('fo_cliente');
    let clienteId = '';
    let cliente = null;
    let localId = '';
    let localNome = 'Sede';
    let obraDescricao = '';

    if (temCampoCliente) {
      clienteId = documentRef.getElementById('fo_cliente')?.value || '';
      if (!clienteId) {
        showAlert('Selecione o cliente.');
        return { ok: false };
      }
      cliente = dados.clientes?.find(item => item.id === clienteId);
      localId = documentRef.getElementById('fo_local')?.value || '';
      if (localId === '__novo__') {
        const nomeNovoLocal = (documentRef.getElementById('fo_local_nome')?.value || '').trim();
        if (!nomeNovoLocal) {
          showAlert('Indique o nome do novo local.');
          return { ok: false };
        }
        const novoLocalId = gerarId();
        dados.locais = dados.locais || [];
        dados.locais.push({
          id: novoLocalId,
          adminId: adminId,
          clienteId: clienteId,
          nome: nomeNovoLocal,
          morada: cliente?.morada || '',
          dataCriacao: Date.now()
        });
        localId = novoLocalId;
        localNome = nomeNovoLocal;
      } else if (localId) {
        localNome = dados.locais?.find(item => item.id === localId)?.nome || 'Sede';
      }
      obraDescricao = (cliente?.nome || '') + ' / ' + localNome;
    } else {
      obraDescricao = documentRef.getElementById('fo_obra_desc')?.value.trim() || '';
    }

    return {
      ok: true,
      serviceOrderId: servicoIdCampo,
      workId: obraIdCampo,
      hours: horas,
      employeeId: funcionarioId,
      adminId: adminId,
      clientId: clienteId,
      localId: localId,
      workDescription: obraDescricao
    };
  }

  window.TotalGestSaveFormFolhaContext = { prepare: prepare };
})();
