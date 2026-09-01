from pathlib import Path

app_path = Path('app.html')
sw_path = Path('sw.js')
app = app_path.read_text(encoding='utf-8')
sw = sw_path.read_text(encoding='utf-8')

protected = {
    'bootstrapSupabase()': app.count('bootstrapSupabase()'),
    'supabase.auth': app.count('supabase.auth'),
    'faturarOSViaTOConline(': app.count('faturarOSViaTOConline('),
    'faturarOSViaMoloni(': app.count('faturarOSViaMoloni('),
    '_verificarPagamentoMoloni(': app.count('_verificarPagamentoMoloni('),
    'emitirGuiaTransporteMoloni(': app.count('emitirGuiaTransporteMoloni('),
    'emitirNotaCreditoMoloni(': app.count('emitirNotaCreditoMoloni('),
    'tbody.innerHTML = servicos.map(': app.count('tbody.innerHTML = servicos.map('),
    'window.TotalGestServicesSelection.selectVisibleServices({': app.count('window.TotalGestServicesSelection.selectVisibleServices({'),
    'window.TotalGestServicesView.specialtyAndHistoryNotice({': app.count('window.TotalGestServicesView.specialtyAndHistoryNotice({'),
}

func_start = app.index('        function renderizarServicos() {')
func_end = app.index('\n        function ', func_start + 1)
block = app[func_start:func_end]

start_marker = "                const podeEditar = usuarioLogado?.role === 'admin' || usuarioLogado?.role === 'subadmin' || usuarioLogado?.role === 'encarregado';"
end_marker = '                const _idsAtribOS = (s.funcionariosIds && s.funcionariosIds.length) ? s.funcionariosIds : (s.funcionarioId ? [s.funcionarioId] : []);'
assert block.count(start_marker) == 1
assert block.count(end_marker) == 1
start = block.index(start_marker)
end = block.index(end_marker, start)
old = block[start:end]
for required in [
    'statusBadge(s.status)',
    "alterarStatusOS('${s.id}', this.value)",
    "dados.folhasObra?.find(f => f.servicoId === s.id)",
    "abrirFolhaDetalhe('${folhaOS.id}')",
    "criarFolhaDaOS('${s.id}')"
]:
    assert required in old, required

replacement = """                const podeEditar = usuarioLogado?.role === 'admin' || usuarioLogado?.role === 'subadmin' || usuarioLogado?.role === 'encarregado';
                const statusHtml = window.TotalGestServicesView.statusControl({
                    serviceId: s.id,
                    status: s.status || 'pendente',
                    canEdit: podeEditar,
                    badgeClass: statusBadge(s.status)
                });
                const folhaOS = s.status === 'concluído' ? dados.folhasObra?.find(f => f.servicoId === s.id) : null;
                const btnCriarFolha = window.TotalGestServicesView.workSheetActions({
                    serviceId: s.id,
                    status: s.status,
                    sheetId: folhaOS?.id || '',
                    workId: s.obraId || ''
                });
"""
block = block[:start] + replacement + block[end:]
assert block.count('window.TotalGestServicesView.statusControl({') == 1
assert block.count('window.TotalGestServicesView.workSheetActions({') == 1
assert "alterarStatusOS('${s.id}', this.value)" not in block
assert "abrirFolhaDetalhe('${folhaOS.id}')" not in block
app = app[:func_start] + block + app[func_end:]

for needle, count in protected.items():
    assert app.count(needle) == count, (needle, count, app.count(needle))

assert "const CACHE = 'totalgest-v128';" in sw
assert "const CACHE = 'totalgest-v129';" not in sw
sw = sw.replace("const CACHE = 'totalgest-v128';", "const CACHE = 'totalgest-v129';", 1)

app_path.write_text(app, encoding='utf-8')
sw_path.write_text(sw, encoding='utf-8')

new_start = app.index('        function renderizarServicos() {')
new_end = app.index('\n        function ', new_start + 1)
new_block = app[new_start:new_end]
print(f'RENDERIZAR_SERVICOS_AFTER chars={len(new_block)} lines={len(new_block.splitlines())}')
print('SERVICES_ROW_CONTROLS_MIGRATION=OK')
