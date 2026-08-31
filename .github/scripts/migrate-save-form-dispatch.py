from pathlib import Path

APP = Path('app.html')
SHELL = Path('assets/js/app-shell.js')
SW = Path('sw.js')

app = APP.read_text(encoding='utf-8')
shell = SHELL.read_text(encoding='utf-8')
sw = SW.read_text(encoding='utf-8')

function_start = app.index('async function _salvarFormularioInterno(e)')
start_token = "            if (ent === 'funcionario') {\n"
end_token = "            const _persistenciaFormulario = window.TotalGestSaveFormPersist.apply({\n"
start = app.index(start_token, function_start)
end = app.index(end_token, start)
old = app[start:end]
for token in [
    'TotalGestSaveFormFuncionarioOrchestrator.run({',
    'TotalGestSaveFormCliente.prepare({',
    'TotalGestSaveFormServico.run({',
    'TotalGestSaveFormFolha.run({',
    'TotalGestSaveFormRequisicao.run({',
    'TotalGestSaveFormFornecedor.run({',
    'TotalGestSaveFormArtigo.run({',
    'TotalGestSaveFormObra.run({'
]:
    assert token in old, token

new = """            const _dispatchFormulario = await window.TotalGestSaveFormDispatch.run({
                entity: ent,
                document: document,
                data: dados,
                user: usuarioLogado,
                isEdit: isEdit,
                editingId: idEditando,
                item: item,
                newWorkId: _novaOSObraId,
                approvingAssistanceId: _aprovandoAssistenciaId,
                tenantId: _tenantId,
                generateId: gerarId,
                showError: mostrarErro,
                showAlert: alert,
                showConfirm: confirm,
                confirmDialog: tgConfirm,
                verifyEmployeeLimit: verificarLimiteFuncionarios,
                saveData: guardarDados,
                audit: registarAuditoria,
                closeModal: fecharModal,
                renderAll: renderizarTudo,
                createAuth: criarUtilizadorAuth,
                vehicleAssigned: veiculoJaAtribuido,
                emailRegistered: emailJaRegistado,
                selectedWorkTypes: _sTiposTrabalhoSelecionados,
                blockIfAbsent: _bloquearSeAusenteEmOS,
                timeToMinutes: _horaMin,
                employeeName: obterNomeFuncionario,
                generateRegistrationNumber: gerarNumeroRegistoServidor,
                hoursCorrectedManually: _foHorasCorrigidasManualmente,
                hoursForServiceOrder: _horasPicadasOS,
                hoursForWork: _horasPicadasObra,
                captureSignature: capturarAssinatura,
                uploadImage: _uploadImagemStorage,
                getToday: getDataHoje,
                advancePeriodicity: avancarPeriodicidade,
                notify: _notificarFuncionario,
                extraMaterials: _foMatExtra,
                setPendingConsumption: value => { _folhaConsumoPendente = value; },
                clearExtraMaterials: () => { _foMatExtra = []; },
                FileReader: FileReader,
                saveWarehouse: _guardarArmazem,
                intVal: _intVal,
                createServiceOrder: criarOSdaObra,
                employeeHandler: window.TotalGestSaveFormFuncionarioOrchestrator,
                clientHandler: window.TotalGestSaveFormCliente,
                serviceHandler: window.TotalGestSaveFormServico,
                sheetHandler: window.TotalGestSaveFormFolha,
                requestHandler: window.TotalGestSaveFormRequisicao,
                supplierHandler: window.TotalGestSaveFormFornecedor,
                articleHandler: window.TotalGestSaveFormArtigo,
                workHandler: window.TotalGestSaveFormObra,
                serviceValidation: window.TotalGestSaveFormServicoValidation,
                serviceContext: window.TotalGestSaveFormServicoContext,
                serviceObject: window.TotalGestSaveFormServicoObject,
                serviceConflicts: window.TotalGestSaveFormServicoConflicts,
                serviceRegistration: window.TotalGestSaveFormServicoRegistration
            });
            if (_dispatchFormulario.stop) return;
            obj = _dispatchFormulario.value;

"""
app = app[:start] + new + app[end:]

anchor = 'saveFormContactValidation: true'
assert app.count(anchor) == 1, app.count(anchor)
app = app.replace(anchor, anchor + ', saveFormDispatch: true', 1)

shell_anchor = "    saveFormContactValidation: './assets/js/app-save-form-contact-validation.js',\n"
assert shell.count(shell_anchor) == 1, shell.count(shell_anchor)
shell = shell.replace(shell_anchor, shell_anchor + "    saveFormDispatch: './assets/js/app-save-form-dispatch.js',\n", 1)
load_anchor = "    if (options.saveFormContactValidation === true) pedidos.push(MODULOS.saveFormContactValidation);\n"
assert shell.count(load_anchor) == 1, shell.count(load_anchor)
shell = shell.replace(load_anchor, load_anchor + "    if (options.saveFormDispatch === true) pedidos.push(MODULOS.saveFormDispatch);\n", 1)

assert "const CACHE = 'totalgest-v79';" in sw
sw = sw.replace("const CACHE = 'totalgest-v79';", "const CACHE = 'totalgest-v80';", 1)
sw_anchor = "  './assets/js/app-save-form-contact-validation.js',\n"
assert sw.count(sw_anchor) == 1, sw.count(sw_anchor)
sw = sw.replace(sw_anchor, sw_anchor + "  './assets/js/app-save-form-dispatch.js',\n", 1)

assert app.count('window.TotalGestSaveFormDispatch.run({') == 1
new_end = app.index(end_token, start)
new_block = app[start:new_end]
for token in [
    'TotalGestSaveFormFuncionarioOrchestrator.run({',
    'TotalGestSaveFormCliente.prepare({',
    'TotalGestSaveFormServico.run({',
    'TotalGestSaveFormFolha.run({',
    'TotalGestSaveFormRequisicao.run({',
    'TotalGestSaveFormObra.run({'
]:
    assert token not in new_block, token
assert shell.count('./assets/js/app-save-form-dispatch.js') == 1
assert sw.count('./assets/js/app-save-form-dispatch.js') == 1

APP.write_text(app, encoding='utf-8')
SHELL.write_text(shell, encoding='utf-8')
SW.write_text(sw, encoding='utf-8')
