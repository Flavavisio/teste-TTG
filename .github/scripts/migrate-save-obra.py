from pathlib import Path

APP = Path('app.html')
SHELL = Path('assets/js/app-shell.js')
SW = Path('sw.js')

app = APP.read_text(encoding='utf-8')
shell = SHELL.read_text(encoding='utf-8')
sw = SW.read_text(encoding='utf-8')

start_token = "            } else if (ent === 'obra') {\n"
end_token = "            } else {\n                fecharModal();\n"
assert app.count(start_token) == 1, app.count(start_token)
assert app.count(end_token) >= 1, app.count(end_token)
start = app.index(start_token)
end = app.index(end_token, start)
old = app[start:end]

for token in [
    "dados.locais.push({",
    "_guardarArmazem('obras', obj, isEdit)",
    "tgConfirm('A obra passou a Ativa.",
    "criarOSdaObra(obraId)",
    "criarOSdaObra(novoObraId, true)"
]:
    assert token in old, token

new = """            } else if (ent === 'obra') {
                window.TotalGestSaveFormObra.run({
                    document: document,
                    data: dados,
                    user: usuarioLogado,
                    isEdit: isEdit,
                    editingId: idEditando,
                    generateId: gerarId,
                    showError: mostrarErro,
                    showAlert: alert,
                    saveWarehouse: _guardarArmazem,
                    confirm: tgConfirm,
                    createServiceOrder: criarOSdaObra
                });
                return;
"""
app = app[:start] + new + app[end:]

anchor = 'saveFormRequisicao: true'
assert app.count(anchor) == 1, app.count(anchor)
app = app.replace(anchor, anchor + ', saveFormObra: true', 1)

shell_anchor = "    saveFormRequisicao: './assets/js/app-save-form-requisicao.js',\n"
assert shell.count(shell_anchor) == 1
shell = shell.replace(shell_anchor, shell_anchor + "    saveFormObra: './assets/js/app-save-form-obra.js',\n", 1)
load_anchor = "    if (options.saveFormRequisicao === true) pedidos.push(MODULOS.saveFormRequisicao);\n"
assert shell.count(load_anchor) == 1
shell = shell.replace(load_anchor, load_anchor + "    if (options.saveFormObra === true) pedidos.push(MODULOS.saveFormObra);\n", 1)

assert "const CACHE = 'totalgest-v52';" in sw
sw = sw.replace("const CACHE = 'totalgest-v52';", "const CACHE = 'totalgest-v53';", 1)
sw_anchor = "  './assets/js/app-save-form-requisicao.js',\n"
assert sw.count(sw_anchor) == 1
sw = sw.replace(sw_anchor, sw_anchor + "  './assets/js/app-save-form-obra.js',\n", 1)

assert app.count('window.TotalGestSaveFormObra.run({') == 1
new_end = app.index(end_token, start)
new_branch = app[start:new_end]
for token in [
    "dados.locais.push({",
    "_guardarArmazem('obras'",
    "tgConfirm('A obra passou a Ativa.",
    "criarOSdaObra(obraId)"
]:
    assert token not in new_branch, token
assert shell.count('./assets/js/app-save-form-obra.js') == 1
assert sw.count('./assets/js/app-save-form-obra.js') == 1

APP.write_text(app, encoding='utf-8')
SHELL.write_text(shell, encoding='utf-8')
SW.write_text(sw, encoding='utf-8')
