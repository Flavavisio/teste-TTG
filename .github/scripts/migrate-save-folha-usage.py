from pathlib import Path

APP = Path('app.html')
SHELL = Path('assets/js/app-shell.js')
SW = Path('sw.js')

app = APP.read_text(encoding='utf-8')
shell = SHELL.read_text(encoding='utf-8')
sw = SW.read_text(encoding='utf-8')

start_token = "            if (ent === 'folha') {\n                const folhaId = isEdit ? idEditando : obj.id;\n"
end_token = "                if (_folhaOSPendente && _folhaOSPendente.osId === obj.servicoId) {\n"
assert app.count(start_token) == 1, app.count(start_token)
start = app.index(start_token)
end = app.index(end_token, start)
old = app[start:end]
for token in [
    '_aplicarConsumoFolha(folhaId, obj.obraId || null, _folhaConsumoPendente);',
    '_folhaConsumoPendente = [];',
    '(dados.ponto || []).forEach',
    '(dados.obraPontoLonga || []).forEach'
]:
    assert token in old, token

new = """            if (ent === 'folha') {
                window.TotalGestSaveFormFolhaUsage.apply({
                    data: dados,
                    value: obj,
                    isEdit: isEdit,
                    editingId: idEditando,
                    pendingConsumption: _folhaConsumoPendente,
                    pendingWork: _folhaObraPendente,
                    applyConsumption: _aplicarConsumoFolha
                });
                _folhaConsumoPendente = [];
"""
app = app[:start] + new + app[end:]

anchor = 'saveFormServicoNotifications: true'
assert app.count(anchor) == 1, app.count(anchor)
app = app.replace(anchor, anchor + ', saveFormFolhaUsage: true', 1)

shell_anchor = "    saveFormServicoNotifications: './assets/js/app-save-form-servico-notifications.js',\n"
assert shell.count(shell_anchor) == 1, shell.count(shell_anchor)
shell = shell.replace(shell_anchor, shell_anchor + "    saveFormFolhaUsage: './assets/js/app-save-form-folha-usage.js',\n", 1)
load_anchor = "    if (options.saveFormServicoNotifications === true) pedidos.push(MODULOS.saveFormServicoNotifications);\n"
assert shell.count(load_anchor) == 1, shell.count(load_anchor)
shell = shell.replace(load_anchor, load_anchor + "    if (options.saveFormFolhaUsage === true) pedidos.push(MODULOS.saveFormFolhaUsage);\n", 1)

assert "const CACHE = 'totalgest-v73';" in sw
sw = sw.replace("const CACHE = 'totalgest-v73';", "const CACHE = 'totalgest-v74';", 1)
sw_anchor = "  './assets/js/app-save-form-servico-notifications.js',\n"
assert sw.count(sw_anchor) == 1, sw.count(sw_anchor)
sw = sw.replace(sw_anchor, sw_anchor + "  './assets/js/app-save-form-folha-usage.js',\n", 1)

assert app.count('window.TotalGestSaveFormFolhaUsage.apply({') == 1
new_end = app.index(end_token, start)
new_block = app[start:new_end]
assert '(dados.ponto || []).forEach' not in new_block
assert '(dados.obraPontoLonga || []).forEach' not in new_block
assert shell.count('./assets/js/app-save-form-folha-usage.js') == 1
assert sw.count('./assets/js/app-save-form-folha-usage.js') == 1

APP.write_text(app, encoding='utf-8')
SHELL.write_text(shell, encoding='utf-8')
SW.write_text(sw, encoding='utf-8')
