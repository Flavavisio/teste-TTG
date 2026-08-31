from pathlib import Path

APP = Path('app.html')
SHELL = Path('assets/js/app-shell.js')
SW = Path('sw.js')

app = APP.read_text(encoding='utf-8')
shell = SHELL.read_text(encoding='utf-8')
sw = SW.read_text(encoding='utf-8')

start_token = "            try {\n                await guardarDados(dados);\n            } catch (err) {\n"
end_token = "            const _tornouSeSubadmin = ent === 'funcionario'"
function_start = app.index('async function _salvarFormularioInterno(e)')
end = app.index(end_token, function_start)
start = app.rfind(start_token, function_start, end)
assert start >= 0
old = app[start:end]
for token in [
    "registarAuditoria(isEdit ? 'editar' : 'criar'",
    "if (ent === 'servico' && _novaOSObraId) window._osObraCriadaComSucesso = true;",
    'fecharModal();',
    'renderizarTudo();'
]:
    assert token in old, token

new = """            await window.TotalGestSaveFormFinalize.run({
                data: dados,
                value: obj,
                entity: ent,
                isEdit: isEdit,
                editingId: idEditando,
                newWorkId: _novaOSObraId,
                saveData: guardarDados,
                showAlert: alert,
                audit: registarAuditoria,
                markServiceWorkCreated: () => { window._osObraCriadaComSucesso = true; },
                closeModal: fecharModal,
                renderAll: renderizarTudo
            });
"""
app = app[:start] + new + app[end:]

anchor = 'saveFormFolhaObraPending: true'
assert app.count(anchor) == 1, app.count(anchor)
app = app.replace(anchor, anchor + ', saveFormFinalize: true', 1)

shell_anchor = "    saveFormFolhaObraPending: './assets/js/app-save-form-folha-obra-pending.js',\n"
assert shell.count(shell_anchor) == 1, shell.count(shell_anchor)
shell = shell.replace(shell_anchor, shell_anchor + "    saveFormFinalize: './assets/js/app-save-form-finalize.js',\n", 1)
load_anchor = "    if (options.saveFormFolhaObraPending === true) pedidos.push(MODULOS.saveFormFolhaObraPending);\n"
assert shell.count(load_anchor) == 1, shell.count(load_anchor)
shell = shell.replace(load_anchor, load_anchor + "    if (options.saveFormFinalize === true) pedidos.push(MODULOS.saveFormFinalize);\n", 1)

assert "const CACHE = 'totalgest-v76';" in sw
sw = sw.replace("const CACHE = 'totalgest-v76';", "const CACHE = 'totalgest-v77';", 1)
sw_anchor = "  './assets/js/app-save-form-folha-obra-pending.js',\n"
assert sw.count(sw_anchor) == 1, sw.count(sw_anchor)
sw = sw.replace(sw_anchor, sw_anchor + "  './assets/js/app-save-form-finalize.js',\n", 1)

assert app.count('window.TotalGestSaveFormFinalize.run({') == 1
new_end = app.index(end_token, start)
new_block = app[start:new_end]
assert "registarAuditoria(isEdit ? 'editar' : 'criar'" not in new_block
assert new_block.count('window._osObraCriadaComSucesso = true;') == 1
assert new_block.count('fecharModal();') == 0
assert new_block.count('renderizarTudo();') == 0
assert shell.count('./assets/js/app-save-form-finalize.js') == 1
assert sw.count('./assets/js/app-save-form-finalize.js') == 1

APP.write_text(app, encoding='utf-8')
SHELL.write_text(shell, encoding='utf-8')
SW.write_text(sw, encoding='utf-8')
