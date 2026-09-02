/* Total Gest — gravação do formulário de requisição. */
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
    const guardarDados = opts.saveData;
    const fecharModal = opts.closeModal;
    const renderizarTudo = opts.renderAll;
    const showAlert = opts.showAlert;
    const FileReaderCtor = opts.FileReader || window.FileReader;

    const produtoInputs = documentRef.querySelectorAll('.item-produto');
    const qtdInputs = documentRef.querySelectorAll('.item-qtd');
    let itens = [];
    for (let i = 0; i < produtoInputs.length; i++) {
      const nome = produtoInputs[i].value.trim();
      const qtd = parseInt(qtdInputs[i].value) || 1;
      if (nome) itens.push({ nome, quantidade: qtd });
    }

    let funcionarioId;
    if (usuarioLogado?.role === 'admin') {
      funcionarioId = documentRef.getElementById('req_funcionario')?.value || null;
    } else {
      funcionarioId = usuarioLogado.id;
    }

    const obj = {
      obraDescricao: documentRef.getElementById('req_obra_desc').value.trim(),
      fornecedor: documentRef.getElementById('req_fornecedor').value.trim(),
      descricao: documentRef.getElementById('req_descricao').value.trim(),
      itens: itens,
      data: documentRef.getElementById('req_data').value,
      funcionarioId: funcionarioId,
      adminId: usuarioLogado?.role === 'admin' ? usuarioLogado.id : (usuarioLogado?.role === 'encarregado' ?
        usuarioLogado.adminId : usuarioLogado?.adminId),
      status: 'pendente_aprov'
    };

    if (!obj.obraDescricao || !obj.descricao) {
      showAlert('Obra e descrição são obrigatórios.');
      return;
    }

    function finalizarRequisicao(objFinal) {
      let lista = dados.requisicoes || [];
      if (isEdit) {
        const idx = lista.findIndex(i => i.id === idEditando);
        if (idx !== -1) lista[idx] = { ...lista[idx], ...objFinal };
      } else {
        objFinal.id = gerarId();
        lista.push(objFinal);
      }
      dados.requisicoes = lista;
      guardarDados(dados);
      fecharModal();
      renderizarTudo();
      showAlert('Requisição ' + (isEdit ? 'atualizada' : 'criada') + ' com sucesso!');
    }

    const fileInput = documentRef.getElementById('req_anexo');
    if (fileInput && fileInput.files && fileInput.files[0]) {
      const reader = new FileReaderCtor();
      reader.onload = function (ev) {
        obj.anexo = ev.target.result;
        finalizarRequisicao(obj);
      };
      reader.readAsDataURL(fileInput.files[0]);
      return;
    }

    const reqAtual = dados.requisicoes?.find(x => x.id === idEditando);
    obj.anexo = reqAtual && reqAtual.anexo ? reqAtual.anexo : null;
    finalizarRequisicao(obj);
  }

  window.TotalGestSaveFormRequisicao = { run: run };
})();
