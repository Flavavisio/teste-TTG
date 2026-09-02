/* Total Gest — seleção e apresentação do domínio Requisições */
(function () {
  'use strict';

  function selectRequisitionsForUser(requisitions, user, tenantId) {
    let list = Array.isArray(requisitions) ? requisitions.slice() : [];
    if (user && user.role === 'admin') {
      list = list.filter(function (request) { return request.adminId === tenantId; });
    } else if (user && user.role === 'encarregado') {
      list = list.filter(function (request) { return request.funcionarioId === user.id; });
    } else if (user && user.role === 'funcionario') {
      list = list.filter(function (request) { return request.funcionarioId === user.id; });
    }
    if (user && user.role === 'superadmin') list = [];
    return list;
  }

  function requisitionStatusLabel(status) {
    return status === 'pendente_aprov' ? 'Pendente' :
      status === 'em_andamento' ? 'Em andamento' :
      status === 'aguarda_validacao' ? 'Aguarda Validação' :
      status === 'concluído' ? 'Concluído' :
      status === 'rejeitado' ? 'Rejeitado' : status;
  }

  function canApproveRequisition(request, user, tenantId) {
    return (((user && user.role === 'admin') || (user && user.role === 'subadmin')) && request.adminId === tenantId) ||
      ((user && user.role === 'encarregado') && request.funcionarioId === user.id);
  }

  function requisitionActionsHtml(request, options) {
    const o = options || {};
    const user = o.user || null;
    const tenantId = o.tenantId;
    let actions = '';
    if (canApproveRequisition(request, user, tenantId) && request.status === 'pendente_aprov') {
      actions += `
                        <button class="btn btn-sm btn-success" onclick="aprovarRequisicao('${request.id}')"><i class="fas fa-check"></i> Aprovar</button>
                        <button class="btn btn-sm btn-danger" onclick="rejeitarRequisicao('${request.id}')"><i class="fas fa-times"></i> Rejeitar</button>
                    `;
    }
    if (((user && user.role === 'admin') || (user && user.role === 'subadmin')) && request.adminId === tenantId && request.status === 'aguarda_validacao') {
      actions += `
                        <button class="btn btn-sm btn-success" onclick="validarRequisicao('${request.id}')"><i class="fas fa-check-circle"></i> Validar</button>
                        <button class="btn btn-sm btn-danger" onclick="rejeitarRequisicao('${request.id}')"><i class="fas fa-times"></i> Rejeitar</button>
                    `;
    }
    if (((user && user.role === 'admin') || (user && user.role === 'subadmin')) && request.adminId === tenantId) {
      actions += `<button class="btn btn-sm btn-warning" onclick="abrirModal('requisicao','${request.id}')"><i class="fas fa-edit"></i></button>`;
    }
    return actions;
  }

  function requisitionRowHtml(request, options) {
    const o = options || {};
    const escapeHtml = o.escapeHtml;
    const items = escapeHtml(request.itens ? request.itens.map(function (item) { return `${item.nome} (${item.quantidade})`; }).join(', ') : '-');
    const work = escapeHtml(request.servicoId ? o.getServiceDescription(request.servicoId) : (request.obraDescricao || '-'));
    const supplier = escapeHtml(request.fornecedor || '-');
    const statusLabel = requisitionStatusLabel(request.status);
    const actions = requisitionActionsHtml(request, { user: o.user, tenantId: o.tenantId });
    return `
                        <tr>
                            <td>${work}</td>
                            <td>${supplier}</td>
                            <td>${request.descricao || '-'}</td>
                            <td>${items}</td>
                            <td>${request.data || '-'}</td>
                            <td><span class="${o.getStatusBadge(request.status)}">${statusLabel}</span></td>
                            <td>
                                <div class="acoes">
                                    ${actions}
                                    ${request.anexo ? `<a href="${request.anexo}" target="_blank" class="anexo-link" title="Ver anexo"><i class="fas fa-paperclip"></i></a>` : ''}
                                </div>
                            </td>
                        </tr>
                    `;
  }

  function requisitionsViewElements(doc) {
    return {
      tbody: doc.getElementById('tabelaRequisicoes'),
      empty: doc.getElementById('emptyRequisicoes')
    };
  }

  function renderRequisitionsArea(options) {
    const o = options || {};
    const elements = requisitionsViewElements(o.document);
    const list = Array.isArray(o.list) ? o.list : [];
    if (list.length === 0) {
      elements.tbody.innerHTML = '';
      elements.empty.style.display = 'block';
      return false;
    }
    elements.empty.style.display = 'none';
    elements.tbody.innerHTML = list.map(function (request) {
      return requisitionRowHtml(request, o);
    }).join('');
    return true;
  }

  window.TotalGestRequisitionsView = {
    selectRequisitionsForUser: selectRequisitionsForUser,
    requisitionStatusLabel: requisitionStatusLabel,
    canApproveRequisition: canApproveRequisition,
    requisitionActionsHtml: requisitionActionsHtml,
    requisitionRowHtml: requisitionRowHtml,
    requisitionsViewElements: requisitionsViewElements,
    renderRequisitionsArea: renderRequisitionsArea
  };
})();
