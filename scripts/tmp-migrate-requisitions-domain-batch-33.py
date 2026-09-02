from pathlib import Path

app_path = Path('app.html')
shell_path = Path('assets/js/app-shell.js')
module_path = Path('assets/js/app-requisitions-view.js')
sw_path = Path('sw.js')

app = app_path.read_text(encoding='utf-8')
shell = shell_path.read_text(encoding='utf-8')
sw = sw_path.read_text(encoding='utf-8')


def block(text, marker):
    s = text.index(marker)
    e = text.index('\n        function ', s + len(marker))
    return text[s:e]

protected_markers = {
    'services': '        function renderizarServicos() {',
    'point': '        function renderizarPonto() {',
    'alerts': '        function renderizarAlertas() {',
    'clients': '        function renderizarClientes() {',
    'employees': '        function renderizarFuncionarios() {',
    'managers': '        function renderizarEncarregados() {',
}
protected = {name: block(app, marker) for name, marker in protected_markers.items()}
old_requisitions = block(app, '        function renderizarRequisicoes() {')
assert len(old_requisitions) == 4352, len(old_requisitions)

module = r'''/* Total Gest — seleção e apresentação do domínio Requisições */
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
'''

new_requisitions = '''        function renderizarRequisicoes() {
            const tenantId = _tenantId();
            const requisitions = window.TotalGestRequisitionsView.selectRequisitionsForUser(
                dados.requisicoes || [],
                usuarioLogado,
                tenantId
            );
            window.TotalGestRequisitionsView.renderRequisitionsArea({
                document,
                list: requisitions,
                user: usuarioLogado,
                tenantId,
                escapeHtml: escapeHtmlSimples,
                getServiceDescription: obterDescricaoOS,
                getStatusBadge: statusBadge
            });
        }'''

assert app.count(old_requisitions) == 1
app = app.replace(old_requisitions, new_requisitions, 1)

assert "    teamView: './assets/js/app-team-view.js'," in shell
shell = shell.replace("    teamView: './assets/js/app-team-view.js',", "    teamView: './assets/js/app-team-view.js',\n    requisitionsView: './assets/js/app-requisitions-view.js',", 1)
assert '    if (options.teamView === true) pedidos.push(MODULOS.teamView);' in shell
shell = shell.replace('    if (options.teamView === true) pedidos.push(MODULOS.teamView);', '    if (options.teamView === true) pedidos.push(MODULOS.teamView);\n    if (options.requisitionsView === true) pedidos.push(MODULOS.requisitionsView);', 1)

boot = '            clientsView: true, teamView: true, dashboardCounts: true,'
assert app.count(boot) == 1, app.count(boot)
app = app.replace(boot, '            clientsView: true, teamView: true, requisitionsView: true, dashboardCounts: true,', 1)

assert "const CACHE = 'totalgest-v175';" in sw
sw = sw.replace("const CACHE = 'totalgest-v175';", "const CACHE = 'totalgest-v176';", 1)

for name, original in protected.items():
    assert block(app, protected_markers[name]) == original, name

new_block = block(app, '        function renderizarRequisicoes() {')
assert new_block.count('selectRequisitionsForUser(') == 1
assert new_block.count('renderRequisitionsArea({') == 1
for moved in ['aprovarRequisicao(', 'rejeitarRequisicao(', 'validarRequisicao(', "abrirModal('requisicao'", "document.getElementById('tabelaRequisicoes')"]:
    assert moved not in new_block, moved
assert app.count('requisitionsView: true,') == 1
assert shell.count("requisitionsView: './assets/js/app-requisitions-view.js'") == 1
assert shell.count('if (options.requisitionsView === true) pedidos.push(MODULOS.requisitionsView);') == 1
assert 'bootstrapSupabase()' in app

app_path.write_text(app, encoding='utf-8')
shell_path.write_text(shell, encoding='utf-8')
module_path.write_text(module, encoding='utf-8')
sw_path.write_text(sw, encoding='utf-8')

print('REQUISITIONS_DOMAIN_CUTS=7')
for name in protected:
    print(name.upper() + '_BLOCK_UNCHANGED=OK')
print('AUTH_BOOTSTRAP_PRESERVED=OK')
print('REQUISITIONS_BEFORE_CHARS=', len(old_requisitions))
print('REQUISITIONS_AFTER_CHARS=', len(new_block))
print('REQUISITIONS_AFTER_LINES=', new_block.count('\n') + 1)
print('REQUISITIONS_DOMAIN_SEPARATION=OK')
