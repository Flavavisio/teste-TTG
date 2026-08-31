from pathlib import Path

APP = Path('app.html')
SHELL = Path('assets/js/app-shell.js')
SW = Path('sw.js')
MODULE = Path('assets/js/app-card-visibility.js')

app = APP.read_text(encoding='utf-8')
shell = SHELL.read_text(encoding='utf-8')
sw = SW.read_text(encoding='utf-8')

marker = 'function ajustarVisibilidadeCards()'
assert app.count(marker) == 1, app.count(marker)
start = app.index(marker)
brace = app.index('{', start)

def scan_end(text, brace):
    depth = 0
    quote = None
    escape = False
    line_comment = False
    block_comment = False
    i = brace
    while i < len(text):
        c = text[i]
        n = text[i + 1] if i + 1 < len(text) else ''
        if line_comment:
            if c == '\n': line_comment = False
        elif block_comment:
            if c == '*' and n == '/': block_comment = False; i += 1
        elif quote:
            if escape: escape = False
            elif c == '\\': escape = True
            elif c == quote: quote = None
        else:
            if c == '/' and n == '/': line_comment = True; i += 1
            elif c == '/' and n == '*': block_comment = True; i += 1
            elif c in ('\"', "'"): quote = c
            elif c == '{': depth += 1
            elif c == '}':
                depth -= 1
                if depth == 0: return i + 1
            elif c == '`': raise AssertionError('unexpected template literal in ajustarVisibilidadeCards')
        i += 1
    raise AssertionError('unclosed ajustarVisibilidadeCards')

end = scan_end(app, brace)
old = app[start:end]
assert len(old.splitlines()) == 306, len(old.splitlines())
for token in [
    "document.querySelectorAll('.card-principal')",
    "usuarioLogado?.role === 'vendedor'",
    "usuarioLogado?.role === 'vigilante'",
    "adminAtual()?.ehDistribuidor",
    "cardName === 'agenda-obras'",
    "cardName === 'frota'",
    "cardName === 'contratos'",
    "localStorage.getItem('tg_aprovacao_ate_' + _admId)",
    "dados.pedidosRenovacao"
]:
    assert token in old, token

body = app[brace + 1:end - 1]
prefix = """/* Total Gest — política de visibilidade dos cartões principais. */
(function () {
  'use strict';

  function run(options) {
    const opts = options || {};
    const document = opts.document;
    const usuarioLogado = opts.user;
    const dados = opts.data;
    const localStorage = opts.localStorage;
    const _licencaValidaTenant = opts.licenseValid;
    const moduloFrotaAtivo = opts.moduleFleetActive;
    const adminDoUtilizador = opts.userAdmin;
    const _utilizadorTemVeiculo = opts.userHasVehicle;
    const moduloCrmAtivo = opts.moduleCrmActive;
    const moduloRondasAtivo = opts.moduleRoundsActive;
    const adminAtual = opts.currentAdmin;
    const moduloAssistAtivo = opts.moduleAssistActive;
    const moduloErpAtivo = opts.moduleErpActive;
    const moduloArmazemAtivo = opts.moduleWarehouseActive;
    const moduloContratosAtivo = opts.moduleContractsActive;
"""
suffix = """
  }

  window.TotalGestCardVisibility = { run: run };
})();
"""
MODULE.write_text(prefix + body + suffix, encoding='utf-8')

new = """function ajustarVisibilidadeCards() {
            window.TotalGestCardVisibility.run({
                document: document,
                user: usuarioLogado,
                data: dados,
                localStorage: localStorage,
                licenseValid: _licencaValidaTenant,
                moduleFleetActive: moduloFrotaAtivo,
                userAdmin: adminDoUtilizador,
                userHasVehicle: _utilizadorTemVeiculo,
                moduleCrmActive: moduloCrmAtivo,
                moduleRoundsActive: moduloRondasAtivo,
                currentAdmin: adminAtual,
                moduleAssistActive: moduloAssistAtivo,
                moduleErpActive: moduloErpAtivo,
                moduleWarehouseActive: moduloArmazemAtivo,
                moduleContractsActive: moduloContratosAtivo
            });
        }"""
app = app[:start] + new + app[end:]

init_anchor = 'profileSave: true'
assert app.count(init_anchor) == 1, app.count(init_anchor)
app = app.replace(init_anchor, init_anchor + ', cardVisibility: true', 1)

shell_anchor = "    profileSave: './assets/js/app-profile-save.js',\n"
assert shell.count(shell_anchor) == 1, shell.count(shell_anchor)
shell = shell.replace(shell_anchor, shell_anchor + "    cardVisibility: './assets/js/app-card-visibility.js',\n", 1)
load_anchor = "    if (options.profileSave === true) pedidos.push(MODULOS.profileSave);\n"
assert shell.count(load_anchor) == 1, shell.count(load_anchor)
shell = shell.replace(load_anchor, load_anchor + "    if (options.cardVisibility === true) pedidos.push(MODULOS.cardVisibility);\n", 1)

assert "const CACHE = 'totalgest-v92';" in sw
sw = sw.replace("const CACHE = 'totalgest-v92';", "const CACHE = 'totalgest-v93';", 1)
sw_anchor = "  './assets/js/app-profile-save.js',\n"
assert sw.count(sw_anchor) == 1, sw.count(sw_anchor)
sw = sw.replace(sw_anchor, sw_anchor + "  './assets/js/app-card-visibility.js',\n", 1)

new_start = app.index(marker)
new_end = scan_end(app, app.index('{', new_start))
new_block = app[new_start:new_end]
assert new_block.count('window.TotalGestCardVisibility.run({') == 1
for token in [".card-principal", "cardName === 'frota'", 'dados.pedidosRenovacao']:
    assert token not in new_block, token
assert shell.count('./assets/js/app-card-visibility.js') == 1
assert sw.count('./assets/js/app-card-visibility.js') == 1

APP.write_text(app, encoding='utf-8')
SHELL.write_text(shell, encoding='utf-8')
SW.write_text(sw, encoding='utf-8')
