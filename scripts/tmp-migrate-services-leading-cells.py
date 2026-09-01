from pathlib import Path
import subprocess

app_path = Path('app.html')
view_path = Path('assets/js/app-services-view.js')
sw_path = Path('sw.js')

view = view_path.read_text(encoding='utf-8')
anchor = """  function serviceRow(options) {
"""
assert view.count(anchor) == 1, view.count(anchor)
assert 'function serviceRowFromData(options)' not in view
helper = """  function serviceRowFromData(options) {
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
view = view.replace(anchor, helper + anchor, 1)
export_old = '  window.TotalGestServicesView = { serviceHistoryLoadedSinceLabel, specialtyAndHistoryNotice, servicesTableState, statusControl, serviceStatusControl, workSheetActions, rowLeadingCells, primaryRowActions, erpRowActions, rowActions, serviceRow };'
export_new = '  window.TotalGestServicesView = { serviceHistoryLoadedSinceLabel, specialtyAndHistoryNotice, servicesTableState, statusControl, serviceStatusControl, workSheetActions, rowLeadingCells, primaryRowActions, erpRowActions, rowActions, serviceRowFromData, serviceRow };'
assert view.count(export_old) == 1, view.count(export_old)
view = view.replace(export_old, export_new, 1)
view_path.write_text(view, encoding='utf-8')

app = app_path.read_text(encoding='utf-8')
function_marker = '        function renderizarServicos() {'
assert app.count(function_marker) == 1, app.count(function_marker)
start = app.index(function_marker)
end = app.index('\n        function ', start + len(function_marker))
before = app[start:end]
old_leading = """                return window.TotalGestServicesView.serviceRow({
                    leadingCells: {
                        number: rowData.number,
                        hasMaterials: rowData.hasMaterials,
                        clientName: rowData.clientName,
                        employeeName: rowData.employeeName,
                        date: s.data || '-',
                        time: s.hora || '-',
                        description: escapeHtmlSimples(s.descricao || '-'),
                        workTypesHtml: _tiposTrabalhoBadgesHTML(s),
                        statusHtml
                    },
                    actions: {
"""
new_leading = """                return window.TotalGestServicesView.serviceRowFromData({
                    service: s,
                    rowData,
                    descriptionHtml: escapeHtmlSimples(s.descricao || '-'),
                    workTypesHtml: _tiposTrabalhoBadgesHTML(s),
                    statusHtml,
                    actions: {
"""
assert before.count(old_leading) == 1, before.count(old_leading)
actions_start = before.index('                    actions: {', before.index(old_leading))
actions_end = before.index('\n                });', actions_start)
actions_before = before[actions_start:actions_end]
app = app.replace(old_leading, new_leading, 1)
app_path.write_text(app, encoding='utf-8')

sw = sw_path.read_text(encoding='utf-8')
assert sw.count("const CACHE = 'totalgest-v139';") == 1, sw.count("const CACHE = 'totalgest-v139';")
sw = sw.replace("const CACHE = 'totalgest-v139';", "const CACHE = 'totalgest-v140';", 1)
sw_path.write_text(sw, encoding='utf-8')

final_app = app_path.read_text(encoding='utf-8')
start = final_app.index(function_marker)
end = final_app.index('\n        function ', start + len(function_marker))
block = final_app[start:end]
assert block.count('serviceRowFromData({') == 1
assert block.count('serviceRow({') == 0
assert block.count('leadingCells: {') == 0
assert block.count('actions: {') == 1
for marker in ['selectVisibleServices({', 'selectPendingSpecialtyServices({', 'filterAndSortServices({', 'servicesTableState({', 'serviceStatusControl({', 'prepareServiceRow({']:
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
const actions = { serviceId: 'svc-1', role: 'funcionario', status: 'pendente' };
const leadingCells = {
  number: 'OS-1',
  hasMaterials: true,
  clientName: 'Cliente',
  employeeName: 'Técnico',
  date: '2026-09-01',
  time: '10:00',
  description: 'Teste',
  workTypesHtml: '<span>Tipo</span>',
  statusHtml: '<span>pendente</span>'
};
const expected = view.serviceRow({ leadingCells, actions });
const actual = view.serviceRowFromData({
  service: { data: '2026-09-01', hora: '10:00' },
  rowData: { number: 'OS-1', hasMaterials: true, clientName: 'Cliente', employeeName: 'Técnico' },
  descriptionHtml: 'Teste',
  workTypesHtml: '<span>Tipo</span>',
  statusHtml: '<span>pendente</span>',
  actions
});
assert.strictEqual(actual, expected);
const expectedDefaults = view.serviceRow({
  leadingCells: { number: 'OS-2', date: '-', time: '-', description: '-', workTypesHtml: '', statusHtml: '' },
  actions
});
const actualDefaults = view.serviceRowFromData({
  service: {},
  rowData: { number: 'OS-2' },
  descriptionHtml: '-',
  workTypesHtml: '',
  statusHtml: '',
  actions
});
assert.strictEqual(actualDefaults, expectedDefaults);
console.log('SERVICE_LEADING_CELLS_UNIT=OK');
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
