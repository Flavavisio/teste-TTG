from pathlib import Path

APP = Path('app.html')
SHELL = Path('assets/js/app-shell.js')
SW = Path('sw.js')
MODULE = Path('assets/js/app-profile-save-worker.js')

app = APP.read_text(encoding='utf-8')
shell = SHELL.read_text(encoding='utf-8')
sw = SW.read_text(encoding='utf-8')

fn_marker = 'function salvarPerfil(e) {'
admin_marker = "            } else if (usuarioLogado.role === 'admin' || usuarioLogado.role === 'subadmin') {"
assert app.count(fn_marker) == 1
fn = app.index(fn_marker)
admin = app.index(admin_marker, fn)
branch_marker = "            } else {\n"
branch = app.index(branch_marker, admin)
end_marker = "            }\n        }\n"
end = app.index(end_marker, branch)
old = app[branch + len(branch_marker):end]
for token in [
    'dados.funcionarios?.find',
    'dados.encarregados?.find',
    "document.getElementById('perf_telefone')",
    "document.getElementById('perf_foto')",
    'guardarDados(dados);',
    'fecharModalPerfil();',
    'renderizarTudo();'
]:
    assert token in old, token

module = r'''/* Total Gest — gravação do perfil de colaborador/encarregado. */
(function () {
  'use strict';

  function run(options) {
    const opts = options || {};
    const documentRef = opts.document;
    const data = opts.data;
    const user = opts.user;
    const nome = opts.name;
    const senha = opts.password;
    const func = data.funcionarios?.find(function (employee) { return employee.id === user.id; }) ||
      data.encarregados?.find(function (foreman) { return foreman.id === user.id; });
    if (!func) return;

    func.nome = nome;
    const telefone = documentRef.getElementById('perf_telefone')?.value.trim();
    if (telefone !== undefined) func.telefone = telefone;
    if (senha) func.senha = senha;

    function concluir() {
      opts.saveData(data);
      opts.closeModal();
      user.nome = nome;
      opts.renderAll();
      opts.alert('Perfil atualizado com sucesso!');
    }

    const fotoInput = documentRef.getElementById('perf_foto');
    if (fotoInput && fotoInput.files && fotoInput.files[0]) {
      const reader = new FileReader();
      reader.onload = function (ev) {
        func.foto = ev.target.result;
        concluir();
      };
      reader.readAsDataURL(fotoInput.files[0]);
      return;
    }
    concluir();
  }

  window.TotalGestProfileSaveWorker = { run: run };
})();
'''
MODULE.write_text(module, encoding='utf-8')

new = """                window.TotalGestProfileSaveWorker.run({
                    document: document,
                    data: dados,
                    user: usuarioLogado,
                    name: nome,
                    password: senha,
                    saveData: guardarDados,
                    closeModal: fecharModalPerfil,
                    renderAll: renderizarTudo,
                    alert: alert
                });
"""
app = app[:branch + len(branch_marker)] + new + app[end:]

init_anchor = 'profileSaveAdmin: true'
assert app.count(init_anchor) == 1
app = app.replace(init_anchor, init_anchor + ', profileSaveWorker: true', 1)

shell_anchor = "    profileSaveAdmin: './assets/js/app-profile-save-admin.js',\n"
assert shell.count(shell_anchor) == 1
shell = shell.replace(shell_anchor, shell_anchor + "    profileSaveWorker: './assets/js/app-profile-save-worker.js',\n", 1)
load_anchor = "    if (options.profileSaveAdmin === true) pedidos.push(MODULOS.profileSaveAdmin);\n"
assert shell.count(load_anchor) == 1
shell = shell.replace(load_anchor, load_anchor + "    if (options.profileSaveWorker === true) pedidos.push(MODULOS.profileSaveWorker);\n", 1)

assert "const CACHE = 'totalgest-v90';" in sw
sw = sw.replace("const CACHE = 'totalgest-v90';", "const CACHE = 'totalgest-v91';", 1)
sw_anchor = "  './assets/js/app-profile-save-admin.js',\n"
assert sw.count(sw_anchor) == 1
sw = sw.replace(sw_anchor, sw_anchor + "  './assets/js/app-profile-save-worker.js',\n", 1)

fn_end = app.index('// =============================================================\n        //  INICIALIZAÇÃO', fn)
fn_block = app[fn:fn_end]
assert fn_block.count('window.TotalGestProfileSaveWorker.run({') == 1
assert "document.getElementById('perf_foto')" not in fn_block
assert shell.count('./assets/js/app-profile-save-worker.js') == 1
assert sw.count('./assets/js/app-profile-save-worker.js') == 1

APP.write_text(app, encoding='utf-8')
SHELL.write_text(shell, encoding='utf-8')
SW.write_text(sw, encoding='utf-8')
