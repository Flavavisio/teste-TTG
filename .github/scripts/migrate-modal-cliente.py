from pathlib import Path

APP=Path('app.html')
SHELL=Path('assets/js/app-shell.js')
SW=Path('sw.js')
MOD=Path('assets/js/app-modal-cliente.js')
app=APP.read_text(encoding='utf-8')
shell=SHELL.read_text(encoding='utf-8')
sw=SW.read_text(encoding='utf-8')

modal_start=app.index('        function abrirModal(')
start_token="            } else if (entidade === 'cliente') {\n"
end_token="            } else if (entidade === 'servico') {\n"
start=app.index(start_token, modal_start)
end=app.index(end_token, start)
block=app[start:end]
assert block.count('html = `') == 1
assert 'moduloErpAtivo(adminAtual())' in block
rhs=block[block.index('html = ')+len('html = '):].strip()
assert rhs.startswith('`') and rhs.endswith('`;')
expression=rhs[:-1]

module="""/* Total Gest — formulário do modal de cliente. */
(function () {
  'use strict';

  function render(options) {
    const opts = options || {};
    const item = opts.item || null;
    const adminAtual = function () { return opts.admin || null; };
    const moduloErpAtivo = opts.moduloErpAtivo;

    return __EXPRESSION__;
  }

  window.TotalGestModalCliente = { render: render };
})();
""".replace('__EXPRESSION__', expression)
MOD.write_text(module, encoding='utf-8')

replacement="""            } else if (entidade === 'cliente') {
                html = window.TotalGestModalCliente.render({
                    item: item,
                    admin: adminAtual(),
                    moduloErpAtivo: moduloErpAtivo
                });
"""
app=app[:start]+replacement+app[end:]

if app.count('modalCliente: true') != 0:
    raise SystemExit('modalCliente já registado em app.html')
anchor='modalFuncionario: true'
if app.count(anchor) != 1:
    raise SystemExit(f'Âncora init inesperada: {app.count(anchor)}')
app=app.replace(anchor, anchor+', modalCliente: true', 1)

shell_anchor="    modalFuncionario: './assets/js/app-modal-funcionario.js',\n"
assert shell.count(shell_anchor)==1
shell=shell.replace(shell_anchor, shell_anchor+"    modalCliente: './assets/js/app-modal-cliente.js',\n",1)
load_anchor="    if (options.modalFuncionario === true) pedidos.push(MODULOS.modalFuncionario);\n"
assert shell.count(load_anchor)==1
shell=shell.replace(load_anchor, load_anchor+"    if (options.modalCliente === true) pedidos.push(MODULOS.modalCliente);\n",1)

assert "const CACHE = 'totalgest-v42';" in sw
sw=sw.replace("const CACHE = 'totalgest-v42';", "const CACHE = 'totalgest-v43';", 1)
sw_anchor="  './assets/js/app-modal-funcionario.js',\n"
assert sw.count(sw_anchor)==1
sw=sw.replace(sw_anchor, sw_anchor+"  './assets/js/app-modal-cliente.js',\n",1)

assert app.count('window.TotalGestModalCliente.render({')==1
new_end=app.index(end_token, start)
new_branch=app[start:new_end]
assert 'html = `' not in new_branch
assert shell.count("./assets/js/app-modal-cliente.js")==1
assert sw.count("./assets/js/app-modal-cliente.js")==1

APP.write_text(app, encoding='utf-8')
SHELL.write_text(shell, encoding='utf-8')
SW.write_text(sw, encoding='utf-8')
