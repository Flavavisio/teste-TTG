from pathlib import Path

APP=Path('app.html'); SHELL=Path('assets/js/app-shell.js'); SW=Path('sw.js'); MOD=Path('assets/js/app-modal-folha.js')
app=APP.read_text(encoding='utf-8'); shell=SHELL.read_text(encoding='utf-8'); sw=SW.read_text(encoding='utf-8')
modal_start=app.index('        function abrirModal(')
start_token="            } else if (entidade === 'folha') {\n"
end_token="            } else if (entidade === 'requisicao') {\n"
start=app.index(start_token,modal_start); end=app.index(end_token,start)
block=app[start:end]
assert block.count('html = `')==1
for token in ['dados.clientes','dados.locais','dados.obras','_clienteLabel(','_gerarOpcoesHoras(','_pessoasParaAtribuir(','usuarioLogado']:
    assert token in block, token
rhs=block[block.index('html = ')+len('html = '):].strip(); assert rhs.startswith('`') and rhs.endswith('`;'); expression=rhs[:-1]
module="""/* Total Gest — formulário do modal de folha de obra. */
(function () {
  'use strict';
  function render(options) {
    const opts = options || {};
    const item = opts.item || null;
    const dados = opts.data || {};
    const usuarioLogado = opts.user || null;
    const _clienteLabel = opts.clienteLabel;
    const _gerarOpcoesHoras = opts.gerarOpcoesHoras;
    const _pessoasParaAtribuir = opts.pessoasParaAtribuir;
    return __EXPRESSION__;
  }
  window.TotalGestModalFolha = { render: render };
})();
""".replace('__EXPRESSION__',expression)
MOD.write_text(module,encoding='utf-8')
replacement="""            } else if (entidade === 'folha') {
                html = window.TotalGestModalFolha.render({
                    item: item,
                    data: dados,
                    user: usuarioLogado,
                    clienteLabel: _clienteLabel,
                    gerarOpcoesHoras: _gerarOpcoesHoras,
                    pessoasParaAtribuir: _pessoasParaAtribuir
                });
"""
app=app[:start]+replacement+app[end:]
assert app.count('modalFolha: true')==0
anchor='modalArtigo: true'; assert app.count(anchor)==1; app=app.replace(anchor,anchor+', modalFolha: true',1)
shell_anchor="    modalArtigo: './assets/js/app-modal-artigo.js',\n"; assert shell.count(shell_anchor)==1
shell=shell.replace(shell_anchor,shell_anchor+"    modalFolha: './assets/js/app-modal-folha.js',\n",1)
load_anchor="    if (options.modalArtigo === true) pedidos.push(MODULOS.modalArtigo);\n"; assert shell.count(load_anchor)==1
shell=shell.replace(load_anchor,load_anchor+"    if (options.modalFolha === true) pedidos.push(MODULOS.modalFolha);\n",1)
assert "const CACHE = 'totalgest-v46';" in sw; sw=sw.replace("const CACHE = 'totalgest-v46';","const CACHE = 'totalgest-v47';",1)
sw_anchor="  './assets/js/app-modal-artigo.js',\n"; assert sw.count(sw_anchor)==1
sw=sw.replace(sw_anchor,sw_anchor+"  './assets/js/app-modal-folha.js',\n",1)
assert app.count('window.TotalGestModalFolha.render({')==1
new_end=app.index(end_token,start); assert 'html = `' not in app[start:new_end]
APP.write_text(app,encoding='utf-8'); SHELL.write_text(shell,encoding='utf-8'); SW.write_text(sw,encoding='utf-8')
