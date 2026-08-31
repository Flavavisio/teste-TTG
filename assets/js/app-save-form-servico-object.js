/* Total Gest — construção do objeto da Ordem de Serviço. */
(function () {
  'use strict';

  function prepare(options) {
    const opts = options || {};
    const doc = opts.document || document;
    const existingOrder = opts.existingOrder || null;

    const obj = {
      clienteId: doc.getElementById('s_cliente').value,
      funcionarioId: opts.employeeId,
      funcionariosIds: opts.employeeIds,
      relatorioResponsavelId: doc.getElementById('s_relatorio_responsavel')
        ? (doc.getElementById('s_relatorio_responsavel').value || null)
        : (existingOrder ? existingOrder.relatorioResponsavelId : null),
      obraId: existingOrder ? (existingOrder.obraId || null) : (opts.newWorkId || null),
      valor: doc.getElementById('s_valor')
        ? (doc.getElementById('s_valor').value === '' ? null : Number(doc.getElementById('s_valor').value))
        : (existingOrder ? existingOrder.valor : null),
      pagamentoLocal: doc.getElementById('s_pagamento_local')
        ? doc.getElementById('s_pagamento_local').checked
        : (existingOrder ? !!existingOrder.pagamentoLocal : false),
      duracao: doc.getElementById('s_duracao')
        ? (doc.getElementById('s_duracao').value === '' ? null : parseInt(doc.getElementById('s_duracao').value, 10))
        : (existingOrder ? existingOrder.duracao : null),
      duracaoDias: doc.getElementById('s_duracao_dias')
        ? (doc.getElementById('s_duracao_dias').value === '' ? null : parseInt(doc.getElementById('s_duracao_dias').value, 10))
        : (existingOrder ? existingOrder.duracaoDias : null),
      morada: doc.getElementById('s_morada')
        ? (doc.getElementById('s_morada').value.trim() || null)
        : (existingOrder ? existingOrder.morada : null),
      localId: opts.localId || null,
      numeroPorta: doc.getElementById('s_numero_porta')
        ? (doc.getElementById('s_numero_porta').value.trim() || null)
        : (existingOrder ? existingOrder.numeroPorta : null),
      codigoPostal: doc.getElementById('s_codigo_postal')
        ? (doc.getElementById('s_codigo_postal').value.trim() || null)
        : (existingOrder ? existingOrder.codigoPostal : null),
      cidade: doc.getElementById('s_cidade')
        ? (doc.getElementById('s_cidade').value.trim() || null)
        : (existingOrder ? existingOrder.cidade : null),
      freguesia: doc.getElementById('s_freguesia')
        ? (doc.getElementById('s_freguesia').value.trim() || null)
        : (existingOrder ? existingOrder.freguesia : null),
      data: doc.getElementById('s_data').value,
      hora: doc.getElementById('s_hora').value,
      descricao: doc.getElementById('s_descricao').value.trim(),
      observacoes: doc.getElementById('s_observacoes')?.value.trim() || null,
      status: doc.getElementById('s_status').value,
      tiposTrabalho: opts.selectedWorkTypes(),
      adminId: opts.adminId
    };

    obj._eraAprovacaoAssistencia = !!(
      opts.approvingAssistanceId &&
      opts.editingId === opts.approvingAssistanceId &&
      (obj.status === 'por aprovar' || !obj.status)
    );
    if (obj._eraAprovacaoAssistencia) obj.status = 'pendente';

    return obj;
  }

  window.TotalGestSaveFormServicoObject = { prepare: prepare };
})();
