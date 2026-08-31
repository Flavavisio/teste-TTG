from pathlib import Path

APP=Path('app.html'); SHELL=Path('assets/js/app-shell.js'); SW=Path('sw.js'); MOD=Path('assets/js/app-modal-artigo.js')
app=APP.read_text(encoding='utf-8'); shell=SHELL.read_text(encoding='utf-8'); sw=SW.read_text(encoding='utf-8')
modal_start=app.index('        function abrirModal(')
start_token="            } else if (entidade === 'artigo') {\n"
end_token="            } else if (entidade === 'obra') {\n"
start=app.index(start_token,modal_start); end=app.index(end_token,start)
block=app[start:end]; body=block[len(start_token):]
assert body.count('const marcas = _marcasTenant();')==1
assert body.count('html = `')==1
assert '_optsCategoria(' in body
assert 'UNIDADES_ARTIGO.map(' in body
render_body=body.replace('                html = `','                return `',1)
assert 'html = `' not in render_body
module="""/* Total Gest — formulário do modal de artigo. */
(function () {
  'use strict';
  function render(options) {
    const opts = options || {};
    const item = opts.item || null;
    const _marcasTenant = opts.marcasTenant;
    const _optsCategoria = opts.optsCategoria;
    const UNIDADES_ARTIGO = opts.unidadesArtigo || [];
__BODY__  }
  window.TotalGestModalArtigo = { render: render };
})();
""".replace('__BODY__',render_body)
MOD.write_text(module,encoding='utf-8')
replacement="""            } else if (entidade === 'artigo') {
                html = window.TotalGestModalArtigo.render({
                    item: item,
                    marcasTenant: _marcasTenant,
                    optsCategoria: _optsCategoria,
                    unidadesArtigo: UNIDADES_ARTIGO
                });
"""
app=app[:start]+replacement+app[end:]
assert app.count('modalArtigo: true')==0
anchor='modalRequisicao: true'; assert app.count(anchor)==1
app=app.replace(anchor,anchor+', modalArtigo: true',1)
shell_anchor="    modalRequisicao: './assets/js/app-modal-requisicao.js',\n"; assert shell.count(shell_anchor)==1
shell=shell.replace(shell_anchor,shell_anchor+"    modalArtigo: './assets/js/app-modal-artigo.js',\n",1)
load_anchor="    if (options.modalRequisicao === true) pedidos.push(MODULOS.modalRequisicao);\n"; assert shell.count(load_anchor)==1
shell=shell.replace(load_anchor,load_anchor+"    if (options.modalArtigo === true) pedidos.push(MODULOS.modalArtigo);\n",1)
assert "const CACHE = 'totalgest-v45';" in sw
sw=sw.replace("const CACHE = 'totalgest-v45';","const CACHE = 'totalgest-v46';",1)
sw_anchor="  './assets/js/app-modal-requisicao.js',\n"; assert sw.count(sw_anchor)==1
sw=sw.replace(sw_anchor,sw_anchor+"  './assets/js/app-modal-artigo.js',\n",1)
assert app.count('window.TotalGestModalArtigo.render({')==1
new_end=app.index(end_token,start); new_branch=app[start:new_end]
assert 'const marcas = _marcasTenant();' not in new_branch
assert 'html = `' not in new_branch
APP.write_text(app,encoding='utf-8'); SHELL.write_text(shell,encoding='utf-8'); SW.write_text(sw,encoding='utf-8')
