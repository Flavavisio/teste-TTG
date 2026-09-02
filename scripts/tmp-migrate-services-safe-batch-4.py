from pathlib import Path
import subprocess

app_path = Path('app.html')
view_path = Path('assets/js/app-services-view.js')
sw_path = Path('sw.js')

view = view_path.read_text(encoding='utf-8')

# Corte 1: aviso completo de especialidades/histórico
anchor_table = """  function servicesTableState(options) {
"""
assert view.count(anchor_table) == 1
assert 'function renderPendingSpecialtyNotice(options)' not in view
helper_notice = """  function renderPendingSpecialtyNotice(options) {
    const opts = options || {};
    if (!opts.element) return false;
    const selectPending = typeof opts.selectPending === 'function' ? opts.selectPending : function () { return { canSeePending: false, pendingServices: [] }; };
    return applySpecialtyAndHistoryNotice({
      element: opts.element,
      pendingState: selectPending(opts.services || []),
      loadedSince: opts.loadedSince
    });
  }

"""
view = view.replace(anchor_table, helper_notice + anchor_table, 1)

# Corte 2: renderer configurado do estado da tabela
anchor_status = """  function statusControl(options) {
"""
assert view.count(anchor_status) == 1
assert 'function createServicesTableStateRenderer(options)' not in view
helper_table = """  function createServicesTableStateRenderer(options) {
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
view = view.replace(anchor_status, helper_table + anchor_status, 1)

# Corte 3: renderer preparado da coleção de linhas
anchor_service_row = """  function serviceRow(options) {
"""
assert view.count(anchor_service_row) == 1
assert 'function createPreparedServiceRowsRenderer(options)' not in view
helper_rows = """  function createPreparedServiceRowsRenderer(options) {
    const opts = options || {};
    const prepareRow = typeof opts.prepareRow === 'function' ? opts.prepareRow : function () { return {}; };
    const renderRow = typeof opts.renderRow === 'function' ? opts.renderRow : function () { return ''; };
    const buildActions = typeof opts.buildActions === 'function' ? opts.buildActions : function () { return {}; };
    return function (services) {
      return renderServiceRowsToTable({
        tbody: opts.tbody,
        services: services || [],
        renderItem: service => {
          const rowData = prepareRow(service);
          return renderRow(service, rowData, buildActions(service, rowData));
        }
      });
    };
  }

"""
view = view.replace(anchor_service_row, helper_rows + anchor_service_row, 1)

export_old = "window.TotalGestServicesView = { servicesViewElements, serviceHistoryLoadedSinceLabel, specialtyAndHistoryNotice, specialtyAndHistoryNoticeFromState, applySpecialtyAndHistoryNotice, servicesTableState, applyServicesTableState, renderServicesTableState, statusControl, serviceStatusControl, workSheetActions, rowLeadingCells, primaryRowActions, erpRowActions, rowActions, serviceRowFromData, createServiceRowRenderer, renderServiceRowsToTable, serviceRow };"
export_new = "window.TotalGestServicesView = { servicesViewElements, serviceHistoryLoadedSinceLabel, specialtyAndHistoryNotice, specialtyAndHistoryNoticeFromState, applySpecialtyAndHistoryNotice, renderPendingSpecialtyNotice, servicesTableState, applyServicesTableState, renderServicesTableState, createServicesTableStateRenderer, statusControl, serviceStatusControl, workSheetActions, rowLeadingCells, primaryRowActions, erpRowActions, rowActions, serviceRowFromData, createServiceRowRenderer, renderServiceRowsToTable, createPreparedServiceRowsRenderer, serviceRow };"
assert view.count(export_old) == 1
view = view.replace(export_old, export_new, 1)
view_path.write_text(view, encoding='utf-8')

app = app_path.read_text(encoding='utf-8')
marker = '        function renderizarServicos() {'
assert app.count(marker) == 1
start = app.index(marker)
end = app.index('\n        function ', start + len(marker))
before = app[start:end]

# Guardar corpo literal do objeto actions antes da alteração
old_actions_marker = '                    return renderRow(s, rowData, {'
actions_start_before = before.index(old_actions_marker) + len(old_actions_marker)
actions_end_before = before.index('\n                    });', actions_start_before)
actions_body_before = before[actions_start_before:actions_end_before]

old_notice = """            const avisoDiv = viewElements.noticeElement;
            if (avisoDiv) {
                const selectPendingSpecialty = window.TotalGestServicesSelection.createPendingSpecialtySelector({
                    user: usuarioLogado,
                    getPendingTypes: serviceId => _tiposEspecialidadePendentes(serviceId)
                });
                window.TotalGestServicesView.applySpecialtyAndHistoryNotice({
                    element: avisoDiv,
                    pendingState: selectPendingSpecialty(servicos),
                    loadedSince: _servicosCarregadoDesde
                });
            }
"""
new_notice = """            const selectPendingSpecialty = window.TotalGestServicesSelection.createPendingSpecialtySelector({
                user: usuarioLogado,
                getPendingTypes: serviceId => _tiposEspecialidadePendentes(serviceId)
            });
            window.TotalGestServicesView.renderPendingSpecialtyNotice({
                element: viewElements.noticeElement,
                services: servicos,
                selectPending: selectPendingSpecialty,
                loadedSince: _servicosCarregadoDesde
            });
"""
assert before.count(old_notice) == 1
app = app.replace(old_notice, new_notice, 1)

old_table = """            const hasRows = window.TotalGestServicesView.renderServicesTableState({
                totalCount: totalGeralOS,
                visibleCount: servicos.length,
                renderToolbar: _toolbarHtml,
                toolbarElement: viewElements.toolbarElement,
                tbody,
                emptyElement: empty
            });
            if (!hasRows) return;
"""
new_table = """            const renderTableState = window.TotalGestServicesView.createServicesTableStateRenderer({
                renderToolbar: _toolbarHtml,
                toolbarElement: viewElements.toolbarElement,
                tbody,
                emptyElement: empty
            });
            if (!renderTableState(totalGeralOS, servicos.length)) return;
"""
assert before.count(old_table) == 1
app = app.replace(old_table, new_table, 1)

# Substituir apenas o invólucro de preparação/renderização; corpo actions permanece literal
start = app.index(marker)
end = app.index('\n        function ', start + len(marker))
current = app[start:end]
old_rows_open = """            window.TotalGestServicesView.renderServiceRowsToTable({
                tbody,
                services: servicos,
                renderItem: s => {
                    const rowData = prepareRow(s);
                    return renderRow(s, rowData, {
"""
new_rows_open = """            const renderPreparedRows = window.TotalGestServicesView.createPreparedServiceRowsRenderer({
                tbody,
                prepareRow,
                renderRow,
                buildActions: (s, rowData) => ({
"""
assert current.count(old_rows_open) == 1
current = current.replace(old_rows_open, new_rows_open, 1)
old_rows_close = """                    });
                }
            });
"""
new_rows_close = """                })
            });
            renderPreparedRows(servicos);
"""
assert current.count(old_rows_close) == 1
current = current.replace(old_rows_close, new_rows_close, 1)
app = app[:start] + current + app[end:]
app_path.write_text(app, encoding='utf-8')

sw = sw_path.read_text(encoding='utf-8')
assert sw.count("const CACHE = 'totalgest-v146';") == 1
sw = sw.replace("const CACHE = 'totalgest-v146';", "const CACHE = 'totalgest-v147';", 1)
sw_path.write_text(sw, encoding='utf-8')

final_app = app_path.read_text(encoding='utf-8')
start = final_app.index(marker)
end = final_app.index('\n        function ', start + len(marker))
block = final_app[start:end]

for item in ['servicesViewElements(document)','selectVisibleServicesFromData({','createPendingSpecialtySelector({','renderPendingSpecialtyNotice({','createServiceFilterSorter({','filterServices(servicos)','createServicesTableStateRenderer({','renderTableState(totalGeralOS, servicos.length)','createServiceRowPreparer({','createServiceRowRenderer({','createPreparedServiceRowsRenderer({','renderPreparedRows(servicos)','buildActions: (s, rowData) => ({']:
    assert block.count(item) == 1, (item, block.count(item))
for item in ['applySpecialtyAndHistoryNotice({','renderServicesTableState({','renderServiceRowsToTable({','const rowData = prepareRow(s);','return renderRow(s, rowData, {']:
    assert block.count(item) == 0, (item, block.count(item))
for item in ['invoiceTOId:','invoiceMoloniId:','invoiceMoloniUrl:','receiptMoloniUrl:','guideMoloniId:','guideMoloniUrl:','creditNoteMoloniId:','creditNoteMoloniUrl:']:
    assert block.count(item) == 1, (item, block.count(item))
new_actions_marker = '                buildActions: (s, rowData) => ({'
actions_start_after = block.index(new_actions_marker) + len(new_actions_marker)
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
vm.runInContext(fs.readFileSync('assets/js/app-services-view.js', 'utf8'), context);
const view = context.window.TotalGestServicesView;

const notice = { innerHTML: '' };
let selectCalls = 0;
const selectPending = services => { selectCalls += 1; assert.strictEqual(services.length, 2); return { canSeePending: false, pendingServices: [] }; };
assert.strictEqual(view.renderPendingSpecialtyNotice({ element: notice, services: [{},{}], selectPending, loadedSince: '2026-06-01' }), true);
assert.strictEqual(selectCalls, 1);
assert.ok(notice.innerHTML.includes('A mostrar concluídas desde'));
assert.strictEqual(view.renderPendingSpecialtyNotice({ element: null }), false);

const toolbar = { innerHTML: '' }, tbody = { innerHTML: '' }, empty = { style: {} };
const renderTableState = view.createServicesTableStateRenderer({ renderToolbar: () => 'TB', toolbarElement: toolbar, tbody, emptyElement: empty });
assert.strictEqual(renderTableState(2, 1), true);
assert.strictEqual(toolbar.innerHTML, 'TB');
assert.strictEqual(renderTableState(2, 0), false);

const tbody2 = { innerHTML: '' };
const seen = [];
const prepared = view.createPreparedServiceRowsRenderer({
  tbody: tbody2,
  prepareRow: s => ({ n: s.id + '-row' }),
  renderRow: (s, row, actions) => { seen.push([s.id, row.n, actions.a]); return `<tr>${s.id}</tr>`; },
  buildActions: (s, row) => ({ a: s.id + ':' + row.n })
});
assert.strictEqual(prepared([{ id: '1' }, { id: '2' }]), true);
assert.strictEqual(tbody2.innerHTML, '<tr>1</tr><tr>2</tr>');
assert.deepStrictEqual(JSON.parse(JSON.stringify(seen)), [['1','1-row','1:1-row'],['2','2-row','2:2-row']]);
console.log('SAFE_BATCH_4_UNIT=OK');
"""
subprocess.run(['node', '-e', node_test], check=True)
subprocess.run(['node', '--check', 'assets/js/app-services-view.js'], check=True)
subprocess.run(['node', '--check', 'sw.js'], check=True)
subprocess.run(['git', 'diff', '--check'], check=True)
print('SAFE_CUTS=3')
print('ACTIONS_SEGMENT_UNCHANGED=OK')
print('RENDERIZAR_SERVICOS_BEFORE_CHARS=', len(before))
print('RENDERIZAR_SERVICOS_AFTER_CHARS=', len(block))
print('RENDERIZAR_SERVICOS_AFTER_LINES=', len(block.splitlines()))
print('STRUCTURE=OK')
