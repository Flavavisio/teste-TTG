from pathlib import Path

APP = Path('app.html')
SHELL = Path('assets/js/app-shell.js')
SW = Path('sw.js')

app = APP.read_text(encoding='utf-8')
shell = SHELL.read_text(encoding='utf-8')
sw = SW.read_text(encoding='utf-8')

start_token = "                if (_folhaOSPendente && _folhaOSPendente.osId === obj.servicoId) {\n"
end_token = "                if (_folhaObraPendente && _folhaObraPendente.obraId === obj.obraId) {\n"
assert app.count(start_token) == 1, app.count(start_token)
start = app.index(start_token)
end = app.index(end_token, start)
old = app[start:end]
for token in [
    'const { osId, terminou } = _folhaOSPendente;',
    '_folhaOSPendente = null;',
    'const pendentesEspec = _tiposEspecialidadePendentes(osId);',
    'abrirFilaRelatoriosEspecialidade(osId, pendentesEspec, _finalizarOS);',
    "osv.status = 'stand by';",
    'renderizarAgendaObras();'
]:
    assert token in old, token

new = """                window.TotalGestSaveFormFolhaOsPending.apply({
                    value: obj,
                    pending: _folhaOSPendente,
                    data: dados,
                    clearPending: () => { _folhaOSPendente = null; },
                    pendingSpecialty: _tiposEspecialidadePendentes,
                    completeService: _concluirOS,
                    openSpecialtyQueue: abrirFilaRelatoriosEspecialidade,
                    saveData: guardarDados,
                    renderAgenda: renderizarAgendaObras,
                    renderPoint: typeof renderizarPonto === 'function' ? renderizarPonto : null,
                    showAlert: alert
                });
"""
app = app[:start] + new + app[end:]

anchor = 'saveFormFolhaUsage: true'
assert app.count(anchor) == 1, app.count(anchor)
app = app.replace(anchor, anchor + ', saveFormFolhaOsPending: true', 1)

shell_anchor = "    saveFormFolhaUsage: './assets/js/app-save-form-folha-usage.js',\n"
assert shell.count(shell_anchor) == 1, shell.count(shell_anchor)
shell = shell.replace(shell_anchor, shell_anchor + "    saveFormFolhaOsPending: './assets/js/app-save-form-folha-os-pending.js',\n", 1)
load_anchor = "    if (options.saveFormFolhaUsage === true) pedidos.push(MODULOS.saveFormFolhaUsage);\n"
assert shell.count(load_anchor) == 1, shell.count(load_anchor)
shell = shell.replace(load_anchor, load_anchor + "    if (options.saveFormFolhaOsPending === true) pedidos.push(MODULOS.saveFormFolhaOsPending);\n", 1)

assert "const CACHE = 'totalgest-v74';" in sw
sw = sw.replace("const CACHE = 'totalgest-v74';", "const CACHE = 'totalgest-v75';", 1)
sw_anchor = "  './assets/js/app-save-form-folha-usage.js',\n"
assert sw.count(sw_anchor) == 1, sw.count(sw_anchor)
sw = sw.replace(sw_anchor, sw_anchor + "  './assets/js/app-save-form-folha-os-pending.js',\n", 1)

assert app.count('window.TotalGestSaveFormFolhaOsPending.apply({') == 1
new_end = app.index(end_token, start)
new_block = app[start:new_end]
for token in [
    'const { osId, terminou } = _folhaOSPendente;',
    'abrirFilaRelatoriosEspecialidade(osId, pendentesEspec, _finalizarOS);',
    "osv.status = 'stand by';"
]:
    assert token not in new_block, token
assert shell.count('./assets/js/app-save-form-folha-os-pending.js') == 1
assert sw.count('./assets/js/app-save-form-folha-os-pending.js') == 1

APP.write_text(app, encoding='utf-8')
SHELL.write_text(shell, encoding='utf-8')
SW.write_text(sw, encoding='utf-8')
