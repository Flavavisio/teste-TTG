/* Total Gest — notificações pós-gravação de Ordem de Serviço. */
(function () {
  'use strict';

  function run(options) {
    const opts = options || {};
    const obj = opts.value || {};
    const oldService = opts.oldService || null;
    const data = opts.data || {};

    if (!opts.isEdit) {
      const recipients = [...new Set([...(obj.funcionariosIds || []), obj.funcionarioId].filter(Boolean))];
      if (recipients.length) {
        const whenText = obj.data ? ('agendada para ' + obj.data + (obj.hora ? ', ' + obj.hora : '')) : 'ainda sem data definida';
        const clientText = obj.clienteId ? (opts.clientName(obj.clienteId) || '') : '';
        const message = (clientText ? clientText + ' — ' : '') + (obj.descricao ? obj.descricao + ' — ' : '') + whenText + '.';
        recipients.forEach(function (employeeId) {
          opts.notify(employeeId, '🧾 Nova Ordem de Serviço atribuída', message, obj.adminId);
        });
      }

      if (obj.pagamentoLocal && obj.clienteId) {
        const creator = data.administradores?.find(function (admin) { return admin.id === obj.adminId; });
        const companyName = creator?.empresa || creator?.nome || 'A empresa';
        const whenClientText = obj.data ? (obj.data + (obj.hora ? ' às ' + obj.hora : '')) : 'uma data a combinar';
        const valueText = obj.valor != null ? opts.formatEuro(obj.valor) : 'a combinar';
        opts.notify(obj.clienteId, '💶 Pagamento no local', companyName + ' criou a ordem de serviço ' + (obj.numeroRegisto ? 'nº ' + obj.numeroRegisto : '') + ' para ' + whenClientText + '. Deverá ter consigo o valor de ' + valueText + ' para efetuar o pagamento no final do serviço. Obrigado.', obj.adminId);
      } else if (obj.clienteId && obj.data) {
        const whenClientText2 = obj.data + (obj.hora ? ' às ' + obj.hora : '');
        opts.notify(obj.clienteId, '📅 Visita agendada', 'Foi agendada uma visita para ' + whenClientText2 + (obj.descricao ? ' — ' + obj.descricao : '') + '.', obj.adminId);
      }
      return;
    }

    if (!oldService) return;

    const idsBefore = [...new Set([...(oldService.funcionariosIds || []), oldService.funcionarioId].filter(Boolean))];
    const idsAfter = [...new Set([...(obj.funcionariosIds || []), obj.funcionarioId].filter(Boolean))];
    const dateChanged = ('data' in obj) && obj.data !== oldService.data;
    const timeChanged = ('hora' in obj) && obj.hora !== oldService.hora;
    const removed = idsBefore.filter(function (id) { return !idsAfter.includes(id); });
    const kept = idsAfter.filter(function (id) { return idsBefore.includes(id); });
    const number = obj.numeroRegisto || oldService.numeroRegisto || '';

    if (dateChanged || timeChanged) {
      const whenText = obj.data ? ('agendada agora para ' + obj.data + (obj.hora ? ', ' + obj.hora : '')) : 'ficou sem data definida';
      kept.forEach(function (employeeId) {
        opts.notify(employeeId, '📅 OS ' + (number ? '#' + number + ' ' : '') + 'alterada', 'A data/hora foi alterada — ' + whenText + '.', obj.adminId || oldService.adminId);
      });
    }

    if (removed.length) {
      removed.forEach(function (employeeId) {
        opts.notify(employeeId, '🚫 Retirado de uma OS', 'Já não estás atribuído à OS ' + (number ? '#' + number : '') + '.', obj.adminId || oldService.adminId);
      });
    }

    if (obj._eraAprovacaoAssistencia && obj.clienteId) {
      const whenClientText = obj.data ? (obj.data + (obj.hora ? ' às ' + obj.hora : '')) : 'uma data a combinar';
      opts.notify(obj.clienteId, '✅ Pedido de assistência aceite', 'O teu pedido de assistência foi aceite e agendado para ' + whenClientText + '.', obj.adminId || oldService.adminId);
    }
  }

  window.TotalGestSaveFormServicoNotifications = { run: run };
})();
