from pathlib import Path

APP = Path('app.html')
SHELL = Path('assets/js/app-shell.js')
SW = Path('sw.js')

app = APP.read_text(encoding='utf-8')
shell = SHELL.read_text(encoding='utf-8')
sw = SW.read_text(encoding='utf-8')

start_marker = "            if (usuarioLogado.role === 'superadmin') {\n"
end_marker = "            } else if (usuarioLogado.role === 'admin' && adminAtual()?.ehDistribuidor) {\n"
assert app.count(start_marker) == 1, app.count(start_marker)
assert app.count(end_marker) == 1, app.count(end_marker)
start = app.index(start_marker) + len(start_marker)
end = app.index(end_marker, start)
old = app[start:end]
for token in [
    'const config = obterConfig();',
    'const db = obterDadosBancarios() || {};',
    'campos.innerHTML = `',
    'perf_estado_online_equipa',
    'migrarContasAuth()'
]:
    assert token in old, token

new = """                campos.innerHTML = window.TotalGestProfileModalSuperadmin.render({
                    config: obterConfig(),
                    bankData: obterDadosBancarios() || {},
                    getConfig: obterConfig
                });
"""
app = app[:start] + new + app[end:]

init_anchor = 'saveFormPostPersist: true'
assert app.count(init_anchor) == 1, app.count(init_anchor)
app = app.replace(init_anchor, init_anchor + ', profileModalSuperadmin: true', 1)

shell_anchor = "    saveFormPostPersist: './assets/js/app-save-form-post-persist.js',\n"
assert shell.count(shell_anchor) == 1, shell.count(shell_anchor)
shell = shell.replace(shell_anchor, shell_anchor + "    profileModalSuperadmin: './assets/js/app-profile-modal-superadmin.js',\n", 1)
load_anchor = "    if (options.saveFormPostPersist === true) pedidos.push(MODULOS.saveFormPostPersist);\n"
assert shell.count(load_anchor) == 1, shell.count(load_anchor)
shell = shell.replace(load_anchor, load_anchor + "    if (options.profileModalSuperadmin === true) pedidos.push(MODULOS.profileModalSuperadmin);\n", 1)

assert "const CACHE = 'totalgest-v81';" in sw
sw = sw.replace("const CACHE = 'totalgest-v81';", "const CACHE = 'totalgest-v82';", 1)
sw_anchor = "  './assets/js/app-save-form-post-persist.js',\n"
assert sw.count(sw_anchor) == 1, sw.count(sw_anchor)
sw = sw.replace(sw_anchor, sw_anchor + "  './assets/js/app-profile-modal-superadmin.js',\n", 1)

assert app.count('window.TotalGestProfileModalSuperadmin.render({') == 1
new_end = app.index(end_marker, start)
new_block = app[start:new_end]
for token in ['const config = obterConfig();', 'campos.innerHTML = `', 'migrarContasAuth()']:
    assert token not in new_block, token
assert shell.count('./assets/js/app-profile-modal-superadmin.js') == 1
assert sw.count('./assets/js/app-profile-modal-superadmin.js') == 1

APP.write_text(app, encoding='utf-8')
SHELL.write_text(shell, encoding='utf-8')
SW.write_text(sw, encoding='utf-8')
