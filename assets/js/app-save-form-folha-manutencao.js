/* Total Gest — manutenção automática associada à folha de obra. */
(function () {
  'use strict';

  function apply(options) {
    const opts = options || {};
    const dados = opts.data || {};
    const obj = opts.sheet || {};
    const isEdit = opts.isEdit === true;
    const gerarId = opts.generateId;
    const getDataHoje = opts.getToday;
    const avancarPeriodicidade = opts.advancePeriodicity;
    const notificar = opts.notify;

    if (!isEdit && obj.servicoId) {
      const serviceOrder = dados.servicos?.find(function (item) { return item.id === obj.servicoId; });
      if (serviceOrder?.contratoId) {
        const contract = dados.contratos?.find(function (item) { return item.id === serviceOrder.contratoId; });
        if (contract) {
          obj.contratoId = contract.id;
          const nextDate = avancarPeriodicidade(obj.data || getDataHoje(), contract.periodicidade);
          dados.registosManutencao = dados.registosManutencao || [];
          dados.registosManutencao.push({
            id: gerarId(),
            adminId: contract.adminId,
            contratoId: contract.id,
            equipamentoId: contract.equipamentoId,
            dataRealizacao: obj.data || getDataHoje(),
            tecnicoId: obj.funcionarioId || contract.tecnicoId || null,
            observacoes: 'Manutenção concluída via OS ' + (serviceOrder.numeroRegisto || '') + '.',
            proximaData: nextDate,
            dataCriacao: Date.now()
          });
          contract.proximaManutencao = nextDate;
          if (contract.clienteId) {
            notificar(contract.clienteId, '✅ Manutenção realizada', 'A manutenção do contrato ' + (contract.numero || '') + ' foi concluída com sucesso.', contract.adminId);
          }
        }
      }
    }
  }

  window.TotalGestSaveFormFolhaManutencao = { apply: apply };
})();
