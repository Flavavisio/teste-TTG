from pathlib import Path

app_path=Path('app.html'); shell_path=Path('assets/js/app-shell.js'); sw_path=Path('sw.js')
app=app_path.read_text(encoding='utf-8'); shell=shell_path.read_text(encoding='utf-8'); sw=sw_path.read_text(encoding='utf-8')
start_token="            } else if (ent === 'artigo') {\n"
end_token="            } else if (ent === 'obra') {\n"
assert app.count(start_token)==1 and app.count(end_token)==1
start=app.index(start_token); end=app.index(end_token,start); old=app[start:end]
for token in ["document.getElementById('ar_nome')", "_guardarArmazem('artigos', obj, isEdit); return;"]:
    assert token in old, token
new="""            } else if (ent === 'artigo') {
                window.TotalGestSaveFormArtigo.run({
                    document: document,
                    user: usuarioLogado,
                    isEdit: isEdit,
                    showAlert: alert,
                    intVal: _intVal,
                    saveWarehouse: _guardarArmazem
                });
                return;
"""
app=app[:start]+new+app[end:]
anchor='saveFormFornecedor: true'; assert app.count(anchor)==1
app=app.replace(anchor,anchor+', saveFormArtigo: true',1)
shell_anchor="    saveFormFornecedor: './assets/js/app-save-form-fornecedor.js',\n"; assert shell.count(shell_anchor)==1
shell=shell.replace(shell_anchor,shell_anchor+"    saveFormArtigo: './assets/js/app-save-form-artigo.js',\n",1)
load_anchor="    if (options.saveFormFornecedor === true) pedidos.push(MODULOS.saveFormFornecedor);\n"; assert shell.count(load_anchor)==1
shell=shell.replace(load_anchor,load_anchor+"    if (options.saveFormArtigo === true) pedidos.push(MODULOS.saveFormArtigo);\n",1)
assert "const CACHE = 'totalgest-v50';" in sw
sw=sw.replace("const CACHE = 'totalgest-v50';","const CACHE = 'totalgest-v51';",1)
sw_anchor="  './assets/js/app-save-form-fornecedor.js',\n"; assert sw.count(sw_anchor)==1
sw=sw.replace(sw_anchor,sw_anchor+"  './assets/js/app-save-form-artigo.js',\n",1)
assert app.count('window.TotalGestSaveFormArtigo.run({')==1
new_end=app.index(end_token,start); new_branch=app[start:new_end]
assert "document.getElementById('ar_nome')" not in new_branch
assert "_guardarArmazem('artigos'" not in new_branch
app_path.write_text(app,encoding='utf-8'); shell_path.write_text(shell,encoding='utf-8'); sw_path.write_text(sw,encoding='utf-8')
