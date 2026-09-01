from pathlib import Path

APP = Path('app.html')
SHELL = Path('assets/js/app-shell.js')
SW = Path('sw.js')

app = APP.read_text(encoding='utf-8')
shell = SHELL.read_text(encoding='utf-8')
sw = SW.read_text(encoding='utf-8')


def alertas_region(text):
    start = text.index('        function renderizarAlertas() {')
    end = text.index('\n        function ', start + 1)
    return start, end, text[start:end]

protected = {
    'bootstrapSupabase()': app.count('bootstrapSupabase()'),
    'supabase.auth': app.count('supabase.auth'),
    '_notificarPorFaseVencimento(': app.count('_notificarPorFaseVencimento('),
    '_notificarAdminESubadmin(': app.count('_notificarAdminESubadmin('),
    'function renderizarAlertas()': app.count('function renderizarAlertas()'),
}

start, end, body = alertas_region(app)
block_start = "            const icone = t => t === 'danger'\n"
block_end = '''                </div>`;\n            }'''
assert body.count(block_start) == 1, body.count(block_start)
start_rel = body.index(block_start)
end_rel = body.rindex(block_end, start_rel) + len(block_end)
old = body[start_rel:end_rel]
assert 'const linhasHtml = alertas.map' in old
assert "if (_ehPerfilMobile())" in old
assert old.count('cont.innerHTML = `<div class="alertas-card">') == 2, old.count('cont.innerHTML = `<div class="alertas-card">')
assert 'alertas-h--acordeao' in old
assert '<div class="alertas-h"><i class="fas fa-bell"></i> Alertas e Pendências</div>' in old

replacement = '''            cont.innerHTML = window.TotalGestAlertsView.alertsCard({\n                alertas: alertas,\n                mobile: _ehPerfilMobile()\n            });'''
body = body[:start_rel] + replacement + body[end_rel:]
app = app[:start] + body + app[end:]

init_anchor = '            reportsView: true,\n'
assert app.count(init_anchor) == 1, app.count(init_anchor)
app = app.replace(init_anchor, init_anchor + '            alertsView: true,\n', 1)

module_anchor = "    reportsView: './assets/js/app-reports-view.js',\n"
assert shell.count(module_anchor) == 1, shell.count(module_anchor)
shell = shell.replace(module_anchor, module_anchor + "    alertsView: './assets/js/app-alerts-view.js',\n", 1)

loader_anchor = '    if (options.reportsView === true) pedidos.push(MODULOS.reportsView);\n'
assert shell.count(loader_anchor) == 1, shell.count(loader_anchor)
shell = shell.replace(loader_anchor, loader_anchor + '    if (options.alertsView === true) pedidos.push(MODULOS.alertsView);\n', 1)

asset_anchor = "  './assets/js/app-reports-view.js',\n"
assert sw.count(asset_anchor) == 1, sw.count(asset_anchor)
sw = sw.replace(asset_anchor, asset_anchor + "  './assets/js/app-alerts-view.js',\n", 1)
assert sw.count("const CACHE = 'totalgest-v117';") == 1
sw = sw.replace("const CACHE = 'totalgest-v117';", "const CACHE = 'totalgest-v118';", 1)

for needle, before in protected.items():
    assert app.count(needle) == before, (needle, before, app.count(needle))

_, _, after = alertas_region(app)
assert after.count('window.TotalGestAlertsView.alertsCard({') == 1
assert 'const linhasHtml = alertas.map' not in after
assert "const icone = t => t === 'danger'" not in after
assert app.count('alertsView: true,') == 1
assert shell.count("alertsView: './assets/js/app-alerts-view.js',") == 1
assert shell.count('if (options.alertsView === true) pedidos.push(MODULOS.alertsView);') == 1
assert sw.count("'./assets/js/app-alerts-view.js',") == 1
assert sw.count("const CACHE = 'totalgest-v118';") == 1

APP.write_text(app, encoding='utf-8')
SHELL.write_text(shell, encoding='utf-8')
SW.write_text(sw, encoding='utf-8')
print(f'RENDERIZAR_ALERTAS_AFTER chars={len(after)} lines={after.count(chr(10))+1}')
print('ALERTS_VIEW_MIGRATION=OK')
