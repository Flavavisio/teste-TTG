from pathlib import Path
import subprocess

app_path = Path('app.html')
view_path = Path('assets/js/app-services-view.js')
sw_path = Path('sw.js')

view = view_path.read_text(encoding='utf-8')
anchor = """  function statusControl(options) {
"""
assert view.count(anchor) == 1, view.count(anchor)
assert 'function applyServicesTableState(options)' not in view
helper = """  function applyServicesTableState(options) {
    const opts = options || {};
    const state = opts.state || {};
    if (opts.toolbarElement) opts.toolbarElement.innerHTML = state.toolbarHtml || '';
    if (!state.hasRows) {
      opts.tbody.innerHTML = state.emptyRowsHtml || '';
      opts.emptyElement.style.display = state.emptyDisplay || 'none';
      return false;
    }
    opts.emptyElement.style.display = state.emptyDisplay || 'none';
    return true;
  }

"""
view = view.replace(anchor, helper + anchor, 1)
export_old = '  window.TotalGestServicesView = { serviceHistoryLoadedSinceLabel, specialtyAndHistoryNotice, servicesTableState, statusControl, serviceStatusControl, workSheetActions, rowLeadingCells, primaryRowActions, erpRowActions, rowActions, serviceRowFromData, serviceRow };'
export_new = '  window.TotalGestServicesView = { serviceHistoryLoadedSinceLabel, specialtyAndHistoryNotice, servicesTableState, applyServicesTableState, statusControl, serviceStatusControl, workSheetActions, rowLeadingCells, primaryRowActions, erpRowActions, rowActions, serviceRowFromData, serviceRow };'
assert view.count(export_old) == 1, view.count(export_old)
view = view.replace(export_old, export_new, 1)
view_path.write_text(view, encoding='utf-8')

app = app_path.read_text(encoding='utf-8')
function_marker = '        function renderizarServicos() {'
assert app.count(function_marker) == 1, app.count(function_marker)
start = app.index(function_marker)
end = app.index('\n        function ', start + len(function_marker))
before = app[start:end]
old = """            const tbOS = document.getElementById('servicosToolbar');
            if (tbOS) tbOS.innerHTML = tableState.toolbarHtml;
            if (!tableState.hasRows) {
                tbody.innerHTML = tableState.emptyRowsHtml;
                empty.style.display = tableState.emptyDisplay;
                return;
            }
            empty.style.display = tableState.emptyDisplay;
"""
new = """            const tbOS = document.getElementById('servicosToolbar');
            const hasRows = window.TotalGestServicesView.applyServicesTableState({
                state: tableState,
                toolbarElement: tbOS,
                tbody,
                emptyElement: empty
            });
            if (!hasRows) return;
"""
assert before.count(old) == 1, before.count(old)
app = app.replace(old, new, 1)
app_path.write_text(app, encoding='utf-8')

sw = sw_path.read_text(encoding='utf-8')
assert sw.count("const CACHE = 'totalgest-v140';") == 1, sw.count("const CACHE = 'totalgest-v140';")
sw = sw.replace("const CACHE = 'totalgest-v140';", "const CACHE = 'totalgest-v141';", 1)
sw_path.write_text(sw, encoding='utf-8')

final_app = app_path.read_text(encoding='utf-8')
start = final_app.index(function_marker)
end = final_app.index('\n        function ', start + len(function_marker))
block = final_app[start:end]
assert block.count('applyServicesTableState({') == 1
assert 'tbOS.innerHTML = tableState.toolbarHtml' not in block
assert 'tbody.innerHTML = tableState.emptyRowsHtml' not in block
assert 'empty.style.display = tableState.emptyDisplay' not in block
assert block.count('if (!hasRows) return;') == 1
for marker in ['selectVisibleServices({', 'selectPendingSpecialtyServices({', 'filterAndSortServices({', 'servicesTableState({', 'serviceStatusControl({', 'prepareServiceRow({', 'serviceRowFromData({']:
    assert block.count(marker) == 1, (marker, block.count(marker))
for marker in ['invoiceTOId:', 'invoiceMoloniId:', 'invoiceMoloniUrl:', 'receiptMoloniUrl:', 'guideMoloniId:', 'guideMoloniUrl:', 'creditNoteMoloniId:', 'creditNoteMoloniUrl:']:
    assert block.count(marker) == 1, (marker, block.count(marker))
assert len(block) < len(before), (len(before), len(block))

node_test = r"""
const fs = require('fs');
const vm = require('vm');
const assert = require('assert');
const context = { window: {} };
vm.createContext(context);
vm.runInContext(fs.readFileSync('assets/js/app-services-view.js', 'utf8'), context);
const view = context.window.TotalGestServicesView;

const toolbar = { innerHTML: 'old' };
const tbody = { innerHTML: 'rows' };
const empty = { style: { display: 'old' } };
let hasRows = view.applyServicesTableState({
  state: { hasRows: false, toolbarHtml: '<b>tb</b>', emptyRowsHtml: '<tr><td>none</td></tr>', emptyDisplay: 'block' },
  toolbarElement: toolbar,
  tbody,
  emptyElement: empty
});
assert.strictEqual(hasRows, false);
assert.strictEqual(toolbar.innerHTML, '<b>tb</b>');
assert.strictEqual(tbody.innerHTML, '<tr><td>none</td></tr>');
assert.strictEqual(empty.style.display, 'block');

const toolbar2 = { innerHTML: '' };
const tbody2 = { innerHTML: 'keep' };
const empty2 = { style: { display: 'old' } };
hasRows = view.applyServicesTableState({
  state: { hasRows: true, toolbarHtml: 'toolbar', emptyRowsHtml: 'unused', emptyDisplay: 'none' },
  toolbarElement: toolbar2,
  tbody: tbody2,
  emptyElement: empty2
});
assert.strictEqual(hasRows, true);
assert.strictEqual(toolbar2.innerHTML, 'toolbar');
assert.strictEqual(tbody2.innerHTML, 'keep');
assert.strictEqual(empty2.style.display, 'none');

const tbody3 = { innerHTML: 'keep' };
const empty3 = { style: { display: 'old' } };
assert.strictEqual(view.applyServicesTableState({
  state: { hasRows: true, toolbarHtml: 'ignored', emptyDisplay: 'none' },
  toolbarElement: null,
  tbody: tbody3,
  emptyElement: empty3
}), true);
assert.strictEqual(tbody3.innerHTML, 'keep');
assert.strictEqual(empty3.style.display, 'none');
console.log('SERVICE_TABLE_DOM_STATE_UNIT=OK');
"""
subprocess.run(['node', '-e', node_test], check=True)
subprocess.run(['node', '--check', 'assets/js/app-services-view.js'], check=True)
subprocess.run(['node', '--check', 'assets/js/app-services-selection.js'], check=True)
subprocess.run(['node', '--check', 'sw.js'], check=True)
subprocess.run(['git', 'diff', '--check'], check=True)

print('RENDERIZAR_SERVICOS_BEFORE_CHARS=', len(before))
print('RENDERIZAR_SERVICOS_AFTER_CHARS=', len(block))
print('RENDERIZAR_SERVICOS_AFTER_LINES=', len(block.splitlines()))
print('STRUCTURE=OK')
