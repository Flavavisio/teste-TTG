/* Total Gest — seleção e apresentação do domínio Ferramentas */
(function () {
  'use strict';

  function toolsViewElements(doc) {
    return {
      table: doc.getElementById('tabelaFerramentas'),
      empty: doc.getElementById('emptyFerramentas'),
      count: doc.getElementById('countFerramentas'),
      historyTable: doc.getElementById('tabelaHistoricoLevantamentos'),
      historyEmpty: doc.getElementById('emptyHistoricoLevantamentos')
    };
  }

  function selectToolsForTenant(tools, tenantId) {
    return (Array.isArray(tools) ? tools : []).filter(function (tool) { return tool.adminId === tenantId; });
  }

  function selectToolHistoryForTenant(history, tenantId) {
    return (Array.isArray(history) ? history : []).filter(function (entry) { return entry.adminId === tenantId; }).sort(function (a,b) {
      return (b.dataLevantamento || 0) - (a.dataLevantamento || 0);
    });
  }

  function formatToolDate(value) {
    return new Date(value).toLocaleString('pt-PT', { day:'2-digit', month:'2-digit', hour:'2-digit', minute:'2-digit' });
  }

  function toolAvailabilityBadge(openEntry) {
    return openEntry
      ? '<span class="badge" style="background:#f59e0b;color:#fff;">Levantado</span>'
      : '<span class="badge" style="background:#16a34a;color:#fff;">Disponível</span>';
  }

  function toolRowHtml(tool, options) {
    const o=options || {};
    const openEntry=o.getCurrentState(tool.id);
    return `<tr>
                    <td><strong>${o.escapeHtml(tool.nome)}</strong>${tool.descricao ? `<div class="help-text">${o.escapeHtml(tool.descricao)}</div>` : ''}</td>
                    <td><span style="font-family:monospace;background:#f1f5f9;padding:3px 8px;border-radius:6px;font-size:.82rem;">${tool.codigo}</span></td>
                    <td>${toolAvailabilityBadge(openEntry)}</td>
                    <td>${openEntry ? o.escapeHtml(o.getEmployeeName(openEntry.funcionarioId)) : '—'}</td>
                    <td>${openEntry ? formatToolDate(openEntry.dataLevantamento) : '—'}</td>
                    <td>
                        <button class="btn btn-sm btn-outline" onclick="abrirModalFerramenta('${tool.id}')" title="Ver / editar"><i class="fas fa-pen"></i></button>
                        <button class="btn btn-sm" style="background:#152a52;color:#fff;" onclick="imprimirQRFerramenta('${tool.id}')" title="Imprimir QR Code"><i class="fas fa-print"></i></button>
                    </td>
                </tr>`;
  }

  function historyStatusBadge(entry) {
    return entry.estado === 'levantado'
      ? '<span class="badge" style="background:#f59e0b;color:#fff;">Em uso</span>'
      : (entry.teveProblema
          ? '<span class="badge" style="background:#dc2626;color:#fff;">Devolvido c/ problema</span>'
          : '<span class="badge" style="background:#16a34a;color:#fff;">Devolvido OK</span>');
  }

  function toolHistoryRowHtml(entry, options) {
    const o=options || {};
    const tool=(Array.isArray(o.tools) ? o.tools : []).find(function (item) { return item.id === entry.ferramentaId; });
    return `<tr>
                        <td>${o.escapeHtml((tool && tool.nome) || '(equipamento eliminado)')}</td>
                        <td>${o.escapeHtml(o.getEmployeeName(entry.funcionarioId))}</td>
                        <td>${formatToolDate(entry.dataLevantamento)}</td>
                        <td>${entry.dataDevolucao ? formatToolDate(entry.dataDevolucao) : '—'}</td>
                        <td>${historyStatusBadge(entry)}</td>
                        <td>${entry.anomaliaLevantamento ? `<span style="color:#dc2626;"><i class="fas fa-triangle-exclamation"></i> ${o.escapeHtml(entry.descricaoAnomaliaLevantamento || '')}</span>` : '—'}</td>
                        <td>${entry.teveProblema ? o.escapeHtml(entry.descricaoProblema || '') : '—'}</td>
                    </tr>`;
  }

  function applyToolsState(elements, list, options) {
    elements.table.innerHTML=list.map(function (tool) { return toolRowHtml(tool,options); }).join('');
    if (elements.empty) elements.empty.style.display=list.length ? 'none' : 'block';
    if (elements.count) elements.count.textContent=list.length;
  }

  function applyToolHistoryState(elements, history, options) {
    if (!elements.historyTable) return;
    elements.historyTable.innerHTML=history.map(function (entry) { return toolHistoryRowHtml(entry,options); }).join('');
    if (elements.historyEmpty) elements.historyEmpty.style.display=history.length ? 'none' : 'block';
  }

  function renderToolsArea(options) {
    const o=options || {};
    const elements=toolsViewElements(o.document);
    if (!elements.table) return false;
    const list=selectToolsForTenant(o.tools,o.tenantId);
    const history=selectToolHistoryForTenant(o.history,o.tenantId);
    const renderOptions={
      tools:o.tools,
      escapeHtml:o.escapeHtml,
      getCurrentState:o.getCurrentState,
      getEmployeeName:o.getEmployeeName
    };
    applyToolsState(elements,list,renderOptions);
    applyToolHistoryState(elements,history,renderOptions);
    return { list:list, history:history };
  }

  window.TotalGestToolsView={
    toolsViewElements:toolsViewElements,
    selectToolsForTenant:selectToolsForTenant,
    selectToolHistoryForTenant:selectToolHistoryForTenant,
    formatToolDate:formatToolDate,
    toolAvailabilityBadge:toolAvailabilityBadge,
    toolRowHtml:toolRowHtml,
    historyStatusBadge:historyStatusBadge,
    toolHistoryRowHtml:toolHistoryRowHtml,
    applyToolsState:applyToolsState,
    applyToolHistoryState:applyToolHistoryState,
    renderToolsArea:renderToolsArea
  };
})();
