from pathlib import Path

APP = Path('app.html')
SHELL = Path('assets/js/app-shell.js')
SW = Path('sw.js')

app = APP.read_text(encoding='utf-8')
shell = SHELL.read_text(encoding='utf-8')
sw = SW.read_text(encoding='utf-8')

function_start = app.index('async function _salvarFormularioInterno(e)')
start_token = "            const _persistenciaFormulario = window.TotalGestSaveFormPersist.apply({\n"
end_token = "\n        }\n        // Os clientes entram no Portal"
start = app.index(start_token, function_start)
end = app.index(end_token, start)
old = app[start:end]
for token in [
    'window.TotalGestSaveFormPersist.apply({',
    'window.TotalGestSaveFormServicoNotifications.run({',
    'window.TotalGestSaveFormFolhaUsage.apply({',
    'window.TotalGestSaveFormFolhaOsPending.apply({',
    'window.TotalGestSaveFormFolhaObraPending.apply({',
    'window.TotalGestSaveFormFinalize.run({',
    'window.TotalGestSaveFormAuth.run({'
]:
    assert token in old, token

new = """            const _posPersistenciaFormulario = await window.TotalGestSaveFormPostPersist.run({
                entity: ent,
                data: dados,
                value: obj,
                isEdit: isEdit,
                editingId: idEditando,
                newWorkId: _novaOSObraId,
                generateId: gerarId,
                persist: window.TotalGestSaveFormPersist,
                serviceNotifications: window.TotalGestSaveFormServicoNotifications,
                sheetUsage: window.TotalGestSaveFormFolhaUsage,
                sheetOsPending: window.TotalGestSaveFormFolhaOsPending,
                sheetWorkPending: window.TotalGestSaveFormFolhaObraPending,
                finalize: window.TotalGestSaveFormFinalize,
                auth: window.TotalGestSaveFormAuth,
                clientName: obterNomeCliente,
                notify: _notificarFuncionario,
                formatEuro: _finEur,
                getPendingConsumption: () => _folhaConsumoPendente,
                clearPendingConsumption: () => { _folhaConsumoPendente = []; },
                getPendingServiceOrder: () => _folhaOSPendente,
                clearPendingServiceOrder: () => { _folhaOSPendente = null; },
                getPendingWork: () => _folhaObraPendente,
                clearPendingWork: () => { _folhaObraPendente = null; },
                applyConsumption: _aplicarConsumoFolha,
                pendingSpecialty: _tiposEspecialidadePendentes,
                completeService: _concluirOS,
                openSpecialtyQueue: abrirFilaRelatoriosEspecialidade,
                saveData: guardarDados,
                renderAgenda: renderizarAgendaObras,
                renderPoint: typeof renderizarPonto === 'function' ? renderizarPonto : null,
                getToday: getDataHoje,
                renderAll: renderizarTudo,
                showAlert: alert,
                audit: registarAuditoria,
                markServiceWorkCreated: () => { window._osObraCriadaComSucesso = true; },
                closeModal: fecharModal,
                createAuth: criarUtilizadorAuth,
                clientTechnicalEmail: _emailFantasmaCliente
            });
            if (!_posPersistenciaFormulario.ok) return;
            obj = _posPersistenciaFormulario.value;
"""
app = app[:start] + new + app[end:]

anchor = 'saveFormDispatch: true'
assert app.count(anchor) == 1, app.count(anchor)
app = app.replace(anchor, anchor + ', saveFormPostPersist: true', 1)

shell_anchor = "    saveFormDispatch: './assets/js/app-save-form-dispatch.js',\n"
assert shell.count(shell_anchor) == 1, shell.count(shell_anchor)
shell = shell.replace(shell_anchor, shell_anchor + "    saveFormPostPersist: './assets/js/app-save-form-post-persist.js',\n", 1)
load_anchor = "    if (options.saveFormDispatch === true) pedidos.push(MODULOS.saveFormDispatch);\n"
assert shell.count(load_anchor) == 1, shell.count(load_anchor)
shell = shell.replace(load_anchor, load_anchor + "    if (options.saveFormPostPersist === true) pedidos.push(MODULOS.saveFormPostPersist);\n", 1)

assert "const CACHE = 'totalgest-v80';" in sw
sw = sw.replace("const CACHE = 'totalgest-v80';", "const CACHE = 'totalgest-v81';", 1)
sw_anchor = "  './assets/js/app-save-form-dispatch.js',\n"
assert sw.count(sw_anchor) == 1, sw.count(sw_anchor)
sw = sw.replace(sw_anchor, sw_anchor + "  './assets/js/app-save-form-post-persist.js',\n", 1)

assert app.count('window.TotalGestSaveFormPostPersist.run({') == 1
new_end = app.index(end_token, start)
new_block = app[start:new_end]
for token in [
    'window.TotalGestSaveFormPersist.apply({',
    'window.TotalGestSaveFormServicoNotifications.run({',
    'window.TotalGestSaveFormFolhaUsage.apply({',
    'window.TotalGestSaveFormFinalize.run({',
    'window.TotalGestSaveFormAuth.run({'
]:
    assert token not in new_block, token
assert shell.count('./assets/js/app-save-form-post-persist.js') == 1
assert sw.count('./assets/js/app-save-form-post-persist.js') == 1

APP.write_text(app, encoding='utf-8')
SHELL.write_text(shell, encoding='utf-8')
SW.write_text(sw, encoding='utf-8')
