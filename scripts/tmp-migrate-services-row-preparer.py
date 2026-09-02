from pathlib import Path
import subprocess

app_path = Path('app.html')
selection_path = Path('assets/js/app-services-selection.js')
sw_path = Path('sw.js')

selection = selection_path.read_text(encoding='utf-8')
anchor = """  function filterAndSortServices(options) {
"""
assert selection.count(anchor) == 1, selection.count(anchor)
assert 'function createServiceRowPreparer(options)' not in selection
helper = """  function createServiceRowPreparer(options) {
    options = options || {};
    return function (service) {
      return prepareServiceRow({
        service: service || {},
        administrators: options.administrators,
        getEmployeeName: options.getEmployeeName,
        getClientName: options.getClientName,
        generateNumber: options.generateNumber,
        hasMaterials: options.hasMaterials,
        isErpActive: options.isErpActive
      });
    };
  }

"""
selection = selection.replace(anchor, helper + anchor, 1)
export_old = """    prepareServiceRow: prepareServiceRow,
    filterAndSortServices: filterAndSortServices
"""
export_new = """    prepareServiceRow: prepareServiceRow,
    createServiceRowPreparer: createServiceRowPreparer,
    filterAndSortServices: filterAndSortServices
"""
assert selection.count(export_old) == 1, selection.count(export_old)
selection = selection.replace(export_old, export_new, 1)
selection_path.write_text(selection, encoding='utf-8')

app = app_path.read_text(encoding='utf-8')
function_marker = '        function renderizarServicos() {'
assert app.count(function_marker) == 1, app.count(function_marker)
start = app.index(function_marker)
end = app.index('\n        function ', start + len(function_marker))
before = app[start:end]
old = """            tbody.innerHTML = servicos.map(s => {
                const rowData = window.TotalGestServicesSelection.prepareServiceRow({
                    service: s,
                    administrators: dados.administradores || [],
                    getEmployeeName: obterNomeFuncionario,
                    getClientName: obterNomeCliente,
                    generateNumber: gerarNumeroRegisto,
                    hasMaterials: _osTemMateriais,
                    isErpActive: moduloErpAtivo
                });
"""
new = """            const prepareRow = window.TotalGestServicesSelection.createServiceRowPreparer({
                administrators: dados.administradores || [],
                getEmployeeName: obterNomeFuncionario,
                getClientName: obterNomeCliente,
                generateNumber: gerarNumeroRegisto,
                hasMaterials: _osTemMateriais,
                isErpActive: moduloErpAtivo
            });
            tbody.innerHTML = servicos.map(s => {
                const rowData = prepareRow(s);
"""
assert before.count(old) == 1, before.count(old)
actions_start = before.index('                    actions: {')
actions_end = before.index('\n                });', actions_start)
actions_before = before[actions_start:actions_end]
app = app.replace(old, new, 1)
app_path.write_text(app, encoding='utf-8')

sw = sw_path.read_text(encoding='utf-8')
assert sw.count("const CACHE = 'totalgest-v142';") == 1, sw.count("const CACHE = 'totalgest-v142';")
sw = sw.replace("const CACHE = 'totalgest-v142';", "const CACHE = 'totalgest-v143';", 1)
sw_path.write_text(sw, encoding='utf-8')

final_app = app_path.read_text(encoding='utf-8')
start = final_app.index(function_marker)
end = final_app.index('\n        function ', start + len(function_marker))
block = final_app[start:end]
assert block.count('createServiceRowPreparer({') == 1
assert block.count('prepareServiceRow({') == 0
assert block.count('const rowData = prepareRow(s);') == 1
assert block.count('actions: {') == 1
for marker in ['selectVisibleServices({', 'selectPendingSpecialtyServices({', 'filterAndSortServices({', 'servicesTableState({', 'applyServicesTableState({', 'serviceRowFromData({']:
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
vm.runInContext(fs.readFileSync('assets/js/app-services-selection.js', 'utf8'), context);
const selection = context.window.TotalGestServicesSelection;
const administrators = [
  { id: 'admin-1', integracaoFaturacao: { provider: 'moloni' } },
  { id: 'admin-2', integracaoFaturacao: { provider: 'toconline' } }
];
const options = {
  administrators,
  getEmployeeName: id => ({ e1: 'Ana', e2: 'Bruno' }[id] || id),
  getClientName: id => ({ c1: 'Cliente A' }[id] || id),
  generateNumber: () => 'OS-GERADA',
  hasMaterials: id => id === 'svc-1',
  isErpActive: administrator => administrator?.id === 'admin-1'
};
const service = {
  id: 'svc-1',
  adminId: 'admin-1',
  clienteId: 'c1',
  funcionariosIds: ['e1', 'e2'],
  numeroRegisto: ''
};
const expected = selection.prepareServiceRow({ service, ...options });
const prepareRow = selection.createServiceRowPreparer(options);
const actual = prepareRow(service);
assert.deepStrictEqual(JSON.parse(JSON.stringify(actual)), JSON.parse(JSON.stringify(expected)));
assert.strictEqual(actual.employeeName, 'Ana<br>Bruno');
assert.strictEqual(actual.number, 'OS-GERADA');
assert.strictEqual(actual.hasMaterials, true);
assert.strictEqual(actual.erpActive, true);
assert.strictEqual(actual.provider, 'moloni');

const emptyExpected = selection.prepareServiceRow({ service: {} });
const emptyActual = selection.createServiceRowPreparer()();
assert.deepStrictEqual(JSON.parse(JSON.stringify(emptyActual)), JSON.parse(JSON.stringify(emptyExpected)));
console.log('SERVICE_ROW_PREPARER_UNIT=OK');
"""
subprocess.run(['node', '-e', node_test], check=True)
subprocess.run(['node', '--check', 'assets/js/app-services-selection.js'], check=True)
subprocess.run(['node', '--check', 'assets/js/app-services-view.js'], check=True)
subprocess.run(['node', '--check', 'sw.js'], check=True)
subprocess.run(['git', 'diff', '--check'], check=True)

print('ACTIONS_SEGMENT_UNCHANGED=OK')
print('RENDERIZAR_SERVICOS_BEFORE_CHARS=', len(before))
print('RENDERIZAR_SERVICOS_AFTER_CHARS=', len(block))
print('RENDERIZAR_SERVICOS_AFTER_LINES=', len(block.splitlines()))
print('STRUCTURE=OK')
