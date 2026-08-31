from pathlib import Path

APP = Path('app.html')
SHELL = Path('assets/js/app-shell.js')
SW = Path('sw.js')

app = APP.read_text(encoding='utf-8')
shell = SHELL.read_text(encoding='utf-8')
sw = SW.read_text(encoding='utf-8')

start_token = '                // Se a folha vem de uma OS ligada a um contrato, regista a manutenção automaticamente\n'
end_token = '                window.TotalGestSaveFormFolhaAssist.apply({\n'
assert app.count(start_token) == 1, app.count(start_token)
assert app.count(end_token) == 1, app.count(end_token)
start = app.index(start_token)
end = app.index(end_token, start)
old = app[start:end]
for token in [
    'if (!isEdit && obj.servicoId)',
    'dados.registosManutencao.push({',
    'cont.proximaManutencao = proximaData;',
    "_notificarFuncionario(cont.clienteId, '✅ Manutenção realizada'"
]:
    assert token in old, token

new = """                // Se a folha vem de uma OS ligada a um contrato, regista a manutenção automaticamente
                window.TotalGestSaveFormFolhaManutencao.apply({
                    data: dados,
                    sheet: obj,
                    isEdit: isEdit,
                    generateId: gerarId,
                    getToday: getDataHoje,
                    advancePeriodicity: avancarPeriodicidade,
                    notify: _notificarFuncionario
                });
"""
app = app[:start] + new + app[end:]

anchor = 'saveFormFolhaConsumos: true'
assert app.count(anchor) == 1, app.count(anchor)
app = app.replace(anchor, anchor + ', saveFormFolhaManutencao: true', 1)

shell_anchor = "    saveFormFolhaConsumos: './assets/js/app-save-form-folha-consumos.js',\n"
assert shell.count(shell_anchor) == 1
shell = shell.replace(shell_anchor, shell_anchor + "    saveFormFolhaManutencao: './assets/js/app-save-form-folha-manutencao.js',\n", 1)
load_anchor = "    if (options.saveFormFolhaConsumos === true) pedidos.push(MODULOS.saveFormFolhaConsumos);\n"
assert shell.count(load_anchor) == 1
shell = shell.replace(load_anchor, load_anchor + "    if (options.saveFormFolhaManutencao === true) pedidos.push(MODULOS.saveFormFolhaManutencao);\n", 1)

assert "const CACHE = 'totalgest-v58';" in sw
sw = sw.replace("const CACHE = 'totalgest-v58';", "const CACHE = 'totalgest-v59';", 1)
sw_anchor = "  './assets/js/app-save-form-folha-consumos.js',\n"
assert sw.count(sw_anchor) == 1
sw = sw.replace(sw_anchor, sw_anchor + "  './assets/js/app-save-form-folha-manutencao.js',\n", 1)

assert app.count('window.TotalGestSaveFormFolhaManutencao.apply({') == 1
new_end = app.index(end_token, start)
new_block = app[start:new_end]
for token in [
    'dados.registosManutencao.push({',
    'cont.proximaManutencao = proximaData;',
    "_notificarFuncionario(cont.clienteId, '✅ Manutenção realizada'"
]:
    assert token not in new_block, token
assert shell.count('./assets/js/app-save-form-folha-manutencao.js') == 1
assert sw.count('./assets/js/app-save-form-folha-manutencao.js') == 1

APP.write_text(app, encoding='utf-8')
SHELL.write_text(shell, encoding='utf-8')
SW.write_text(sw, encoding='utf-8')
