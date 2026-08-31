from pathlib import Path

APP = Path('app.html')
SHELL = Path('assets/js/app-shell.js')
SW = Path('sw.js')
MODULE = Path('assets/js/app-profile-save-distributor.js')

app = APP.read_text(encoding='utf-8')
shell = SHELL.read_text(encoding='utf-8')
sw = SW.read_text(encoding='utf-8')

fn_marker = 'function salvarPerfil(e) {'
branch_marker = "            } else if (usuarioLogado.role === 'admin' && adminAtual()?.ehDistribuidor) {\n"
next_marker = "            } else if (usuarioLogado.role === 'admin' || usuarioLogado.role === 'subadmin') {"
assert app.count(fn_marker) == 1, app.count(fn_marker)
fn = app.index(fn_marker)
branch = app.index(branch_marker, fn)
next_branch = app.index(next_marker, branch)
old = app[branch + len(branch_marker):next_branch]

for token in [
    'const admin = adminAtual();',
    "const empresa = document.getElementById('perf_empresa')?.value.trim() || '';",
    "const telefone = document.getElementById('perf_telefone')?.value.trim() || '';",
    'const aplicarDist = (logoData) => {',
    "const fileInputDist = document.getElementById('perf_logo');",
    'guardarDados(dados);',
    'aplicarConfigHeader();',
    'renderizarTudo();'
]:
    assert token in old, token

module = r'''/* Total Gest — gravação do perfil de distribuidor. */
(function () {
  'use strict';

  function run(options) {
    const opts = options || {};
    const documentRef = opts.document;
    const data = opts.data;
    const user = opts.user;
    const nome = opts.name;
    const senha = opts.password;
    const admin = opts.getAdmin();
    if (!admin) return;

    const empresa = documentRef.getElementById('perf_empresa')?.value.trim() || '';
    const telefone = documentRef.getElementById('perf_telefone')?.value.trim() || '';
    const func = data.funcionarios?.find(function (employee) { return employee.id === user.id; });

    function aplicarDist(logoData) {
      admin.nome = nome;
      admin.empresa = empresa;
      admin.layout = documentRef.getElementById('perf_layout')?.value || 'sidebar';
      if (senha) admin.senha = senha;
      if (logoData !== undefined) admin.logo = logoData;
      if (func) {
        func.nome = nome;
        func.telefone = telefone;
        if (senha) func.senha = senha;
      }
      opts.saveData(data);
      opts.closeModal();
      user.nome = nome;
      opts.applyHeaderConfig();
      opts.renderAll();
      opts.alert('Perfil atualizado com sucesso!');
    }

    const fileInputDist = documentRef.getElementById('perf_logo');
    if (fileInputDist && fileInputDist.files && fileInputDist.files[0]) {
      const reader = new FileReader();
      reader.onload = function (ev) { aplicarDist(ev.target.result); };
      reader.readAsDataURL(fileInputDist.files[0]);
    } else {
      aplicarDist(undefined);
    }
  }

  window.TotalGestProfileSaveDistributor = { run: run };
})();
'''
MODULE.write_text(module, encoding='utf-8')

new = """                window.TotalGestProfileSaveDistributor.run({
                    document: document,
                    data: dados,
                    user: usuarioLogado,
                    name: nome,
                    password: senha,
                    getAdmin: adminAtual,
                    saveData: guardarDados,
                    closeModal: fecharModalPerfil,
                    applyHeaderConfig: aplicarConfigHeader,
                    renderAll: renderizarTudo,
                    alert: alert
                });
"""
app = app[:branch + len(branch_marker)] + new + app[next_branch:]

init_anchor = 'profileSaveSuperadmin: true'
assert app.count(init_anchor) == 1, app.count(init_anchor)
app = app.replace(init_anchor, init_anchor + ', profileSaveDistributor: true', 1)

shell_anchor = "    profileSaveSuperadmin: './assets/js/app-profile-save-superadmin.js',\n"
assert shell.count(shell_anchor) == 1, shell.count(shell_anchor)
shell = shell.replace(shell_anchor, shell_anchor + "    profileSaveDistributor: './assets/js/app-profile-save-distributor.js',\n", 1)
load_anchor = "    if (options.profileSaveSuperadmin === true) pedidos.push(MODULOS.profileSaveSuperadmin);\n"
assert shell.count(load_anchor) == 1, shell.count(load_anchor)
shell = shell.replace(load_anchor, load_anchor + "    if (options.profileSaveDistributor === true) pedidos.push(MODULOS.profileSaveDistributor);\n", 1)

assert "const CACHE = 'totalgest-v88';" in sw
sw = sw.replace("const CACHE = 'totalgest-v88';", "const CACHE = 'totalgest-v89';", 1)
sw_anchor = "  './assets/js/app-profile-save-superadmin.js',\n"
assert sw.count(sw_anchor) == 1, sw.count(sw_anchor)
sw = sw.replace(sw_anchor, sw_anchor + "  './assets/js/app-profile-save-distributor.js',\n", 1)

fn_end = app.index('// =============================================================\n        //  INICIALIZAÇÃO', fn)
fn_block = app[fn:fn_end]
assert fn_block.count('window.TotalGestProfileSaveDistributor.run({') == 1
for token in [
    'const aplicarDist = (logoData) => {',
    "const fileInputDist = document.getElementById('perf_logo');"
]:
    assert token not in fn_block, token
assert fn_block.count("} else if (usuarioLogado.role === 'admin' || usuarioLogado.role === 'subadmin') {") == 1
assert shell.count('./assets/js/app-profile-save-distributor.js') == 1
assert sw.count('./assets/js/app-profile-save-distributor.js') == 1

APP.write_text(app, encoding='utf-8')
SHELL.write_text(shell, encoding='utf-8')
SW.write_text(sw, encoding='utf-8')
