/* Total Gest — seleção e apresentação do domínio Clientes */
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
