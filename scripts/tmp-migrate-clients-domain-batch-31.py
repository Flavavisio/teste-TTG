from pathlib import Path

app_path = Path('app.html')
shell_path = Path('assets/js/app-shell.js')
module_path = Path('assets/js/app-clients-view.js')
sw_path = Path('sw.js')

app = app_path.read_text(encoding='utf-8')
shell = shell_path.read_text(encoding='utf-8')
sw = sw_path.read_text(encoding='utf-8')


def block(text, marker):
    s = text.index(marker)
    e = text.index('\n        function ', s + len(marker))
    return text[s:e]

protected = {
    'services': block(app, '        function renderizarServicos() {'),
    'point': block(app, '        function renderizarPonto() {'),
    'alerts': block(app, '        function renderizarAlertas() {'),
    'persist': block(app, '        async function _guardarEdicaoPontoRegisto(regId) {'),
    'repair': block(app, '        async function _repararEntradasPresas() {'),
}

old_clients = block(app, '        function renderizarClientes() {')
assert len(old_clients) == 4183, len(old_clients)

module = r'''/* Total Gest — seleção e apresentação do domínio Clientes */
(function () {
  'use strict';

  function selectClientsForUser(clients, user) {
    let list = Array.isArray(clients) ? clients.slice() : [];
    if (user && (user.role === 'admin' || user.role === 'subadmin')) {
      const tenantId = user.role === 'admin' ? user.id : user.adminId;
      list = list.filter(function (client) { return client.adminId === tenantId; });
    }
    if (user && (user.role === 'superadmin' || user.role === 'funcionario' || user.role === 'encarregado')) {
      list = [];
    }
    return list;
  }

  function prepareClientsForRendering(options) {
    const o = options || {};
    let list = selectClientsForUser(o.clients, o.user);
    const total = list.length;
    if (typeof o.applyFilterSort === 'function') list = o.applyFilterSort(list);
    return { list: list, total: total };
  }

  function clientsViewElements(doc) {
    return {
      tbody: doc.getElementById('tabelaClientes'),
      empty: doc.getElementById('emptyCli'),
      toolbar: doc.getElementById('clientesToolbar')
    };
  }

  function clientInstallationsCount(locations, clientId) {
    return (Array.isArray(locations) ? locations : []).filter(function (location) {
      return location.clienteId === clientId;
    }).length;
  }

  function clientRowsHtml(client, options) {
    const o = options || {};
    const escapeHtml = o.escapeHtml;
    const numLocais = clientInstallationsCount(o.locations, client.id);
    return `
                    <tr>
                        <td>${escapeHtml(client.numeroCliente || '-')}</td>
                        <td>
                            <button class="btn btn-sm" style="background:#f1f5f9;color:#334155;margin-right:6px;" onclick="_toggleAcordeaoCliente('${client.id}')" title="${numLocais > 0 ? (numLocais + ' instalação(ões) + Sede') : 'Ver Sede / intervenções'}"><i class="fas fa-chevron-down" id="acordeao-icone-${client.id}"></i></button>
                            <strong>${escapeHtml(client.nome)}</strong>
                            <span style="font-size:.7rem;color:#64748b;margin-left:6px;">(${numLocais > 0 ? (numLocais + 1) + ' instalações' : 'Sede'})</span>
                        </td>
                        <td>${escapeHtml(client.telefone || '-')}</td>
                        <td>${escapeHtml(client.endereco || '-')}</td>
                        <td>${escapeHtml(client.email || '-')}</td>
                        <td>
                            <div class="acoes">
                                <button class="btn btn-sm" style="background:#0ea5e9;color:#fff;" onclick="abrirHistoricoCliente('${client.id}')" title="Histórico de intervenções"><i class="fas fa-clock-rotate-left"></i></button>
                                <button class="btn btn-sm" style="background:#0f766e;color:#fff;" onclick="abrirModalNovoLocalCliente('${client.id}')" title="Adicionar outra morada/instalação"><i class="fas fa-map-pin"></i></button>
                                <button class="btn btn-sm btn-warning" onclick="abrirModal('cliente','${client.id}')"><i class="fas fa-edit"></i></button>
                                <button class="btn btn-sm btn-danger" onclick="excluirEntidade('cliente','${client.id}')"><i class="fas fa-trash"></i></button>
                            </div>
                        </td>
                    </tr>
                    <tr id="acordeao-cliente-${client.id}" style="display:none;background:#f8fafc;">
                        <td colspan="5" style="padding:14px 20px;">
                            <div id="acordeao-conteudo-${client.id}"><p style="color:#94a3b8;">A carregar…</p></div>
                        </td>
                    </tr>
                `;
  }

  function renderClientsArea(options) {
    const o = options || {};
    const elements = clientsViewElements(o.document);
    const list = Array.isArray(o.list) ? o.list : [];
    const total = Number(o.total || 0);
    if (elements.toolbar) elements.toolbar.innerHTML = total ? o.toolbarHtml('clientes', 'Pesquisar por nome, telefone, email…', list.length, total) : '';
    if (list.length === 0) {
      elements.tbody.innerHTML = '';
      elements.empty.style.display = total ? 'none' : 'block';
      if (total && !list.length) elements.tbody.innerHTML = '<tr><td colspan="6" style="text-align:center;color:#94a3b8;">Sem resultados para essa pesquisa.</td></tr>';
      return false;
    }
    elements.empty.style.display = 'none';
    elements.tbody.innerHTML = list.map(function (client) {
      return clientRowsHtml(client, { locations: o.locations, escapeHtml: o.escapeHtml });
    }).join('');
    return true;
  }

  window.TotalGestClientsView = {
    selectClientsForUser: selectClientsForUser,
    prepareClientsForRendering: prepareClientsForRendering,
    clientsViewElements: clientsViewElements,
    clientInstallationsCount: clientInstallationsCount,
    clientRowsHtml: clientRowsHtml,
    renderClientsArea: renderClientsArea
  };
})();
'''

new_clients = '''        function renderizarClientes() {
            const clientsState = window.TotalGestClientsView.prepareClientsForRendering({
                clients: dados.clientes || [],
                user: usuarioLogado,
                applyFilterSort: lista => _aplicarFiltroOrdenacao('clientes', lista, ['nome', 'numeroCliente', 'telefone', 'endereco', 'email'], {
                    nome: (a, b) => (a.nome || '').localeCompare(b.nome || ''),
                    numeroCliente: (a, b) => (a.numeroCliente || '').localeCompare(b.numeroCliente || '', undefined, { numeric: true })
                })
            });
            window.TotalGestClientsView.renderClientsArea({
                document,
                list: clientsState.list,
                total: clientsState.total,
                locations: dados.locais || [],
                toolbarHtml: _toolbarHtml,
                escapeHtml: escapeHtmlSimples
            });
        }'''

assert app.count(old_clients) == 1
app = app.replace(old_clients, new_clients, 1)

assert "    alertsView: './assets/js/app-alerts-view.js'," in shell
shell = shell.replace("    alertsView: './assets/js/app-alerts-view.js',", "    alertsView: './assets/js/app-alerts-view.js',\n    clientsView: './assets/js/app-clients-view.js',", 1)
assert "    if (options.alertsView === true) pedidos.push(MODULOS.alertsView);" in shell
shell = shell.replace("    if (options.alertsView === true) pedidos.push(MODULOS.alertsView);", "    if (options.alertsView === true) pedidos.push(MODULOS.alertsView);\n    if (options.clientsView === true) pedidos.push(MODULOS.clientsView);", 1)

# A configuração de arranque já contém alertsView; inserir Clientes logo depois.
needle = '            alertsView: true,'
assert app.count(needle) == 1, app.count(needle)
app = app.replace(needle, needle + '\n            clientsView: true,', 1)

assert "const CACHE = 'totalgest-v173';" in sw
sw = sw.replace("const CACHE = 'totalgest-v173';", "const CACHE = 'totalgest-v174';", 1)

for name, original in protected.items():
    assert block(app, {
        'services':'        function renderizarServicos() {',
        'point':'        function renderizarPonto() {',
        'alerts':'        function renderizarAlertas() {',
        'persist':'        async function _guardarEdicaoPontoRegisto(regId) {',
        'repair':'        async function _repararEntradasPresas() {'
    }[name]) == original, name

assert app.count('window.TotalGestClientsView.prepareClientsForRendering({') == 1
assert app.count('window.TotalGestClientsView.renderClientsArea({') == 1
assert 'document.getElementById(\'tabelaClientes\')' not in block(app, '        function renderizarClientes() {')
assert '_toggleAcordeaoCliente' not in block(app, '        function renderizarClientes() {')
assert "clientsView: true," in app
assert "clientsView: './assets/js/app-clients-view.js'" in shell

app_path.write_text(app, encoding='utf-8')
shell_path.write_text(shell, encoding='utf-8')
module_path.write_text(module, encoding='utf-8')
sw_path.write_text(sw, encoding='utf-8')

new_block = block(app, '        function renderizarClientes() {')
print('CLIENT_DOMAIN_CUTS=6')
print('SERVICES_BLOCK_UNCHANGED=OK')
print('POINT_BLOCK_UNCHANGED=OK')
print('ALERTS_BLOCK_UNCHANGED=OK')
print('POINT_PERSISTENCE_UNCHANGED=OK')
print('POINT_REPAIR_UNCHANGED=OK')
print('CLIENTS_BEFORE_CHARS=', len(old_clients))
print('CLIENTS_AFTER_CHARS=', len(new_block))
print('CLIENTS_AFTER_LINES=', new_block.count('\n') + 1)
print('CLIENT_DOMAIN_SEPARATION=OK')
