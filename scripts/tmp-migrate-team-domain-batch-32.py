from pathlib import Path

app_path=Path('app.html'); shell_path=Path('assets/js/app-shell.js'); module_path=Path('assets/js/app-team-view.js'); sw_path=Path('sw.js')
app=app_path.read_text(encoding='utf-8'); shell=shell_path.read_text(encoding='utf-8'); sw=sw_path.read_text(encoding='utf-8')

def block(text, marker):
    s=text.index(marker); e=text.index('\n        function ',s+len(marker)); return text[s:e]

protected={
    'services':block(app,'        function renderizarServicos() {'),
    'point':block(app,'        function renderizarPonto() {'),
    'alerts':block(app,'        function renderizarAlertas() {'),
    'clients':block(app,'        function renderizarClientes() {'),
}
old_employees=block(app,'        function renderizarFuncionarios() {')
old_managers=block(app,'        function renderizarEncarregados() {')
assert len(old_employees)==6266,len(old_employees)
assert len(old_managers)==2307,len(old_managers)

module=r'''/* Total Gest — seleção e apresentação do domínio Equipa / Colaboradores */
(function () {
  'use strict';

  function selectEmployeesForUser(options) {
    const o = options || {};
    const user = o.user;
    let list = [];
    if (user && (user.role === 'admin' || user.role === 'subadmin')) {
      const managers = (Array.isArray(o.managers) ? o.managers : [])
        .filter(function (manager) { return manager.adminId === o.tenantId; })
        .map(function (manager) { return Object.assign({}, manager, { role: 'encarregado', _tipo: 'encarregado' }); });
      const employees = typeof o.getEmployeesByAdmin === 'function' ? (o.getEmployeesByAdmin(o.tenantId) || []) : [];
      list = employees.concat(managers);
    } else if (user && user.role === 'encarregado') {
      const manager = (Array.isArray(o.managers) ? o.managers : []).find(function (item) { return item.id === user.id; });
      if (manager) {
        list = (Array.isArray(o.employees) ? o.employees : []).filter(function (employee) {
          return employee.adminId === manager.adminId &&
            Array.isArray(manager.funcionariosIds) && manager.funcionariosIds.includes(employee.id) &&
            employee.role !== 'admin' && employee.role !== 'superadmin';
        });
      }
    } else if (user && user.role === 'funcionario') {
      list = [];
    }
    return list;
  }

  function prepareEmployeesForRendering(options) {
    const o = options || {};
    let list = selectEmployeesForUser(o);
    const hasBaseItems = list.length > 0;
    if (hasBaseItems && typeof o.applyFilterSort === 'function') list = o.applyFilterSort(list);
    return { list: list, hasBaseItems: hasBaseItems };
  }

  function employeesViewElements(doc) {
    return { tbody: doc.getElementById('tabelaFuncionarios'), empty: doc.getElementById('emptyFunc') };
  }

  function employeeAvatarHtml(person, escapeHtml) {
    if (person.foto) return `<img src="${person.foto}" style="width:38px;height:38px;border-radius:50%;object-fit:cover;border:1px solid #e2e8f0;flex:none;" />`;
    return `<span style="width:38px;height:38px;border-radius:50%;background:#e0e7ff;color:#4f46e5;display:inline-flex;align-items:center;justify-content:center;font-weight:700;flex:none;">${escapeHtml((person.nome || '?').charAt(0).toUpperCase())}</span>`;
  }

  function employeeNameCellHtml(person, mobile, escapeHtml) {
    const nameHtml = mobile ? escapeHtml(person.nome).split(' ').join('<br>') : escapeHtml(person.nome);
    const avatarHtml = employeeAvatarHtml(person, escapeHtml);
    return mobile
      ? `<div style="display:flex;flex-direction:column;align-items:center;gap:4px;text-align:center;width:74px;">${avatarHtml}<strong style="font-size:.78rem;line-height:1.25;">${nameHtml}</strong>${person.suspenso ? '<span class="badge" style="background:#fee2e2;color:#991b1b;">Suspenso</span>' : ''}</div>`
      : `<div style="display:flex;align-items:center;gap:10px;">${avatarHtml}<strong>${nameHtml}</strong>${person.suspenso ? '<span class="badge" style="background:#fee2e2;color:#991b1b;margin-left:4px;">Suspenso</span>' : ''}</div>`;
  }

  function vacationBalanceHtml(person, options) {
    const o = options || {};
    const available = o.getAvailableVacation(person.id);
    const total = o.getTotalVacation(person.id);
    const color = available <= 0 ? '#dc2626' : (available <= 5 ? '#d97706' : '#16a34a');
    return `<span style="font-weight:700;color:${color};">${available}</span> <span style="color:#94a3b8;">/ ${total}</span>`;
  }

  function employeeActionsHtml(person, userRole) {
    if (userRole !== 'admin' && userRole !== 'subadmin') return '';
    const type = person._tipo === 'encarregado' ? 'encarregado' : 'funcionario';
    const permissions = person.role === 'subadmin' && userRole === 'admin'
      ? `<button class="btn btn-sm" style="background:#0e7490;color:#fff;" onclick="abrirModalPermissoes('${person.id}')" title="Permissões deste Sub-Admin"><i class="fas fa-shield-halved"></i></button>` : '';
    const editDelete = person._tipo === 'encarregado'
      ? `<button class="btn btn-sm btn-warning" onclick="abrirModalEditarEncarregado('${person.id}')"><i class="fas fa-edit"></i></button>
                                           <button class="btn btn-sm btn-danger" onclick="excluirEncarregado('${person.id}')"><i class="fas fa-trash"></i></button>`
      : `<button class="btn btn-sm btn-warning" onclick="abrirModal('funcionario','${person.id}')"><i class="fas fa-edit"></i></button>
                                           <button class="btn btn-sm btn-danger" onclick="excluirEntidade('funcionario','${person.id}')"><i class="fas fa-trash"></i></button>`;
    return `${permissions}
                                    <button class="btn btn-sm" style="background:${person.suspenso ? '#16a34a' : '#b45309'};color:#fff;" onclick="toggleSuspensaoPessoa('${type}','${person.id}')" title="${person.suspenso ? 'Reativar' : 'Suspender'}"><i class="fas ${person.suspenso ? 'fa-rotate-left' : 'fa-user-slash'}"></i></button>
                                    <button class="btn btn-sm" style="background:#6d28d9;color:#fff;" onclick="definirPin('${type}','${person.id}')" title="Definir PIN do Modo Quiosque"><i class="fas fa-hashtag"></i></button>
                                    <button class="btn btn-sm" style="background:#0f6b5c;color:#fff;" onclick="repararContaAcesso('${type}','${person.id}')" title="Criar/reparar conta de acesso (login)"><i class="fas fa-key"></i></button>
                                    ${editDelete}`;
  }

  function employeeRowHtml(person, options) {
    const o = options || {};
    return `
                    <tr style="${person.suspenso ? 'opacity:.5;' : ''}">
                        <td>${employeeNameCellHtml(person, o.mobile === true, o.escapeHtml)}</td>
                        <td>${o.escapeHtml(person.cargo || '-')}</td>
                        <td>${o.escapeHtml(person.telefone || '-')}</td>
                        <td>${o.escapeHtml(person.email || '-')}</td>
                        <td><span class="badge ${person.role === 'encarregado' ? 'badge-encarregado' : 'badge-pendente'}">${person.role || 'funcionario'}</span></td>
                        <td>${person.horasSemanais || 40}h</td>
                        <td>${vacationBalanceHtml(person, o)}</td>
                        <td>
                            <div class="acoes">
                                ${employeeActionsHtml(person, o.userRole)}
                            </div>
                        </td>
                    </tr>
                `;
  }

  function renderEmployeesArea(options) {
    const o = options || {};
    const elements = employeesViewElements(o.document);
    if (!o.hasBaseItems) {
      elements.tbody.innerHTML = '';
      elements.empty.style.display = 'block';
      return false;
    }
    elements.empty.style.display = 'none';
    elements.tbody.innerHTML = (Array.isArray(o.list) ? o.list : []).map(function (person) {
      return employeeRowHtml(person, o);
    }).join('');
    if (typeof o.updateSortArrow === 'function') o.updateSortArrow('funcionarios');
    return true;
  }

  function selectManagersForUser(options) {
    const o = options || {};
    const allowed = !!(o.user && (o.user.role === 'admin' || o.user.role === 'subadmin'));
    const list = allowed ? (Array.isArray(o.managers) ? o.managers : []).filter(function (manager) { return manager.adminId === o.tenantId; }) : [];
    return { allowed: allowed, list: list };
  }

  function managersViewElements(doc) {
    return { tbody: doc.getElementById('tabelaEncarregados'), empty: doc.getElementById('emptyEncarregados') };
  }

  function managerRowHtml(manager, options) {
    const o = options || {};
    const employeeNames = o.getEmployeeNames(manager.funcionariosIds);
    return `
                        <tr>
                            <td><strong>${o.escapeHtml(manager.nome)}</strong></td>
                            <td>${o.escapeHtml(manager.email || '')}</td>
                            <td>${employeeNames}</td>
                            <td>
                                <div class="acoes">
                                    <button class="btn btn-sm" style="background:#6d28d9;color:#fff;" onclick="definirPin('encarregado','${manager.id}')" title="Definir PIN do Modo Quiosque"><i class="fas fa-hashtag"></i></button>
                                    <button class="btn btn-sm" style="background:#0f6b5c;color:#fff;" onclick="repararContaAcesso('encarregado','${manager.id}')" title="Criar/reparar conta de acesso (login)"><i class="fas fa-key"></i></button>
                                    <button class="btn btn-sm btn-warning" onclick="abrirModalEditarEncarregado('${manager.id}')"><i class="fas fa-edit"></i></button>
                                    <button class="btn btn-sm btn-danger" onclick="excluirEncarregado('${manager.id}')"><i class="fas fa-trash"></i></button>
                                </div>
                            </td>
                        </tr>
                    `;
  }

  function renderManagersArea(options) {
    const o = options || {};
    const elements = managersViewElements(o.document);
    if (!o.allowed) {
      elements.tbody.innerHTML = '';
      elements.empty.style.display = 'block';
      elements.empty.textContent = 'Apenas administradores podem ver esta secção.';
      return false;
    }
    if (!Array.isArray(o.list) || !o.list.length) {
      elements.tbody.innerHTML = '';
      elements.empty.style.display = 'block';
      return false;
    }
    elements.empty.style.display = 'none';
    elements.tbody.innerHTML = o.list.map(function (manager) { return managerRowHtml(manager, o); }).join('');
    return true;
  }

  window.TotalGestTeamView = {
    selectEmployeesForUser: selectEmployeesForUser,
    prepareEmployeesForRendering: prepareEmployeesForRendering,
    employeesViewElements: employeesViewElements,
    employeeAvatarHtml: employeeAvatarHtml,
    employeeNameCellHtml: employeeNameCellHtml,
    vacationBalanceHtml: vacationBalanceHtml,
    employeeActionsHtml: employeeActionsHtml,
    employeeRowHtml: employeeRowHtml,
    renderEmployeesArea: renderEmployeesArea,
    selectManagersForUser: selectManagersForUser,
    managersViewElements: managersViewElements,
    managerRowHtml: managerRowHtml,
    renderManagersArea: renderManagersArea
  };
})();
'''

new_employees='''        function renderizarFuncionarios() {
            const tenantId = _tenantId();
            const employeeState = window.TotalGestTeamView.prepareEmployeesForRendering({
                employees: dados.funcionarios || [],
                managers: dados.encarregados || [],
                user: usuarioLogado,
                tenantId,
                getEmployeesByAdmin: getFuncionariosByAdmin,
                applyFilterSort: lista => _aplicarFiltroOrdenacao('funcionarios', lista, [], {
                    nome: (a, b) => (a.nome || '').localeCompare(b.nome || '', 'pt', { sensitivity: 'base' }),
                    role: (a, b) => (a.role || 'funcionario').localeCompare(b.role || 'funcionario', 'pt', { sensitivity: 'base' })
                })
            });
            window.TotalGestTeamView.renderEmployeesArea({
                document,
                list: employeeState.list,
                hasBaseItems: employeeState.hasBaseItems,
                mobile: _ehPerfilMobile(),
                userRole: usuarioLogado?.role || '',
                escapeHtml: escapeHtmlSimples,
                getAvailableVacation: feriasDisponiveis,
                getTotalVacation: feriasTotaisPessoa,
                updateSortArrow: _atualizarSetaOrdenacao
            });
        }'''

new_managers='''        function renderizarEncarregados() {
            const managerState = window.TotalGestTeamView.selectManagersForUser({
                managers: dados.encarregados || [],
                user: usuarioLogado,
                tenantId: _tenantId()
            });
            window.TotalGestTeamView.renderManagersArea({
                document,
                list: managerState.list,
                allowed: managerState.allowed,
                escapeHtml: escapeHtmlSimples,
                getEmployeeNames: getFuncionariosNomes
            });
        }'''

assert app.count(old_employees)==1 and app.count(old_managers)==1
app=app.replace(old_employees,new_employees,1).replace(old_managers,new_managers,1)

assert "    clientsView: './assets/js/app-clients-view.js'," in shell
shell=shell.replace("    clientsView: './assets/js/app-clients-view.js',","    clientsView: './assets/js/app-clients-view.js',\n    teamView: './assets/js/app-team-view.js',",1)
assert '    if (options.clientsView === true) pedidos.push(MODULOS.clientsView);' in shell
shell=shell.replace('    if (options.clientsView === true) pedidos.push(MODULOS.clientsView);','    if (options.clientsView === true) pedidos.push(MODULOS.clientsView);\n    if (options.teamView === true) pedidos.push(MODULOS.teamView);',1)

boot='reportsView: true, alertsView: true, clientsView: true, dashboardCounts: true,'
assert app.count(boot)==1,app.count(boot)
app=app.replace(boot,'reportsView: true, alertsView: true, clientsView: true, teamView: true, dashboardCounts: true,',1)

assert "const CACHE = 'totalgest-v174';" in sw
sw=sw.replace("const CACHE = 'totalgest-v174';","const CACHE = 'totalgest-v175';",1)

for name,original in protected.items():
    marker={'services':'        function renderizarServicos() {','point':'        function renderizarPonto() {','alerts':'        function renderizarAlertas() {','clients':'        function renderizarClientes() {'}[name]
    assert block(app,marker)==original,name

emp=block(app,'        function renderizarFuncionarios() {'); man=block(app,'        function renderizarEncarregados() {')
for x in ['prepareEmployeesForRendering({','renderEmployeesArea({']:
    assert emp.count(x)==1,(x,emp.count(x))
for x in ['selectManagersForUser({','renderManagersArea({']:
    assert man.count(x)==1,(x,man.count(x))
for x in ['toggleSuspensaoPessoa(','definirPin(','repararContaAcesso(','abrirModalEditarEncarregado(','excluirEncarregado(']:
    assert x not in emp and x not in man,x
assert app.count('teamView: true,')==1

app_path.write_text(app,encoding='utf-8'); shell_path.write_text(shell,encoding='utf-8'); module_path.write_text(module,encoding='utf-8'); sw_path.write_text(sw,encoding='utf-8')
print('TEAM_DOMAIN_CUTS=10')
print('SERVICES_BLOCK_UNCHANGED=OK'); print('POINT_BLOCK_UNCHANGED=OK'); print('ALERTS_BLOCK_UNCHANGED=OK'); print('CLIENTS_BLOCK_UNCHANGED=OK')
print('EMPLOYEES_BEFORE_CHARS=',len(old_employees)); print('EMPLOYEES_AFTER_CHARS=',len(emp)); print('EMPLOYEES_AFTER_LINES=',emp.count('\n')+1)
print('MANAGERS_BEFORE_CHARS=',len(old_managers)); print('MANAGERS_AFTER_CHARS=',len(man)); print('MANAGERS_AFTER_LINES=',man.count('\n')+1)
print('TEAM_DOMAIN_SEPARATION=OK')
