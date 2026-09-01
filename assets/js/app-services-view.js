/* Total Gest — apresentação da área de Ordens de Serviço */
(function () {
  'use strict';

  function specialtyAndHistoryNotice(options) {
    const opts = options || {};
    const pending = Array.isArray(opts.pendingServices) ? opts.pendingServices : [];
    const canSeePending = opts.canSeePending === true;
    const loadedSinceLabel = opts.loadedSinceLabel || '—';

    let html = '';

    if (canSeePending && pending.length) {
      const preview = pending.slice(0, 4).map(item => {
        const number = item.number || '';
        const types = Array.isArray(item.types) ? item.types.join(', ') : '';
        return `${number} (${types})`;
      }).join(' · ');

      html += `<div style="background:#fef3c7;border:1px solid #f59e0b;color:#92400e;border-radius:8px;padding:10px 14px;margin-bottom:10px;font-size:.85rem;">
        <i class="fas fa-triangle-exclamation"></i> <strong>${pending.length}</strong> OS já dada(s) como concluída(s) ainda tem(êm) relatório(s) de especialidade por preencher: ${preview}${pending.length > 4 ? ' ...' : ''}
      </div>`;
    }

    html += `<div style="margin-bottom:10px;">
      <button class="btn btn-sm" id="btn-carregar-os-antigas" style="background:#f1f5f9;color:#334155;" onclick="carregarOSMaisAntigo()"><i class="fas fa-clock-rotate-left"></i> Carregar OS mais antigas (+3 meses)</button>
      <span style="font-size:.75rem;color:#94a3b8;margin-left:8px;">A mostrar concluídas desde ${loadedSinceLabel}. Pendentes/em andamento aparecem sempre, seja qual for a idade.</span>
    </div>`;

    return html;
  }

  function statusControl(options) {
    const opts = options || {};
    const status = opts.status || 'pendente';
    const serviceId = opts.serviceId || '';

    if (status === 'por aprovar') {
      return '<span style="background:#fde68a;color:#92400e;padding:3px 10px;border-radius:999px;font-size:.74rem;font-weight:700;"><i class="fas fa-clock"></i> por aprovar</span>';
    }

    if (opts.canEdit === true && status !== 'concluído') {
      return `
        <select class="status-select" onchange="alterarStatusOS('${serviceId}', this.value)">
          <option value="pendente" ${status === 'pendente' ? 'selected' : ''}>pendente</option>
          <option value="em andamento" ${status === 'em andamento' ? 'selected' : ''}>em andamento</option>
          <option value="stand by" ${status === 'stand by' ? 'selected' : ''}>stand by</option>
          <option value="concluído" ${status === 'concluído' ? 'selected' : ''}>concluído</option>
        </select>
      `;
    }

    return `<span class="${opts.badgeClass || ''}">${status}</span>`;
  }

  function workSheetActions(options) {
    const opts = options || {};
    if (opts.status !== 'concluído') return '';

    const serviceId = opts.serviceId || '';
    if (opts.sheetId) {
      let html = `<button class="btn btn-sm" style="background:#0ea5e9;color:#fff;" onclick="abrirFolhaDetalhe('${opts.sheetId}')" title="Ver folha de obra e gerar PDF"><i class="fas fa-eye"></i></button>`;
      if (opts.workId) {
        html += ` <button class="btn btn-sm btn-success" onclick="criarFolhaDaOS('${serviceId}')" title="Criar mais uma folha de obra para esta OS"><i class="fas fa-plus"></i></button>`;
      } else {
        html += ` <button class="btn btn-sm" style="background:#16a34a;color:#fff;opacity:.55;cursor:not-allowed;" onclick="alert('Já existe uma folha de obra para esta OS.')" title="Já existe uma folha de obra para esta OS"><i class="fas fa-clipboard-check"></i></button>`;
      }
      return html;
    }

    return `<button class="btn btn-sm btn-success" onclick="criarFolhaDaOS('${serviceId}')"><i class="fas fa-clipboard-list"></i> Folha</button>`;
  }

  function rowLeadingCells(options) {
    const opts = options || {};
    return `
      <td><strong>${opts.number || ''}</strong> ${opts.hasMaterials ? '<i class="fas fa-boxes-stacked" style="color:#0891b2;" title="Esta OS tem materiais associados"></i>' : ''}</td>
      <td>${opts.clientName || ''}</td>
      <td>${opts.employeeName || 'Todos'}</td>
      <td>${opts.date || '-'}</td>
      <td>${opts.time || '-'}</td>
      <td>${opts.description || '-'}</td>
      <td>${opts.workTypesHtml || '<span style="color:#94a3b8;">-</span>'}</td>
      <td>${opts.statusHtml || ''}</td>`;
  }

  window.TotalGestServicesView = {
    specialtyAndHistoryNotice,
    statusControl,
    workSheetActions,
    rowLeadingCells
  };
})();
