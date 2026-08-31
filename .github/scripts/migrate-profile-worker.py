from pathlib import Path

APP = Path('app.html')
SHELL = Path('assets/js/app-shell.js')
SW = Path('sw.js')
MODULE = Path('assets/js/app-profile-modal-worker.js')

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
            assert end >= 0
            i = end + 2
            continue
        if c == '{':
            depth += 1
        elif c == '}':
            depth -= 1
            if depth == 0:
                return i + 1
        i += 1
    raise AssertionError('expressão sem fecho')


fn_marker = 'function abrirEditarPerfil() {'
assert app.count(fn_marker) == 1, app.count(fn_marker)
fn = app.index(fn_marker)
start_marker = "            } else {\n                const func = dados.funcionarios?.find(f => f.id === usuarioLogado.id) || dados.encarregados?.find(e => e.id === usuarioLogado.id);\n"
branch = app.index(start_marker, fn)
assert branch < app.index("            overlay.classList.add('open');", fn)
start = branch + len("            } else {\n")
end_marker = "            }\n            overlay.classList.add('open');"
end = app.index(end_marker, start)
old = app[start:end]

for token in [
    'const func = dados.funcionarios?.find',
    'if (!func) return;',
    'const _fmtData =',
    'const _apoliceHtml =',
    'const _saudeHtml =',
    'campos.innerHTML = `',
    "usuarioLogado.role === 'subadmin'",
    "usuarioLogado.role === 'encarregado'"
]:
    assert token in old, token

prefix = '                campos.innerHTML = `'
render_stmt = old.index(prefix)
open_tick = render_stmt + len(prefix) - 1
close_tick = scan_template(old, open_tick)
template = old[open_tick + 1:close_tick]
assert template.count('usuarioLogado.role') == 2, template.count('usuarioLogado.role')
template = template.replace('usuarioLogado.role', 'role')

module = """/* Total Gest — conteúdo do modal de perfil de funcionário/encarregado. */
(function () {
  'use strict';

  function render(options) {
    const opts = options || {};
    const func = opts.employee || null;
    const role = opts.role || '';
    if (!func) return null;

    const _fmtData = (d) => d ? new Date(d + 'T00:00:00').toLocaleDateString('pt-PT') : null;
    const _apoliceHtml = (func.apoliceNumero || func.apoliceSeguradora || func.apoliceValidade) ? `
                        <div class="ff-secao ff-tint-doc">
                            <div class="ff-secao-head"><i class="fas fa-shield-halved"></i> Apólice de Seguro de Acidentes de Trabalho</div>
                            <div class="ff-secao-body">
                                <div class="form-group"><label>Número da apólice</label><input type="text" value="${func.apoliceNumero || '—'}" disabled style="background:#e9edf2;" /></div>
                                <div class="form-group"><label>Seguradora</label><input type="text" value="${func.apoliceSeguradora || '—'}" disabled style="background:#e9edf2;" /></div>
                                <div class="form-group"><label>Validade</label><input type="text" value="${_fmtData(func.apoliceValidade) || '—'}" disabled style="background:#e9edf2;" /></div>
                            </div>
                        </div>` : '';
    const _saudeHtml = (func.saudeApoliceNumero || func.saudeApoliceSeguradora || func.saudeApoliceValidade) ? `
                        <div class="ff-secao ff-tint-doc">
                            <div class="ff-secao-head"><i class="fas fa-heart-pulse"></i> Seguro de Saúde</div>
                            <div class="ff-secao-body">
                                <div class="form-group"><label>Número da apólice</label><input type="text" value="${func.saudeApoliceNumero || '—'}" disabled style="background:#e9edf2;" /></div>
                                <div class="form-group"><label>Seguradora</label><input type="text" value="${func.saudeApoliceSeguradora || '—'}" disabled style="background:#e9edf2;" /></div>
                                <div class="form-group"><label>Validade</label><input type="text" value="${_fmtData(func.saudeApoliceValidade) || '—'}" disabled style="background:#e9edf2;" /></div>
                            </div>
                        </div>` : '';

    return `""" + template + """`;
  }

  window.TotalGestProfileModalWorker = { render: render };
})();
"""
MODULE.write_text(module, encoding='utf-8')

new = """                const _perfilColaborador = window.TotalGestProfileModalWorker.render({
                    employee: dados.funcionarios?.find(f => f.id === usuarioLogado.id) || dados.encarregados?.find(e => e.id === usuarioLogado.id) || null,
                    role: usuarioLogado.role
                });
                if (_perfilColaborador == null) return;
                campos.innerHTML = _perfilColaborador;
"""
app = app[:start] + new + app[end:]

init_anchor = 'profileModalAdmin: true'
assert app.count(init_anchor) == 1, app.count(init_anchor)
app = app.replace(init_anchor, init_anchor + ', profileModalWorker: true', 1)

shell_anchor = "    profileModalAdmin: './assets/js/app-profile-modal-admin.js',\n"
assert shell.count(shell_anchor) == 1, shell.count(shell_anchor)
shell = shell.replace(shell_anchor, shell_anchor + "    profileModalWorker: './assets/js/app-profile-modal-worker.js',\n", 1)
load_anchor = "    if (options.profileModalAdmin === true) pedidos.push(MODULOS.profileModalAdmin);\n"
assert shell.count(load_anchor) == 1, shell.count(load_anchor)
shell = shell.replace(load_anchor, load_anchor + "    if (options.profileModalWorker === true) pedidos.push(MODULOS.profileModalWorker);\n", 1)

assert "const CACHE = 'totalgest-v84';" in sw
sw = sw.replace("const CACHE = 'totalgest-v84';", "const CACHE = 'totalgest-v85';", 1)
sw_anchor = "  './assets/js/app-profile-modal-admin.js',\n"
assert sw.count(sw_anchor) == 1, sw.count(sw_anchor)
sw = sw.replace(sw_anchor, sw_anchor + "  './assets/js/app-profile-modal-worker.js',\n", 1)

assert app.count('window.TotalGestProfileModalWorker.render({') == 1
fn_end = app.index("\n        }", fn)
fn_block = app[fn:fn_end]
for token in ['const _apoliceHtml =', 'const _saudeHtml =', 'perf_foto_placeholder', '_ativarNotificacoesPush()']:
    assert token not in fn_block, token
assert shell.count('./assets/js/app-profile-modal-worker.js') == 1
assert sw.count('./assets/js/app-profile-modal-worker.js') == 1

APP.write_text(app, encoding='utf-8')
SHELL.write_text(shell, encoding='utf-8')
SW.write_text(sw, encoding='utf-8')
