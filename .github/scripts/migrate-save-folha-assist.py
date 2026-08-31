from pathlib import Path

APP = Path('app.html')
SHELL = Path('assets/js/app-shell.js')
SW = Path('sw.js')

app = APP.read_text(encoding='utf-8')
shell = SHELL.read_text(encoding='utf-8')
sw = SW.read_text(encoding='utf-8')

start_token = '                // OS gerada a partir de uma Assistência (Total Gest Assist)'
end_token = '                _folhaConsumoPendente = Array.from('
start = app.index(start_token)
end = app.index(end_token, start)
old_prepare = app[start:end]
for token in [
    'let _foAssistenciaParaAtualizar = null, _foNovoEstadoAssistencia = null;',
    "dados.servicos?.find(s => s.id === obj.servicoId)",
    "document.getElementById('fo_estado_assistencia')?.value || ''",
    '(dados.assistencias || []).find('
]:
    assert token in old_prepare, token

new_prepare = """                // OS gerada a partir de uma Assistência (Total Gest Assist) — o estado é obrigatório aqui,
                // e atualiza-se automaticamente do lado do Assist ao gravar a folha.
                const _foAssist = window.TotalGestSaveFormFolhaAssist.prepare({
                    document: document,
                    data: dados,
                    serviceOrderId: obj.servicoId,
                    showAlert: alert
                });
                if (!_foAssist.ok) return;
                const _foAssistenciaParaAtualizar = _foAssist.assistance;
                const _foNovoEstadoAssistencia = _foAssist.newState;

"""
app = app[:start] + new_prepare + app[end:]

apply_old = """                if (_foAssistenciaParaAtualizar && _foNovoEstadoAssistencia) {
                    _foAssistenciaParaAtualizar.estado = _foNovoEstadoAssistencia;
                    _foAssistenciaParaAtualizar.dataModificacao = Date.now();
                }
"""
assert app.count(apply_old) == 1, app.count(apply_old)
apply_new = """                window.TotalGestSaveFormFolhaAssist.apply({
                    assistance: _foAssistenciaParaAtualizar,
                    newState: _foNovoEstadoAssistencia
                });
"""
app = app.replace(apply_old, apply_new, 1)

anchor = 'saveFormFolhaObject: true'
assert app.count(anchor) == 1, app.count(anchor)
app = app.replace(anchor, anchor + ', saveFormFolhaAssist: true', 1)

shell_anchor = "    saveFormFolhaObject: './assets/js/app-save-form-folha-object.js',\n"
assert shell.count(shell_anchor) == 1
shell = shell.replace(shell_anchor, shell_anchor + "    saveFormFolhaAssist: './assets/js/app-save-form-folha-assist.js',\n", 1)
load_anchor = "    if (options.saveFormFolhaObject === true) pedidos.push(MODULOS.saveFormFolhaObject);\n"
assert shell.count(load_anchor) == 1
shell = shell.replace(load_anchor, load_anchor + "    if (options.saveFormFolhaAssist === true) pedidos.push(MODULOS.saveFormFolhaAssist);\n", 1)

assert "const CACHE = 'totalgest-v56';" in sw
sw = sw.replace("const CACHE = 'totalgest-v56';", "const CACHE = 'totalgest-v57';", 1)
sw_anchor = "  './assets/js/app-save-form-folha-object.js',\n"
assert sw.count(sw_anchor) == 1
sw = sw.replace(sw_anchor, sw_anchor + "  './assets/js/app-save-form-folha-assist.js',\n", 1)

assert app.count('window.TotalGestSaveFormFolhaAssist.prepare({') == 1
assert app.count('window.TotalGestSaveFormFolhaAssist.apply({') == 1
new_end = app.index(end_token, start)
new_block = app[start:new_end]
for token in [
    "dados.servicos?.find(s => s.id === obj.servicoId)",
    "document.getElementById('fo_estado_assistencia')?.value || ''",
    '(dados.assistencias || []).find('
]:
    assert token not in new_block, token
assert shell.count('./assets/js/app-save-form-folha-assist.js') == 1
assert sw.count('./assets/js/app-save-form-folha-assist.js') == 1

APP.write_text(app, encoding='utf-8')
SHELL.write_text(shell, encoding='utf-8')
SW.write_text(sw, encoding='utf-8')
