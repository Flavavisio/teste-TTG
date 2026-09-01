from pathlib import Path
import subprocess

app_path = Path('app.html')
view_path = Path('assets/js/app-services-view.js')
sw_path = Path('sw.js')

view = view_path.read_text(encoding='utf-8')
anchor = """  function specialtyAndHistoryNotice(options) {
"""
assert view.count(anchor) == 1, view.count(anchor)
assert 'function serviceHistoryLoadedSinceLabel(value)' not in view
helper = """  function serviceHistoryLoadedSinceLabel(value) {
    if (!value) return '—';
    return new Date(value + 'T00:00:00').toLocaleDateString('pt-PT');
  }

"""
view = view.replace(anchor, helper + anchor, 1)
export_old = '  window.TotalGestServicesView = { specialtyAndHistoryNotice, servicesTableState, statusControl, serviceStatusControl, workSheetActions, rowLeadingCells, primaryRowActions, erpRowActions, rowActions, serviceRow };'
export_new = '  window.TotalGestServicesView = { serviceHistoryLoadedSinceLabel, specialtyAndHistoryNotice, servicesTableState, statusControl, serviceStatusControl, workSheetActions, rowLeadingCells, primaryRowActions, erpRowActions, rowActions, serviceRow };'
assert view.count(export_old) == 1, view.count(export_old)
view = view.replace(export_old, export_new, 1)
view_path.write_text(view, encoding='utf-8')

app = app_path.read_text(encoding='utf-8')
function_marker = '        function renderizarServicos() {'
assert app.count(function_marker) == 1, app.count(function_marker)
start = app.index(function_marker)
end = app.index('\n        function ', start + len(function_marker))
before = app[start:end]
old_label = """                    loadedSinceLabel: _servicosCarregadoDesde
                        ? new Date(_servicosCarregadoDesde + 'T00:00:00').toLocaleDateString('pt-PT')
                        : '—'
"""
new_label = """                    loadedSinceLabel: window.TotalGestServicesView.serviceHistoryLoadedSinceLabel(_servicosCarregadoDesde)
"""
assert before.count(old_label) == 1, before.count(old_label)
app = app.replace(old_label, new_label, 1)
app_path.write_text(app, encoding='utf-8')

sw = sw_path.read_text(encoding='utf-8')
assert sw.count("const CACHE = 'totalgest-v138';") == 1, sw.count("const CACHE = 'totalgest-v138';")
sw = sw.replace("const CACHE = 'totalgest-v138';", "const CACHE = 'totalgest-v139';", 1)
sw_path.write_text(sw, encoding='utf-8')

final_app = app_path.read_text(encoding='utf-8')
start = final_app.index(function_marker)
end = final_app.index('\n        function ', start + len(function_marker))
block = final_app[start:end]
assert block.count('serviceHistoryLoadedSinceLabel(_servicosCarregadoDesde)') == 1
assert "new Date(_servicosCarregadoDesde + 'T00:00:00')" not in block
for marker in ['selectVisibleServices({', 'selectPendingSpecialtyServices({', 'filterAndSortServices({', 'servicesTableState({', 'serviceStatusControl({', 'prepareServiceRow({', 'serviceRow({']:
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
assert.strictEqual(view.serviceHistoryLoadedSinceLabel(''), '—');
assert.strictEqual(view.serviceHistoryLoadedSinceLabel(null), '—');
const value = '2026-09-01';
const expected = new Date(value + 'T00:00:00').toLocaleDateString('pt-PT');
assert.strictEqual(view.serviceHistoryLoadedSinceLabel(value), expected);
console.log('SERVICE_HISTORY_LABEL_UNIT=OK');
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
