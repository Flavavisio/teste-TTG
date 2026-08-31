from pathlib import Path

APP = Path('app.html')
SHELL = Path('assets/js/app-shell.js')
SW = Path('sw.js')

app = APP.read_text(encoding='utf-8')
shell = SHELL.read_text(encoding='utf-8')
sw = SW.read_text(encoding='utf-8')

branch_start_token = "            if (ent === 'funcionario') {\n"
branch_end_token = "            } else if (ent === 'cliente') {\n"
assert app.count(branch_start_token) == 1, app.count(branch_start_token)
assert app.count(branch_end_token) == 1, app.count(branch_end_token)
branch_start = app.index(branch_start_token)
branch_end = app.index(branch_end_token, branch_start)
branch = app[branch_start:branch_end]

special_token = "                if (!isEdit && _roleTipo === 'encarregado') {\n"
assert branch.count(special_token) == 1, branch.count(special_token)
normal_start = app.index("                obj = {\n", branch_start)
assert normal_start < branch_end
old = app[normal_start:branch_end]

for token in [
    "role: (!isEdit && _roleTipo === 'subadmin')",
    "const _fSenhaVal = document.getElementById('f_senha').value;",
    "const ocupado = veiculoJaAtribuido(obj.veiculoId, 'func', isEdit ? idEditando : null);",
    "if (await emailJaRegistado(obj.email, isEdit ? idEditando : null))"
]:
    assert token in old, token

new = """                const _funcResultado = await window.TotalGestSaveFormFuncionario.prepare({
                    document: document,
                    data: dados,
                    user: usuarioLogado,
                    isEdit: isEdit,
                    editingId: idEditando,
                    roleType: _roleTipo,
                    vehicleAssigned: veiculoJaAtribuido,
                    emailRegistered: emailJaRegistado,
                    showAlert: alert
                });
                if (!_funcResultado.ok) return;
                obj = _funcResultado.value;
"""
app = app[:normal_start] + new + app[branch_end:]

init_anchor = 'saveFormCliente: true'
assert app.count(init_anchor) == 1, app.count(init_anchor)
app = app.replace(init_anchor, init_anchor + ', saveFormFuncionario: true', 1)

shell_anchor = "    saveFormCliente: './assets/js/app-save-form-cliente.js',\n"
assert shell.count(shell_anchor) == 1, shell.count(shell_anchor)
shell = shell.replace(shell_anchor, shell_anchor + "    saveFormFuncionario: './assets/js/app-save-form-funcionario.js',\n", 1)
load_anchor = "    if (options.saveFormCliente === true) pedidos.push(MODULOS.saveFormCliente);\n"
assert shell.count(load_anchor) == 1, shell.count(load_anchor)
shell = shell.replace(load_anchor, load_anchor + "    if (options.saveFormFuncionario === true) pedidos.push(MODULOS.saveFormFuncionario);\n", 1)

assert "const CACHE = 'totalgest-v62';" in sw
sw = sw.replace("const CACHE = 'totalgest-v62';", "const CACHE = 'totalgest-v63';", 1)
sw_anchor = "  './assets/js/app-save-form-cliente.js',\n"
assert sw.count(sw_anchor) == 1, sw.count(sw_anchor)
sw = sw.replace(sw_anchor, sw_anchor + "  './assets/js/app-save-form-funcionario.js',\n", 1)

new_branch_end = app.index(branch_end_token, branch_start)
new_branch = app[branch_start:new_branch_end]
assert new_branch.count('window.TotalGestSaveFormFuncionario.prepare({') == 1
for token in [
    "role: (!isEdit && _roleTipo === 'subadmin')",
    "const _fSenhaVal = document.getElementById('f_senha').value;",
    "if (await emailJaRegistado(obj.email, isEdit ? idEditando : null))"
]:
    assert token not in new_branch, token
assert "if (!isEdit && _roleTipo === 'encarregado')" in new_branch
assert shell.count('./assets/js/app-save-form-funcionario.js') == 1
assert sw.count('./assets/js/app-save-form-funcionario.js') == 1

APP.write_text(app, encoding='utf-8')
SHELL.write_text(shell, encoding='utf-8')
SW.write_text(sw, encoding='utf-8')
