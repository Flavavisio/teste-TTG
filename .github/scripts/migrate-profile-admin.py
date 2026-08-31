from pathlib import Path

APP = Path('app.html')
SHELL = Path('assets/js/app-shell.js')
SW = Path('sw.js')
MODULE = Path('assets/js/app-profile-modal-admin.js')

app = APP.read_text(encoding='utf-8')
shell = SHELL.read_text(encoding='utf-8')
sw = SW.read_text(encoding='utf-8')

fn_marker = '        function abrirEditarPerfil() {'
start_marker = "            } else if (usuarioLogado.role === 'admin' || usuarioLogado.role === 'subadmin') {\n"
last_field = 'perf_contrato_modo_wizard'
tail_token = "                        ` : ''}\n                        </div>\n                    `;\n"
assert app.count(fn_marker) == 1, app.count(fn_marker)
fn = app.index(fn_marker)
start_branch = app.index(start_marker, fn)
start = start_branch + len(start_marker)
last = app.index(last_field, start)
tail = app.index(tail_token, last)
end = tail + len(tail_token)
old = app[start:end]

for token in [
    'const admin = adminAtual();',
    'const func = dados.funcionarios?.find',
    'campos.innerHTML = `',
    'FERIADOS_MUNICIPAIS',
    'moduloContratosAtivo(admin)',
    'perf_seguranca_ativo',
    'perf_contrato_modo_wizard'
]:
    assert token in old, token

prefix = '                campos.innerHTML = `'
suffix = '                    `;\n'
assert old.count(prefix) == 1, old.count(prefix)
assert old.endswith(suffix), repr(old[-140:])
template = old[old.index(prefix) + len(prefix):-len(suffix)]

module = """/* Total Gest — conteúdo do modal de perfil de admin/subadmin. */
(function () {
  'use strict';

  function render(options) {
    const opts = options || {};
    const admin = opts.admin || null;
    const func = opts.employee || null;
    const FERIADOS_MUNICIPAIS = opts.municipalHolidays || {};
    const moduloContratosAtivo = opts.contractsModuleEnabled;

    return `""" + template + """`;
  }

  window.TotalGestProfileModalAdmin = { render: render };
})();
"""
MODULE.write_text(module, encoding='utf-8')

new = """                campos.innerHTML = window.TotalGestProfileModalAdmin.render({
                    admin: adminAtual(),
                    employee: dados.funcionarios?.find(f => f.id === usuarioLogado.id) || null,
                    municipalHolidays: FERIADOS_MUNICIPAIS,
                    contractsModuleEnabled: moduloContratosAtivo
                });
"""
app = app[:start] + new + app[end:]

init_anchor = 'profileModalDistributor: true'
assert app.count(init_anchor) == 1, app.count(init_anchor)
app = app.replace(init_anchor, init_anchor + ', profileModalAdmin: true', 1)

shell_anchor = "    profileModalDistributor: './assets/js/app-profile-modal-distributor.js',\n"
assert shell.count(shell_anchor) == 1, shell.count(shell_anchor)
shell = shell.replace(shell_anchor, shell_anchor + "    profileModalAdmin: './assets/js/app-profile-modal-admin.js',\n", 1)
load_anchor = "    if (options.profileModalDistributor === true) pedidos.push(MODULOS.profileModalDistributor);\n"
assert shell.count(load_anchor) == 1, shell.count(load_anchor)
shell = shell.replace(load_anchor, load_anchor + "    if (options.profileModalAdmin === true) pedidos.push(MODULOS.profileModalAdmin);\n", 1)

assert "const CACHE = 'totalgest-v83';" in sw
sw = sw.replace("const CACHE = 'totalgest-v83';", "const CACHE = 'totalgest-v84';", 1)
sw_anchor = "  './assets/js/app-profile-modal-distributor.js',\n"
assert sw.count(sw_anchor) == 1, sw.count(sw_anchor)
sw = sw.replace(sw_anchor, sw_anchor + "  './assets/js/app-profile-modal-admin.js',\n", 1)

assert app.count('window.TotalGestProfileModalAdmin.render({') == 1
new_block = app[start:start + len(new)]
for token in ['campos.innerHTML = `', 'perf_contrato_modo_wizard', 'perf_seguranca_ativo']:
    assert token not in new_block, token
assert shell.count('./assets/js/app-profile-modal-admin.js') == 1
assert sw.count('./assets/js/app-profile-modal-admin.js') == 1

APP.write_text(app, encoding='utf-8')
SHELL.write_text(shell, encoding='utf-8')
SW.write_text(sw, encoding='utf-8')
