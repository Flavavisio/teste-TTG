from pathlib import Path

APP = Path('app.html')
SHELL = Path('assets/js/app-shell.js')
SW = Path('sw.js')
MODULE = Path('assets/js/app-profile-modal-admin.js')

app = APP.read_text(encoding='utf-8')
shell = SHELL.read_text(encoding='utf-8')
sw = SW.read_text(encoding='utf-8')


def scan_quoted(text, pos, quote):
    assert text[pos] == quote
    i = pos + 1
    while i < len(text):
        if text[i] == '\\':
            i += 2
            continue
        if text[i] == quote:
            return i
        i += 1
    raise AssertionError('string sem fecho')


def scan_template(text, pos):
    assert text[pos] == '`'
    i = pos + 1
    while i < len(text):
        c = text[i]
        if c == '\\':
            i += 2
            continue
        if c == '`':
            return i
        if c == '$' and i + 1 < len(text) and text[i + 1] == '{':
            i = scan_expression(text, i + 2)
            continue
        i += 1
    raise AssertionError('template sem fecho')


def scan_expression(text, pos):
    depth = 1
    i = pos
    while i < len(text):
        c = text[i]
        if c in ("'", '"'):
            i = scan_quoted(text, i, c) + 1
            continue
        if c == '`':
            i = scan_template(text, i) + 1
            continue
        if c == '/' and i + 1 < len(text) and text[i + 1] == '/':
            nl = text.find('\n', i + 2)
            i = len(text) if nl < 0 else nl + 1
            continue
        if c == '/' and i + 1 < len(text) and text[i + 1] == '*':
            end = text.find('*/', i + 2)
            assert end >= 0, 'comentário sem fecho'
            i = end + 2
            continue
        if c == '{':
            depth += 1
        elif c == '}':
            depth -= 1
            if depth == 0:
                return i + 1
        i += 1
    raise AssertionError('expressão de template sem fecho')


fn_marker = '        function abrirEditarPerfil() {'
start_marker = "            } else if (usuarioLogado.role === 'admin' || usuarioLogado.role === 'subadmin') {\n"
assert app.count(fn_marker) == 1, app.count(fn_marker)
fn = app.index(fn_marker)
start_branch = app.index(start_marker, fn)
start = start_branch + len(start_marker)

prefix = '                campos.innerHTML = `'
render_stmt = app.index(prefix, start)
assert render_stmt > start
open_tick = render_stmt + len(prefix) - 1
close_tick = scan_template(app, open_tick)
end = close_tick + 1
while end < len(app) and app[end] in ' \t':
    end += 1
assert app[end] == ';', repr(app[end:end + 40])
end += 1
if app.startswith('\r\n', end):
    end += 2
elif app.startswith('\n', end):
    end += 1

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

template = app[open_tick + 1:close_tick]
assert template.count('perf_contrato_modo_wizard') == 1
assert template.count('perf_seguranca_ativo') == 1

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
