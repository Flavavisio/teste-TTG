from pathlib import Path

APP = Path('app.html')
SHELL = Path('assets/js/app-shell.js')
SW = Path('sw.js')

app = APP.read_text(encoding='utf-8')
shell = SHELL.read_text(encoding='utf-8')
sw = SW.read_text(encoding='utf-8')

start_token = "            } else if (ent === 'servico') {\n"
end_token = "            } else if (ent === 'folha') {\n"
assert app.count(start_token) == 1, app.count(start_token)
assert app.count(end_token) == 1, app.count(end_token)
start = app.index(start_token)
end = app.index(end_token, start)
old = app[start:end]
for token in [
    'TotalGestSaveFormServicoValidation.validate({',
    'TotalGestSaveFormServicoContext.prepare({',
    'TotalGestSaveFormServicoObject.prepare({',
    'TotalGestSaveFormServicoConflicts.validate({',
    'TotalGestSaveFormServicoRegistration.apply({'
]:
    assert old.count(token) == 1, (token, old.count(token))

new = """            } else if (ent === 'servico') {
                const _servicoResultado = await window.TotalGestSaveFormServico.run({
                    document: document,
                    data: dados,
                    user: usuarioLogado,
                    isEdit: isEdit,
                    item: item,
                    editingId: idEditando,
                    newWorkId: _novaOSObraId,
                    approvingAssistanceId: _aprovandoAssistenciaId,
                    tenantId: _tenantId,
                    generateId: gerarId,
                    selectedWorkTypes: _sTiposTrabalhoSelecionados,
                    blockIfAbsent: _bloquearSeAusenteEmOS,
                    showAlert: alert,
                    showError: mostrarErro,
                    showConfirm: confirm,
                    timeToMinutes: _horaMin,
                    employeeName: obterNomeFuncionario,
                    generateRegistrationNumber: gerarNumeroRegistoServidor,
                    validation: window.TotalGestSaveFormServicoValidation,
                    context: window.TotalGestSaveFormServicoContext,
                    object: window.TotalGestSaveFormServicoObject,
                    conflicts: window.TotalGestSaveFormServicoConflicts,
                    registration: window.TotalGestSaveFormServicoRegistration
                });
                if (!_servicoResultado.ok) return;
                obj = _servicoResultado.value;
"""
app = app[:start] + new + app[end:]

anchor = 'saveFormServicoRegistration: true'
assert app.count(anchor) == 1, app.count(anchor)
app = app.replace(anchor, anchor + ', saveFormServico: true', 1)

shell_anchor = "    saveFormServicoRegistration: './assets/js/app-save-form-servico-registration.js',\n"
assert shell.count(shell_anchor) == 1, shell.count(shell_anchor)
shell = shell.replace(shell_anchor, shell_anchor + "    saveFormServico: './assets/js/app-save-form-servico.js',\n", 1)
load_anchor = "    if (options.saveFormServicoRegistration === true) pedidos.push(MODULOS.saveFormServicoRegistration);\n"
assert shell.count(load_anchor) == 1, shell.count(load_anchor)
shell = shell.replace(load_anchor, load_anchor + "    if (options.saveFormServico === true) pedidos.push(MODULOS.saveFormServico);\n", 1)

assert "const CACHE = 'totalgest-v70';" in sw
sw = sw.replace("const CACHE = 'totalgest-v70';", "const CACHE = 'totalgest-v71';", 1)
sw_anchor = "  './assets/js/app-save-form-servico-registration.js',\n"
assert sw.count(sw_anchor) == 1, sw.count(sw_anchor)
sw = sw.replace(sw_anchor, sw_anchor + "  './assets/js/app-save-form-servico.js',\n", 1)

assert app.count('window.TotalGestSaveFormServico.run({') == 1
branch_end = app.index(end_token, start)
branch = app[start:branch_end]
for token in [
    'TotalGestSaveFormServicoValidation.validate({',
    'TotalGestSaveFormServicoContext.prepare({',
    'TotalGestSaveFormServicoObject.prepare({',
    'TotalGestSaveFormServicoConflicts.validate({',
    'TotalGestSaveFormServicoRegistration.apply({'
]:
    assert token not in branch, token
assert shell.count('./assets/js/app-save-form-servico.js') == 1
assert sw.count('./assets/js/app-save-form-servico.js') == 1

APP.write_text(app, encoding='utf-8')
SHELL.write_text(shell, encoding='utf-8')
SW.write_text(sw, encoding='utf-8')
