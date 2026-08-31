from pathlib import Path

APP = Path('app.html')
SHELL = Path('assets/js/app-shell.js')
SW = Path('sw.js')

app = APP.read_text(encoding='utf-8')
shell = SHELL.read_text(encoding='utf-8')
sw = SW.read_text(encoding='utf-8')

fn_marker = '        function abrirEditarPerfil() {'
start_marker = "            } else if (usuarioLogado.role === 'admin' && adminAtual()?.ehDistribuidor) {\n"
end_marker = "            } else if (usuarioLogado.role === 'admin' || usuarioLogado.role === 'subadmin') {\n"
assert app.count(fn_marker) == 1, app.count(fn_marker)
fn = app.index(fn_marker)
start_branch = app.index(start_marker, fn)
end = app.index(end_marker, start_branch)
start = start_branch + len(start_marker)
old = app[start:end]
for token in [
    'const admin = adminAtual();',
    'const func = dados.funcionarios?.find',
    'campos.innerHTML = `',
    'distribuidorDesconto',
    'perf_layout'
]:
    assert token in old, token

new = """                campos.innerHTML = window.TotalGestProfileModalDistributor.render({
                    admin: adminAtual(),
                    employee: dados.funcionarios?.find(f => f.id === usuarioLogado.id) || null
                });
"""
app = app[:start] + new + app[end:]

init_anchor = 'profileModalSuperadmin: true'
assert app.count(init_anchor) == 1, app.count(init_anchor)
app = app.replace(init_anchor, init_anchor + ', profileModalDistributor: true', 1)

shell_anchor = "    profileModalSuperadmin: './assets/js/app-profile-modal-superadmin.js',\n"
assert shell.count(shell_anchor) == 1, shell.count(shell_anchor)
shell = shell.replace(shell_anchor, shell_anchor + "    profileModalDistributor: './assets/js/app-profile-modal-distributor.js',\n", 1)
load_anchor = "    if (options.profileModalSuperadmin === true) pedidos.push(MODULOS.profileModalSuperadmin);\n"
assert shell.count(load_anchor) == 1, shell.count(load_anchor)
shell = shell.replace(load_anchor, load_anchor + "    if (options.profileModalDistributor === true) pedidos.push(MODULOS.profileModalDistributor);\n", 1)

assert "const CACHE = 'totalgest-v82';" in sw
sw = sw.replace("const CACHE = 'totalgest-v82';", "const CACHE = 'totalgest-v83';", 1)
sw_anchor = "  './assets/js/app-profile-modal-superadmin.js',\n"
assert sw.count(sw_anchor) == 1, sw.count(sw_anchor)
sw = sw.replace(sw_anchor, sw_anchor + "  './assets/js/app-profile-modal-distributor.js',\n", 1)

assert app.count('window.TotalGestProfileModalDistributor.render({') == 1
new_end = app.index(end_marker, start)
new_block = app[start:new_end]
for token in ['const admin = adminAtual();', 'campos.innerHTML = `', 'distribuidorDesconto']:
    assert token not in new_block, token
assert shell.count('./assets/js/app-profile-modal-distributor.js') == 1
assert sw.count('./assets/js/app-profile-modal-distributor.js') == 1

APP.write_text(app, encoding='utf-8')
SHELL.write_text(shell, encoding='utf-8')
SW.write_text(sw, encoding='utf-8')
