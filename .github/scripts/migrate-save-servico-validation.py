from pathlib import Path

APP = Path('app.html')
SHELL = Path('assets/js/app-shell.js')
SW = Path('sw.js')

app = APP.read_text(encoding='utf-8')
shell = SHELL.read_text(encoding='utf-8')
sw = SW.read_text(encoding='utf-8')

branch_start_token = "            } else if (ent === 'servico') {\n"
branch_end_token = "            } else if (ent === 'folha') {\n"
assert app.count(branch_start_token) == 1, app.count(branch_start_token)
assert app.count(branch_end_token) == 1, app.count(branch_end_token)
branch_start = app.index(branch_start_token)
branch_end = app.index(branch_end_token, branch_start)

end_token = "                let funcionarioId = document.getElementById('s_funcionario').value || null;\n"
assert app.count(end_token) == 1, app.count(end_token)
end = app.index(end_token, branch_start)
old = app[branch_start:end]
for token in [
    "Os funcionários não podem criar ordens de serviço.",
    "Descreve o trabalho a realizar nesta Ordem de Serviço",
    "const _sStatusNovo = document.getElementById('s_status')?.value;",
    "Não é possível concluir esta OS: falta marcar"
]:
    assert token in old, token

new = """            } else if (ent === 'servico') {
                const _servicoValidacao = window.TotalGestSaveFormServicoValidation.validate({
                    document: document,
                    data: dados,
                    user: usuarioLogado,
                    isEdit: isEdit,
                    item: item,
                    showAlert: alert,
                    showError: mostrarErro
                });
                if (!_servicoValidacao.ok) return;
"""
app = app[:branch_start] + new + app[end:]

init_anchor = 'saveFormFuncionarioOrchestrator: true'
assert app.count(init_anchor) == 1, app.count(init_anchor)
app = app.replace(init_anchor, init_anchor + ', saveFormServicoValidation: true', 1)

shell_anchor = "    saveFormFuncionarioOrchestrator: './assets/js/app-save-form-funcionario-orchestrator.js',\n"
assert shell.count(shell_anchor) == 1, shell.count(shell_anchor)
shell = shell.replace(shell_anchor, shell_anchor + "    saveFormServicoValidation: './assets/js/app-save-form-servico-validation.js',\n", 1)
load_anchor = "    if (options.saveFormFuncionarioOrchestrator === true) pedidos.push(MODULOS.saveFormFuncionarioOrchestrator);\n"
assert shell.count(load_anchor) == 1, shell.count(load_anchor)
shell = shell.replace(load_anchor, load_anchor + "    if (options.saveFormServicoValidation === true) pedidos.push(MODULOS.saveFormServicoValidation);\n", 1)

assert "const CACHE = 'totalgest-v65';" in sw
sw = sw.replace("const CACHE = 'totalgest-v65';", "const CACHE = 'totalgest-v66';", 1)
sw_anchor = "  './assets/js/app-save-form-funcionario-orchestrator.js',\n"
assert sw.count(sw_anchor) == 1, sw.count(sw_anchor)
sw = sw.replace(sw_anchor, sw_anchor + "  './assets/js/app-save-form-servico-validation.js',\n", 1)

new_branch_end = app.index(branch_end_token, branch_start)
new_branch = app[branch_start:new_branch_end]
assert new_branch.count('window.TotalGestSaveFormServicoValidation.validate({') == 1
for token in [
    "Os funcionários não podem criar ordens de serviço.",
    "const _sStatusNovo = document.getElementById('s_status')?.value;",
    "Não é possível concluir esta OS: falta marcar"
]:
    assert token not in new_branch, token
assert shell.count('./assets/js/app-save-form-servico-validation.js') == 1
assert sw.count('./assets/js/app-save-form-servico-validation.js') == 1

APP.write_text(app, encoding='utf-8')
SHELL.write_text(shell, encoding='utf-8')
SW.write_text(sw, encoding='utf-8')
