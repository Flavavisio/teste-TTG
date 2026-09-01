from pathlib import Path
import subprocess

app_path = Path('app.html')
view_path = Path('assets/js/app-services-view.js')
sw_path = Path('sw.js')

view = view_path.read_text(encoding='utf-8')
status_anchor = """  function workSheetActions(options) {
"""
assert view.count(status_anchor) == 1, view.count(status_anchor)
assert 'function serviceStatusControl(options)' not in view
helper = """  function serviceStatusControl(options) {
    const opts = options || {};
    const role = opts.role || '';
    return statusControl({
      serviceId: opts.serviceId || '',
      status: opts.status || 'pendente',
      canEdit: role === 'admin' || role === 'subadmin' || role === 'encarregado',
      badgeClass: opts.badgeClass || ''
    });
  }

"""
view = view.replace(status_anchor, helper + status_anchor, 1)
export_old = '  window.TotalGestServicesView = { specialtyAndHistoryNotice, servicesTableState, statusControl, workSheetActions, rowLeadingCells, primaryRowActions, erpRowActions, rowActions, serviceRow };'
export_new = '  window.TotalGestServicesView = { specialtyAndHistoryNotice, servicesTableState, statusControl, serviceStatusControl, workSheetActions, rowLeadingCells, primaryRowActions, erpRowActions, rowActions, serviceRow };'
assert view.count(export_old) == 1, view.count(export_old)
view = view.replace(export_old, export_new, 1)
view_path.write_text(view, encoding='utf-8')

app = app_path.read_text(encoding='utf-8')
function_marker = '        function renderizarServicos() {'
assert app.count(function_marker) == 1, app.count(function_marker)
start = app.index(function_marker)
end = app.index('\n        function ', start + len(function_marker))
before = app[start:end]
old_status = """                const podeEditar = usuarioLogado?.role === 'admin' || usuarioLogado?.role === 'subadmin' || usuarioLogado?.role === 'encarregado';
                const statusHtml = window.TotalGestServicesView.statusControl({
                    serviceId: s.id,
                    status: s.status || 'pendente',
                    canEdit: podeEditar,
                    badgeClass: statusBadge(s.status)
                });
"""
new_status = """                const statusHtml = window.TotalGestServicesView.serviceStatusControl({
                    serviceId: s.id,
                    status: s.status || 'pendente',
                    role: usuarioLogado?.role || '',
                    badgeClass: statusBadge(s.status)
                });
"""
assert before.count(old_status) == 1, before.count(old_status)
app = app.replace(old_status, new_status, 1)
app_path.write_text(app, encoding='utf-8')

sw = sw_path.read_text(encoding='utf-8')
assert sw.count("const CACHE = 'totalgest-v137';") == 1, sw.count("const CACHE = 'totalgest-v137';")
sw = sw.replace("const CACHE = 'totalgest-v137';", "const CACHE = 'totalgest-v138';", 1)
sw_path.write_text(sw, encoding='utf-8')

final_app = app_path.read_text(encoding='utf-8')
start = final_app.index(function_marker)
end = final_app.index('\n        function ', start + len(function_marker))
block = final_app[start:end]
assert block.count('serviceStatusControl({') == 1
assert block.count('statusControl({') == 0
assert 'const podeEditar =' not in block
for marker in ['prepareServiceRow({', 'filterAndSortServices({', 'servicesTableState({', 'serviceRow({']:
    assert block.count(marker) == 1, (marker, block.count(marker))
for marker in ['workSheetActions({', 'rowLeadingCells({', 'rowActions({', 'const folhaOS =', 'const btnCriarFolha =']:
    assert block.count(marker) == 0, (marker, block.count(marker))
assert len(block) < len(before), (len(before), len(block))

node_test = r"""
const fs = require('fs');
const vm = require('vm');
const assert = require('assert');
const context = { window: {} };
vm.createContext(context);
vm.runInContext(fs.readFileSync('assets/js/app-services-view.js', 'utf8'), context);
const view = context.window.TotalGestServicesView;
for (const role of ['admin', 'subadmin', 'encarregado']) {
  const html = view.serviceStatusControl({ serviceId: 'svc-1', status: 'pendente', role, badgeClass: 'badge-pendente' });
  assert.ok(html.startsWith('<select class="status-select"'));
  assert.ok(html.includes("alterarStatusOS('svc-1'"));
}
const employeeHtml = view.serviceStatusControl({ serviceId: 'svc-1', status: 'pendente', role: 'funcionario', badgeClass: 'badge-pendente' });
assert.strictEqual(employeeHtml, '<span class="badge-pendente">pendente</span>');
const approvalHtml = view.serviceStatusControl({ serviceId: 'svc-2', status: 'por aprovar', role: 'admin', badgeClass: 'ignored' });
assert.ok(approvalHtml.includes('por aprovar'));
assert.ok(!approvalHtml.includes('<select'));
const completedHtml = view.serviceStatusControl({ serviceId: 'svc-3', status: 'concluído', role: 'admin', badgeClass: 'badge-done' });
assert.strictEqual(completedHtml, '<span class="badge-done">concluído</span>');
console.log('SERVICE_STATUS_CONTROL_UNIT=OK');
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
