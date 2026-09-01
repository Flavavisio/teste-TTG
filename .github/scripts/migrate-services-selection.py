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
    'faturarOSViaTOConline(': app.count('faturarOSViaTOConline('),
    'faturarOSViaMoloni(': app.count('faturarOSViaMoloni('),
    '_verificarPagamentoMoloni(': app.count('_verificarPagamentoMoloni('),
    'emitirGuiaTransporteMoloni(': app.count('emitirGuiaTransporteMoloni('),
    'emitirNotaCreditoMoloni(': app.count('emitirNotaCreditoMoloni('),
    'tbody.innerHTML = servicos.map(': app.count('tbody.innerHTML = servicos.map('),
}

func_start = app.index('        function renderizarServicos() {')
func_end = app.index('\n        function ', func_start + 1)
block = app[func_start:func_end]

start_marker = '            let servicos = dados.servicos || [];'
end_marker = '            const totalGeralOS = servicos.length;'
assert block.count(start_marker) == 1
assert block.count(end_marker) == 1
start = block.index(start_marker)
end = block.index(end_marker, start)
old = block[start:end]
for required in [
    "usuarioLogado.role === 'admin'",
    "usuarioLogado.role === 'subadmin'",
    "usuarioLogado.role === 'encarregado'",
    "usuarioLogado.role === 'funcionario'",
    "usuarioLogado?.role === 'superadmin'",
    'dados.encarregados?.find',
    'dados.funcionarios?.find'
]:
    assert required in old, required

replacement = """            let servicos = window.TotalGestServicesSelection.selectVisibleServices({
                services: dados.servicos || [],
                user: usuarioLogado,
                encarregados: dados.encarregados || [],
                funcionarios: dados.funcionarios || []
            });

"""
block = block[:start] + replacement + block[end:]
assert block.count('window.TotalGestServicesSelection.selectVisibleServices({') == 1
for old_role in [
    "usuarioLogado.role === 'encarregado'",
    "usuarioLogado.role === 'funcionario'",
    "usuarioLogado?.role === 'superadmin'"
]:
    assert old_role not in block[:block.index(end_marker)]
app = app[:func_start] + block + app[func_end:]

assert shell.count("    alertsView: './assets/js/app-alerts-view.js',") == 1
assert "servicesSelection: './assets/js/app-services-selection.js'" not in shell
shell = shell.replace(
    "    alertsView: './assets/js/app-alerts-view.js',",
    "    alertsView: './assets/js/app-alerts-view.js',\n    servicesSelection: './assets/js/app-services-selection.js',",
    1
)
assert shell.count('    if (options.alertsView === true) pedidos.push(MODULOS.alertsView);') == 1
shell = shell.replace(
    '    if (options.alertsView === true) pedidos.push(MODULOS.alertsView);',
    '    if (options.alertsView === true) pedidos.push(MODULOS.alertsView);\n    if (options.servicesSelection === true) pedidos.push(MODULOS.servicesSelection);',
    1
)

assert app.count('licenseAddons: true') == 1, app.count('licenseAddons: true')
assert 'servicesSelection: true' not in app
app = app.replace('licenseAddons: true', 'licenseAddons: true, servicesSelection: true', 1)

assert sw.count("'./assets/js/app-alerts-view.js',") == 1
assert "'./assets/js/app-services-selection.js'," not in sw
sw = sw.replace(
    "'./assets/js/app-alerts-view.js',",
    "'./assets/js/app-alerts-view.js',\n    './assets/js/app-services-selection.js',",
    1
)
assert "const CACHE = 'totalgest-v126';" in sw
assert "const CACHE = 'totalgest-v127';" not in sw
sw = sw.replace("const CACHE = 'totalgest-v126';", "const CACHE = 'totalgest-v127';", 1)

for needle, count in protected.items():
    assert app.count(needle) == count, (needle, count, app.count(needle))

app_path.write_text(app, encoding='utf-8')
shell_path.write_text(shell, encoding='utf-8')
sw_path.write_text(sw, encoding='utf-8')

new_start = app.index('        function renderizarServicos() {')
new_end = app.index('\n        function ', new_start + 1)
new_block = app[new_start:new_end]
print(f'RENDERIZAR_SERVICOS_AFTER chars={len(new_block)} lines={len(new_block.splitlines())}')
print('SERVICES_SELECTION_MIGRATION=OK')
