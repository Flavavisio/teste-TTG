from pathlib import Path

APP = Path('app.html')
SHELL = Path('assets/js/app-shell.js')
SW = Path('sw.js')

app = APP.read_text(encoding='utf-8')
shell = SHELL.read_text(encoding='utf-8')
sw = SW.read_text(encoding='utf-8')

start_token = "            } else if (ent === 'requisicao') {\n"
end_token = "            } else if (ent === 'fornecedor') {\n"
assert app.count(start_token) == 1, app.count(start_token)
assert app.count(end_token) == 1, app.count(end_token)
start = app.index(start_token)
end = app.index(end_token, start)
old = app[start:end]

for token in [
    "document.querySelectorAll('.item-produto')",
    "new FileReader()",
    "function finalizarRequisicao(objFinal)",
    "dados.requisicoes = lista",
    "guardarDados(dados)",
    "renderizarTudo()"
]:
    assert token in old, token

new = """            } else if (ent === 'requisicao') {
                window.TotalGestSaveFormRequisicao.run({
                    document: document,
                    data: dados,
                    user: usuarioLogado,
                    isEdit: isEdit,
                    editingId: idEditando,
                    generateId: gerarId,
                    saveData: guardarDados,
                    closeModal: fecharModal,
                    renderAll: renderizarTudo,
                    showAlert: alert,
                    FileReader: FileReader
                });
                return;
"""
app = app[:start] + new + app[end:]

anchor = 'saveFormArtigo: true'
assert app.count(anchor) == 1, app.count(anchor)
app = app.replace(anchor, anchor + ', saveFormRequisicao: true', 1)

shell_anchor = "    saveFormArtigo: './assets/js/app-save-form-artigo.js',\n"
assert shell.count(shell_anchor) == 1
shell = shell.replace(shell_anchor, shell_anchor + "    saveFormRequisicao: './assets/js/app-save-form-requisicao.js',\n", 1)
load_anchor = "    if (options.saveFormArtigo === true) pedidos.push(MODULOS.saveFormArtigo);\n"
assert shell.count(load_anchor) == 1
shell = shell.replace(load_anchor, load_anchor + "    if (options.saveFormRequisicao === true) pedidos.push(MODULOS.saveFormRequisicao);\n", 1)

assert "const CACHE = 'totalgest-v51';" in sw
sw = sw.replace("const CACHE = 'totalgest-v51';", "const CACHE = 'totalgest-v52';", 1)
sw_anchor = "  './assets/js/app-save-form-artigo.js',\n"
assert sw.count(sw_anchor) == 1
sw = sw.replace(sw_anchor, sw_anchor + "  './assets/js/app-save-form-requisicao.js',\n", 1)

assert app.count('window.TotalGestSaveFormRequisicao.run({') == 1
new_end = app.index(end_token, start)
new_branch = app[start:new_end]
for token in [
    "document.querySelectorAll('.item-produto')",
    "new FileReader()",
    "function finalizarRequisicao(objFinal)",
    "dados.requisicoes = lista"
]:
    assert token not in new_branch, token
assert shell.count('./assets/js/app-save-form-requisicao.js') == 1
assert sw.count('./assets/js/app-save-form-requisicao.js') == 1

APP.write_text(app, encoding='utf-8')
SHELL.write_text(shell, encoding='utf-8')
SW.write_text(sw, encoding='utf-8')
