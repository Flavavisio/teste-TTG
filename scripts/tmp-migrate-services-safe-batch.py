from pathlib import Path
import subprocess

app_path = Path('app.html')
selection_path = Path('assets/js/app-services-selection.js')
view_path = Path('assets/js/app-services-view.js')
sw_path = Path('sw.js')

# --- Corte 1 + 2: wrappers de seleção ---
selection = selection_path.read_text(encoding='utf-8')
anchor_select = """  function selectPendingSpecialtyServices(options) {
"""
assert selection.count(anchor_select) == 1
assert 'function selectVisibleServicesFromData(options)' not in selection
helper_visible = """  function selectVisibleServicesFromData(options) {
    options = options || {};
    const data = options.data || {};
    return selectVisibleServices({
      services: data.servicos || [],
      user: options.user || null,
      encarregados: data.encarregados || [],
      funcionarios: data.funcionarios || []
    });
  }

"""
selection = selection.replace(anchor_select, helper_visible + anchor_select, 1)
anchor_prepare = """  function prepareServiceRow(options) {
"""
assert selection.count(anchor_prepare) == 1
assert 'function selectPendingSpecialtyServicesForUser(options)' not in selection
helper_pending = """  function selectPendingSpecialtyServicesForUser(options) {
    options = options || {};
    return selectPendingSpecialtyServices({
      services: options.services,
      role: options.user?.role || '',
      getPendingTypes: options.getPendingTypes
    });
  }

"""
selection = selection.replace(anchor_prepare, helper_pending + anchor_prepare, 1)
export_old = """    selectVisibleServices: selectVisibleServices,
    selectPendingSpecialtyServices: selectPendingSpecialtyServices,
    prepareServiceRow: prepareServiceRow,
"""
export_new = """    selectVisibleServices: selectVisibleServices,
    selectVisibleServicesFromData: selectVisibleServicesFromData,
    selectPendingSpecialtyServices: selectPendingSpecialtyServices,
    selectPendingSpecialtyServicesForUser: selectPendingSpecialtyServicesForUser,
    prepareServiceRow: prepareServiceRow,
"""
assert selection.count(export_old) == 1
selection = selection.replace(export_old, export_new, 1)
selection_path.write_text(selection, encoding='utf-8')

# --- Corte 3 + 4: composição do aviso e estado da tabela ---
view = view_path.read_text(encoding='utf-8')
anchor_table = """  function servicesTableState(options) {
"""
assert view.count(anchor_table) == 1
assert 'function specialtyAndHistoryNoticeFromState(options)' not in view
helper_notice = """  function specialtyAndHistoryNoticeFromState(options) {
    const opts = options || {};
    const pendingState = opts.pendingState || {};
    return specialtyAndHistoryNotice({
      canSeePending: pendingState.canSeePending === true,
      pendingServices: pendingState.pendingServices,
      loadedSinceLabel: serviceHistoryLoadedSinceLabel(opts.loadedSince)
    });
  }

"""
view = view.replace(anchor_table, helper_notice + anchor_table, 1)
anchor_status = """  function statusControl(options) {
"""
assert view.count(anchor_status) == 1
assert 'function renderServicesTableState(options)' not in view
helper_table = """  function renderServicesTableState(options) {
    const opts = options || {};
    const state = servicesTableState({
      totalCount: opts.totalCount,
      visibleCount: opts.visibleCount,
      renderToolbar: opts.renderToolbar
    });
    return applyServicesTableState({
      state,
      toolbarElement: opts.toolbarElement,
      tbody: opts.tbody,
      emptyElement: opts.emptyElement
    });
  }

"""
view = view.replace(anchor_status, helper_table + anchor_status, 1)
export_old_view = "window.TotalGestServicesView = { serviceHistoryLoadedSinceLabel, specialtyAndHistoryNotice, servicesTableState, applyServicesTableState, statusControl, serviceStatusControl, workSheetActions, rowLeadingCells, primaryRowActions, erpRowActions, rowActions, serviceRowFromData, serviceRow };"
export_new_view = "window.TotalGestServicesView = { serviceHistoryLoadedSinceLabel, specialtyAndHistoryNotice, specialtyAndHistoryNoticeFromState, servicesTableState, applyServicesTableState, renderServicesTableState, statusControl, serviceStatusControl, workSheetActions, rowLeadingCells, primaryRowActions, erpRowActions, rowActions, serviceRowFromData, serviceRow };"
assert view.count(export_old_view) == 1
view = view.replace(export_old_view, export_new_view, 1)
view_path.write_text(view, encoding='utf-8')

# --- Alterar apenas as quatro fronteiras em renderizarServicos ---
app = app_path.read_text(encoding='utf-8')
marker = '        function renderizarServicos() {'
assert app.count(marker) == 1
start = app.index(marker)
end = app.index('\n        function ', start + len(marker))
before = app[start:end]

old_visible = """            let servicos = window.TotalGestServicesSelection.selectVisibleServices({
                services: dados.servicos || [],
                user: usuarioLogado,
                encarregados: dados.encarregados || [],
                funcionarios: dados.funcionarios || []
            });
"""
new_visible = """            let servicos = window.TotalGestServicesSelection.selectVisibleServicesFromData({
                data: dados,
                user: usuarioLogado
            });
"""
assert before.count(old_visible) == 1
app = app.replace(old_visible, new_visible, 1)

old_notice = """                const _pendingSpecialty = window.TotalGestServicesSelection.selectPendingSpecialtyServices({
                    services: servicos,
                    role: usuarioLogado?.role || '',
                    getPendingTypes: serviceId => _tiposEspecialidadePendentes(serviceId)
                });
                avisoDiv.innerHTML = window.TotalGestServicesView.specialtyAndHistoryNotice({
                    canSeePending: _pendingSpecialty.canSeePending,
                    pendingServices: _pendingSpecialty.pendingServices,
                    loadedSinceLabel: window.TotalGestServicesView.serviceHistoryLoadedSinceLabel(_servicosCarregadoDesde)
                });
"""
new_notice = """                const _pendingSpecialty = window.TotalGestServicesSelection.selectPendingSpecialtyServicesForUser({
                    services: servicos,
                    user: usuarioLogado,
                    getPendingTypes: serviceId => _tiposEspecialidadePendentes(serviceId)
                });
                avisoDiv.innerHTML = window.TotalGestServicesView.specialtyAndHistoryNoticeFromState({
                    pendingState: _pendingSpecialty,
                    loadedSince: _servicosCarregadoDesde
                });
"""
assert before.count(old_notice) == 1
app = app.replace(old_notice, new_notice, 1)

old_table = """            const tableState = window.TotalGestServicesView.servicesTableState({
                totalCount: totalGeralOS,
                visibleCount: servicos.length,
                renderToolbar: _toolbarHtml
            });
            const tbOS = document.getElementById('servicosToolbar');
            const hasRows = window.TotalGestServicesView.applyServicesTableState({
                state: tableState,
                toolbarElement: tbOS,
                tbody,
                emptyElement: empty
            });
"""
new_table = """            const hasRows = window.TotalGestServicesView.renderServicesTableState({
                totalCount: totalGeralOS,
                visibleCount: servicos.length,
                renderToolbar: _toolbarHtml,
                toolbarElement: document.getElementById('servicosToolbar'),
                tbody,
                emptyElement: empty
            });
"""
assert before.count(old_table) == 1
app = app.replace(old_table, new_table, 1)
app_path.write_text(app, encoding='utf-8')

# cache único para todo o lote
sw = sw_path.read_text(encoding='utf-8')
assert sw.count("const CACHE = 'totalgest-v143';") == 1
sw = sw.replace("const CACHE = 'totalgest-v143';", "const CACHE = 'totalgest-v144';", 1)
sw_path.write_text(sw, encoding='utf-8')

# --- Estrutura e preservação do actions ---
final_app = app_path.read_text(encoding='utf-8')
start = final_app.index(marker)
end = final_app.index('\n        function ', start + len(marker))
block = final_app[start:end]
for item in ['selectVisibleServicesFromData({','selectPendingSpecialtyServicesForUser({','specialtyAndHistoryNoticeFromState({','renderServicesTableState({','createServiceRowPreparer({','filterAndSortServices({','serviceRowFromData({']:
    assert block.count(item) == 1, (item, block.count(item))
for item in ['selectVisibleServices({','selectPendingSpecialtyServices({','specialtyAndHistoryNotice({','serviceHistoryLoadedSinceLabel(_servicosCarregadoDesde)','servicesTableState({','applyServicesTableState({','const tableState =','const tbOS =']:
    assert block.count(item) == 0, (item, block.count(item))
for item in ['invoiceTOId:','invoiceMoloniId:','invoiceMoloniUrl:','receiptMoloniUrl:','guideMoloniId:','guideMoloniUrl:','creditNoteMoloniId:','creditNoteMoloniUrl:']:
    assert block.count(item) == 1, (item, block.count(item))
actions_start_before = before.index('                    actions: {')
actions_end_before = before.index('\n                });', actions_start_before)
actions_before = before[actions_start_before:actions_end_before]
actions_start_after = block.index('                    actions: {')
actions_end_after = block.index('\n                });', actions_start_after)
actions_after = block[actions_start_after:actions_end_after]
assert actions_after == actions_before
assert len(block) < len(before), (len(before), len(block))

# --- Testes unitários de equivalência dos 4 cortes ---
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

const data = {
  servicos: [
    { id: 's1', adminId: 'a1', status: 'concluído', numeroRegisto: 'OS-1' },
    { id: 's2', adminId: 'a2', status: 'pendente', numeroRegisto: 'OS-2' }
  ],
  encarregados: [],
  funcionarios: []
};
const user = { id: 'a1', role: 'admin' };
assert.deepStrictEqual(
  JSON.parse(JSON.stringify(sel.selectVisibleServicesFromData({ data, user }))),
  JSON.parse(JSON.stringify(sel.selectVisibleServices({ services: data.servicos, user, encarregados: [], funcionarios: [] })))
);

const getPendingTypes = id => id === 's1' ? ['AVAC'] : [];
const p1 = sel.selectPendingSpecialtyServicesForUser({ services: data.servicos, user, getPendingTypes });
const p2 = sel.selectPendingSpecialtyServices({ services: data.servicos, role: 'admin', getPendingTypes });
assert.deepStrictEqual(JSON.parse(JSON.stringify(p1)), JSON.parse(JSON.stringify(p2)));

const n1 = view.specialtyAndHistoryNoticeFromState({ pendingState: p1, loadedSince: '2026-06-01' });
const n2 = view.specialtyAndHistoryNotice({ canSeePending: p1.canSeePending, pendingServices: p1.pendingServices, loadedSinceLabel: view.serviceHistoryLoadedSinceLabel('2026-06-01') });
assert.strictEqual(n1, n2);

function element() { return { innerHTML: 'KEEP', style: { display: 'KEEP' } }; }
const toolbar1 = element(), tbody1 = element(), empty1 = element();
const toolbar2 = element(), tbody2 = element(), empty2 = element();
const renderToolbar = (...args) => 'TB:' + args.join('|');
const state = view.servicesTableState({ totalCount: 2, visibleCount: 1, renderToolbar });
const expected = view.applyServicesTableState({ state, toolbarElement: toolbar1, tbody: tbody1, emptyElement: empty1 });
const actual = view.renderServicesTableState({ totalCount: 2, visibleCount: 1, renderToolbar, toolbarElement: toolbar2, tbody: tbody2, emptyElement: empty2 });
assert.strictEqual(actual, expected);
assert.strictEqual(toolbar2.innerHTML, toolbar1.innerHTML);
assert.strictEqual(tbody2.innerHTML, tbody1.innerHTML);
assert.strictEqual(empty2.style.display, empty1.style.display);

const toolbar3 = element(), tbody3 = element(), empty3 = element();
const toolbar4 = element(), tbody4 = element(), empty4 = element();
const emptyState = view.servicesTableState({ totalCount: 2, visibleCount: 0, renderToolbar });
const expectedEmpty = view.applyServicesTableState({ state: emptyState, toolbarElement: toolbar3, tbody: tbody3, emptyElement: empty3 });
const actualEmpty = view.renderServicesTableState({ totalCount: 2, visibleCount: 0, renderToolbar, toolbarElement: toolbar4, tbody: tbody4, emptyElement: empty4 });
assert.strictEqual(actualEmpty, expectedEmpty);
assert.strictEqual(toolbar4.innerHTML, toolbar3.innerHTML);
assert.strictEqual(tbody4.innerHTML, tbody3.innerHTML);
assert.strictEqual(empty4.style.display, empty3.style.display);
console.log('SAFE_BATCH_UNIT=OK');
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
