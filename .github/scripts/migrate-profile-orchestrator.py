from pathlib import Path

APP = Path('app.html')
SHELL = Path('assets/js/app-shell.js')
SW = Path('sw.js')

app = APP.read_text(encoding='utf-8')
shell = SHELL.read_text(encoding='utf-8')
sw = SW.read_text(encoding='utf-8')

start_marker = 'function abrirEditarPerfil() {'
end_marker = '\n        function previewPerfilLogo(e) {'
assert app.count(start_marker) == 1, app.count(start_marker)
start = app.index(start_marker)
end = app.index(end_marker, start)
old = app[start:end]

for token in [
    'window.TotalGestProfileModalSuperadmin.render({',
    'window.TotalGestProfileModalDistributor.render({',
    'window.TotalGestProfileModalAdmin.render({',
    'window.TotalGestProfileModalWorker.render({',
    "overlay.classList.add('open');"
]:
    assert old.count(token) == 1, (token, old.count(token))

new = """function abrirEditarPerfil() {
            if (!usuarioLogado) return;
            const overlay = document.getElementById('modalPerfilOverlay');
            const campos = document.getElementById('perfilCampos');
            const _perfilHtml = window.TotalGestProfileModal.render({
                user: usuarioLogado,
                getAdmin: adminAtual,
                getConfig: obterConfig,
                getBankData: obterDadosBancarios,
                employees: dados.funcionarios || [],
                foremen: dados.encarregados || [],
                municipalHolidays: FERIADOS_MUNICIPAIS,
                contractsModuleEnabled: moduloContratosAtivo
            });
            if (_perfilHtml == null) return;
            campos.innerHTML = _perfilHtml;
            overlay.classList.add('open');
        }
"""
app = app[:start] + new + app[end:]

init_anchor = 'profileModalWorker: true'
assert app.count(init_anchor) == 1, app.count(init_anchor)
app = app.replace(init_anchor, init_anchor + ', profileModal: true', 1)

module_anchor = "    profileModalWorker: './assets/js/app-profile-modal-worker.js',\n"
assert shell.count(module_anchor) == 1, shell.count(module_anchor)
shell = shell.replace(module_anchor, module_anchor + "    profileModal: './assets/js/app-profile-modal.js',\n", 1)
load_anchor = "    if (options.profileModalWorker === true) pedidos.push(MODULOS.profileModalWorker);\n"
assert shell.count(load_anchor) == 1, shell.count(load_anchor)
shell = shell.replace(load_anchor, load_anchor + "    if (options.profileModal === true) pedidos.push(MODULOS.profileModal);\n", 1)

assert "const CACHE = 'totalgest-v85';" in sw
sw = sw.replace("const CACHE = 'totalgest-v85';", "const CACHE = 'totalgest-v86';", 1)
sw_anchor = "  './assets/js/app-profile-modal-worker.js',\n"
assert sw.count(sw_anchor) == 1, sw.count(sw_anchor)
sw = sw.replace(sw_anchor, sw_anchor + "  './assets/js/app-profile-modal.js',\n", 1)

assert app.count('window.TotalGestProfileModal.render({') == 1
profile_block = app[start:app.index(end_marker, start)]
assert len(profile_block.splitlines()) <= 20, len(profile_block.splitlines())
for token in [
    'window.TotalGestProfileModalSuperadmin.render({',
    'window.TotalGestProfileModalDistributor.render({',
    'window.TotalGestProfileModalAdmin.render({',
    'window.TotalGestProfileModalWorker.render({'
]:
    assert token not in profile_block, token
assert shell.count('./assets/js/app-profile-modal.js') == 1
assert sw.count('./assets/js/app-profile-modal.js') == 1

APP.write_text(app, encoding='utf-8')
SHELL.write_text(shell, encoding='utf-8')
SW.write_text(sw, encoding='utf-8')
