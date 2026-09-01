from pathlib import Path
import subprocess

app_path = Path('app.html')
view_path = Path('assets/js/app-services-view.js')
sw_path = Path('sw.js')

view = view_path.read_text(encoding='utf-8')
export_old = '  window.TotalGestServicesView = { specialtyAndHistoryNotice, servicesTableState, statusControl, workSheetActions, rowLeadingCells, primaryRowActions, erpRowActions, rowActions };'
export_new = '  window.TotalGestServicesView = { specialtyAndHistoryNotice, servicesTableState, statusControl, workSheetActions, rowLeadingCells, primaryRowActions, erpRowActions, rowActions, serviceRow };'
assert view.count(export_old) == 1, view.count(export_old)
assert 'function serviceRow(options)' not in view
helper = """  function serviceRow(options) {
    const opts = options || {};
    return `<tr>${rowLeadingCells(opts.leadingCells || {})}${rowActions(opts.actions || {})}</tr>`;
  }

"""
view = view.replace(export_old, helper + export_new)
view_path.write_text(view, encoding='utf-8')

app = app_path.read_text(encoding='utf-8')
function_marker = '        function renderizarServicos() {'
assert app.count(function_marker) == 1, app.count(function_marker)
start = app.index(function_marker)
end = app.index('\n        function ', start + len(function_marker))
before = app[start:end]

dead_block = """                const folhaOS = s.status === 'concluído' ? dados.folhasObra?.find(f => f.servicoId === s.id) : null;
                const btnCriarFolha = window.TotalGestServicesView.workSheetActions({
                    serviceId: s.id,
                    status: s.status,
                    sheetId: folhaOS?.id || '',
                    workId: s.obraId || ''
                });
"""
assert before.count(dead_block) == 1, before.count(dead_block)
app = app.replace(dead_block, '', 1)

old_return = """                return `
                        <tr>
                            ${window.TotalGestServicesView.rowLeadingCells({
                                number: rowData.number,
                                hasMaterials: rowData.hasMaterials,
                                clientName: rowData.clientName,
                                employeeName: rowData.employeeName,
                                date: s.data || '-',
                                time: s.hora || '-',
                                description: escapeHtmlSimples(s.descricao || '-'),
                                workTypesHtml: _tiposTrabalhoBadgesHTML(s),
                                statusHtml
                            })}
                            ${window.TotalGestServicesView.rowActions({
                                serviceId: s.id,
                                status: s.status,
                                role: usuarioLogado?.role || '',
                                localPayment: s.pagamentoLocal === true,
                                paid: s.pago === true,
                                receiptMoloniId: s.reciboMoloniId || '',
                                canManage: usuarioLogado?.role === 'admin' || usuarioLogado?.role === 'subadmin',
                                hasValue: s.valor != null,
                                erpActive: rowData.erpActive,
                                provider: rowData.provider,
                                invoiceTOId: s.faturaTOConlineId || '',
                                invoiceMoloniId: s.faturaMoloniId || '',
                                invoiceMoloniUrl: s.faturaMoloniUrl || '',
                                receiptMoloniUrl: s.reciboMoloniUrl || '',
                                guideMoloniId: s.guiaMoloniId || '',
                                guideMoloniUrl: s.guiaMoloniUrl || '',
                                creditNoteMoloniId: s.notaCreditoMoloniId || '',
                                creditNoteMoloniUrl: s.notaCreditoMoloniUrl || ''
                            })}
                        </tr>
                    `;"""
new_return = """                return window.TotalGestServicesView.serviceRow({
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
                        serviceId: s.id,
                        status: s.status,
                        role: usuarioLogado?.role || '',
                        localPayment: s.pagamentoLocal === true,
                        paid: s.pago === true,
                        receiptMoloniId: s.reciboMoloniId || '',
                        canManage: usuarioLogado?.role === 'admin' || usuarioLogado?.role === 'subadmin',
                        hasValue: s.valor != null,
                        erpActive: rowData.erpActive,
                        provider: rowData.provider,
                        invoiceTOId: s.faturaTOConlineId || '',
                        invoiceMoloniId: s.faturaMoloniId || '',
                        invoiceMoloniUrl: s.faturaMoloniUrl || '',
                        receiptMoloniUrl: s.reciboMoloniUrl || '',
                        guideMoloniId: s.guiaMoloniId || '',
                        guideMoloniUrl: s.guiaMoloniUrl || '',
                        creditNoteMoloniId: s.notaCreditoMoloniId || '',
                        creditNoteMoloniUrl: s.notaCreditoMoloniUrl || ''
                    }
                });"""
current = app[start:end]
assert current.count(old_return) == 1, current.count(old_return)
app = app.replace(old_return, new_return, 1)
app_path.write_text(app, encoding='utf-8')

sw = sw_path.read_text(encoding='utf-8')
assert sw.count("const CACHE = 'totalgest-v136';") == 1, sw.count("const CACHE = 'totalgest-v136';")
sw = sw.replace("const CACHE = 'totalgest-v136';", "const CACHE = 'totalgest-v137';")
sw_path.write_text(sw, encoding='utf-8')

final_app = app_path.read_text(encoding='utf-8')
start = final_app.index(function_marker)
end = final_app.index('\n        function ', start + len(function_marker))
block = final_app[start:end]
assert block.count('serviceRow({') == 1
for marker in ['workSheetActions({', 'rowLeadingCells({', 'rowActions({', 'const folhaOS =', 'const btnCriarFolha =']:
    assert block.count(marker) == 0, (marker, block.count(marker))
for marker in ['statusControl({', 'prepareServiceRow({', 'filterAndSortServices({', 'servicesTableState({']:
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
const html = view.serviceRow({
  leadingCells: {
    number: 'OS-1', clientName: 'Cliente', employeeName: 'Todos', date: '2026-09-01', time: '10:00', description: 'Teste', statusHtml: '<span>pendente</span>'
  },
  actions: { serviceId: 'svc-1', role: 'funcionario', status: 'pendente' }
});
assert.ok(html.startsWith('<tr><td><strong>OS-1</strong>'));
assert.ok(html.includes("abrirVerOS('svc-1')"));
assert.ok(html.endsWith('</td></tr>'));
console.log('SERVICE_ROW_UNIT=OK');
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
