from pathlib import Path

app_path=Path('app.html')
shell_path=Path('assets/js/app-shell.js')
module_path=Path('assets/js/app-works-view.js')
sw_path=Path('sw.js')
app=app_path.read_text(encoding='utf-8')
shell=shell_path.read_text(encoding='utf-8')
sw=sw_path.read_text(encoding='utf-8')

def block(text, marker):
    s=text.index(marker)
    starts=[]
    for pat in ['\n        function ','\n        async function ']:
        p=text.find(pat,s+len(marker))
        if p!=-1: starts.append(p)
    assert starts, marker
    return text[s:min(starts)]

protected_markers={
    'services':'        function renderizarServicos() {',
    'point':'        function renderizarPonto() {',
    'alerts':'        function renderizarAlertas() {',
    'clients':'        function renderizarClientes() {',
    'employees':'        function renderizarFuncionarios() {',
    'managers':'        function renderizarEncarregados() {',
    'requisitions':'        function renderizarRequisicoes() {',
    'articles':'        function renderizarArtigos() {',
    'suppliers':'        function renderizarFornecedores() {',
}
protected={k:block(app,v) for k,v in protected_markers.items()}
old_works=block(app,'        function renderizarObras() {')
assert len(old_works)==4392,len(old_works)

module=r'''/* Total Gest — seleção e apresentação do domínio Obras */
(function () {
  'use strict';

  function worksViewElements(doc) {
    return {
      table: doc.getElementById('tabelaObras'),
      toolbar: doc.getElementById('obrasToolbar'),
      count: doc.getElementById('countObras'),
      preparation: doc.getElementById('obrasPrep'),
      active: doc.getElementById('obrasAtivas'),
      suspended: doc.getElementById('obrasSusp'),
      completed: doc.getElementById('obrasConcl')
    };
  }

  function worksRoleState(user) {
    const role=user && user.role;
    return {
      isAdminView: role === 'admin' || role === 'subadmin',
      isManagerView: role === 'encarregado'
    };
  }

  function selectWorksForView(works, adminId, isAdminView) {
    let list=(Array.isArray(works) ? works : []).filter(function (work) {
      return work.adminId === adminId && !work.longaDuracao;
    });
    if (!isAdminView) list=list.filter(function (work) { return work.estado !== 'concluida'; });
    return list;
  }

  function filterAndSortWorks(options, list) {
    const o=options || {};
    return o.applyFilterSort('obras', list,
      ['nome','morada','cidade',function (work) { return o.getClientName(work.clienteId); }],
      {
        nome:function (a,b) { return (a.nome || '').localeCompare(b.nome || ''); },
        estado:function (a,b) { return (a.estado || '').localeCompare(b.estado || ''); }
      });
  }

  function renderWorksToolbar(elements, options, visibleCount, totalCount) {
    if (!elements.toolbar) return;
    elements.toolbar.innerHTML=totalCount
      ? options.toolbarHtml('obras','Pesquisar por nome, cliente, morada…',visibleCount,totalCount)
      : '';
  }

  function workerWorkActionsHtml(work, roleState) {
    let actions=`<button class="btn btn-sm" style="background:#334155;color:#fff;" onclick="abrirObraLongaDetalhe('${work.id}')" title="Ver Obra"><i class="fas fa-eye"></i> Ver Obra</button> <button class="btn btn-sm" style="background:#0f766e;color:#fff;" onclick="_obraEscolherRelatorio('${work.id}')" title="Relatório da obra"><i class="fas fa-file-lines"></i></button>`;
    if (roleState.isManagerView && work.estado !== 'concluida') actions += ` <button class="btn btn-sm" style="background:#0f766e;color:#fff;" onclick="finalizarObraLonga('${work.id}')" title="Finalizar obra"><i class="fas fa-flag-checkered"></i> Finalizar</button>`;
    return actions;
  }

  function workerWorkRowHtml(work, options, roleState) {
    return `<tr>
                        <td><strong>${options.escapeHtml(work.nome)}</strong></td><td>${work.clienteId ? options.getClientName(work.clienteId) : '—'}</td>
                        <td>${options.getFullAddress(work)}</td><td>${options.getStateSelect(work)}</td>
                        <td>${workerWorkActionsHtml(work,roleState)}</td>
                    </tr>`;
  }

  function workMaterialsCount(materials, workId) {
    return (Array.isArray(materials) ? materials : []).filter(function (material) { return material.obraId === workId; }).length;
  }

  function adminWorkRowHtml(work, options) {
    const materialsCount=workMaterialsCount(options.materials,work.id);
    return `<tr>
<td>${options.escapeHtml(work.nome)}</td><td>${work.clienteId ? options.getClientName(work.clienteId) : '—'}</td><td>${options.getFullAddress(work)}</td><td>${options.getStateSelect(work)}</td>
                <td><button class="btn btn-sm" style="background:#334155;color:#fff;" onclick="abrirObraLongaDetalhe('${work.id}')" title="Ver Obra"><i class="fas fa-eye"></i> Ver Obra</button>
                    <button class="btn btn-sm btn-primary" onclick="abrirPlanoMateriais('${work.id}')" title="Plano de materiais"><i class="fas fa-tasks"></i> Materiais${materialsCount ? ' (' + materialsCount + ')' : ''}</button>
                    <button class="btn btn-sm" style="background:#0f766e;color:#fff;" onclick="_obraEscolherRelatorio('${work.id}')" title="Relatório da obra"><i class="fas fa-file-lines"></i></button>
                    <button class="btn btn-sm btn-outline" onclick="abrirModal('obra','${work.id}')"><i class="fas fa-pen"></i></button>
                    <button class="btn btn-sm btn-danger" onclick="eliminarRegisto('obras','${work.id}')"><i class="fas fa-trash"></i></button></td>
            </tr>`;
  }

  function worksStatusCounts(list) {
    const works=Array.isArray(list) ? list : [];
    return {
      preparation: works.filter(function (work) { return (work.estado || 'preparacao') === 'preparacao'; }).length,
      active: works.filter(function (work) { return work.estado === 'ativa'; }).length,
      suspended: works.filter(function (work) { return work.estado === 'suspensa'; }).length,
      completed: works.filter(function (work) { return work.estado === 'concluida'; }).length
    };
  }

  function applyAdminWorksCounters(elements, list) {
    const counts=worksStatusCounts(list);
    if (elements.count) elements.count.textContent=list.length;
    if (elements.preparation) elements.preparation.textContent=counts.preparation;
    if (elements.active) elements.active.textContent=counts.active;
    if (elements.suspended) elements.suspended.textContent=counts.suspended;
    if (elements.completed) elements.completed.textContent=counts.completed;
    return counts;
  }

  function emptyWorksRow(totalCount) {
    return `<tr><td colspan="5" style="text-align:center;color:#94a3b8;">${totalCount ? 'Sem resultados para essa pesquisa.' : 'Sem obras.'}</td></tr>`;
  }

  function renderWorksArea(options) {
    const o=options || {};
    const elements=worksViewElements(o.document);
    if (!elements.table) return false;
    const roleState=worksRoleState(o.user);
    let list=selectWorksForView(o.works,o.adminId,roleState.isAdminView);
    const totalCount=list.length;
    list=filterAndSortWorks(o,list);
    renderWorksToolbar(elements,o,list.length,totalCount);
    if (!roleState.isAdminView) {
      elements.table.innerHTML=list.length ? list.map(function (work) {
        return workerWorkRowHtml(work,o,roleState);
      }).join('') : emptyWorksRow(totalCount);
      return { list:list, totalCount:totalCount, roleState:roleState };
    }
    elements.table.innerHTML=list.length ? list.map(function (work) {
      return adminWorkRowHtml(work,o);
    }).join('') : emptyWorksRow(totalCount);
    const counts=applyAdminWorksCounters(elements,list);
    return { list:list, totalCount:totalCount, roleState:roleState, counts:counts };
  }

  window.TotalGestWorksView={
    worksViewElements:worksViewElements,
    worksRoleState:worksRoleState,
    selectWorksForView:selectWorksForView,
    filterAndSortWorks:filterAndSortWorks,
    renderWorksToolbar:renderWorksToolbar,
    workerWorkActionsHtml:workerWorkActionsHtml,
    workerWorkRowHtml:workerWorkRowHtml,
    workMaterialsCount:workMaterialsCount,
    adminWorkRowHtml:adminWorkRowHtml,
    worksStatusCounts:worksStatusCounts,
    applyAdminWorksCounters:applyAdminWorksCounters,
    emptyWorksRow:emptyWorksRow,
    renderWorksArea:renderWorksArea
  };
})();
'''

new_works='''        function renderizarObras() {
            window.TotalGestWorksView.renderWorksArea({
                document,
                works: dados.obras || [],
                materials: dados.obraMateriais || [],
                user: usuarioLogado,
                adminId: _tenantArmazem(),
                applyFilterSort: _aplicarFiltroOrdenacao,
                toolbarHtml: _toolbarHtml,
                escapeHtml: escapeHtmlSimples,
                getClientName: obterNomeCliente,
                getFullAddress: _moradaCompletaObra,
                getStateSelect: _estadoSelectObra
            });
        }'''

assert app.count(old_works)==1
app=app.replace(old_works,new_works,1)

assert "    inventoryView: './assets/js/app-inventory-view.js'," in shell
shell=shell.replace("    inventoryView: './assets/js/app-inventory-view.js',","    inventoryView: './assets/js/app-inventory-view.js',\n    worksView: './assets/js/app-works-view.js',",1)
assert '    if (options.inventoryView === true) pedidos.push(MODULOS.inventoryView);' in shell
shell=shell.replace('    if (options.inventoryView === true) pedidos.push(MODULOS.inventoryView);','    if (options.inventoryView === true) pedidos.push(MODULOS.inventoryView);\n    if (options.worksView === true) pedidos.push(MODULOS.worksView);',1)

boot='            clientsView: true, teamView: true, requisitionsView: true, inventoryView: true, dashboardCounts: true,'
assert app.count(boot)==1,app.count(boot)
app=app.replace(boot,'            clientsView: true, teamView: true, requisitionsView: true, inventoryView: true, worksView: true, dashboardCounts: true,',1)

assert "const CACHE = 'totalgest-v177';" in sw
sw=sw.replace("const CACHE = 'totalgest-v177';","const CACHE = 'totalgest-v178';",1)

for name,original in protected.items():
    assert block(app,protected_markers[name])==original,name

new_block=block(app,'        function renderizarObras() {')
assert new_block.count('renderWorksArea({')==1
for moved in ["document.getElementById('tabelaObras')",'_aplicarFiltroOrdenacao(\'obras\'',"abrirObraLongaDetalhe('","abrirPlanoMateriais('","finalizarObraLonga('","abrirModal('obra'","eliminarRegisto('obras'",'obrasPrep']:
    assert moved not in new_block,moved
assert shell.count("worksView: './assets/js/app-works-view.js'")==1
assert shell.count('if (options.worksView === true) pedidos.push(MODULOS.worksView);')==1
assert app.count('worksView: true,')==1
assert 'bootstrapSupabase()' in app

app_path.write_text(app,encoding='utf-8')
shell_path.write_text(shell,encoding='utf-8')
module_path.write_text(module,encoding='utf-8')
sw_path.write_text(sw,encoding='utf-8')
print('WORKS_DOMAIN_CUTS=10')
for name in protected: print(name.upper()+'_BLOCK_UNCHANGED=OK')
print('AUTH_BOOTSTRAP_PRESERVED=OK')
print('WORKS_BEFORE_CHARS=',len(old_works)); print('WORKS_AFTER_CHARS=',len(new_block)); print('WORKS_AFTER_LINES=',new_block.count('\n')+1)
print('WORKS_DOMAIN_SEPARATION=OK')
