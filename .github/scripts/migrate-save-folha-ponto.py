from pathlib import Path

APP = Path('app.html')
SHELL = Path('assets/js/app-shell.js')
SW = Path('sw.js')

app = APP.read_text(encoding='utf-8')
shell = SHELL.read_text(encoding='utf-8')
sw = SW.read_text(encoding='utf-8')

old = """                // A folha de obra pode ser criada diretamente (botão \"Folha\" na lista de OS),
                // sem passar pelo botão \"Saída\" da Agenda — nesse caso o registo de ponto desta
                // OS ficava aberto para sempre, e a próxima entrada noutra OS era bloqueada com
                // \"ainda tens uma entrada em aberto\", mesmo já tendo preenchido a folha. Ao
                // submeter a folha, fecha aqui qualquer entrada pendente desta mesma OS.
                if (obj.servicoId) {
                    const _pontoAbertoDestaOS = (dados.ponto || []).find(p => p.servicoId === obj.servicoId && p.funcionarioId === obj.funcionarioId && p.entrada && !p.saida);
                    if (_pontoAbertoDestaOS) _pontoAbertoDestaOS.saida = new Date().toTimeString().slice(0, 5);
                }
"""
assert app.count(old) == 1, app.count(old)
new = """                // A folha de obra pode ser criada diretamente (botão \"Folha\" na lista de OS),
                // sem passar pelo botão \"Saída\" da Agenda — fecha aqui qualquer entrada pendente da mesma OS.
                window.TotalGestSaveFormFolhaPonto.apply({
                    data: dados,
                    sheet: obj
                });
"""
app = app.replace(old, new, 1)

anchor = 'saveFormFolhaManutencao: true'
assert app.count(anchor) == 1, app.count(anchor)
app = app.replace(anchor, anchor + ', saveFormFolhaPonto: true', 1)

shell_anchor = "    saveFormFolhaManutencao: './assets/js/app-save-form-folha-manutencao.js',\n"
assert shell.count(shell_anchor) == 1, shell.count(shell_anchor)
shell = shell.replace(shell_anchor, shell_anchor + "    saveFormFolhaPonto: './assets/js/app-save-form-folha-ponto.js',\n", 1)
load_anchor = "    if (options.saveFormFolhaManutencao === true) pedidos.push(MODULOS.saveFormFolhaManutencao);\n"
assert shell.count(load_anchor) == 1, shell.count(load_anchor)
shell = shell.replace(load_anchor, load_anchor + "    if (options.saveFormFolhaPonto === true) pedidos.push(MODULOS.saveFormFolhaPonto);\n", 1)

assert "const CACHE = 'totalgest-v59';" in sw
sw = sw.replace("const CACHE = 'totalgest-v59';", "const CACHE = 'totalgest-v60';", 1)
sw_anchor = "  './assets/js/app-save-form-folha-manutencao.js',\n"
assert sw.count(sw_anchor) == 1, sw.count(sw_anchor)
sw = sw.replace(sw_anchor, sw_anchor + "  './assets/js/app-save-form-folha-ponto.js',\n", 1)

assert app.count('window.TotalGestSaveFormFolhaPonto.apply({') == 1
assert shell.count('./assets/js/app-save-form-folha-ponto.js') == 1
assert sw.count('./assets/js/app-save-form-folha-ponto.js') == 1

APP.write_text(app, encoding='utf-8')
SHELL.write_text(shell, encoding='utf-8')
SW.write_text(sw, encoding='utf-8')
