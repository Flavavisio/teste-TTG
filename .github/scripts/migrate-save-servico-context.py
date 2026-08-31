from pathlib import Path

APP = Path('app.html')
SHELL = Path('assets/js/app-shell.js')
SW = Path('sw.js')

app = APP.read_text(encoding='utf-8')
shell = SHELL.read_text(encoding='utf-8')
sw = SW.read_text(encoding='utf-8')

start_token = "                let funcionarioId = document.getElementById('s_funcionario').value || null;\n"
end_token = "                obj = {\n"
assert app.count(start_token) == 1, app.count(start_token)
start = app.index(start_token)
end = app.index(end_token, start)
old = app[start:end]

for token in [
    "const _funcCheckCont = document.getElementById('s_func_checkboxes');",
    "if (usuarioLogado?.role === 'admin' || usuarioLogado?.role === 'subadmin')",
    "const _osExist = isEdit ? (dados.servicos || []).find(x => x.id === idEditando) : null;",
    "if (_sLocalIdResolvido === '__novo__')",
    "dados.locais.push({"
]:
    assert token in old, token

new = """                const _servicoContexto = window.TotalGestSaveFormServicoContext.prepare({
                    document: document,
                    data: dados,
                    user: usuarioLogado,
                    isEdit: isEdit,
                    editingId: idEditando,
                    tenantId: _tenantId,
                    generateId: gerarId,
                    showAlert: alert,
                    showConfirm: confirm
                });
                if (!_servicoContexto.ok) return;
                let funcionarioId = _servicoContexto.employeeId;
                const funcionariosIds = _servicoContexto.employeeIds;
                const adminId = _servicoContexto.adminId;
                const _osExist = _servicoContexto.existingOrder;
                const _sLocalIdResolvido = _servicoContexto.localId;
"""
app = app[:start] + new + app[end:]

anchor = 'saveFormServicoValidation: true'
assert app.count(anchor) == 1, app.count(anchor)
app = app.replace(anchor, anchor + ', saveFormServicoContext: true', 1)

shell_anchor = "    saveFormServicoValidation: './assets/js/app-save-form-servico-validation.js',\n"
assert shell.count(shell_anchor) == 1, shell.count(shell_anchor)
shell = shell.replace(shell_anchor, shell_anchor + "    saveFormServicoContext: './assets/js/app-save-form-servico-context.js',\n", 1)
load_anchor = "    if (options.saveFormServicoValidation === true) pedidos.push(MODULOS.saveFormServicoValidation);\n"
assert shell.count(load_anchor) == 1, shell.count(load_anchor)
shell = shell.replace(load_anchor, load_anchor + "    if (options.saveFormServicoContext === true) pedidos.push(MODULOS.saveFormServicoContext);\n", 1)

assert "const CACHE = 'totalgest-v66';" in sw
sw = sw.replace("const CACHE = 'totalgest-v66';", "const CACHE = 'totalgest-v67';", 1)
sw_anchor = "  './assets/js/app-save-form-servico-validation.js',\n"
assert sw.count(sw_anchor) == 1, sw.count(sw_anchor)
sw = sw.replace(sw_anchor, sw_anchor + "  './assets/js/app-save-form-servico-context.js',\n", 1)

assert app.count('window.TotalGestSaveFormServicoContext.prepare({') == 1
new_end = app.index(end_token, start)
new_block = app[start:new_end]
for token in [
    "const _funcCheckCont = document.getElementById('s_func_checkboxes');",
    "dados.locais.push({",
    "const _osExist = isEdit ? (dados.servicos || []).find"
]:
    assert token not in new_block, token
assert shell.count('./assets/js/app-save-form-servico-context.js') == 1
assert sw.count('./assets/js/app-save-form-servico-context.js') == 1

APP.write_text(app, encoding='utf-8')
SHELL.write_text(shell, encoding='utf-8')
SW.write_text(sw, encoding='utf-8')
