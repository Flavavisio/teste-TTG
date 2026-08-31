from pathlib import Path

app_path = Path('app.html')
shell_path = Path('assets/js/app-shell.js')
sw_path = Path('sw.js')
app = app_path.read_text(encoding='utf-8')
shell = shell_path.read_text(encoding='utf-8')
sw = sw_path.read_text(encoding='utf-8')

start_at = app.index('        function _salvarFormularioInterno(')
start_token = "            } else if (ent === 'fornecedor') {\n"
end_token = "            } else if (ent === 'artigo') {\n"
start = app.index(start_token, start_at)
end = app.index(end_token, start)
old = app[start:end]
assert "document.getElementById('fr_nome')" in old
assert "_guardarArmazem('fornecedores', obj, isEdit); return;" in old

new = """            } else if (ent === 'fornecedor') {
                window.TotalGestSaveFormFornecedor.run({
                    document: document,
                    user: usuarioLogado,
                    isEdit: isEdit,
                    showAlert: alert,
                    saveWarehouse: _guardarArmazem
                });
                return;
"""
app = app[:start] + new + app[end:]

anchor = 'modalObra: true'
assert app.count(anchor) == 1
app = app.replace(anchor, anchor + ', saveFormFornecedor: true', 1)

shell_anchor = "    modalObra: './assets/js/app-modal-obra.js',\n"
assert shell.count(shell_anchor) == 1
shell = shell.replace(shell_anchor, shell_anchor + "    saveFormFornecedor: './assets/js/app-save-form-fornecedor.js',\n", 1)
load_anchor = "    if (options.modalObra === true) pedidos.push(MODULOS.modalObra);\n"
assert shell.count(load_anchor) == 1
shell = shell.replace(load_anchor, load_anchor + "    if (options.saveFormFornecedor === true) pedidos.push(MODULOS.saveFormFornecedor);\n", 1)

assert "const CACHE = 'totalgest-v49';" in sw
sw = sw.replace("const CACHE = 'totalgest-v49';", "const CACHE = 'totalgest-v50';", 1)
sw_anchor = "  './assets/js/app-modal-obra.js',\n"
assert sw.count(sw_anchor) == 1
sw = sw.replace(sw_anchor, sw_anchor + "  './assets/js/app-save-form-fornecedor.js',\n", 1)

assert app.count('window.TotalGestSaveFormFornecedor.run({') == 1
assert shell.count('./assets/js/app-save-form-fornecedor.js') == 1
assert sw.count('./assets/js/app-save-form-fornecedor.js') == 1

app_path.write_text(app, encoding='utf-8')
shell_path.write_text(shell, encoding='utf-8')
sw_path.write_text(sw, encoding='utf-8')
