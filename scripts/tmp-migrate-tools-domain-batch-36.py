from pathlib import Path

app_path=Path('app.html')
shell_path=Path('assets/js/app-shell.js')
module_path=Path('assets/js/app-tools-view.js')
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
    'works':'        function renderizarObras() {',
}
protected={k:block(app,v) for k,v in protected_markers.items()}
old_tools=block(app,'        function renderizarFerramentas() {')
assert len(old_tools)==3745,len(old_tools)

module=r'''/* Total Gest — seleção e apresentação do domínio Ferramentas */
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
'''

new_tools='''        function renderizarFerramentas() {
            window.TotalGestToolsView.renderToolsArea({
                document,
                tenantId: _tenantId(),
                tools: dados.ferramentas || [],
                history: dados.levantamentosFerramentas || [],
                escapeHtml: escapeHtmlSimples,
                getCurrentState: _ferramentaEstadoAtual,
                getEmployeeName: obterNomeFuncionario
            });
        }'''

assert app.count(old_tools)==1
app=app.replace(old_tools,new_tools,1)

assert "    worksView: './assets/js/app-works-view.js'," in shell
shell=shell.replace("    worksView: './assets/js/app-works-view.js',","    worksView: './assets/js/app-works-view.js',\n    toolsView: './assets/js/app-tools-view.js',",1)
assert '    if (options.worksView === true) pedidos.push(MODULOS.worksView);' in shell
shell=shell.replace('    if (options.worksView === true) pedidos.push(MODULOS.worksView);','    if (options.worksView === true) pedidos.push(MODULOS.worksView);\n    if (options.toolsView === true) pedidos.push(MODULOS.toolsView);',1)

boot='            clientsView: true, teamView: true, requisitionsView: true, inventoryView: true, worksView: true, dashboardCounts: true,'
assert app.count(boot)==1,app.count(boot)
app=app.replace(boot,'            clientsView: true, teamView: true, requisitionsView: true, inventoryView: true, worksView: true, toolsView: true, dashboardCounts: true,',1)

assert "const CACHE = 'totalgest-v178';" in sw
sw=sw.replace("const CACHE = 'totalgest-v178';","const CACHE = 'totalgest-v179';",1)

for name,original in protected.items():
    assert block(app,protected_markers[name])==original,name

new_block=block(app,'        function renderizarFerramentas() {')
assert new_block.count('renderToolsArea({')==1
for moved in ["document.getElementById('tabelaFerramentas')","abrirModalFerramenta('","imprimirQRFerramenta('",'tabelaHistoricoLevantamentos','emptyHistoricoLevantamentos']:
    assert moved not in new_block,moved
assert shell.count("toolsView: './assets/js/app-tools-view.js'")==1
assert shell.count('if (options.toolsView === true) pedidos.push(MODULOS.toolsView);')==1
assert app.count('toolsView: true,')==1
assert 'bootstrapSupabase()' in app

app_path.write_text(app,encoding='utf-8')
shell_path.write_text(shell,encoding='utf-8')
module_path.write_text(module,encoding='utf-8')
sw_path.write_text(sw,encoding='utf-8')
print('TOOLS_DOMAIN_CUTS=9')
for name in protected: print(name.upper()+'_BLOCK_UNCHANGED=OK')
print('AUTH_BOOTSTRAP_PRESERVED=OK')
print('TOOLS_BEFORE_CHARS=',len(old_tools)); print('TOOLS_AFTER_CHARS=',len(new_block)); print('TOOLS_AFTER_LINES=',new_block.count('\n')+1)
print('TOOLS_DOMAIN_SEPARATION=OK')
