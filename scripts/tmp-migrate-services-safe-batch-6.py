from pathlib import Path

app=Path('app.html'); selp=Path('assets/js/app-services-selection.js'); viewp=Path('assets/js/app-services-view.js'); swp=Path('sw.js')
sel=selp.read_text(encoding='utf-8')
anchor='  function prepareServicesForRendering(options) {\n'
assert sel.count(anchor)==1 and 'function createServiceRenderDependencies(options)' not in sel
helper="""  function createServiceRenderDependencies(options) {
    options = options || {};
    return {
      selectPendingSpecialty: createPendingSpecialtySelector({ user: options.user || null, getPendingTypes: options.getPendingTypes }),
      prepareRow: createServiceRowPreparerFromData({ data: options.data || {}, getEmployeeName: options.getEmployeeName, getClientName: options.getClientName, generateNumber: options.generateNumber, hasMaterials: options.hasMaterials, isErpActive: options.isErpActive })
    };
  }

"""
sel=sel.replace(anchor,helper+anchor,1)
old='    createServiceRowPreparerFromData: createServiceRowPreparerFromData,\n    prepareServicesForRendering: prepareServicesForRendering,'
new='    createServiceRowPreparerFromData: createServiceRowPreparerFromData,\n    createServiceRenderDependencies: createServiceRenderDependencies,\n    prepareServicesForRendering: prepareServicesForRendering,'
assert sel.count(old)==1
selp.write_text(sel.replace(old,new,1),encoding='utf-8')

view=viewp.read_text(encoding='utf-8')
anchor='  function servicesTableState(options) {\n'
assert view.count(anchor)==1 and 'function createPendingSpecialtyNoticeRenderer(options)' not in view
helper="""  function createPendingSpecialtyNoticeRenderer(options) {
    const opts = options || {};
    return function (services) { return renderPendingSpecialtyNotice({ element: opts.element, services: services || [], selectPending: opts.selectPending, loadedSince: opts.loadedSince }); };
  }

"""
view=view.replace(anchor,helper+anchor,1)
anchor='  function serviceRow(options) {\n'
assert view.count(anchor)==1 and 'function createServicesAreaRenderer(options)' not in view
helper="""  function createServicesAreaRenderer(options) {
    const opts = options || {}, elements = opts.elements || {};
    const renderNotice = createPendingSpecialtyNoticeRenderer({ element: elements.noticeElement, selectPending: opts.selectPending, loadedSince: opts.loadedSince });
    const renderTableState = createServicesTableStateRenderer({ renderToolbar: opts.renderToolbar, elements });
    const renderRows = createServiceRowsRenderer({ elements, prepareRow: opts.prepareRow, role: opts.role, getBadgeClass: opts.getBadgeClass, escapeDescription: opts.escapeDescription, getWorkTypesHtml: opts.getWorkTypesHtml, buildActions: opts.buildActions });
    return function (selectionState) {
      const state = selectionState || {}, services = Array.isArray(state.services) ? state.services : [];
      renderNotice(state.sourceServices || []);
      if (!renderTableState(state.totalCount, services.length)) return false;
      renderRows(services);
      return true;
    };
  }

"""
view=view.replace(anchor,helper+anchor,1)
old='renderPendingSpecialtyNotice, servicesTableState'
new='renderPendingSpecialtyNotice, createPendingSpecialtyNoticeRenderer, servicesTableState'
assert view.count(old)==1
view=view.replace(old,new,1)
old='createPreparedServiceRowsRenderer, createServiceRowsRenderer, serviceRow'
new='createPreparedServiceRowsRenderer, createServiceRowsRenderer, createServicesAreaRenderer, serviceRow'
assert view.count(old)==1
viewp.write_text(view.replace(old,new,1),encoding='utf-8')

text=app.read_text(encoding='utf-8'); marker='        function renderizarServicos() {'; start=text.index(marker); end=text.index('\n        function ',start+len(marker)); before=text[start:end]
am='                buildActions: (s, rowData) => ({'; a0=before.index(am)+len(am); a1=before.index('\n                })',a0); actions=before[a0:a1]
start_old=before.index('            const servicos = selectionState.services;')
start_actions=before.index(am)
prefix=before[:start_old]
action_tail=before[start_actions:]
new_mid="""            const renderDependencies = window.TotalGestServicesSelection.createServiceRenderDependencies({
                data: dados,
                user: usuarioLogado,
                getPendingTypes: serviceId => _tiposEspecialidadePendentes(serviceId),
                getEmployeeName: obterNomeFuncionario,
                getClientName: obterNomeCliente,
                generateNumber: gerarNumeroRegisto,
                hasMaterials: _osTemMateriais,
                isErpActive: moduloErpAtivo
            });
            const renderServicesArea = window.TotalGestServicesView.createServicesAreaRenderer({
                elements: viewElements,
                selectPending: renderDependencies.selectPendingSpecialty,
                loadedSince: _servicosCarregadoDesde,
                renderToolbar: _toolbarHtml,
                prepareRow: renderDependencies.prepareRow,
                role: usuarioLogado?.role || '',
                getBadgeClass: statusBadge,
                escapeDescription: escapeHtmlSimples,
                getWorkTypesHtml: _tiposTrabalhoBadgesHTML,
"""
# manter corpo actions literal; trocar apenas fecho final
newblock=prefix+new_mid+action_tail
newblock=newblock.replace('            renderPreparedRows(servicos);','            renderServicesArea(selectionState);',1)
text=text[:start]+newblock+text[end:]; app.write_text(text,encoding='utf-8')

sw=swp.read_text(encoding='utf-8'); assert "const CACHE = 'totalgest-v148';" in sw; swp.write_text(sw.replace("const CACHE = 'totalgest-v148';","const CACHE = 'totalgest-v149';",1),encoding='utf-8')
final=app.read_text(encoding='utf-8'); s=final.index(marker); e=final.index('\n        function ',s+len(marker)); block=final[s:e]
a0=block.index(am)+len(am); a1=block.index('\n                })',a0); assert block[a0:a1]==actions
assert 'createServiceRenderDependencies({' in block and 'createServicesAreaRenderer({' in block and 'renderServicesArea(selectionState);' in block
assert 'renderPendingSpecialtyNotice({' not in block and 'createServicesTableStateRenderer({' not in block and 'createServiceRowsRenderer({' not in block
assert len(block)<len(before)
print('SAFE_CUTS=3'); print('ACTIONS_SEGMENT_UNCHANGED=OK'); print('BEFORE=',len(before)); print('AFTER=',len(block)); print('LINES=',len(block.splitlines())); print('STRUCTURE=OK')
