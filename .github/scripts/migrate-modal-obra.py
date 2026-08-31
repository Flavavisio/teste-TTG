from pathlib import Path

APP=Path('app.html'); SHELL=Path('assets/js/app-shell.js'); SW=Path('sw.js'); MOD=Path('assets/js/app-modal-obra.js')
app=APP.read_text(encoding='utf-8'); shell=SHELL.read_text(encoding='utf-8'); sw=SW.read_text(encoding='utf-8')
modal_start=app.index('        function abrirModal(')
start_token="            } else if (entidade === 'obra') {\n"
end_token="            } else {\n                html = '<p>Funcionalidade em desenvolvimento.</p>';\n"
start=app.index(start_token,modal_start); end=app.index(end_token,start)
block=app[start:end]; body=block[len(start_token):]
for token in ['dados.clientes','dados.locais','dados.funcionarios','dados.encarregados','_tenantId()','_clienteLabel(','usuarioLogado','obrasAvancadoAtivo(adminAtual())','moduloCrmAtivo(adminAtual())']:
    assert token in body, token
assert body.count('html = `')==1
module="""/* Total Gest — formulário do modal de obra. */
(function () {
  'use strict';
  function render(options) {
    const opts = options || {};
    const item = opts.item || null;
    const dados = opts.data || {};
    const usuarioLogado = opts.user || null;
    const _tenantId = function () { return opts.tenantId; };
    const _clienteLabel = opts.clienteLabel;
    const obrasAvancadoAtivo = opts.obrasAvancadoAtivo;
    const moduloCrmAtivo = opts.moduloCrmAtivo;
    const adminAtual = function () { return opts.admin || null; };
    let html = '';
__BODY__    return html;
  }
  window.TotalGestModalObra = { render: render };
})();
""".replace('__BODY__',body)
MOD.write_text(module,encoding='utf-8')
replacement="""            } else if (entidade === 'obra') {
                html = window.TotalGestModalObra.render({
                    item: item,
                    data: dados,
                    user: usuarioLogado,
                    tenantId: _tenantId(),
                    admin: adminAtual(),
                    clienteLabel: _clienteLabel,
                    obrasAvancadoAtivo: obrasAvancadoAtivo,
                    moduloCrmAtivo: moduloCrmAtivo
                });
"""
app=app[:start]+replacement+app[end:]
assert app.count('modalObra: true')==0
anchor='modalServico: true'; assert app.count(anchor)==1; app=app.replace(anchor,anchor+', modalObra: true',1)
shell_anchor="    modalServico: './assets/js/app-modal-servico.js',\n"; assert shell.count(shell_anchor)==1
shell=shell.replace(shell_anchor,shell_anchor+"    modalObra: './assets/js/app-modal-obra.js',\n",1)
load_anchor="    if (options.modalServico === true) pedidos.push(MODULOS.modalServico);\n"; assert shell.count(load_anchor)==1
shell=shell.replace(load_anchor,load_anchor+"    if (options.modalObra === true) pedidos.push(MODULOS.modalObra);\n",1)
assert "const CACHE = 'totalgest-v48';" in sw; sw=sw.replace("const CACHE = 'totalgest-v48';","const CACHE = 'totalgest-v49';",1)
sw_anchor="  './assets/js/app-modal-servico.js',\n"; assert sw.count(sw_anchor)==1
sw=sw.replace(sw_anchor,sw_anchor+"  './assets/js/app-modal-obra.js',\n",1)
assert app.count('window.TotalGestModalObra.render({')==1
new_end=app.index(end_token,start); new_branch=app[start:new_end]
assert 'const cliOpts =' not in new_branch
assert 'html = `' not in new_branch
APP.write_text(app,encoding='utf-8'); SHELL.write_text(shell,encoding='utf-8'); SW.write_text(sw,encoding='utf-8')
