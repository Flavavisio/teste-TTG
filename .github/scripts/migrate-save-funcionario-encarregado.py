from pathlib import Path

APP = Path('app.html')
SHELL = Path('assets/js/app-shell.js')
SW = Path('sw.js')

app = APP.read_text(encoding='utf-8')
shell = SHELL.read_text(encoding='utf-8')
sw = SW.read_text(encoding='utf-8')

branch_start_token = "            if (ent === 'funcionario') {\n"
branch_end_token = "            } else if (ent === 'cliente') {\n"
branch_start = app.index(branch_start_token)
branch_end = app.index(branch_end_token, branch_start)

start_token = "                if (!isEdit && _roleTipo === 'encarregado') {\n"
end_token = "                const _funcResultado = await window.TotalGestSaveFormFuncionario.prepare({\n"
assert app.count(start_token) == 1, app.count(start_token)
assert app.count(end_token) == 1, app.count(end_token)
start = app.index(start_token, branch_start)
end = app.index(end_token, start)
assert end < branch_end
old = app[start:end]

for token in [
    'dados.encarregados.push(encObj);',
    'guardarDados(dados);',
    "registarAuditoria('criar', 'encarregado'",
    'await guardarDados(dados);',
    "criarUtilizadorAuth(encObj.email, encObj.senha, 'encarregado'"
]:
    assert token in old, token

new = """                const _encResultado = await window.TotalGestSaveFormFuncionarioEncarregado.run({
                    document: document,
                    data: dados,
                    user: usuarioLogado,
                    isEdit: isEdit,
                    roleType: _roleTipo,
                    generateId: gerarId,
                    saveData: guardarDados,
                    audit: registarAuditoria,
                    closeModal: fecharModal,
                    renderAll: renderizarTudo,
                    createAuth: criarUtilizadorAuth,
                    showAlert: alert
                });
                if (_encResultado.handled) return;

"""
app = app[:start] + new + app[end:]

init_anchor = 'saveFormFuncionario: true'
assert app.count(init_anchor) == 1, app.count(init_anchor)
app = app.replace(init_anchor, init_anchor + ', saveFormFuncionarioEncarregado: true', 1)

shell_anchor = "    saveFormFuncionario: './assets/js/app-save-form-funcionario.js',\n"
assert shell.count(shell_anchor) == 1, shell.count(shell_anchor)
shell = shell.replace(shell_anchor, shell_anchor + "    saveFormFuncionarioEncarregado: './assets/js/app-save-form-funcionario-encarregado.js',\n", 1)
load_anchor = "    if (options.saveFormFuncionario === true) pedidos.push(MODULOS.saveFormFuncionario);\n"
assert shell.count(load_anchor) == 1, shell.count(load_anchor)
shell = shell.replace(load_anchor, load_anchor + "    if (options.saveFormFuncionarioEncarregado === true) pedidos.push(MODULOS.saveFormFuncionarioEncarregado);\n", 1)

assert "const CACHE = 'totalgest-v63';" in sw
sw = sw.replace("const CACHE = 'totalgest-v63';", "const CACHE = 'totalgest-v64';", 1)
sw_anchor = "  './assets/js/app-save-form-funcionario.js',\n"
assert sw.count(sw_anchor) == 1, sw.count(sw_anchor)
sw = sw.replace(sw_anchor, sw_anchor + "  './assets/js/app-save-form-funcionario-encarregado.js',\n", 1)

new_branch_end = app.index(branch_end_token, branch_start)
new_branch = app[branch_start:new_branch_end]
assert new_branch.count('window.TotalGestSaveFormFuncionarioEncarregado.run({') == 1
for token in [
    'dados.encarregados.push(encObj);',
    "registarAuditoria('criar', 'encarregado'",
    "criarUtilizadorAuth(encObj.email, encObj.senha, 'encarregado'"
]:
    assert token not in new_branch, token
assert new_branch.count('window.TotalGestSaveFormFuncionario.prepare({') == 1
assert shell.count('./assets/js/app-save-form-funcionario-encarregado.js') == 1
assert sw.count('./assets/js/app-save-form-funcionario-encarregado.js') == 1

APP.write_text(app, encoding='utf-8')
SHELL.write_text(shell, encoding='utf-8')
SW.write_text(sw, encoding='utf-8')
