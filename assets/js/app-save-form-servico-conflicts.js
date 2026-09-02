/* Total Gest — validações posteriores do objeto da Ordem de Serviço. */
(function () {
  'use strict';

  function validate(options) {
    const opts = options || {};
    const obj = opts.value || {};
    const data = opts.data || {};
    const user = opts.user || null;
    const isEdit = opts.isEdit === true;
    const editingId = opts.editingId || null;

    if (opts.blockIfAbsent([...(obj.funcionariosIds || []), obj.funcionarioId].filter(Boolean), obj.data)) {
      return { ok: false };
    }

    if (!obj.clienteId) {
      opts.showAlert('Selecione um cliente.');
      return { ok: false };
    }

    if (!isEdit && obj.localId && obj.data && (obj.tiposTrabalho || []).length) {
      const outrasNoMesmoDia = (data.servicos || []).filter(function (servico) {
        return servico.id !== editingId &&
          servico.clienteId === obj.clienteId &&
          servico.localId === obj.localId &&
          servico.data === obj.data;
      });
      const tiposRepetidos = obj.tiposTrabalho.filter(function (tipo) {
        return outrasNoMesmoDia.some(function (servico) {
          return (servico.tiposTrabalho || []).includes(tipo);
        });
      });
      if (tiposRepetidos.length) {
        const continuar = opts.showConfirm(`⚠️ Já existe outra Ordem de Serviço para este cliente, neste mesmo local, no mesmo dia (${obj.data}), com o(s) tipo(s) de relatório: ${tiposRepetidos.join(', ')}.\n\nPode ser sem querer duplicado. Queres criar esta OS na mesma?`);
        if (!continuar) return { ok: false };
      }
    }

    if (!obj.funcionarioId && user?.role === 'funcionario') {
      obj.funcionarioId = user.id;
    }

    if (obj.funcionarioId && obj.data && obj.hora && (user?.role === 'admin' || user?.role === 'subadmin')) {
      const inicioNova = opts.timeToMinutes(obj.hora);
      const fimNova = inicioNova + (parseInt(obj.duracao, 10) || 60);
      const outras = (data.servicos || []).filter(function (servico) {
        return servico.id !== editingId &&
          servico.funcionarioId === obj.funcionarioId &&
          servico.data === obj.data &&
          servico.hora;
      });
      const emConflito = outras.find(function (servico) {
        const ini2 = opts.timeToMinutes(servico.hora);
        const fim2 = ini2 + (parseInt(servico.duracao, 10) || 60);
        return inicioNova < fim2 && fimNova > ini2;
      });
      if (emConflito) {
        const nomeFunc = opts.employeeName(obj.funcionarioId) || 'este funcionário';
        const continuar = opts.showConfirm(`⚠️ Sobreposição de horário: ${nomeFunc} já tem a OS #${emConflito.numeroRegisto || ''} marcada para ${emConflito.data} às ${emConflito.hora}.\n\nQueres continuar e criar esta OS na mesma?`);
        if (!continuar) return { ok: false };
      }
    }

    return { ok: true, value: obj };
  }

  window.TotalGestSaveFormServicoConflicts = { validate: validate };
})();
