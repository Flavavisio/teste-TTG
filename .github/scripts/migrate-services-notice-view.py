from pathlib import Path

app_path = Path('app.html')
shell_path = Path('assets/js/app-shell.js')
sw_path = Path('sw.js')
app = app_path.read_text(encoding='utf-8')
shell = shell_path.read_text(encoding='utf-8')
sw = sw_path.read_text(encoding='utf-8')

protected = {
    'bootstrapSupabase()': app.count('bootstrapSupabase()'),
    'supabase.auth': app.count('supabase.auth'),
    'window.TotalGestServicesSelection.selectVisibleServices({': app.count('window.TotalGestServicesSelection.selectVisibleServices({'),
    'tbody.innerHTML = servicos.map(': app.count('tbody.innerHTML = servicos.map('),
    'faturarOSViaTOConline(': app.count('faturarOSViaTOConline('),
    'faturarOSViaMoloni(': app.count('faturarOSViaMoloni('),
    '_verificarPagamentoMoloni(': app.count('_verificarPagamentoMoloni('),
    'emitirGuiaTransporteMoloni(': app.count('emitirGuiaTransporteMoloni('),
    'emitirNotaCreditoMoloni(': app.count('emitirNotaCreditoMoloni('),
}

func_start = app.index('        function renderizarServicos() {')
func_end = app.index('\n        function ', func_start + 1)
block = app[func_start:func_end]

start_marker = "            const avisoDiv = document.getElementById('servicosAvisoEspecialidade');"
end_marker = "            servicos = _aplicarFiltroOrdenacao('servicos', servicos,"
assert block.count(start_marker) == 1, block.count(start_marker)
assert block.count(end_marker) == 1, block.count(end_marker)
start = block.index(start_marker)
end = block.index(end_marker, start)
old = block[start:end]
for required in [
    'osComPendente',
    '_tiposEspecialidadePendentes(s.id)',
    'btn-carregar-os-antigas',
    'carregarOSMaisAntigo()',
    '_servicosCarregadoDesde'
]:
    assert required in old, required

replacement = """            const avisoDiv = document.getElementById('servicosAvisoEspecialidade');
            if (avisoDiv) {
                const _podeVerPendentes = usuarioLogado?.role === 'admin' || usuarioLogado?.role === 'subadmin' || usuarioLogado?.role === 'encarregado';
                const _servicosPendentesEspecialidade = _podeVerPendentes
                    ? servicos
                        .filter(s => s.status === 'concluído')
                        .map(s => ({ number: s.numeroRegisto || '', types: _tiposEspecialidadePendentes(s.id) }))
                        .filter(item => item.types.length > 0)
                    : [];
                avisoDiv.innerHTML = window.TotalGestServicesView.specialtyAndHistoryNotice({
                    canSeePending: _podeVerPendentes,
                    pendingServices: _servicosPendentesEspecialidade,
                    loadedSinceLabel: _servicosCarregadoDesde
                        ? new Date(_servicosCarregadoDesde + 'T00:00:00').toLocaleDateString('pt-PT')
                        : '—'
                });
            }

"""
block = block[:start] + replacement + block[end:]
assert block.count('window.TotalGestServicesView.specialtyAndHistoryNotice({') == 1
for old_visual in [
    'btn-carregar-os-antigas',
    '<i class="fas fa-triangle-exclamation"></i>',
    'A mostrar concluídas desde ${_servicosCarregadoDesde'
]:
    assert old_visual not in block, old_visual
app = app[:func_start] + block + app[func_end:]

assert shell.count("    servicesSelection: './assets/js/app-services-selection.js',") == 1
assert "servicesView: './assets/js/app-services-view.js'" not in shell
shell = shell.replace(
    "    servicesSelection: './assets/js/app-services-selection.js',",
    "    servicesSelection: './assets/js/app-services-selection.js',\n    servicesView: './assets/js/app-services-view.js',",
    1
)
assert shell.count('    if (options.servicesSelection === true) pedidos.push(MODULOS.servicesSelection);') == 1
shell = shell.replace(
    '    if (options.servicesSelection === true) pedidos.push(MODULOS.servicesSelection);',
    '    if (options.servicesSelection === true) pedidos.push(MODULOS.servicesSelection);\n    if (options.servicesView === true) pedidos.push(MODULOS.servicesView);',
    1
)

assert app.count('servicesSelection: true') == 1
assert 'servicesView: true' not in app
app = app.replace('servicesSelection: true', 'servicesSelection: true, servicesView: true', 1)

assert sw.count("'./assets/js/app-services-selection.js',") == 1
assert "'./assets/js/app-services-view.js'," not in sw
sw = sw.replace(
    "'./assets/js/app-services-selection.js',",
    "'./assets/js/app-services-selection.js',\n    './assets/js/app-services-view.js',",
    1
)
assert "const CACHE = 'totalgest-v127';" in sw
assert "const CACHE = 'totalgest-v128';" not in sw
sw = sw.replace("const CACHE = 'totalgest-v127';", "const CACHE = 'totalgest-v128';", 1)

for needle, count in protected.items():
    assert app.count(needle) == count, (needle, count, app.count(needle))

app_path.write_text(app, encoding='utf-8')
shell_path.write_text(shell, encoding='utf-8')
sw_path.write_text(sw, encoding='utf-8')

new_start = app.index('        function renderizarServicos() {')
new_end = app.index('\n        function ', new_start + 1)
new_block = app[new_start:new_end]
print(f'RENDERIZAR_SERVICOS_AFTER chars={len(new_block)} lines={len(new_block.splitlines())}')
print('SERVICES_NOTICE_VIEW_MIGRATION=OK')
