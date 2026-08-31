from pathlib import Path
APP=Path('app.html'); SHELL=Path('assets/js/app-shell.js'); SW=Path('sw.js'); MOD=Path('assets/js/app-modal-fornecedor.js')
app=APP.read_text(encoding='utf-8'); shell=SHELL.read_text(encoding='utf-8'); sw=SW.read_text(encoding='utf-8')
modal_start=app.index('        function abrirModal(')
start_token="            } else if (entidade === 'fornecedor') {\n"; end_token="            } else if (entidade === 'artigo') {\n"
start=app.index(start_token,modal_start); end=app.index(end_token,start); block=app[start:end]
assert block.count('html = `')==1
rhs=block[block.index('html = ')+len('html = '):].strip(); assert rhs.startswith('`') and rhs.endswith('`;'); expression=rhs[:-1]
module="""/* Total Gest — formulário do modal de fornecedor. */
(function () {
  'use strict';
  function render(options) {
    const opts = options || {};
    const item = opts.item || null;
    return __EXPRESSION__;
  }
  window.TotalGestModalFornecedor = { render: render };
})();
""".replace('__EXPRESSION__',expression)
MOD.write_text(module,encoding='utf-8')
replacement="""            } else if (entidade === 'fornecedor') {
                html = window.TotalGestModalFornecedor.render({ item: item });
"""
app=app[:start]+replacement+app[end:]
assert app.count('modalFornecedor: true')==0
anchor='modalCliente: true'; assert app.count(anchor)==1; app=app.replace(anchor,anchor+', modalFornecedor: true',1)
shell_anchor="    modalCliente: './assets/js/app-modal-cliente.js',\n"; assert shell.count(shell_anchor)==1
shell=shell.replace(shell_anchor,shell_anchor+"    modalFornecedor: './assets/js/app-modal-fornecedor.js',\n",1)
load_anchor="    if (options.modalCliente === true) pedidos.push(MODULOS.modalCliente);\n"; assert shell.count(load_anchor)==1
shell=shell.replace(load_anchor,load_anchor+"    if (options.modalFornecedor === true) pedidos.push(MODULOS.modalFornecedor);\n",1)
assert "const CACHE = 'totalgest-v43';" in sw; sw=sw.replace("const CACHE = 'totalgest-v43';","const CACHE = 'totalgest-v44';",1)
sw_anchor="  './assets/js/app-modal-cliente.js',\n"; assert sw.count(sw_anchor)==1
sw=sw.replace(sw_anchor,sw_anchor+"  './assets/js/app-modal-fornecedor.js',\n",1)
assert app.count('window.TotalGestModalFornecedor.render({ item: item })')==1
new_end=app.index(end_token,start); assert 'html = `' not in app[start:new_end]
APP.write_text(app,encoding='utf-8'); SHELL.write_text(shell,encoding='utf-8'); SW.write_text(sw,encoding='utf-8')
