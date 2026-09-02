from pathlib import Path

app=Path('app.html'); selp=Path('assets/js/app-services-selection.js'); viewp=Path('assets/js/app-services-view.js'); swp=Path('sw.js')
sel=selp.read_text(encoding='utf-8')
anchor='  function prepareServicesForRendering(options) {\n'
assert sel.count(anchor)==1 and 'function createServicesRuntimeState(options)' not in sel
helper="""  function createServicesRuntimeState(options) {
    options = options || {};
    return {
      selectionState: prepareServicesForRendering(options),
      renderDependencies: createServiceRenderDependencies(options)
    };
  }

"""
sel=sel.replace(anchor,helper+anchor,1)
old='    createServiceRenderDependencies: createServiceRenderDependencies,\n    prepareServicesForRendering: prepareServicesForRendering,'
new='    createServiceRenderDependencies: createServiceRenderDependencies,\n    createServicesRuntimeState: createServicesRuntimeState,\n    prepareServicesForRendering: prepareServicesForRendering,'
assert sel.count(old)==1
selp.write_text(sel.replace(old,new,1),encoding='utf-8')

view=viewp.read_text(encoding='utf-8')
old_area="""  function createServicesAreaRenderer(options) {
    const opts = options || {}, elements = opts.elements || {};
    const renderNotice = createPendingSpecialtyNoticeRenderer({ element: elements.noticeElement, selectPending: opts.selectPending, loadedSince: opts.loadedSince });
    const renderTableState = createServicesTableStateRenderer({ renderToolbar: opts.renderToolbar, elements });
    const renderRows = createServiceRowsRenderer({ elements, prepareRow: opts.prepareRow, role: opts.role, getBadgeClass: opts.getBadgeClass, escapeDescription: opts.escapeDescription, getWorkTypesHtml: opts.getWorkTypesHtml, buildActions: opts.buildActions });
"""
new_area="""  function createServicesAreaRenderer(options) {
    const opts = options || {}, elements = opts.elements || {}, dependencies = opts.renderDependencies || {};
    const renderNotice = createPendingSpecialtyNoticeRenderer({ element: elements.noticeElement, selectPending: opts.selectPending || dependencies.selectPendingSpecialty, loadedSince: opts.loadedSince });
    const renderTableState = createServicesTableStateRenderer({ renderToolbar: opts.renderToolbar, elements });
    const renderRows = createServiceRowsRenderer({ elements, prepareRow: opts.prepareRow || dependencies.prepareRow, role: opts.role, getBadgeClass: opts.getBadgeClass, escapeDescription: opts.escapeDescription, getWorkTypesHtml: opts.getWorkTypesHtml, buildActions: opts.buildActions });
"""
assert view.count(old_area)==1
view=view.replace(old_area,new_area,1)
anchor='  function serviceRow(options) {\n'
assert view.count(anchor)==1 and 'function createServicesAreaRendererFromDocument(options)' not in view
helper="""  function createServicesAreaRendererFromDocument(options) {
    const opts = options || {};
    return createServicesAreaRenderer({
      elements: servicesViewElements(opts.document || document),
      renderDependencies: opts.renderDependencies,
      loadedSince: opts.loadedSince,
      renderToolbar: opts.renderToolbar,
      role: opts.role,
      getBadgeClass: opts.getBadgeClass,
      escapeDescription: opts.escapeDescription,
      getWorkTypesHtml: opts.getWorkTypesHtml,
      buildActions: opts.buildActions
    });
  }

"""
view=view.replace(anchor,helper+anchor,1)
old='createServiceRowsRenderer, createServicesAreaRenderer, serviceRow'
new='createServiceRowsRenderer, createServicesAreaRenderer, createServicesAreaRendererFromDocument, serviceRow'
assert view.count(old)==1
viewp.write_text(view.replace(old,new,1),encoding='utf-8')

text=app.read_text(encoding='utf-8'); marker='        function renderizarServicos() {'; s=text.index(marker); e=text.index('\n        function ',s+len(marker)); before=text[s:e]
am='                buildActions: (s, rowData) => ({'; a0=before.index(am)+len(am); a1=before.index('\n                })',a0); actions=before[a0:a1]
old_head="""        function renderizarServicos() {
            const viewElements = window.TotalGestServicesView.servicesViewElements(document);
            const selectionState = window.TotalGestServicesSelection.prepareServicesForRendering({
                data: dados,
                user: usuarioLogado,
                applyFilterSort: _aplicarFiltroOrdenacao,
                getTableState: _getTableState,
                getClientName: obterNomeCliente
            });
            const renderDependencies = window.TotalGestServicesSelection.createServiceRenderDependencies({
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
"""
new_head="""        function renderizarServicos() {
            const runtimeState = window.TotalGestServicesSelection.createServicesRuntimeState({
                data: dados,
                user: usuarioLogado,
                applyFilterSort: _aplicarFiltroOrdenacao,
                getTableState: _getTableState,
                getClientName: obterNomeCliente,
                getPendingTypes: serviceId => _tiposEspecialidadePendentes(serviceId),
                getEmployeeName: obterNomeFuncionario,
                generateNumber: gerarNumeroRegisto,
                hasMaterials: _osTemMateriais,
                isErpActive: moduloErpAtivo
            });
            const renderServicesArea = window.TotalGestServicesView.createServicesAreaRendererFromDocument({
                document,
                renderDependencies: runtimeState.renderDependencies,
                loadedSince: _servicosCarregadoDesde,
                renderToolbar: _toolbarHtml,
"""
assert before.count(old_head)==1
block=before.replace(old_head,new_head,1)
block=block.replace('            renderServicesArea(selectionState);','            renderServicesArea(runtimeState.selectionState);',1)
text=text[:s]+block+text[e:]; app.write_text(text,encoding='utf-8')

sw=swp.read_text(encoding='utf-8'); assert "const CACHE = 'totalgest-v149';" in sw; swp.write_text(sw.replace("const CACHE = 'totalgest-v149';","const CACHE = 'totalgest-v150';",1),encoding='utf-8')
final=app.read_text(encoding='utf-8'); s=final.index(marker); e=final.index('\n        function ',s+len(marker)); block=final[s:e]
a0=block.index(am)+len(am); a1=block.index('\n                })',a0); assert block[a0:a1]==actions
for item in ['createServicesRuntimeState({','createServicesAreaRendererFromDocument({','renderDependencies: runtimeState.renderDependencies','renderServicesArea(runtimeState.selectionState);']:
    assert block.count(item)==1,(item,block.count(item))
for item in ['servicesViewElements(document)','prepareServicesForRendering({','createServiceRenderDependencies({','createServicesAreaRenderer({','selectPending: renderDependencies.selectPendingSpecialty','prepareRow: renderDependencies.prepareRow']:
    assert block.count(item)==0,(item,block.count(item))
for item in ['invoiceTOId:','invoiceMoloniId:','invoiceMoloniUrl:','receiptMoloniUrl:','guideMoloniId:','guideMoloniUrl:','creditNoteMoloniId:','creditNoteMoloniUrl:']:
    assert block.count(item)==1,(item,block.count(item))
assert len(block)<len(before)
print('SAFE_CUTS=3'); print('ACTIONS_SEGMENT_UNCHANGED=OK'); print('BEFORE=',len(before)); print('AFTER=',len(block)); print('LINES=',len(block.splitlines())); print('STRUCTURE=OK')
