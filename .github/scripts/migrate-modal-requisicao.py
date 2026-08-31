from pathlib import Path

APP=Path('app.html'); SHELL=Path('assets/js/app-shell.js'); SW=Path('sw.js'); MOD=Path('assets/js/app-modal-requisicao.js')
app=APP.read_text(encoding='utf-8'); shell=SHELL.read_text(encoding='utf-8'); sw=SW.read_text(encoding='utf-8')
modal_start=app.index('        function abrirModal(')
start_token="            } else if (entidade === 'requisicao') {\n"
end_token="            } else if (entidade === 'fornecedor') {\n"
start=app.index(start_token,modal_start); end=app.index(end_token,start)
block=app[start:end]
body=block[len(start_token):]
assert body.count('const hoje = getDataHoje();') == 1
assert body.count('const itensHtml =') == 1
assert body.count('html = `') == 1
assert '_pessoasParaAtribuir(usuarioLogado.id)' in body
assert 'usuarioLogado.id' in body
# Preserva o corpo existente; apenas transforma a atribuição final de html em return.
render_body=body.replace('                html = `','                return `',1)
assert 'html = `' not in render_body

module="""/* Total Gest — formulário do modal de requisição. */
(function () {
  'use strict';

  function render(options) {
    const opts = options || {};
    const item = opts.item || null;
    const usuarioLogado = opts.user || null;
    const getDataHoje = opts.getDataHoje;
    const _pessoasParaAtribuir = opts.pessoasParaAtribuir;
__BODY__  }

  window.TotalGestModalRequisicao = { render: render };
})();
""".replace('__BODY__', render_body)
MOD.write_text(module,encoding='utf-8')

replacement="""            } else if (entidade === 'requisicao') {
                html = window.TotalGestModalRequisicao.render({
                    item: item,
                    user: usuarioLogado,
                    getDataHoje: getDataHoje,
                    pessoasParaAtribuir: _pessoasParaAtribuir
                });
"""
app=app[:start]+replacement+app[end:]

assert app.count('modalRequisicao: true')==0
anchor='modalFornecedor: true'; assert app.count(anchor)==1
app=app.replace(anchor,anchor+', modalRequisicao: true',1)

shell_anchor="    modalFornecedor: './assets/js/app-modal-fornecedor.js',\n"; assert shell.count(shell_anchor)==1
shell=shell.replace(shell_anchor,shell_anchor+"    modalRequisicao: './assets/js/app-modal-requisicao.js',\n",1)
load_anchor="    if (options.modalFornecedor === true) pedidos.push(MODULOS.modalFornecedor);\n"; assert shell.count(load_anchor)==1
shell=shell.replace(load_anchor,load_anchor+"    if (options.modalRequisicao === true) pedidos.push(MODULOS.modalRequisicao);\n",1)

assert "const CACHE = 'totalgest-v44';" in sw
sw=sw.replace("const CACHE = 'totalgest-v44';","const CACHE = 'totalgest-v45';",1)
sw_anchor="  './assets/js/app-modal-fornecedor.js',\n"; assert sw.count(sw_anchor)==1
sw=sw.replace(sw_anchor,sw_anchor+"  './assets/js/app-modal-requisicao.js',\n",1)

assert app.count('window.TotalGestModalRequisicao.render({')==1
new_end=app.index(end_token,start); new_branch=app[start:new_end]
assert 'const hoje = getDataHoje();' not in new_branch
assert 'const itensHtml =' not in new_branch
assert 'html = `' not in new_branch
assert shell.count('./assets/js/app-modal-requisicao.js')==1
assert sw.count('./assets/js/app-modal-requisicao.js')==1

APP.write_text(app,encoding='utf-8'); SHELL.write_text(shell,encoding='utf-8'); SW.write_text(sw,encoding='utf-8')
