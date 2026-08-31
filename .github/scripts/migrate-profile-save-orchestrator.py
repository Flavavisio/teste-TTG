from pathlib import Path

APP = Path('app.html')
SHELL = Path('assets/js/app-shell.js')
SW = Path('sw.js')
MODULE = Path('assets/js/app-profile-save.js')

app = APP.read_text(encoding='utf-8')
shell = SHELL.read_text(encoding='utf-8')
sw = SW.read_text(encoding='utf-8')

start_marker = 'function salvarPerfil(e) {'
end_marker = '// =============================================================\n        //  INICIALIZAÇÃO'
assert app.count(start_marker) == 1
start = app.index(start_marker)
end = app.index(end_marker, start)
old = app[start:end]
for token in [
    "e.preventDefault();",
    "document.getElementById('perf_nome').value.trim()",
    "document.getElementById('perf_senha').value",
    "if (!nome) { alert('Nome é obrigatório.'); return; }",
    'window.TotalGestProfileSaveSuperadmin.run({',
    'window.TotalGestProfileSaveDistributor.run({',
    'window.TotalGestProfileSaveAdmin.run({',
    'window.TotalGestProfileSaveWorker.run({'
]:
    assert old.count(token) == 1, (token, old.count(token))

module = r'''/* Total Gest — orquestração da gravação do perfil. */
(function () {
  'use strict';

  function run(options) {
    const opts = options || {};
    const event = opts.event;
    if (event && typeof event.preventDefault === 'function') event.preventDefault();
    const user = opts.user;
    if (!user) return;

    const documentRef = opts.document;
    const nome = documentRef.getElementById('perf_nome').value.trim();
    const senha = documentRef.getElementById('perf_senha').value;
    if (!nome) {
      opts.alert('Nome é obrigatório.');
      return;
    }

    const common = {
      document: documentRef,
      data: opts.data,
      user: user,
      name: nome,
      password: senha,
      saveData: opts.saveData,
      closeModal: opts.closeModal,
      renderAll: opts.renderAll,
      alert: opts.alert
    };

    if (user.role === 'superadmin') {
      opts.superadmin.run(Object.assign({}, common, {
        getConfig: opts.getConfig,
        saveConfig: opts.saveConfig
      }));
      return;
    }

    if (user.role === 'admin' && opts.getAdmin()?.ehDistribuidor) {
      opts.distributor.run(Object.assign({}, common, {
        getAdmin: opts.getAdmin,
        applyHeaderConfig: opts.applyHeaderConfig
      }));
      return;
    }

    if (user.role === 'admin' || user.role === 'subadmin') {
      opts.admin.run(Object.assign({}, common, {
        getAdmin: opts.getAdmin,
        numberAlreadyUsed: opts.numberAlreadyUsed,
        applyHeaderConfig: opts.applyHeaderConfig
      }));
      return;
    }

    opts.worker.run(common);
  }

  window.TotalGestProfileSave = { run: run };
})();
'''
MODULE.write_text(module, encoding='utf-8')

new = """function salvarPerfil(e) {
            window.TotalGestProfileSave.run({
                event: e,
                document: document,
                data: dados,
                user: usuarioLogado,
                getConfig: obterConfig,
                saveConfig: guardarConfig,
                getAdmin: adminAtual,
                numberAlreadyUsed: _numeroJaUsado,
                saveData: guardarDados,
                closeModal: fecharModalPerfil,
                applyHeaderConfig: aplicarConfigHeader,
                renderAll: renderizarTudo,
                alert: alert,
                superadmin: window.TotalGestProfileSaveSuperadmin,
                distributor: window.TotalGestProfileSaveDistributor,
                admin: window.TotalGestProfileSaveAdmin,
                worker: window.TotalGestProfileSaveWorker
            });
        }

        """
app = app[:start] + new + app[end:]

init_anchor = 'profileSaveWorker: true'
assert app.count(init_anchor) == 1
app = app.replace(init_anchor, init_anchor + ', profileSave: true', 1)

shell_anchor = "    profileSaveWorker: './assets/js/app-profile-save-worker.js',\n"
assert shell.count(shell_anchor) == 1
shell = shell.replace(shell_anchor, shell_anchor + "    profileSave: './assets/js/app-profile-save.js',\n", 1)
load_anchor = "    if (options.profileSaveWorker === true) pedidos.push(MODULOS.profileSaveWorker);\n"
assert shell.count(load_anchor) == 1
shell = shell.replace(load_anchor, load_anchor + "    if (options.profileSave === true) pedidos.push(MODULOS.profileSave);\n", 1)

assert "const CACHE = 'totalgest-v91';" in sw
sw = sw.replace("const CACHE = 'totalgest-v91';", "const CACHE = 'totalgest-v92';", 1)
sw_anchor = "  './assets/js/app-profile-save-worker.js',\n"
assert sw.count(sw_anchor) == 1
sw = sw.replace(sw_anchor, sw_anchor + "  './assets/js/app-profile-save.js',\n", 1)

new_block = app[start:app.index(end_marker, start)]
assert new_block.count('window.TotalGestProfileSave.run({') == 1
for token in [
    "document.getElementById('perf_nome').value.trim()",
    'window.TotalGestProfileSaveSuperadmin.run({',
    'window.TotalGestProfileSaveDistributor.run({',
    'window.TotalGestProfileSaveAdmin.run({',
    'window.TotalGestProfileSaveWorker.run({'
]:
    assert token not in new_block, token
assert shell.count('./assets/js/app-profile-save.js') == 1
assert sw.count('./assets/js/app-profile-save.js') == 1

APP.write_text(app, encoding='utf-8')
SHELL.write_text(shell, encoding='utf-8')
SW.write_text(sw, encoding='utf-8')
