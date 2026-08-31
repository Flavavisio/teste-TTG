from pathlib import Path

APP = Path('app.html')
SHELL = Path('assets/js/app-shell.js')
SW = Path('sw.js')

app = APP.read_text(encoding='utf-8')
shell = SHELL.read_text(encoding='utf-8')
sw = SW.read_text(encoding='utf-8')

context_token = '                const _servicoContexto = window.TotalGestSaveFormServicoContext.prepare({\n'
start_token = '                obj = {\n'
end_token = '                if (_bloquearSeAusenteEmOS('
assert app.count(context_token) == 1, app.count(context_token)
context_pos = app.index(context_token)
start = app.index(start_token, context_pos)
end = app.index(end_token, start)
old = app[start:end]

for token in [
    "clienteId: document.getElementById('s_cliente').value",
    'funcionariosIds: funcionariosIds',
    'tiposTrabalho: _sTiposTrabalhoSelecionados()',
    'obj._eraAprovacaoAssistencia = !!(',
    "if (obj._eraAprovacaoAssistencia) { obj.status = 'pendente'; }"
]:
    assert token in old, token

new = """                obj = window.TotalGestSaveFormServicoObject.prepare({
                    document: document,
                    employeeId: funcionarioId,
                    employeeIds: funcionariosIds,
                    existingOrder: _osExist,
                    newWorkId: _novaOSObraId,
                    localId: _sLocalIdResolvido,
                    adminId: adminId,
                    selectedWorkTypes: _sTiposTrabalhoSelecionados,
                    approvingAssistanceId: _aprovandoAssistenciaId,
                    editingId: idEditando
                });
"""
app = app[:start] + new + app[end:]

anchor = 'saveFormServicoContext: true'
assert app.count(anchor) == 1, app.count(anchor)
app = app.replace(anchor, anchor + ', saveFormServicoObject: true', 1)

shell_anchor = "    saveFormServicoContext: './assets/js/app-save-form-servico-context.js',\n"
assert shell.count(shell_anchor) == 1, shell.count(shell_anchor)
shell = shell.replace(shell_anchor, shell_anchor + "    saveFormServicoObject: './assets/js/app-save-form-servico-object.js',\n", 1)
load_anchor = "    if (options.saveFormServicoContext === true) pedidos.push(MODULOS.saveFormServicoContext);\n"
assert shell.count(load_anchor) == 1, shell.count(load_anchor)
shell = shell.replace(load_anchor, load_anchor + "    if (options.saveFormServicoObject === true) pedidos.push(MODULOS.saveFormServicoObject);\n", 1)

assert "const CACHE = 'totalgest-v67';" in sw
sw = sw.replace("const CACHE = 'totalgest-v67';", "const CACHE = 'totalgest-v68';", 1)
sw_anchor = "  './assets/js/app-save-form-servico-context.js',\n"
assert sw.count(sw_anchor) == 1, sw.count(sw_anchor)
sw = sw.replace(sw_anchor, sw_anchor + "  './assets/js/app-save-form-servico-object.js',\n", 1)

assert app.count('window.TotalGestSaveFormServicoObject.prepare({') == 1
new_end = app.index(end_token, start)
new_block = app[start:new_end]
for token in [
    "clienteId: document.getElementById('s_cliente').value",
    'tiposTrabalho: _sTiposTrabalhoSelecionados()',
    'obj._eraAprovacaoAssistencia = !!('
]:
    assert token not in new_block, token
assert shell.count('./assets/js/app-save-form-servico-object.js') == 1
assert sw.count('./assets/js/app-save-form-servico-object.js') == 1

APP.write_text(app, encoding='utf-8')
SHELL.write_text(shell, encoding='utf-8')
SW.write_text(sw, encoding='utf-8')
