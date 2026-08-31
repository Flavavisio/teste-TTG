from pathlib import Path

APP = Path('app.html')
SHELL = Path('assets/js/app-shell.js')
SW = Path('sw.js')

app = APP.read_text(encoding='utf-8')
shell = SHELL.read_text(encoding='utf-8')
sw = SW.read_text(encoding='utf-8')

start_token = "            const _tornouSeSubadmin = ent === 'funcionario'"
end_token = "        }\n        // Os clientes entram no Portal"
function_start = app.index('async function _salvarFormularioInterno(e)')
start = app.index(start_token, function_start)
end = app.index(end_token, start)
old = app[start:end]
for token in [
    "if (ent === 'funcionario' && (!isEdit || _tornouSeSubadmin) && obj.email && obj.senha)",
    "const _papelConta = obj.role === 'subadmin'",
    'criarUtilizadorAuth(obj.email, obj.senha, _papelConta',
    "if (ent === 'cliente' && obj.portalAtivo && obj.nif && obj.nif !== '999999990' && obj.senha)",
    'const _emailContaCliente = _emailFantasmaCliente(obj.nif, obj.adminId);',
    "criarUtilizadorAuth(_emailContaCliente, obj.senha, 'cliente'"
]:
    assert token in old, token

new = """            await window.TotalGestSaveFormAuth.run({
                entity: ent,
                data: dados,
                value: obj,
                isEdit: isEdit,
                oldEmployee: _funcAntesDeEditar,
                saveData: guardarDados,
                showAlert: alert,
                createAuth: criarUtilizadorAuth,
                clientTechnicalEmail: _emailFantasmaCliente
            });
"""
app = app[:start] + new + app[end:]

anchor = 'saveFormFinalize: true'
assert app.count(anchor) == 1, app.count(anchor)
app = app.replace(anchor, anchor + ', saveFormAuth: true', 1)

shell_anchor = "    saveFormFinalize: './assets/js/app-save-form-finalize.js',\n"
assert shell.count(shell_anchor) == 1, shell.count(shell_anchor)
shell = shell.replace(shell_anchor, shell_anchor + "    saveFormAuth: './assets/js/app-save-form-auth.js',\n", 1)
load_anchor = "    if (options.saveFormFinalize === true) pedidos.push(MODULOS.saveFormFinalize);\n"
assert shell.count(load_anchor) == 1, shell.count(load_anchor)
shell = shell.replace(load_anchor, load_anchor + "    if (options.saveFormAuth === true) pedidos.push(MODULOS.saveFormAuth);\n", 1)

assert "const CACHE = 'totalgest-v77';" in sw
sw = sw.replace("const CACHE = 'totalgest-v77';", "const CACHE = 'totalgest-v78';", 1)
sw_anchor = "  './assets/js/app-save-form-finalize.js',\n"
assert sw.count(sw_anchor) == 1, sw.count(sw_anchor)
sw = sw.replace(sw_anchor, sw_anchor + "  './assets/js/app-save-form-auth.js',\n", 1)

assert app.count('window.TotalGestSaveFormAuth.run({') == 1
new_end = app.index(end_token, start)
new_block = app[start:new_end]
for token in [
    'const _tornouSeSubadmin',
    'const _papelConta',
    'const _emailContaCliente',
    'criarUtilizadorAuth(obj.email',
    'criarUtilizadorAuth(_emailContaCliente'
]:
    assert token not in new_block, token
assert shell.count('./assets/js/app-save-form-auth.js') == 1
assert sw.count('./assets/js/app-save-form-auth.js') == 1

APP.write_text(app, encoding='utf-8')
SHELL.write_text(shell, encoding='utf-8')
SW.write_text(sw, encoding='utf-8')
