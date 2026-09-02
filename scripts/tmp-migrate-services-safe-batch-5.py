from pathlib import Path
import subprocess

app_path = Path('app.html')
selection_path = Path('assets/js/app-services-selection.js')
view_path = Path('assets/js/app-services-view.js')
sw_path = Path('sw.js')

# Corte 1: preparar seleção visível + total + filtro/ordenação numa operação
selection = selection_path.read_text(encoding='utf-8')
anchor_filter_factory = """  function createServiceFilterSorter(options) {
"""
assert selection.count(anchor_filter_factory) == 1
assert 'function prepareServicesForRendering(options)' not in selection
helper_pipeline = """  function prepareServicesForRendering(options) {
    options = options || {};
    const sourceServices = selectVisibleServicesFromData({
      data: options.data || {},
      user: options.user || null
    });
    return {
      sourceServices,
      totalCount: sourceServices.length,
      services: filterAndSortServices({
        services: sourceServices,
        applyFilterSort: options.applyFilterSort,
        getTableState: options.getTableState,
        getClientName: options.getClientName
      })
    };
  }

"""
selection = selection.replace(anchor_filter_factory, helper_pipeline + anchor_filter_factory, 1)

# Corte 2: preparar linhas diretamente a partir de dados
anchor_pipeline = """  function prepareServicesForRendering(options) {
"""
assert selection.count(anchor_pipeline) == 1
assert 'function createServiceRowPreparerFromData(options)' not in selection
helper_preparer_data = """  function createServiceRowPreparerFromData(options) {
    options = options || {};
    const data = options.data || {};
    return createServiceRowPreparer({
      administrators: data.administradores || [],
      getEmployeeName: options.getEmployeeName,
      getClientName: options.getClientName,
      generateNumber: options.generateNumber,
      hasMaterials: options.hasMaterials,
      isErpActive: options.isErpActive
    });
  }

"""
selection = selection.replace(anchor_pipeline, helper_preparer_data + anchor_pipeline, 1)

export_old = """    prepareServiceRow: prepareServiceRow,
    createServiceRowPreparer: createServiceRowPreparer,
    createServiceFilterSorter: createServiceFilterSorter,
    filterAndSortServices: filterAndSortServices
"""
export_new = """    prepareServiceRow: prepareServiceRow,
    createServiceRowPreparer: createServiceRowPreparer,
    createServiceRowPreparerFromData: createServiceRowPreparerFromData,
    prepareServicesForRendering: prepareServicesForRendering,
    createServiceFilterSorter: createServiceFilterSorter,
    filterAndSortServices: filterAndSortServices
"""
assert selection.count(export_old) == 1
selection = selection.replace(export_old, export_new, 1)
selection_path.write_text(selection, encoding='utf-8')

view = view_path.read_text(encoding='utf-8')

# Corte 3: renderer da tabela recebe viewElements diretamente, mantendo compatibilidade
old_table_renderer = """  function createServicesTableStateRenderer(options) {
    const opts = options || {};
    return function (totalCount, visibleCount) {
      return renderServicesTableState({
        totalCount,
        visibleCount,
        renderToolbar: opts.renderToolbar,
        toolbarElement: opts.toolbarElement,
        tbody: opts.tbody,
        emptyElement: opts.emptyElement
      });
    };
  }
"""
new_table_renderer = """  function createServicesTableStateRenderer(options) {
    const opts = options || {};
    const elements = opts.elements || {};
    return function (totalCount, visibleCount) {
      return renderServicesTableState({
        totalCount,
        visibleCount,
        renderToolbar: opts.renderToolbar,
        toolbarElement: opts.toolbarElement || elements.toolbarElement,
        tbody: opts.tbody || elements.tbody,
        emptyElement: opts.emptyElement || elements.emptyElement
      });
    };
  }
"""
assert view.count(old_table_renderer) == 1
view = view.replace(old_table_renderer, new_table_renderer, 1)

# Corte 4: combinar renderer visual da linha + preparação/coleção
anchor_service_row = """  function serviceRow(options) {
"""
assert view.count(anchor_service_row) == 1
assert 'function createServiceRowsRenderer(options)' not in view
helper_combined_rows = """  function createServiceRowsRenderer(options) {
    const opts = options || {};
    const elements = opts.elements || {};
    const renderRow = createServiceRowRenderer({
      role: opts.role || '',
      getBadgeClass: opts.getBadgeClass,
      escapeDescription: opts.escapeDescription,
      getWorkTypesHtml: opts.getWorkTypesHtml
    });
    return createPreparedServiceRowsRenderer({
      tbody: opts.tbody || elements.tbody,
      prepareRow: opts.prepareRow,
      renderRow,
      buildActions: opts.buildActions
    });
  }

"""
view = view.replace(anchor_service_row, helper_combined_rows + anchor_service_row, 1)
export_old_view = "window.TotalGestServicesView = { servicesViewElements, serviceHistoryLoadedSinceLabel, specialtyAndHistoryNotice, specialtyAndHistoryNoticeFromState, applySpecialtyAndHistoryNotice, renderPendingSpecialtyNotice, servicesTableState, applyServicesTableState, renderServicesTableState, createServicesTableStateRenderer, statusControl, serviceStatusControl, workSheetActions, rowLeadingCells, primaryRowActions, erpRowActions, rowActions, serviceRowFromData, createServiceRowRenderer, renderServiceRowsToTable, createPreparedServiceRowsRenderer, serviceRow };"
export_new_view = "window.TotalGestServicesView = { servicesViewElements, serviceHistoryLoadedSinceLabel, specialtyAndHistoryNotice, specialtyAndHistoryNoticeFromState, applySpecialtyAndHistoryNotice, renderPendingSpecialtyNotice, servicesTableState, applyServicesTableState, renderServicesTableState, createServicesTableStateRenderer, statusControl, serviceStatusControl, workSheetActions, rowLeadingCells, primaryRowActions, erpRowActions, rowActions, serviceRowFromData, createServiceRowRenderer, renderServiceRowsToTable, createPreparedServiceRowsRenderer, createServiceRowsRenderer, serviceRow };"
assert view.count(export_old_view) == 1
view = view.replace(export_old_view, export_new_view, 1)
view_path.write_text(view, encoding='utf-8')

# Alterações semânticas em renderizarServicos
app = app_path.read_text(encoding='utf-8')
marker = '        function renderizarServicos() {'
assert app.count(marker) == 1
start = app.index(marker)
end = app.index('\n        function ', start + len(marker))
before = app[start:end]

actions_marker = '                buildActions: (s, rowData) => ({'
actions_start_before = before.index(actions_marker) + len(actions_marker)
actions_end_before = before.index('\n                })', actions_start_before)
actions_body_before = before[actions_start_before:actions_end_before]

old_head = """        function renderizarServicos() {
            const viewElements = window.TotalGestServicesView.servicesViewElements(document);
            const tbody = viewElements.tbody;
            const empty = viewElements.emptyElement;
            let servicos = window.TotalGestServicesSelection.selectVisibleServicesFromData({
                data: dados,
                user: usuarioLogado
            });

            const totalGeralOS = servicos.length;
"""
new_head = """        function renderizarServicos() {
            const viewElements = window.TotalGestServicesView.servicesViewElements(document);
            const selectionState = window.TotalGestServicesSelection.prepareServicesForRendering({
                data: dados,
                user: usuarioLogado,
                applyFilterSort: _aplicarFiltroOrdenacao,
                getTableState: _getTableState,
                getClientName: obterNomeCliente
            });
            const servicos = selectionState.services;
"""
assert before.count(old_head) == 1
app = app.replace(old_head, new_head, 1)

old_notice_services = """                services: servicos,
                selectPending: selectPendingSpecialty,
"""
new_notice_services = """                services: selectionState.sourceServices,
                selectPending: selectPendingSpecialty,
"""
start = app.index(marker)
end = app.index('\n        function ', start + len(marker))
current = app[start:end]
assert current.count(old_notice_services) == 1
current = current.replace(old_notice_services, new_notice_services, 1)
app = app[:start] + current + app[end:]

old_filter = """            const filterServices = window.TotalGestServicesSelection.createServiceFilterSorter({
                applyFilterSort: _aplicarFiltroOrdenacao,
                getTableState: _getTableState,
                getClientName: obterNomeCliente
            });
            servicos = filterServices(servicos);
"""
assert app.count(old_filter) == 1
app = app.replace(old_filter, '', 1)

old_table = """            const renderTableState = window.TotalGestServicesView.createServicesTableStateRenderer({
                renderToolbar: _toolbarHtml,
                toolbarElement: viewElements.toolbarElement,
                tbody,
                emptyElement: empty
            });
            if (!renderTableState(totalGeralOS, servicos.length)) return;
"""
new_table = """            const renderTableState = window.TotalGestServicesView.createServicesTableStateRenderer({
                renderToolbar: _toolbarHtml,
                elements: viewElements
            });
            if (!renderTableState(selectionState.totalCount, servicos.length)) return;
"""
assert app.count(old_table) == 1
app = app.replace(old_table, new_table, 1)

old_prepare = """            const prepareRow = window.TotalGestServicesSelection.createServiceRowPreparer({
                administrators: dados.administradores || [],
                getEmployeeName: obterNomeFuncionario,
                getClientName: obterNomeCliente,
                generateNumber: gerarNumeroRegisto,
                hasMaterials: _osTemMateriais,
                isErpActive: moduloErpAtivo
            });
            const renderRow = window.TotalGestServicesView.createServiceRowRenderer({
                role: usuarioLogado?.role || '',
                getBadgeClass: statusBadge,
                escapeDescription: escapeHtmlSimples,
                getWorkTypesHtml: _tiposTrabalhoBadgesHTML
            });
            const renderPreparedRows = window.TotalGestServicesView.createPreparedServiceRowsRenderer({
                tbody,
                prepareRow,
                renderRow,
                buildActions: (s, rowData) => ({
"""
new_prepare = """            const prepareRow = window.TotalGestServicesSelection.createServiceRowPreparerFromData({
                data: dados,
                getEmployeeName: obterNomeFuncionario,
                getClientName: obterNomeCliente,
                generateNumber: gerarNumeroRegisto,
                hasMaterials: _osTemMateriais,
                isErpActive: moduloErpAtivo
            });
            const renderPreparedRows = window.TotalGestServicesView.createServiceRowsRenderer({
                elements: viewElements,
                prepareRow,
                role: usuarioLogado?.role || '',
                getBadgeClass: statusBadge,
                escapeDescription: escapeHtmlSimples,
                getWorkTypesHtml: _tiposTrabalhoBadgesHTML,
                buildActions: (s, rowData) => ({
"""
assert app.count(old_prepare) == 1
app = app.replace(old_prepare, new_prepare, 1)
app_path.write_text(app, encoding='utf-8')

# Cache
sw = sw_path.read_text(encoding='utf-8')
assert sw.count("const CACHE = 'totalgest-v147';") == 1
sw = sw.replace("const CACHE = 'totalgest-v147';", "const CACHE = 'totalgest-v148';", 1)
sw_path.write_text(sw, encoding='utf-8')

# Validação estrutural + actions byte a byte
final_app = app_path.read_text(encoding='utf-8')
start = final_app.index(marker)
end = final_app.index('\n        function ', start + len(marker))
block = final_app[start:end]
for item in ['servicesViewElements(document)','prepareServicesForRendering({','const servicos = selectionState.services;','createPendingSpecialtySelector({','renderPendingSpecialtyNotice({','services: selectionState.sourceServices','createServicesTableStateRenderer({','elements: viewElements','renderTableState(selectionState.totalCount, servicos.length)','createServiceRowPreparerFromData({','createServiceRowsRenderer({','renderPreparedRows(servicos)','buildActions: (s, rowData) => ({']:
    assert block.count(item) == 1, (item, block.count(item))
for item in ['selectVisibleServicesFromData({','createServiceFilterSorter({','filterServices(servicos)','const totalGeralOS =','const tbody =','const empty =','createServiceRowPreparer({','createServiceRowRenderer({','createPreparedServiceRowsRenderer({']:
    assert block.count(item) == 0, (item, block.count(item))
for item in ['invoiceTOId:','invoiceMoloniId:','invoiceMoloniUrl:','receiptMoloniUrl:','guideMoloniId:','guideMoloniUrl:','creditNoteMoloniId:','creditNoteMoloniUrl:']:
    assert block.count(item) == 1, (item, block.count(item))
actions_start_after = block.index(actions_marker) + len(actions_marker)
actions_end_after = block.index('\n                })', actions_start_after)
actions_body_after = block[actions_start_after:actions_end_after]
assert actions_body_after == actions_body_before, (actions_body_before, actions_body_after)
assert len(block) < len(before), (len(before), len(block))

node_test = r"""
const fs = require('fs');
const vm = require('vm');
const assert = require('assert');
const context = { window: {}, document: { getElementById: () => null } };
vm.createContext(context);
vm.runInContext(fs.readFileSync('assets/js/app-services-selection.js', 'utf8'), context);
vm.runInContext(fs.readFileSync('assets/js/app-services-view.js', 'utf8'), context);
const sel = context.window.TotalGestServicesSelection;
const view = context.window.TotalGestServicesView;

const data = {
  servicos: [
    { id: 's1', adminId: 'a1', clienteId: 'c1', data: '2026-09-01', hora: '10:00', status: 'pendente' },
    { id: 's2', adminId: 'a1', clienteId: 'c2', data: '2026-09-02', hora: '11:00', status: 'concluído' },
    { id: 's3', adminId: 'a2', clienteId: 'c3', data: '2026-09-03', hora: '12:00', status: 'pendente' }
  ],
  encarregados: [], funcionarios: [], administradores: [{ id: 'a1', integracaoFaturacao: { provider: 'moloni' } }]
};
const user = { role: 'admin', id: 'a1' };
const filterOpts = {
  applyFilterSort: (_, items) => items.slice(),
  getTableState: () => ({}),
  getClientName: id => 'Cliente ' + id
};
const source = sel.selectVisibleServicesFromData({ data, user });
const expectedFiltered = sel.filterAndSortServices({ services: source, ...filterOpts });
const state = sel.prepareServicesForRendering({ data, user, ...filterOpts });
assert.strictEqual(state.totalCount, source.length);
assert.deepStrictEqual(JSON.parse(JSON.stringify(state.sourceServices)), JSON.parse(JSON.stringify(source)));
assert.deepStrictEqual(JSON.parse(JSON.stringify(state.services)), JSON.parse(JSON.stringify(expectedFiltered)));

const prepOpts = {
  data,
  getEmployeeName: id => 'Emp ' + id,
  getClientName: id => 'Cliente ' + id,
  generateNumber: () => 'GERADO',
  hasMaterials: id => id === 's1',
  isErpActive: admin => !!admin
};
const oldPreparer = sel.createServiceRowPreparer({ administrators: data.administradores, ...prepOpts });
const newPreparer = sel.createServiceRowPreparerFromData(prepOpts);
assert.deepStrictEqual(JSON.parse(JSON.stringify(newPreparer(data.servicos[0]))), JSON.parse(JSON.stringify(oldPreparer(data.servicos[0]))));

const elements = { toolbarElement: { innerHTML: '' }, tbody: { innerHTML: '' }, emptyElement: { style: {} } };
const tableRenderer = view.createServicesTableStateRenderer({ elements, renderToolbar: () => 'TB' });
assert.strictEqual(tableRenderer(2, 1), true);
assert.strictEqual(elements.toolbarElement.innerHTML, 'TB');

const tbody = { innerHTML: '' };
const rowsElements = { tbody };
const seen = [];
const renderer = view.createServiceRowsRenderer({
  elements: rowsElements,
  prepareRow: s => ({ number: s.id, hasMaterials: false, clientName: 'C', employeeName: 'E' }),
  role: 'funcionario',
  getBadgeClass: s => 'badge-' + s,
  escapeDescription: v => 'ESC:' + v,
  getWorkTypesHtml: () => '<em>T</em>',
  buildActions: (s, row) => { seen.push([s.id, row.number]); return { serviceId: s.id, status: s.status, role: 'funcionario' }; }
});
assert.strictEqual(renderer([{ id: 'r1', status: 'pendente', descricao: 'x', data: '2026-09-01', hora: '10:00' }]), true);
assert.ok(tbody.innerHTML.includes('r1'));
assert.deepStrictEqual(JSON.parse(JSON.stringify(seen)), [['r1','r1']]);
console.log('SAFE_BATCH_5_UNIT=OK');
"""
subprocess.run(['node', '-e', node_test], check=True)
subprocess.run(['node', '--check', 'assets/js/app-services-selection.js'], check=True)
subprocess.run(['node', '--check', 'assets/js/app-services-view.js'], check=True)
subprocess.run(['node', '--check', 'sw.js'], check=True)
subprocess.run(['git', 'diff', '--check'], check=True)
print('SAFE_CUTS=4')
print('ACTIONS_SEGMENT_UNCHANGED=OK')
print('RENDERIZAR_SERVICOS_BEFORE_CHARS=', len(before))
print('RENDERIZAR_SERVICOS_AFTER_CHARS=', len(block))
print('RENDERIZAR_SERVICOS_AFTER_LINES=', len(block.splitlines()))
print('STRUCTURE=OK')
