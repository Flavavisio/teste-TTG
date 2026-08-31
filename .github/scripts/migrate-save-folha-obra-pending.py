from pathlib import Path

APP = Path('app.html')
SHELL = Path('assets/js/app-shell.js')
SW = Path('sw.js')

app = APP.read_text(encoding='utf-8')
shell = SHELL.read_text(encoding='utf-8')
sw = SW.read_text(encoding='utf-8')

start_token = "                if (_folhaObraPendente && _folhaObraPendente.obraId === obj.obraId) {\n"
end_token = "            }\n            try {\n                await guardarDados(dados);\n"
assert app.count(start_token) == 1, app.count(start_token)
start = app.index(start_token)
end = app.index(end_token, start)
old = app[start:end]
for token in [
    'const { obraId, terminou } = _folhaObraPendente;',
    '_folhaObraPendente = null;',
    "obraRec.estado = 'concluida';",
    'obraRec.dataConclusao = getDataHoje();',
    "obraRec.estado = 'suspensa';",
    'renderizarTudo();'
]:
    assert token in old, token

new = """                window.TotalGestSaveFormFolhaObraPending.apply({
                    value: obj,
                    pending: _folhaObraPendente,
                    data: dados,
                    clearPending: () => { _folhaObraPendente = null; },
                    getToday: getDataHoje,
                    saveData: guardarDados,
                    renderAll: renderizarTudo,
                    showAlert: alert
                });
"""
app = app[:start] + new + app[end:]

anchor = 'saveFormFolhaOsPending: true'
assert app.count(anchor) == 1, app.count(anchor)
app = app.replace(anchor, anchor + ', saveFormFolhaObraPending: true', 1)

shell_anchor = "    saveFormFolhaOsPending: './assets/js/app-save-form-folha-os-pending.js',\n"
assert shell.count(shell_anchor) == 1, shell.count(shell_anchor)
shell = shell.replace(shell_anchor, shell_anchor + "    saveFormFolhaObraPending: './assets/js/app-save-form-folha-obra-pending.js',\n", 1)
load_anchor = "    if (options.saveFormFolhaOsPending === true) pedidos.push(MODULOS.saveFormFolhaOsPending);\n"
assert shell.count(load_anchor) == 1, shell.count(load_anchor)
shell = shell.replace(load_anchor, load_anchor + "    if (options.saveFormFolhaObraPending === true) pedidos.push(MODULOS.saveFormFolhaObraPending);\n", 1)

assert "const CACHE = 'totalgest-v75';" in sw
sw = sw.replace("const CACHE = 'totalgest-v75';", "const CACHE = 'totalgest-v76';", 1)
sw_anchor = "  './assets/js/app-save-form-folha-os-pending.js',\n"
assert sw.count(sw_anchor) == 1, sw.count(sw_anchor)
sw = sw.replace(sw_anchor, sw_anchor + "  './assets/js/app-save-form-folha-obra-pending.js',\n", 1)

assert app.count('window.TotalGestSaveFormFolhaObraPending.apply({') == 1
new_end = app.index(end_token, start)
new_block = app[start:new_end]
for token in [
    'const { obraId, terminou } = _folhaObraPendente;',
    "obraRec.estado = 'concluida';",
    "obraRec.estado = 'suspensa';"
]:
    assert token not in new_block, token
assert shell.count('./assets/js/app-save-form-folha-obra-pending.js') == 1
assert sw.count('./assets/js/app-save-form-folha-obra-pending.js') == 1

APP.write_text(app, encoding='utf-8')
SHELL.write_text(shell, encoding='utf-8')
SW.write_text(sw, encoding='utf-8')
