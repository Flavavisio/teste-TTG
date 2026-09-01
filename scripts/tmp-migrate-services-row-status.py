from pathlib import Path
import subprocess

app_path = Path('app.html')
view_path = Path('assets/js/app-services-view.js')
sw_path = Path('sw.js')

view = view_path.read_text(encoding='utf-8')
old_helper = """  function serviceRowFromData(options) {
    const opts = options || {};
    const service = opts.service || {};
    const rowData = opts.rowData || {};
    return serviceRow({
      leadingCells: {
        number: rowData.number,
        hasMaterials: rowData.hasMaterials,
        clientName: rowData.clientName,
        employeeName: rowData.employeeName,
        date: service.data || '-',
        time: service.hora || '-',
        description: opts.descriptionHtml || '-',
        workTypesHtml: opts.workTypesHtml,
        statusHtml: opts.statusHtml
      },
      actions: opts.actions || {}
    });
  }
"""
new_helper = """  function serviceRowFromData(options) {
    const opts = options || {};
    const service = opts.service || {};
    const rowData = opts.rowData || {};
    const statusHtml = opts.statusHtml != null ? opts.statusHtml : serviceStatusControl({
      serviceId: service.id || '',
      status: service.status || 'pendente',
      role: opts.role || '',
      badgeClass: opts.badgeClass || ''
    });
    return serviceRow({
      leadingCells: {
        number: rowData.number,
        hasMaterials: rowData.hasMaterials,
        clientName: rowData.clientName,
        employeeName: rowData.employeeName,
        date: service.data || '-',
        time: service.hora || '-',
        description: opts.descriptionHtml || '-',
        workTypesHtml: opts.workTypesHtml,
        statusHtml
      },
      actions: opts.actions || {}
    });
  }
"""
assert view.count(old_helper) == 1, view.count(old_helper)
view = view.replace(old_helper, new_helper, 1)
view_path.write_text(view, encoding='utf-8')

app = app_path.read_text(encoding='utf-8')
function_marker = '        function renderizarServicos() {'
assert app.count(function_marker) == 1, app.count(function_marker)
start = app.index(function_marker)
end = app.index('\n        function ', start + len(function_marker))
before = app[start:end]

old_status = """                const statusHtml = window.TotalGestServicesView.serviceStatusControl({
                    serviceId: s.id,
                    status: s.status || 'pendente',
                    role: usuarioLogado?.role || '',
                    badgeClass: statusBadge(s.status)
                });
"""
assert before.count(old_status) == 1, before.count(old_status)
app = app.replace(old_status, '', 1)

old_row = """                return window.TotalGestServicesView.serviceRowFromData({
                    service: s,
                    rowData,
                    descriptionHtml: escapeHtmlSimples(s.descricao || '-'),
                    workTypesHtml: _tiposTrabalhoBadgesHTML(s),
                    statusHtml,
                    actions: {
"""
new_row = """                return window.TotalGestServicesView.serviceRowFromData({
                    service: s,
                    rowData,
                    role: usuarioLogado?.role || '',
                    badgeClass: statusBadge(s.status),
                    descriptionHtml: escapeHtmlSimples(s.descricao || '-'),
                    workTypesHtml: _tiposTrabalhoBadgesHTML(s),
                    actions: {
"""
assert before.count(old_row) == 1, before.count(old_row)
actions_start = before.index('                    actions: {', before.index(old_row))
actions_end = before.index('\n                });', actions_start)
actions_before = before[actions_start:actions_end]
app = app.replace(old_row, new_row, 1)
app_path.write_text(app, encoding='utf-8')

sw = sw_path.read_text(encoding='utf-8')
assert sw.count("const CACHE = 'totalgest-v141';") == 1, sw.count("const CACHE = 'totalgest-v141';")
sw = sw.replace("const CACHE = 'totalgest-v141';", "const CACHE = 'totalgest-v142';", 1)
sw_path.write_text(sw, encoding='utf-8')

final_app = app_path.read_text(encoding='utf-8')
start = final_app.index(function_marker)
end = final_app.index('\n        function ', start + len(function_marker))
block = final_app[start:end]
assert block.count('serviceRowFromData({') == 1
assert block.count('serviceStatusControl({') == 0
assert block.count('const statusHtml =') == 0
assert block.count('role: usuarioLogado?.role ||') >= 1
assert block.count('badgeClass: statusBadge(s.status)') == 1
assert block.count('actions: {') == 1
for marker in ['selectVisibleServices({', 'selectPendingSpecialtyServices({', 'filterAndSortServices({', 'servicesTableState({', 'applyServicesTableState({', 'prepareServiceRow({']:
    assert block.count(marker) == 1, (marker, block.count(marker))
for marker in ['invoiceTOId:', 'invoiceMoloniId:', 'invoiceMoloniUrl:', 'receiptMoloniUrl:', 'guideMoloniId:', 'guideMoloniUrl:', 'creditNoteMoloniId:', 'creditNoteMoloniUrl:']:
    assert block.count(marker) == 1, (marker, block.count(marker))
actions_start_after = block.index('                    actions: {')
actions_end_after = block.index('\n                });', actions_start_after)
actions_after = block[actions_start_after:actions_end_after]
assert actions_after == actions_before
assert len(block) < len(before), (len(before), len(block))

node_test = r"""
const fs = require('fs');
const vm = require('vm');
const assert = require('assert');
const context = { window: {} };
vm.createContext(context);
vm.runInContext(fs.readFileSync('assets/js/app-services-view.js', 'utf8'), context);
const view = context.window.TotalGestServicesView;
const service = { id: 'svc-1', status: 'pendente', data: '2026-09-01', hora: '10:00' };
const rowData = { number: 'OS-1', hasMaterials: false, clientName: 'Cliente', employeeName: 'Técnico' };
const actions = { serviceId: 'svc-1', role: 'funcionario', status: 'pendente' };
const expectedStatus = view.serviceStatusControl({ serviceId: 'svc-1', status: 'pendente', role: 'admin', badgeClass: 'badge-pendente' });
const expected = view.serviceRowFromData({
  service,
  rowData,
  descriptionHtml: 'Descrição',
  workTypesHtml: '<span>Tipo</span>',
  statusHtml: expectedStatus,
  actions
});
const actual = view.serviceRowFromData({
  service,
  rowData,
  role: 'admin',
  badgeClass: 'badge-pendente',
  descriptionHtml: 'Descrição',
  workTypesHtml: '<span>Tipo</span>',
  actions
});
assert.strictEqual(actual, expected);
assert.ok(actual.includes('<select class="status-select"'));
const completed = view.serviceRowFromData({
  service: { id: 'svc-2', status: 'concluído' },
  rowData: { number: 'OS-2' },
  role: 'admin',
  badgeClass: 'badge-concluido',
  descriptionHtml: '-',
  workTypesHtml: '',
  actions: { serviceId: 'svc-2', role: 'funcionario', status: 'pendente' }
});
assert.ok(completed.includes('<span class="badge-concluido">concluído</span>'));
assert.ok(!completed.includes('<select class="status-select"'));
console.log('SERVICE_ROW_STATUS_UNIT=OK');
"""
subprocess.run(['node', '-e', node_test], check=True)
subprocess.run(['node', '--check', 'assets/js/app-services-view.js'], check=True)
subprocess.run(['node', '--check', 'assets/js/app-services-selection.js'], check=True)
subprocess.run(['node', '--check', 'sw.js'], check=True)
subprocess.run(['git', 'diff', '--check'], check=True)

print('ACTIONS_SEGMENT_UNCHANGED=OK')
print('RENDERIZAR_SERVICOS_BEFORE_CHARS=', len(before))
print('RENDERIZAR_SERVICOS_AFTER_CHARS=', len(block))
print('RENDERIZAR_SERVICOS_AFTER_LINES=', len(block.splitlines()))
print('STRUCTURE=OK')
