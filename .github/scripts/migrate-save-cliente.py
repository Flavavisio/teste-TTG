from pathlib import Path

APP = Path('app.html')
SHELL = Path('assets/js/app-shell.js')
SW = Path('sw.js')

app = APP.read_text(encoding='utf-8')
shell = SHELL.read_text(encoding='utf-8')
sw = SW.read_text(encoding='utf-8')

start_token = "            } else if (ent === 'cliente') {\n"
end_token = "            } else if (ent === 'servico') {\n"
assert app.count(start_token) == 1, app.count(start_token)
assert app.count(end_token) == 1, app.count(end_token)
start = app.index(start_token)
end = app.index(end_token, start)
old = app[start:end]
for token in [
    "nome: document.getElementById('c_nome').value.trim()",
    "const _NIF_CONSUMIDOR_FINAL = '999999990';",
    "(dados.clientes || []).find",
    "if (obj.portalAtivo && obj.nif === _NIF_CONSUMIDOR_FINAL)"
]:
    assert token in old, token

new = """            } else if (ent === 'cliente') {
                const _clienteResultado = window.TotalGestSaveFormCliente.prepare({
                    document: document,
                    data: dados,
                    user: usuarioLogado,
                    editingId: idEditando,
                    showAlert: alert
                });
                if (!_clienteResultado.ok) return;
                obj = _clienteResultado.value;
"""
app = app[:start] + new + app[end:]

anchor = 'saveFormFolha: true'
assert app.count(anchor) == 1, app.count(anchor)
app = app.replace(anchor, anchor + ', saveFormCliente: true', 1)

shell_anchor = "    saveFormFolha: './assets/js/app-save-form-folha.js',\n"
assert shell.count(shell_anchor) == 1, shell.count(shell_anchor)
shell = shell.replace(shell_anchor, shell_anchor + "    saveFormCliente: './assets/js/app-save-form-cliente.js',\n", 1)
load_anchor = "    if (options.saveFormFolha === true) pedidos.push(MODULOS.saveFormFolha);\n"
assert shell.count(load_anchor) == 1, shell.count(load_anchor)
shell = shell.replace(load_anchor, load_anchor + "    if (options.saveFormCliente === true) pedidos.push(MODULOS.saveFormCliente);\n", 1)

assert "const CACHE = 'totalgest-v61';" in sw
sw = sw.replace("const CACHE = 'totalgest-v61';", "const CACHE = 'totalgest-v62';", 1)
sw_anchor = "  './assets/js/app-save-form-folha.js',\n"
assert sw.count(sw_anchor) == 1, sw.count(sw_anchor)
sw = sw.replace(sw_anchor, sw_anchor + "  './assets/js/app-save-form-cliente.js',\n", 1)

assert app.count('window.TotalGestSaveFormCliente.prepare({') == 1
new_end = app.index(end_token, start)
new_block = app[start:new_end]
for token in [
    "document.getElementById('c_nome')",
    "const _NIF_CONSUMIDOR_FINAL",
    "(dados.clientes || []).find"
]:
    assert token not in new_block, token
assert shell.count('./assets/js/app-save-form-cliente.js') == 1
assert sw.count('./assets/js/app-save-form-cliente.js') == 1

APP.write_text(app, encoding='utf-8')
SHELL.write_text(shell, encoding='utf-8')
SW.write_text(sw, encoding='utf-8')
