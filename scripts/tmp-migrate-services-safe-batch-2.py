from pathlib import Path
import subprocess

app_path = Path('app.html')
selection_path = Path('assets/js/app-services-selection.js')
view_path = Path('assets/js/app-services-view.js')
sw_path = Path('sw.js')

# Corte 1: configurar filtro/ordenação uma vez
selection = selection_path.read_text(encoding='utf-8')
anchor_filter = """  function filterAndSortServices(options) {
"""
assert selection.count(anchor_filter) == 1
assert 'function createServiceFilterSorter(options)' not in selection
helper_filter = """  function createServiceFilterSorter(options) {
    options = options || {};
    return function (services) {
      return filterAndSortServices({
        services: services || [],
        applyFilterSort: options.applyFilterSort,
        getTableState: options.getTableState,
        getClientName: options.getClientName
      });
    };
  }

"""
selection = selection.replace(anchor_filter, helper_filter + anchor_filter, 1)
export_old = """    createServiceRowPreparer: createServiceRowPreparer,
    filterAndSortServices: filterAndSortServices
"""
export_new = """    createServiceRowPreparer: createServiceRowPreparer,
    createServiceFilterSorter: createServiceFilterSorter,
    filterAndSortServices: filterAndSortServices
"""
assert selection.count(export_old) == 1
selection = selection.replace(export_old, export_new, 1)
selection_path.write_text(selection, encoding='utf-8')

# Corte 2: aplicar aviso de especialidade/histórico ao DOM
view = view_path.read_text(encoding='utf-8')
anchor_table = """  function servicesTableState(options) {
"""
assert view.count(anchor_table) == 1
assert 'function applySpecialtyAndHistoryNotice(options)' not in view
helper_notice = """  function applySpecialtyAndHistoryNotice(options) {
    const opts = options || {};
    if (!opts.element) return false;
    opts.element.innerHTML = specialtyAndHistoryNoticeFromState({
      pendingState: opts.pendingState,
      loadedSince: opts.loadedSince
    });
    return true;
  }

"""
view = view.replace(anchor_table, helper_notice + anchor_table, 1)

# Corte 3: configurar apresentação visual das linhas uma vez
anchor_service_row = """  function serviceRow(options) {
"""
assert view.count(anchor_service_row) == 1
assert 'function createServiceRowRenderer(options)' not in view
helper_renderer = """  function createServiceRowRenderer(options) {
    const opts = options || {};
    const getBadgeClass = typeof opts.getBadgeClass === 'function' ? opts.getBadgeClass : function () { return ''; };
    const escapeDescription = typeof opts.escapeDescription === 'function' ? opts.escapeDescription : function (value) { return value == null ? '' : String(value); };
    const getWorkTypesHtml = typeof opts.getWorkTypesHtml === 'function' ? opts.getWorkTypesHtml : function () { return ''; };
    return function (service, rowData, actions) {
      const currentService = service || {};
      return serviceRowFromData({
        service: currentService,
        rowData: rowData || {},
        role: opts.role || '',
        badgeClass: getBadgeClass(currentService.status),
        descriptionHtml: escapeDescription(currentService.descricao || '-'),
        workTypesHtml: getWorkTypesHtml(currentService),
        actions: actions || {}
      });
    };
  }

"""
view = view.replace(anchor_service_row, helper_renderer + anchor_service_row, 1)
export_old_view = "window.TotalGestServicesView = { serviceHistoryLoadedSinceLabel, specialtyAndHistoryNotice, specialtyAndHistoryNoticeFromState, servicesTableState, applyServicesTableState, renderServicesTableState, statusControl, serviceStatusControl, workSheetActions, rowLeadingCells, primaryRowActions, erpRowActions, rowActions, serviceRowFromData, serviceRow };"
export_new_view = "window.TotalGestServicesView = { serviceHistoryLoadedSinceLabel, specialtyAndHistoryNotice, specialtyAndHistoryNoticeFromState, applySpecialtyAndHistoryNotice, servicesTableState, applyServicesTableState, renderServicesTableState, statusControl, serviceStatusControl, workSheetActions, rowLeadingCells, primaryRowActions, erpRowActions, rowActions, serviceRowFromData, createServiceRowRenderer, serviceRow };"
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

actions_start_before = before.index('                    actions: {')
actions_end_before = before.index('\n                });', actions_start_before)
actions_before = before[actions_start_before:actions_end_before]

old_notice = """            const avisoDiv = document.getElementById('servicosAvisoEspecialidade');
            if (avisoDiv) {
                const _pendingSpecialty = window.TotalGestServicesSelection.selectPendingSpecialtyServicesForUser({
                    services: servicos,
                    user: usuarioLogado,
                    getPendingTypes: serviceId => _tiposEspecialidadePendentes(serviceId)
                });
                avisoDiv.innerHTML = window.TotalGestServicesView.specialtyAndHistoryNoticeFromState({
                    pendingState: _pendingSpecialty,
                    loadedSince: _servicosCarregadoDesde
                });
            }
"""
new_notice = """            const avisoDiv = document.getElementById('servicosAvisoEspecialidade');
            if (avisoDiv) {
                const _pendingSpecialty = window.TotalGestServicesSelection.selectPendingSpecialtyServicesForUser({
                    services: servicos,
                    user: usuarioLogado,
                    getPendingTypes: serviceId => _tiposEspecialidadePendentes(serviceId)
                });
                window.TotalGestServicesView.applySpecialtyAndHistoryNotice({
                    element: avisoDiv,
                    pendingState: _pendingSpecialty,
                    loadedSince: _servicosCarregadoDesde
                });
            }
"""
assert before.count(old_notice) == 1
app = app.replace(old_notice, new_notice, 1)

old_filter = """            servicos = window.TotalGestServicesSelection.filterAndSortServices({
                services: servicos,
                applyFilterSort: _aplicarFiltroOrdenacao,
                getTableState: _getTableState,
                getClientName: obterNomeCliente
            });
"""
new_filter = """            const filterServices = window.TotalGestServicesSelection.createServiceFilterSorter({
                applyFilterSort: _aplicarFiltroOrdenacao,
                getTableState: _getTableState,
                getClientName: obterNomeCliente
            });
            servicos = filterServices(servicos);
"""
assert before.count(old_filter) == 1
app = app.replace(old_filter, new_filter, 1)

old_renderer_setup = """            const prepareRow = window.TotalGestServicesSelection.createServiceRowPreparer({
                administrators: dados.administradores || [],
                getEmployeeName: obterNomeFuncionario,
                getClientName: obterNomeCliente,
                generateNumber: gerarNumeroRegisto,
                hasMaterials: _osTemMateriais,
                isErpActive: moduloErpAtivo
            });
            tbody.innerHTML = servicos.map(s => {
                const rowData = prepareRow(s);
                return window.TotalGestServicesView.serviceRowFromData({
                    service: s,
                    rowData,
                    role: usuarioLogado?.role || '',
                    badgeClass: statusBadge(s.status),
                    descriptionHtml: escapeHtmlSimples(s.descricao || '-'),
                    workTypesHtml: _tiposTrabalhoBadgesHTML(s),
                    actions: {
"""
new_renderer_setup = """            const prepareRow = window.TotalGestServicesSelection.createServiceRowPreparer({
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
            tbody.innerHTML = servicos.map(s => {
                const rowData = prepareRow(s);
                return renderRow(s, rowData, {
"""
assert before.count(old_renderer_setup) == 1
app = app.replace(old_renderer_setup, new_renderer_setup, 1)

old_renderer_end = """                    }
                });
            }).join('');
"""
new_renderer_end = """                });
            }).join('');
"""
# only target the row renderer ending nearest the actions block by bounded function rewrite
start = app.index(marker)
end = app.index('\n        function ', start + len(marker))
current = app[start:end]
assert current.count(old_renderer_end) == 1, current.count(old_renderer_end)
current = current.replace(old_renderer_end, new_renderer_end, 1)
app = app[:start] + current + app[end:]
app_path.write_text(app, encoding='utf-8')

# cache
sw = sw_path.read_text(encoding='utf-8')
assert sw.count("const CACHE = 'totalgest-v144';") == 1
sw = sw.replace("const CACHE = 'totalgest-v144';", "const CACHE = 'totalgest-v145';", 1)
sw_path.write_text(sw, encoding='utf-8')

# Estrutura final e preservação estrita do actions
final_app = app_path.read_text(encoding='utf-8')
start = final_app.index(marker)
end = final_app.index('\n        function ', start + len(marker))
block = final_app[start:end]
for item in ['selectVisibleServicesFromData({','selectPendingSpecialtyServicesForUser({','applySpecialtyAndHistoryNotice({','createServiceFilterSorter({','filterServices(servicos)','renderServicesTableState({','createServiceRowPreparer({','createServiceRowRenderer({','return renderRow(s, rowData, {']:
    assert block.count(item) == 1, (item, block.count(item))
for item in ['specialtyAndHistoryNoticeFromState({','filterAndSortServices({','serviceRowFromData({','badgeClass: statusBadge(s.status)','descriptionHtml: escapeHtmlSimples','workTypesHtml: _tiposTrabalhoBadgesHTML']:
    assert block.count(item) == 0, (item, block.count(item))
for item in ['invoiceTOId:','invoiceMoloniId:','invoiceMoloniUrl:','receiptMoloniUrl:','guideMoloniId:','guideMoloniUrl:','creditNoteMoloniId:','creditNoteMoloniUrl:']:
    assert block.count(item) == 1, (item, block.count(item))
actions_marker = '                return renderRow(s, rowData, {'
actions_start_after = block.index(actions_marker) + len('                return renderRow(s, rowData, ')
actions_end_after = block.index('\n                });', actions_start_after)
actions_after = block[actions_start_after:actions_end_after]
assert actions_after == actions_before.replace('                    actions: ', '', 1), (actions_before, actions_after)
assert len(block) < len(before), (len(before), len(block))

node_test = r"""
const fs = require('fs');
const vm = require('vm');
const assert = require('assert');
const context = { window: {} };
vm.createContext(context);
vm.runInContext(fs.readFileSync('assets/js/app-services-selection.js', 'utf8'), context);
vm.runInContext(fs.readFileSync('assets/js/app-services-view.js', 'utf8'), context);
const sel = context.window.TotalGestServicesSelection;
const view = context.window.TotalGestServicesView;

const services = [{ id: 's1', data: '2026-09-01', hora: '10:00', descricao: '<x>', status: 'pendente', clienteId: 'c1' }];
const opts = {
  applyFilterSort: (_, items) => items.slice(),
  getTableState: () => ({}),
  getClientName: id => 'Cliente ' + id
};
const expectedFilter = sel.filterAndSortServices({ services, ...opts });
const actualFilter = sel.createServiceFilterSorter(opts)(services);
assert.deepStrictEqual(JSON.parse(JSON.stringify(actualFilter)), JSON.parse(JSON.stringify(expectedFilter)));

const element = { innerHTML: '' };
const pendingState = { canSeePending: true, pendingServices: [{ number: 'OS-1', types: ['AVAC'] }] };
const expectedNotice = view.specialtyAndHistoryNoticeFromState({ pendingState, loadedSince: '2026-06-01' });
assert.strictEqual(view.applySpecialtyAndHistoryNotice({ element, pendingState, loadedSince: '2026-06-01' }), true);
assert.strictEqual(element.innerHTML, expectedNotice);
assert.strictEqual(view.applySpecialtyAndHistoryNotice({ element: null }), false);

const service = { id: 's1', data: '2026-09-01', hora: '10:00', descricao: '<b>x</b>', status: 'pendente' };
const rowData = { number: 'OS-1', hasMaterials: false, clientName: 'Cliente', employeeName: 'Ana' };
const actions = { serviceId: 's1', status: 'pendente', role: 'funcionario' };
const helpers = {
  role: 'funcionario',
  getBadgeClass: status => 'badge-' + status,
  escapeDescription: value => 'ESC:' + value,
  getWorkTypesHtml: () => '<em>Tipo</em>'
};
const expectedRow = view.serviceRowFromData({
  service,
  rowData,
  role: helpers.role,
  badgeClass: helpers.getBadgeClass(service.status),
  descriptionHtml: helpers.escapeDescription(service.descricao || '-'),
  workTypesHtml: helpers.getWorkTypesHtml(service),
  actions
});
const actualRow = view.createServiceRowRenderer(helpers)(service, rowData, actions);
assert.strictEqual(actualRow, expectedRow);
console.log('SAFE_BATCH_2_UNIT=OK');
"""
subprocess.run(['node', '-e', node_test], check=True)
subprocess.run(['node', '--check', 'assets/js/app-services-selection.js'], check=True)
subprocess.run(['node', '--check', 'assets/js/app-services-view.js'], check=True)
subprocess.run(['node', '--check', 'sw.js'], check=True)
subprocess.run(['git', 'diff', '--check'], check=True)
print('SAFE_CUTS=3')
print('ACTIONS_SEGMENT_UNCHANGED=OK')
print('RENDERIZAR_SERVICOS_BEFORE_CHARS=', len(before))
print('RENDERIZAR_SERVICOS_AFTER_CHARS=', len(block))
print('RENDERIZAR_SERVICOS_AFTER_LINES=', len(block.splitlines()))
print('STRUCTURE=OK')
