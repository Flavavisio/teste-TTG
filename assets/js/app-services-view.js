/* Total Gest — apresentação da área de Ordens de Serviço */
(function () {
  'use strict';

  function serviceHistoryLoadedSinceLabel(value) {
    if (!value) return '—';
    return new Date(value + 'T00:00:00').toLocaleDateString('pt-PT');
  }

  function specialtyAndHistoryNotice(options) {
    const opts = options || {};
    const pending = Array.isArray(opts.pendingServices) ? opts.pendingServices : [];
    const canSeePending = opts.canSeePending === true;
    const loadedSinceLabel = opts.loadedSinceLabel || '—';
    let html = '';
    if (canSeePending && pending.length) {
      const preview = pending.slice(0, 4).map(item => `${item.number || ''} (${Array.isArray(item.types) ? item.types.join(', ') : ''})`).join(' · ');
      html += `<div style="background:#fef3c7;border:1px solid #f59e0b;color:#92400e;border-radius:8px;padding:10px 14px;margin-bottom:10px;font-size:.85rem;"><i class="fas fa-triangle-exclamation"></i> <strong>${pending.length}</strong> OS já dada(s) como concluída(s) ainda tem(êm) relatório(s) de especialidade por preencher: ${preview}${pending.length > 4 ? ' ...' : ''}</div>`;
    }
    html += `<div style="margin-bottom:10px;"><button class="btn btn-sm" id="btn-carregar-os-antigas" style="background:#f1f5f9;color:#334155;" onclick="carregarOSMaisAntigo()"><i class="fas fa-clock-rotate-left"></i> Carregar OS mais antigas (+3 meses)</button><span style="font-size:.75rem;color:#94a3b8;margin-left:8px;">A mostrar concluídas desde ${loadedSinceLabel}. Pendentes/em andamento aparecem sempre, seja qual for a idade.</span></div>`;
    return html;
  }

  function specialtyAndHistoryNoticeFromState(options) {
    const opts = options || {};
    const pendingState = opts.pendingState || {};
    return specialtyAndHistoryNotice({
      canSeePending: pendingState.canSeePending === true,
      pendingServices: pendingState.pendingServices,
      loadedSinceLabel: serviceHistoryLoadedSinceLabel(opts.loadedSince)
    });
  }

  function applySpecialtyAndHistoryNotice(options) {
    const opts = options || {};
    if (!opts.element) return false;
    opts.element.innerHTML = specialtyAndHistoryNoticeFromState({
      pendingState: opts.pendingState,
      loadedSince: opts.loadedSince
    });
    return true;
  }

  function servicesTableState(options) {
    const opts = options || {};
    const totalCount = Number(opts.totalCount) || 0;
    const visibleCount = Number(opts.visibleCount) || 0;
    const renderToolbar = typeof opts.renderToolbar === 'function' ? opts.renderToolbar : function () { return ''; };
    return {
      hasRows: visibleCount > 0,
      toolbarHtml: totalCount ? renderToolbar('servicos', 'Pesquisar por Nº, cliente, descrição, estado…', visibleCount, totalCount) : '',
      emptyRowsHtml: visibleCount === 0 && totalCount ? '<tr><td colspan="9" style="text-align:center;color:#94a3b8;">Sem resultados para essa pesquisa.</td></tr>' : '',
      emptyDisplay: visibleCount === 0 && totalCount === 0 ? 'block' : 'none'
    };
  }

  function applyServicesTableState(options) {
    const opts = options || {};
    const state = opts.state || {};
    if (opts.toolbarElement) opts.toolbarElement.innerHTML = state.toolbarHtml || '';
    if (!state.hasRows) {
      opts.tbody.innerHTML = state.emptyRowsHtml || '';
      opts.emptyElement.style.display = state.emptyDisplay || 'none';
      return false;
    }
    opts.emptyElement.style.display = state.emptyDisplay || 'none';
    return true;
  }

  function renderServicesTableState(options) {
    const opts = options || {};
    const state = servicesTableState({
      totalCount: opts.totalCount,
      visibleCount: opts.visibleCount,
      renderToolbar: opts.renderToolbar
    });
    return applyServicesTableState({
      state,
      toolbarElement: opts.toolbarElement,
      tbody: opts.tbody,
      emptyElement: opts.emptyElement
    });
  }

  function statusControl(options) {
    const opts = options || {}, status = opts.status || 'pendente', serviceId = opts.serviceId || '';
    if (status === 'por aprovar') return '<span style="background:#fde68a;color:#92400e;padding:3px 10px;border-radius:999px;font-size:.74rem;font-weight:700;"><i class="fas fa-clock"></i> por aprovar</span>';
    if (opts.canEdit === true && status !== 'concluído') return `<select class="status-select" onchange="alterarStatusOS('${serviceId}', this.value)"><option value="pendente" ${status === 'pendente' ? 'selected' : ''}>pendente</option><option value="em andamento" ${status === 'em andamento' ? 'selected' : ''}>em andamento</option><option value="stand by" ${status === 'stand by' ? 'selected' : ''}>stand by</option><option value="concluído" ${status === 'concluído' ? 'selected' : ''}>concluído</option></select>`;
    return `<span class="${opts.badgeClass || ''}">${status}</span>`;
  }

  function serviceStatusControl(options) {
    const opts = options || {};
    const role = opts.role || '';
    return statusControl({
      serviceId: opts.serviceId || '',
      status: opts.status || 'pendente',
      canEdit: role === 'admin' || role === 'subadmin' || role === 'encarregado',
      badgeClass: opts.badgeClass || ''
    });
  }

  function workSheetActions(options) {
    const opts = options || {};
    if (opts.status !== 'concluído') return '';
    const serviceId = opts.serviceId || '';
    if (opts.sheetId) {
      let html = `<button class="btn btn-sm" style="background:#0ea5e9;color:#fff;" onclick="abrirFolhaDetalhe('${opts.sheetId}')" title="Ver folha de obra e gerar PDF"><i class="fas fa-eye"></i></button>`;
      html += opts.workId ? ` <button class="btn btn-sm btn-success" onclick="criarFolhaDaOS('${serviceId}')" title="Criar mais uma folha de obra para esta OS"><i class="fas fa-plus"></i></button>` : ` <button class="btn btn-sm" style="background:#16a34a;color:#fff;opacity:.55;cursor:not-allowed;" onclick="alert('Já existe uma folha de obra para esta OS.')" title="Já existe uma folha de obra para esta OS"><i class="fas fa-clipboard-check"></i></button>`;
      return html;
    }
    return `<button class="btn btn-sm btn-success" onclick="criarFolhaDaOS('${serviceId}')"><i class="fas fa-clipboard-list"></i> Folha</button>`;
  }

  function rowLeadingCells(options) {
    const opts = options || {};
    return `<td><strong>${opts.number || ''}</strong> ${opts.hasMaterials ? '<i class="fas fa-boxes-stacked" style="color:#0891b2;" title="Esta OS tem materiais associados"></i>' : ''}</td><td>${opts.clientName || ''}</td><td>${opts.employeeName || 'Todos'}</td><td>${opts.date || '-'}</td><td>${opts.time || '-'}</td><td>${opts.description || '-'}</td><td>${opts.workTypesHtml || '<span style="color:#94a3b8;">-</span>'}</td><td>${opts.statusHtml || ''}</td>`;
  }

  function primaryRowActions(options) {
    const opts = options || {}, serviceId = opts.serviceId || '', status = opts.status || 'pendente', role = opts.role || '';
    const canApprove = role === 'admin' || role === 'encarregado', canManage = role === 'admin' || role === 'subadmin' || role === 'encarregado';
    let html = `<button class="btn btn-sm" style="background:#334155;color:#fff;" onclick="abrirVerOS('${serviceId}')" title="Ver OS — folhas de obra e materiais"><i class="fas fa-eye"></i> Ver OS</button>`;
    if (status === 'por aprovar' && canApprove) html += `<button class="btn btn-sm btn-success" onclick="aprovarAssistencia('${serviceId}')"><i class="fas fa-check"></i> Aprovar</button><button class="btn btn-sm btn-danger" onclick="rejeitarAssistencia('${serviceId}')" title="Rejeitar pedido"><i class="fas fa-times"></i></button>`;
    if (canManage) {
      html += `<button class="btn btn-sm btn-warning" onclick="abrirModal('servico','${serviceId}')" title="Editar"><i class="fas fa-edit"></i></button>${status !== 'concluído' ? `<button class="btn btn-sm" style="background:#0f766e;color:#fff;" onclick="finalizarEGerarReportOS('${serviceId}')" title="Finalizar e gerar relatório completo"><i class="fas fa-flag-checkered"></i></button>` : `<button class="btn btn-sm" style="background:#0f766e;color:#fff;" onclick="gerarRelatorioOSIndividual('${serviceId}')" title="Gerar relatório desta OS"><i class="fas fa-file-lines"></i></button>`}`;
      if (opts.localPayment === true) { const paid = opts.paid === true, note = paid && opts.receiptMoloniId ? ' (recibo emitido na Moloni)' : ''; html += `<button class="btn btn-sm" style="background:${paid ? '#16a34a' : '#dc2626'};color:#fff;font-weight:700;" onclick="_pagoTogglarOS('${serviceId}')" title="${paid ? 'Pago — clica para alterar' + note : 'Não pago — clica para confirmar'}">${paid ? '€ Pago' : '<span style="text-decoration:line-through;">€</span> Não pago'}</button>`; }
    }
    return html;
  }

  function erpRowActions(options) {
    const o = options || {}, id = o.serviceId || '';
    if (o.canManage !== true || o.hasValue !== true || o.erpActive !== true) return '';
    let html = '';
    if (o.status === 'concluído') {
      if (o.provider === 'toconline') html += `<button class="btn btn-sm" style="background:${o.invoiceTOId ? '#64748b' : '#0f766e'};color:#fff;" onclick="faturarOSViaTOConline('${id}')" title="${o.invoiceTOId ? 'Já faturado — clica para faturar de novo' : 'Faturar via TOConline'}"><i class="fas fa-file-invoice"></i> ${o.invoiceTOId ? 'Faturado' : 'Faturar'}</button>`;
      else html += `<button class="btn btn-sm" style="background:${o.invoiceMoloniId ? '#64748b' : '#7c3aed'};color:#fff;" onclick="faturarOSViaMoloni('${id}')" title="${o.invoiceMoloniId ? 'Já faturado — clica para faturar de novo' : 'Faturar via Moloni'}"><i class="fas fa-file-invoice"></i> ${o.invoiceMoloniId ? 'Faturado' : 'Faturar'}</button>`;
    }
    if (o.invoiceMoloniUrl) html += `<a href="${o.invoiceMoloniUrl}" target="_blank" class="btn btn-sm btn-outline" title="Abrir o PDF da fatura na Moloni"><i class="fas fa-file-pdf"></i> Fatura</a>`;
    if (o.invoiceMoloniId && !o.receiptMoloniId && !o.localPayment) html += `<button class="btn btn-sm btn-outline" onclick="_verificarPagamentoMoloni('${id}')" title="Ir verificar à Moloni se esta fatura já foi paga"><i class="fas fa-rotate"></i> Verificar pagamento</button>`;
    if (o.receiptMoloniUrl) html += `<a href="${o.receiptMoloniUrl}" target="_blank" class="btn btn-sm btn-outline" title="Abrir o PDF do recibo na Moloni"><i class="fas fa-receipt"></i> Recibo</a>`;
    html += `<button class="btn btn-sm" style="background:${o.guideMoloniId ? '#64748b' : '#0e7490'};color:#fff;" onclick="emitirGuiaTransporteMoloni('${id}')" title="${o.guideMoloniId ? 'Já tem guia — clica para emitir outra' : 'Emitir Guia de Transporte na Moloni (materiais desta OS)'}"><i class="fas fa-truck"></i> ${o.guideMoloniId ? 'Guia emitida' : 'Guia de Transporte'}</button>`;
    if (o.guideMoloniUrl) html += `<a href="${o.guideMoloniUrl}" target="_blank" class="btn btn-sm btn-outline" title="Abrir o PDF da guia de transporte na Moloni"><i class="fas fa-file-pdf"></i> Guia</a>`;
    if (o.invoiceMoloniId && !o.creditNoteMoloniId) html += `<button class="btn btn-sm btn-danger" onclick="emitirNotaCreditoMoloni('${id}')" title="Anula esta fatura por completo, emitindo uma Nota de Crédito na Moloni"><i class="fas fa-rotate-left"></i> Anular fatura</button>`;
    if (o.creditNoteMoloniUrl) html += `<a href="${o.creditNoteMoloniUrl}" target="_blank" class="btn btn-sm btn-outline" title="Abrir o PDF da nota de crédito na Moloni"><i class="fas fa-file-pdf"></i> Nota Créd.</a>`;
    return html;
  }

  function rowActions(options) {
    const o = options || {};
    let html = primaryRowActions(o);
    html += erpRowActions(o);
    if (o.role === 'admin') html += `<button class="btn btn-sm btn-danger" onclick="excluirEntidade('servico','${o.serviceId || ''}')"><i class="fas fa-trash"></i></button>`;
    return `<td><div class="acoes">${html}</div></td>`;
  }

  function serviceRowFromData(options) {
    const opts = options || {};
    const service = opts.service || {};
    const rowData = opts.rowData || {};
    const statusHtml = opts.statusHtml != null ? opts.statusHtml : serviceStatusControl({
      serviceId: service.id || '',
      status: service.status || 'pendente',
      role: opts.role || '',
      badgeClass: opts.badgeClass || ''
    });
    return serviceRow({
      leadingCells: {
        number: rowData.number,
        hasMaterials: rowData.hasMaterials,
        clientName: rowData.clientName,
        employeeName: rowData.employeeName,
        date: service.data || '-',
        time: service.hora || '-',
        description: opts.descriptionHtml || '-',
        workTypesHtml: opts.workTypesHtml,
        statusHtml
      },
      actions: opts.actions || {}
    });
  }

  function createServiceRowRenderer(options) {
    const opts = options || {};
    const getBadgeClass = typeof opts.getBadgeClass === 'function' ? opts.getBadgeClass : function () { return ''; };
    const escapeDescription = typeof opts.escapeDescription === 'function' ? opts.escapeDescription : function (value) { return value == null ? '' : String(value); };
    const getWorkTypesHtml = typeof opts.getWorkTypesHtml === 'function' ? opts.getWorkTypesHtml : function () { return ''; };
    return function (service, rowData, actions) {
      const currentService = service || {};
      return serviceRowFromData({
        service: currentService,
        rowData: rowData || {},
        role: opts.role || '',
        badgeClass: getBadgeClass(currentService.status),
        descriptionHtml: escapeDescription(currentService.descricao || '-'),
        workTypesHtml: getWorkTypesHtml(currentService),
        actions: actions || {}
      });
    };
  }

  function serviceRow(options) {
    const opts = options || {};
    return `<tr>${rowLeadingCells(opts.leadingCells || {})}${rowActions(opts.actions || {})}</tr>`;
  }

  window.TotalGestServicesView = { serviceHistoryLoadedSinceLabel, specialtyAndHistoryNotice, specialtyAndHistoryNoticeFromState, applySpecialtyAndHistoryNotice, servicesTableState, applyServicesTableState, renderServicesTableState, statusControl, serviceStatusControl, workSheetActions, rowLeadingCells, primaryRowActions, erpRowActions, rowActions, serviceRowFromData, createServiceRowRenderer, serviceRow };
})();
