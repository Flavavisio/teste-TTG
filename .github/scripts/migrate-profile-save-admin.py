from pathlib import Path

APP = Path('app.html')
SHELL = Path('assets/js/app-shell.js')
SW = Path('sw.js')
MODULE = Path('assets/js/app-profile-save-admin.js')

app = APP.read_text(encoding='utf-8')
shell = SHELL.read_text(encoding='utf-8')
sw = SW.read_text(encoding='utf-8')

fn_marker = 'function salvarPerfil(e) {'
branch_marker = "            } else if (usuarioLogado.role === 'admin' || usuarioLogado.role === 'subadmin') {\n"
next_marker = "            } else {\n"
assert app.count(fn_marker) == 1, app.count(fn_marker)
fn = app.index(fn_marker)
branch = app.index(branch_marker, fn)
next_branch = app.index(next_marker, branch)
old = app[branch + len(branch_marker):next_branch]

for token in [
    'const admin = adminAtual();',
    "const anepc = document.getElementById('perf_anepc')?.value.trim() || '';",
    "const registoPrevio = document.getElementById('perf_registo_previo')?.value.trim() || '';",
    "const cor = document.getElementById('perf_cor')?.value.trim() || '';",
    "admin.horaEntradaHabitual = document.getElementById('perf_hora_entrada')?.value || '09:00';",
    "admin.segurancaAtivo = document.getElementById('perf_seguranca_ativo')?.checked || false;",
    'window._perfCertificadoraLogoRemover',
    'window._perfCertificadoraLogoNova',
    'guardarDados(dados);',
    'aplicarConfigHeader();',
    'renderizarTudo();'
]:
    assert token in old, token

module = r'''/* Total Gest — gravação do perfil admin/subadmin. */
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
    const anepc = documentRef.getElementById('perf_anepc')?.value.trim() || '';
    const anepcData = documentRef.getElementById('perf_anepc_data')?.value || '';
    const anepcValidade = documentRef.getElementById('perf_anepc_validade')?.value || '';
    const registoPrevio = documentRef.getElementById('perf_registo_previo')?.value.trim() || '';
    const registoPrevioData = documentRef.getElementById('perf_registo_previo_data')?.value || '';
    const registoPrevioValidade = documentRef.getElementById('perf_registo_previo_validade')?.value || '';
    const nifEmpresa = documentRef.getElementById('perf_nif')?.value.trim() || '';
    const cor = documentRef.getElementById('perf_cor')?.value.trim() || '';

    if (anepc && opts.numberAlreadyUsed('numeroAnepc', anepc, admin.id)) {
      opts.alert('Já existe outra empresa registada com esse número de ANEPC.');
      return;
    }
    if (registoPrevio && opts.numberAlreadyUsed('numeroRegistoPrevio', registoPrevio, admin.id)) {
      opts.alert('Já existe outra empresa com esse número de registo prévio.');
      return;
    }
    if (cor && !/^#[0-9a-fA-F]{6}$/.test(cor)) {
      opts.alert('A cor deve estar no formato #RRGGBB (ex.: #152A52).');
      return;
    }

    function aplicar(logoData) {
      admin.nome = nome;
      admin.empresa = empresa;
      admin.nif = nifEmpresa || null;
      admin.layout = documentRef.getElementById('perf_layout')?.value || 'sidebar';
      admin.numeroAnepc = anepc || null;
      admin.dataAnepc = anepcData || null;
      admin.anepcValidade = anepcValidade || null;
      admin.numeroRegistoPrevio = registoPrevio || null;
      admin.dataRegistoPrevio = registoPrevioData || null;
      admin.registoPrevioValidade = registoPrevioValidade || null;
      admin.corCorporativa = cor || null;
      admin.horaEntradaHabitual = documentRef.getElementById('perf_hora_entrada')?.value || '09:00';
      const tolerancia = documentRef.getElementById('perf_tolerancia_atraso')?.value;
      admin.toleranciaAtrasoMin = tolerancia !== '' && tolerancia != null ? parseInt(tolerancia, 10) : 15;
      admin.osModoWizard = documentRef.getElementById('perf_os_modo_wizard')?.checked || false;
      admin.contratoModoWizard = documentRef.getElementById('perf_contrato_modo_wizard')?.checked || false;
      admin.concelho = documentRef.getElementById('perf_concelho')?.value || null;
      admin.segurancaAtivo = documentRef.getElementById('perf_seguranca_ativo')?.checked || false;
      admin.segurosAtivo = documentRef.getElementById('perf_seguros_ativo')?.checked || false;
      admin.shstAtivo = documentRef.getElementById('perf_shst_ativo')?.checked || false;
      if (senha) admin.senha = senha;
      if (logoData !== undefined) admin.logo = logoData;
      if (window._perfCertificadoraLogoRemover) {
        admin.certificadoraLogo = null;
        window._perfCertificadoraLogoRemover = false;
      }
      if (window._perfCertificadoraLogoNova !== undefined) {
        admin.certificadoraLogo = window._perfCertificadoraLogoNova || null;
        window._perfCertificadoraLogoNova = undefined;
      }
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

    const fileInput = documentRef.getElementById('perf_logo');
    if (fileInput && fileInput.files && fileInput.files[0]) {
      const reader = new FileReader();
      reader.onload = function (ev) { aplicar(ev.target.result); };
      reader.readAsDataURL(fileInput.files[0]);
    } else {
      aplicar(undefined);
    }
  }

  window.TotalGestProfileSaveAdmin = { run: run };
})();
'''
MODULE.write_text(module, encoding='utf-8')

new = """                window.TotalGestProfileSaveAdmin.run({
                    document: document,
                    data: dados,
                    user: usuarioLogado,
                    name: nome,
                    password: senha,
                    getAdmin: adminAtual,
                    numberAlreadyUsed: _numeroJaUsado,
                    saveData: guardarDados,
                    closeModal: fecharModalPerfil,
                    applyHeaderConfig: aplicarConfigHeader,
                    renderAll: renderizarTudo,
                    alert: alert
                });
"""
app = app[:branch + len(branch_marker)] + new + app[next_branch:]

init_anchor = 'profileSaveDistributor: true'
assert app.count(init_anchor) == 1, app.count(init_anchor)
app = app.replace(init_anchor, init_anchor + ', profileSaveAdmin: true', 1)

shell_anchor = "    profileSaveDistributor: './assets/js/app-profile-save-distributor.js',\n"
assert shell.count(shell_anchor) == 1, shell.count(shell_anchor)
shell = shell.replace(shell_anchor, shell_anchor + "    profileSaveAdmin: './assets/js/app-profile-save-admin.js',\n", 1)
load_anchor = "    if (options.profileSaveDistributor === true) pedidos.push(MODULOS.profileSaveDistributor);\n"
assert shell.count(load_anchor) == 1, shell.count(load_anchor)
shell = shell.replace(load_anchor, load_anchor + "    if (options.profileSaveAdmin === true) pedidos.push(MODULOS.profileSaveAdmin);\n", 1)

assert "const CACHE = 'totalgest-v89';" in sw
sw = sw.replace("const CACHE = 'totalgest-v89';", "const CACHE = 'totalgest-v90';", 1)
sw_anchor = "  './assets/js/app-profile-save-distributor.js',\n"
assert sw.count(sw_anchor) == 1, sw.count(sw_anchor)
sw = sw.replace(sw_anchor, sw_anchor + "  './assets/js/app-profile-save-admin.js',\n", 1)

fn_end = app.index('// =============================================================\n        //  INICIALIZAÇÃO', fn)
fn_block = app[fn:fn_end]
assert fn_block.count('window.TotalGestProfileSaveAdmin.run({') == 1
for token in [
    "const anepc = document.getElementById('perf_anepc')?.value.trim() || '';",
    'window._perfCertificadoraLogoRemover',
    'window._perfCertificadoraLogoNova',
    "admin.segurancaAtivo = document.getElementById('perf_seguranca_ativo')?.checked || false;"
]:
    assert token not in fn_block, token
assert fn_block.count("            } else {\n") >= 1
assert shell.count('./assets/js/app-profile-save-admin.js') == 1
assert sw.count('./assets/js/app-profile-save-admin.js') == 1

APP.write_text(app, encoding='utf-8')
SHELL.write_text(shell, encoding='utf-8')
SW.write_text(sw, encoding='utf-8')
