from pathlib import Path

APP = Path('app.html')
SHELL = Path('assets/js/app-shell.js')
SW = Path('sw.js')

app = APP.read_text(encoding='utf-8')
shell = SHELL.read_text(encoding='utf-8')
sw = SW.read_text(encoding='utf-8')

start_token = "                if (_bloquearSeAusenteEmOS([...(obj.funcionariosIds || []), obj.funcionarioId].filter(Boolean), obj.data)) return;\n"
end_token = "                if (!isEdit) {\n                    obj.numeroRegisto = await gerarNumeroRegistoServidor();\n                }\n"
assert app.count(start_token) == 1, app.count(start_token)
assert app.count(end_token) == 1, app.count(end_token)
start = app.index(start_token)
end = app.index(end_token, start)
old = app[start:end]
for token in [
    "if (!obj.clienteId) { alert('Selecione um cliente.'); return; }",
    'const outrasNoMesmoDia = (dados.servicos || []).filter',
    'const tiposRepetidos = obj.tiposTrabalho.filter',
    "if (!obj.funcionarioId && usuarioLogado?.role === 'funcionario')",
    'const inicioNova = _horaMin(obj.hora);',
    'const emConflito = outras.find',
    'const nomeFunc = obterNomeFuncionario(obj.funcionarioId)'
]:
    assert token in old, token

new = """                const _servicoConflitos = window.TotalGestSaveFormServicoConflicts.validate({
                    value: obj,
                    data: dados,
                    user: usuarioLogado,
                    isEdit: isEdit,
                    editingId: idEditando,
                    blockIfAbsent: _bloquearSeAusenteEmOS,
                    showAlert: alert,
                    showConfirm: confirm,
                    timeToMinutes: _horaMin,
                    employeeName: obterNomeFuncionario
                });
                if (!_servicoConflitos.ok) return;
                obj = _servicoConflitos.value;
"""
app = app[:start] + new + app[end:]

anchor = 'saveFormServicoObject: true'
assert app.count(anchor) == 1, app.count(anchor)
app = app.replace(anchor, anchor + ', saveFormServicoConflicts: true', 1)

shell_anchor = "    saveFormServicoObject: './assets/js/app-save-form-servico-object.js',\n"
assert shell.count(shell_anchor) == 1, shell.count(shell_anchor)
shell = shell.replace(shell_anchor, shell_anchor + "    saveFormServicoConflicts: './assets/js/app-save-form-servico-conflicts.js',\n", 1)
load_anchor = "    if (options.saveFormServicoObject === true) pedidos.push(MODULOS.saveFormServicoObject);\n"
assert shell.count(load_anchor) == 1, shell.count(load_anchor)
shell = shell.replace(load_anchor, load_anchor + "    if (options.saveFormServicoConflicts === true) pedidos.push(MODULOS.saveFormServicoConflicts);\n", 1)

assert "const CACHE = 'totalgest-v68';" in sw
sw = sw.replace("const CACHE = 'totalgest-v68';", "const CACHE = 'totalgest-v69';", 1)
sw_anchor = "  './assets/js/app-save-form-servico-object.js',\n"
assert sw.count(sw_anchor) == 1, sw.count(sw_anchor)
sw = sw.replace(sw_anchor, sw_anchor + "  './assets/js/app-save-form-servico-conflicts.js',\n", 1)

assert app.count('window.TotalGestSaveFormServicoConflicts.validate({') == 1
new_end = app.index(end_token, start)
new_block = app[start:new_end]
for token in [
    'const outrasNoMesmoDia = (dados.servicos || []).filter',
    'const tiposRepetidos = obj.tiposTrabalho.filter',
    'const inicioNova = _horaMin(obj.hora);',
    'const emConflito = outras.find'
]:
    assert token not in new_block, token
assert shell.count('./assets/js/app-save-form-servico-conflicts.js') == 1
assert sw.count('./assets/js/app-save-form-servico-conflicts.js') == 1

APP.write_text(app, encoding='utf-8')
SHELL.write_text(shell, encoding='utf-8')
SW.write_text(sw, encoding='utf-8')
