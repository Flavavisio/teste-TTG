from pathlib import Path

APP=Path('app.html'); SHELL=Path('assets/js/app-shell.js'); SW=Path('sw.js'); MOD=Path('assets/js/app-modal-servico.js')
app=APP.read_text(encoding='utf-8'); shell=SHELL.read_text(encoding='utf-8'); sw=SW.read_text(encoding='utf-8')
modal_start=app.index('        function abrirModal(')
start_token="            } else if (entidade === 'servico') {\n"
end_token="            } else if (entidade === 'folha') {\n"
start=app.index(start_token,modal_start); end=app.index(end_token,start)
block=app[start:end]; body=block[len(start_token):]
for token in ['getFuncionariosByAdmin(','dados.encarregados','dados.funcionarios','dados.clientes','_pessoasParaAtribuir(','escapeHtmlSimples(','getDataHoje()','_clienteLabel(','moduloContratosAtivo(','obrasAvancadoAtivo(','moduloArmazemAtivo(','adminAtual()']:
    assert token in body, token
assert body.count('html = ') >= 2
module="""/* Total Gest — formulário do modal de ordem de serviço. */
(function () {
  'use strict';
  function render(options) {
    const opts = options || {};
    const item = opts.item || null;
    const dados = opts.data || {};
    const usuarioLogado = opts.user || null;
    const _tenantId = function () { return opts.tenantId; };
    const getFuncionariosByAdmin = opts.getFuncionariosByAdmin;
    const _pessoasParaAtribuir = opts.pessoasParaAtribuir;
    const escapeHtmlSimples = opts.escapeHtmlSimples;
    const getDataHoje = opts.getDataHoje;
    const _clienteLabel = opts.clienteLabel;
    const moduloContratosAtivo = opts.moduloContratosAtivo;
    const obrasAvancadoAtivo = opts.obrasAvancadoAtivo;
    const moduloArmazemAtivo = opts.moduloArmazemAtivo;
    const adminAtual = function () { return opts.admin || null; };
    let html = '';
__BODY__    return html;
  }
  window.TotalGestModalServico = { render: render };
})();
""".replace('__BODY__',body)
MOD.write_text(module,encoding='utf-8')
replacement="""            } else if (entidade === 'servico') {
                html = window.TotalGestModalServico.render({
                    item: item,
                    data: dados,
                    user: usuarioLogado,
                    tenantId: _tenantId(),
                    admin: adminAtual(),
                    getFuncionariosByAdmin: getFuncionariosByAdmin,
                    pessoasParaAtribuir: _pessoasParaAtribuir,
                    escapeHtmlSimples: escapeHtmlSimples,
                    getDataHoje: getDataHoje,
                    clienteLabel: _clienteLabel,
                    moduloContratosAtivo: moduloContratosAtivo,
                    obrasAvancadoAtivo: obrasAvancadoAtivo,
                    moduloArmazemAtivo: moduloArmazemAtivo
                });
"""
app=app[:start]+replacement+app[end:]
assert app.count('modalServico: true')==0
anchor='modalFolha: true'; assert app.count(anchor)==1; app=app.replace(anchor,anchor+', modalServico: true',1)
shell_anchor="    modalFolha: './assets/js/app-modal-folha.js',\n"; assert shell.count(shell_anchor)==1
shell=shell.replace(shell_anchor,shell_anchor+"    modalServico: './assets/js/app-modal-servico.js',\n",1)
load_anchor="    if (options.modalFolha === true) pedidos.push(MODULOS.modalFolha);\n"; assert shell.count(load_anchor)==1
shell=shell.replace(load_anchor,load_anchor+"    if (options.modalServico === true) pedidos.push(MODULOS.modalServico);\n",1)
assert "const CACHE = 'totalgest-v47';" in sw; sw=sw.replace("const CACHE = 'totalgest-v47';","const CACHE = 'totalgest-v48';",1)
sw_anchor="  './assets/js/app-modal-folha.js',\n"; assert sw.count(sw_anchor)==1
sw=sw.replace(sw_anchor,sw_anchor+"  './assets/js/app-modal-servico.js',\n",1)
assert app.count('window.TotalGestModalServico.render({')==1
new_end=app.index(end_token,start); new_branch=app[start:new_end]
assert 'let funcOpts =' not in new_branch
assert 'const statusOpts =' not in new_branch
assert 'html = `' not in new_branch
APP.write_text(app,encoding='utf-8'); SHELL.write_text(shell,encoding='utf-8'); SW.write_text(sw,encoding='utf-8')
