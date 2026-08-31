from pathlib import Path

APP = Path('app.html')
SHELL = Path('assets/js/app-shell.js')
SW = Path('sw.js')

app = APP.read_text(encoding='utf-8')
shell = SHELL.read_text(encoding='utf-8')
sw = SW.read_text(encoding='utf-8')

start_token = "            if (ent === 'funcionario') {\n"
end_token = "            } else if (ent === 'cliente') {\n"
assert app.count(start_token) == 1, app.count(start_token)
assert app.count(end_token) == 1, app.count(end_token)
start = app.index(start_token)
end = app.index(end_token, start)
old = app[start:end]

for token in [
    "verificarLimiteFuncionarios(",
    "window.TotalGestSaveFormFuncionarioEncarregado.run({",
    "window.TotalGestSaveFormFuncionario.prepare({"
]:
    assert token in old, token

new = """            if (ent === 'funcionario') {
                const _funcOrq = await window.TotalGestSaveFormFuncionarioOrchestrator.run({
                    document: document,
                    data: dados,
                    user: usuarioLogado,
                    isEdit: isEdit,
                    editingId: idEditando,
                    showError: mostrarErro,
                    verifyLimit: verificarLimiteFuncionarios,
                    generateId: gerarId,
                    saveData: guardarDados,
                    audit: registarAuditoria,
                    closeModal: fecharModal,
                    renderAll: renderizarTudo,
                    createAuth: criarUtilizadorAuth,
                    vehicleAssigned: veiculoJaAtribuido,
                    emailRegistered: emailJaRegistado,
                    showAlert: alert
                });
                if (_funcOrq.stop) return;
                obj = _funcOrq.value;
"""
app = app[:start] + new + app[end:]

init_anchor = 'saveFormFuncionarioEncarregado: true'
assert app.count(init_anchor) == 1, app.count(init_anchor)
app = app.replace(init_anchor, init_anchor + ', saveFormFuncionarioOrchestrator: true', 1)

shell_anchor = "    saveFormFuncionarioEncarregado: './assets/js/app-save-form-funcionario-encarregado.js',\n"
assert shell.count(shell_anchor) == 1, shell.count(shell_anchor)
shell = shell.replace(shell_anchor, shell_anchor + "    saveFormFuncionarioOrchestrator: './assets/js/app-save-form-funcionario-orchestrator.js',\n", 1)
load_anchor = "    if (options.saveFormFuncionarioEncarregado === true) pedidos.push(MODULOS.saveFormFuncionarioEncarregado);\n"
assert shell.count(load_anchor) == 1, shell.count(load_anchor)
shell = shell.replace(load_anchor, load_anchor + "    if (options.saveFormFuncionarioOrchestrator === true) pedidos.push(MODULOS.saveFormFuncionarioOrchestrator);\n", 1)

assert "const CACHE = 'totalgest-v64';" in sw
sw = sw.replace("const CACHE = 'totalgest-v64';", "const CACHE = 'totalgest-v65';", 1)
sw_anchor = "  './assets/js/app-save-form-funcionario-encarregado.js',\n"
assert sw.count(sw_anchor) == 1, sw.count(sw_anchor)
sw = sw.replace(sw_anchor, sw_anchor + "  './assets/js/app-save-form-funcionario-orchestrator.js',\n", 1)

new_end = app.index(end_token, start)
new_branch = app[start:new_end]
assert new_branch.count('window.TotalGestSaveFormFuncionarioOrchestrator.run({') == 1
for token in [
    'verificarLimiteFuncionarios(',
    'window.TotalGestSaveFormFuncionarioEncarregado.run({',
    'window.TotalGestSaveFormFuncionario.prepare({'
]:
    assert token not in new_branch, token
assert shell.count('./assets/js/app-save-form-funcionario-orchestrator.js') == 1
assert sw.count('./assets/js/app-save-form-funcionario-orchestrator.js') == 1

APP.write_text(app, encoding='utf-8')
SHELL.write_text(shell, encoding='utf-8')
SW.write_text(sw, encoding='utf-8')
