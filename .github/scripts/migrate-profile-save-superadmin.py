from pathlib import Path

APP = Path('app.html')
SHELL = Path('assets/js/app-shell.js')
SW = Path('sw.js')
MODULE = Path('assets/js/app-profile-save-superadmin.js')

app = APP.read_text(encoding='utf-8')
shell = SHELL.read_text(encoding='utf-8')
sw = SW.read_text(encoding='utf-8')

fn_marker = 'function salvarPerfil(e) {'
branch_marker = "            if (usuarioLogado.role === 'superadmin') {\n"
next_marker = "            } else if (usuarioLogado.role === 'admin' && adminAtual()?.ehDistribuidor) {"
assert app.count(fn_marker) == 1, app.count(fn_marker)
fn = app.index(fn_marker)
branch = app.index(branch_marker, fn)
next_branch = app.index(next_marker, branch)
old = app[branch + len(branch_marker):next_branch]

for token in [
    'const config = obterConfig();',
    'saRec.dadosBancarios = {',
    "const fileInput = document.getElementById('perf_logo');",
    'guardarConfig(config);',
    'guardarDados(dados);',
    'fecharModalPerfil();',
    'usuarioLogado.nome = nome;',
    'renderizarTudo();',
    "alert('Perfil atualizado com sucesso!');"
]:
    assert token in old, token

module = r'''/* Total Gest — gravação do perfil de superadmin. */
(function () {
  'use strict';

  function run(options) {
    const opts = options || {};
    const documentRef = opts.document;
    const data = opts.data;
    const user = opts.user;
    const nome = opts.name;
    const senha = opts.password;

    const config = opts.getConfig();
    config.nome = nome;
    const novoEmailSA = documentRef.getElementById('perf_email')?.value.trim();
    if (novoEmailSA) config.email = novoEmailSA;
    if (senha) config.senha = senha;
    config.mostrarEstadoOnline = documentRef.getElementById('perf_estado_online_equipa')?.checked || false;
    config.layout = documentRef.getElementById('perf_layout')?.value || 'sidebar';

    const saRec = data.administradores?.find(function (admin) { return admin.id === 'superadmin'; }) || (function () {
      const novo = { id: 'superadmin', nome: 'Super Admin', email: 'superadmin@totalgest.pt', senha: 'nao-usado-login-separado', empresa: 'Total Gest', ativo: true, dataCriacao: Date.now() };
      data.administradores = data.administradores || [];
      data.administradores.push(novo);
      return novo;
    })();

    saRec.dadosBancarios = {
      titular: documentRef.getElementById('perf_titular')?.value.trim() || '',
      iban: documentRef.getElementById('perf_iban')?.value.trim() || '',
      banco: documentRef.getElementById('perf_banco')?.value.trim() || '',
      swift: documentRef.getElementById('perf_swift')?.value.trim() || '',
      mbway: documentRef.getElementById('perf_mbway')?.value.trim() || '',
      instrucoes: documentRef.getElementById('perf_instrucoes')?.value.trim() || ''
    };

    function concluir() {
      opts.saveConfig(config);
      const superAdmin = data.funcionarios?.find(function (employee) { return employee.role === 'superadmin'; });
      if (superAdmin) {
        superAdmin.nome = nome;
        if (senha) superAdmin.senha = senha;
      }
      opts.saveData(data);
      opts.closeModal();
      user.nome = nome;
      opts.renderAll();
      opts.alert('Perfil atualizado com sucesso!');
    }

    const fileInput = documentRef.getElementById('perf_logo');
    if (fileInput && fileInput.files && fileInput.files[0]) {
      const reader = new FileReader();
      reader.onload = function (ev) {
        config.logo = ev.target.result;
        concluir();
      };
      reader.readAsDataURL(fileInput.files[0]);
    } else {
      concluir();
    }
  }

  window.TotalGestProfileSaveSuperadmin = { run: run };
})();
'''
MODULE.write_text(module, encoding='utf-8')

new = """                window.TotalGestProfileSaveSuperadmin.run({
                    document: document,
                    data: dados,
                    user: usuarioLogado,
                    name: nome,
                    password: senha,
                    getConfig: obterConfig,
                    saveConfig: guardarConfig,
                    saveData: guardarDados,
                    closeModal: fecharModalPerfil,
                    renderAll: renderizarTudo,
                    alert: alert
                });
"""
app = app[:branch + len(branch_marker)] + new + app[next_branch:]

init_anchor = 'profileHelpers: true'
assert app.count(init_anchor) == 1, app.count(init_anchor)
app = app.replace(init_anchor, init_anchor + ', profileSaveSuperadmin: true', 1)

shell_anchor = "    profileHelpers: './assets/js/app-profile-helpers.js',\n"
assert shell.count(shell_anchor) == 1, shell.count(shell_anchor)
shell = shell.replace(shell_anchor, shell_anchor + "    profileSaveSuperadmin: './assets/js/app-profile-save-superadmin.js',\n", 1)
load_anchor = "    if (options.profileHelpers === true) pedidos.push(MODULOS.profileHelpers);\n"
assert shell.count(load_anchor) == 1, shell.count(load_anchor)
shell = shell.replace(load_anchor, load_anchor + "    if (options.profileSaveSuperadmin === true) pedidos.push(MODULOS.profileSaveSuperadmin);\n", 1)

assert "const CACHE = 'totalgest-v87';" in sw
sw = sw.replace("const CACHE = 'totalgest-v87';", "const CACHE = 'totalgest-v88';", 1)
sw_anchor = "  './assets/js/app-profile-helpers.js',\n"
assert sw.count(sw_anchor) == 1, sw.count(sw_anchor)
sw = sw.replace(sw_anchor, sw_anchor + "  './assets/js/app-profile-save-superadmin.js',\n", 1)

fn_end = app.index('// =============================================================\n        //  INICIALIZAÇÃO', fn)
fn_block = app[fn:fn_end]
assert fn_block.count('window.TotalGestProfileSaveSuperadmin.run({') == 1
for token in [
    'saRec.dadosBancarios = {',
    "const novoEmailSA = document.getElementById('perf_email')?.value.trim();"
]:
    assert token not in fn_block, token
assert fn_block.count("} else if (usuarioLogado.role === 'admin' && adminAtual()?.ehDistribuidor) {") == 1
assert fn_block.count("} else if (usuarioLogado.role === 'admin' || usuarioLogado.role === 'subadmin') {") == 1
assert shell.count('./assets/js/app-profile-save-superadmin.js') == 1
assert sw.count('./assets/js/app-profile-save-superadmin.js') == 1

APP.write_text(app, encoding='utf-8')
SHELL.write_text(shell, encoding='utf-8')
SW.write_text(sw, encoding='utf-8')
