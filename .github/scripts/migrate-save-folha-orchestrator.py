from pathlib import Path

APP = Path('app.html')
SHELL = Path('assets/js/app-shell.js')
SW = Path('sw.js')

app = APP.read_text(encoding='utf-8')
shell = SHELL.read_text(encoding='utf-8')
sw = SW.read_text(encoding='utf-8')

start_token = "            } else if (ent === 'folha') {\n"
end_token = "            } else if (ent === 'requisicao') {\n"
assert app.count(start_token) == 1, app.count(start_token)
assert app.count(end_token) == 1, app.count(end_token)
start = app.index(start_token)
end = app.index(end_token, start)
old = app[start:end]

for token in [
    'window.TotalGestSaveFormFolhaContext.prepare({',
    'await window.TotalGestSaveFormFolhaSignature.prepare({',
    'window.TotalGestSaveFormFolhaObject.prepare({',
    'window.TotalGestSaveFormFolhaAssist.prepare({',
    'window.TotalGestSaveFormFolhaConsumos.prepare({',
    'window.TotalGestSaveFormFolhaManutencao.apply({',
    'window.TotalGestSaveFormFolhaPonto.apply({'
]:
    assert token in old, token

new = """            } else if (ent === 'folha') {
                const _foResultado = await window.TotalGestSaveFormFolha.run({
                    document: document,
                    data: dados,
                    user: usuarioLogado,
                    generateId: gerarId,
                    showError: mostrarErro,
                    showAlert: alert,
                    hoursCorrectedManually: _foHorasCorrigidasManualmente,
                    hoursForServiceOrder: _horasPicadasOS,
                    hoursForWork: _horasPicadasObra,
                    editingId: idEditando,
                    captureSignature: capturarAssinatura,
                    uploadImage: _uploadImagemStorage,
                    isEdit: isEdit,
                    getToday: getDataHoje,
                    advancePeriodicity: avancarPeriodicidade,
                    notify: _notificarFuncionario,
                    extraMaterials: _foMatExtra
                });
                if (!_foResultado.ok) return;
                obj = _foResultado.value;
                _folhaConsumoPendente = _foResultado.pendingConsumption;
                _foMatExtra = [];
"""
app = app[:start] + new + app[end:]

anchor = 'saveFormFolhaPonto: true'
assert app.count(anchor) == 1, app.count(anchor)
app = app.replace(anchor, anchor + ', saveFormFolha: true', 1)

shell_anchor = "    saveFormFolhaPonto: './assets/js/app-save-form-folha-ponto.js',\n"
assert shell.count(shell_anchor) == 1, shell.count(shell_anchor)
shell = shell.replace(shell_anchor, shell_anchor + "    saveFormFolha: './assets/js/app-save-form-folha.js',\n", 1)
load_anchor = "    if (options.saveFormFolhaPonto === true) pedidos.push(MODULOS.saveFormFolhaPonto);\n"
assert shell.count(load_anchor) == 1, shell.count(load_anchor)
shell = shell.replace(load_anchor, load_anchor + "    if (options.saveFormFolha === true) pedidos.push(MODULOS.saveFormFolha);\n", 1)

assert "const CACHE = 'totalgest-v60';" in sw
sw = sw.replace("const CACHE = 'totalgest-v60';", "const CACHE = 'totalgest-v61';", 1)
sw_anchor = "  './assets/js/app-save-form-folha-ponto.js',\n"
assert sw.count(sw_anchor) == 1, sw.count(sw_anchor)
sw = sw.replace(sw_anchor, sw_anchor + "  './assets/js/app-save-form-folha.js',\n", 1)

assert app.count('window.TotalGestSaveFormFolha.run({') == 1
new_end = app.index(end_token, start)
new_block = app[start:new_end]
for token in [
    'window.TotalGestSaveFormFolhaContext.prepare({',
    'window.TotalGestSaveFormFolhaSignature.prepare({',
    'window.TotalGestSaveFormFolhaObject.prepare({',
    'window.TotalGestSaveFormFolhaAssist.prepare({',
    'window.TotalGestSaveFormFolhaConsumos.prepare({',
    'window.TotalGestSaveFormFolhaManutencao.apply({',
    'window.TotalGestSaveFormFolhaPonto.apply({'
]:
    assert token not in new_block, token
assert shell.count('./assets/js/app-save-form-folha.js') == 1
assert sw.count('./assets/js/app-save-form-folha.js') == 1

APP.write_text(app, encoding='utf-8')
SHELL.write_text(shell, encoding='utf-8')
SW.write_text(sw, encoding='utf-8')
