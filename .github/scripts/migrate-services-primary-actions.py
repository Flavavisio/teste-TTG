from pathlib import Path

app_path = Path('app.html')
sw_path = Path('sw.js')
app = app_path.read_text(encoding='utf-8')
sw = sw_path.read_text(encoding='utf-8')

fn_start = app.index('        function renderizarServicos() {')
fn_end = app.index('\n        function ', fn_start + 1)
before = app[fn_start:fn_end]

protected_global = {
    'bootstrapSupabase()': app.count('bootstrapSupabase()'),
    'supabase.auth': app.count('supabase.auth'),
}
protected_services = {
    'window.TotalGestServicesSelection.selectVisibleServices({': before.count('window.TotalGestServicesSelection.selectVisibleServices({'),
    'window.TotalGestServicesView.specialtyAndHistoryNotice({': before.count('window.TotalGestServicesView.specialtyAndHistoryNotice({'),
    'window.TotalGestServicesView.statusControl({': before.count('window.TotalGestServicesView.statusControl({'),
    'window.TotalGestServicesView.workSheetActions({': before.count('window.TotalGestServicesView.workSheetActions({'),
    'window.TotalGestServicesView.rowLeadingCells({': before.count('window.TotalGestServicesView.rowLeadingCells({'),
    'faturarOSViaTOConline(': before.count('faturarOSViaTOConline('),
    'faturarOSViaMoloni(': before.count('faturarOSViaMoloni('),
    '_verificarPagamentoMoloni(': before.count('_verificarPagamentoMoloni('),
    'emitirGuiaTransporteMoloni(': before.count('emitirGuiaTransporteMoloni('),
    'emitirNotaCreditoMoloni(': before.count('emitirNotaCreditoMoloni('),
    "excluirEntidade('servico'": before.count("excluirEntidade('servico'"),
}
for key, value in protected_services.items():
    assert value == 1, (key, value)

start_marker = '                                    <button class="btn btn-sm" style="background:#334155;color:#fff;" onclick="abrirVerOS(\'${s.id}\')" title="Ver OS — folhas de obra e materiais"><i class="fas fa-eye"></i> Ver OS</button>'
end_marker = '                                        ${(() => {'
start = before.index(start_marker)
end = before.index(end_marker, start)
old_region = before[start:end]

for token in [
    'abrirVerOS(', 'aprovarAssistencia(', 'rejeitarAssistencia(',
    "abrirModal('servico'", 'finalizarEGerarReportOS(',
    'gerarRelatorioOSIndividual(', '_pagoTogglarOS('
]:
    assert token in old_region, token
for token in ['faturarOSViaTOConline(', 'faturarOSViaMoloni(', '_verificarPagamentoMoloni(']:
    assert token not in old_region, token

replacement = """                                    ${window.TotalGestServicesView.primaryRowActions({
                                        serviceId: s.id,
                                        status: s.status,
                                        role: usuarioLogado?.role || '',
                                        localPayment: s.pagamentoLocal === true,
                                        paid: s.pago === true,
                                        receiptMoloniId: s.reciboMoloniId || ''
                                    })}
"""

after = before[:start] + replacement + before[end:]
assert after.count('window.TotalGestServicesView.primaryRowActions({') == 1
for token in [
    'abrirVerOS(', 'aprovarAssistencia(', 'rejeitarAssistencia(',
    "abrirModal('servico'", 'finalizarEGerarReportOS(',
    'gerarRelatorioOSIndividual(', '_pagoTogglarOS('
]:
    assert after.count(token) == 0, (token, after.count(token))
for key, value in protected_services.items():
    assert after.count(key) == value, (key, value, after.count(key))

app = app[:fn_start] + after + app[fn_end:]
for key, value in protected_global.items():
    assert app.count(key) == value, (key, value, app.count(key))

assert "const CACHE = 'totalgest-v130';" in sw
sw = sw.replace("const CACHE = 'totalgest-v130';", "const CACHE = 'totalgest-v131';", 1)

app_path.write_text(app, encoding='utf-8')
sw_path.write_text(sw, encoding='utf-8')
print(f'RENDERIZAR_SERVICOS_AFTER chars={len(after)} lines={len(after.splitlines())}')
print('SERVICES_PRIMARY_ACTIONS_MIGRATION=OK')
