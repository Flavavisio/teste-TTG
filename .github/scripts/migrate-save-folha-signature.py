from pathlib import Path

APP = Path('app.html')
SHELL = Path('assets/js/app-shell.js')
SW = Path('sw.js')

app = APP.read_text(encoding='utf-8')
shell = SHELL.read_text(encoding='utf-8')
sw = SW.read_text(encoding='utf-8')

start_token = "                const _foAssinaturaBase64 = capturarAssinatura() || null;\n"
end_token = "                obj = {\n"
assert app.count(start_token) == 1, app.count(start_token)
assert app.count(end_token) >= 1, app.count(end_token)
start = app.index(start_token)
end = app.index(end_token, start)
old = app[start:end]

for token in [
    "const _foFolhaId = idEditando || gerarId();",
    "await _uploadImagemStorage(`${_foAdminId}/folhas/${_foFolhaId}.png`, _foAssinaturaBase64)",
    "if (ok) _foAssinaturaPath = `${_foAdminId}/folhas/${_foFolhaId}.png`;"
]:
    assert token in old, token

new = """                const _foAssinatura = await window.TotalGestSaveFormFolhaSignature.prepare({
                    adminId: _foAdminId,
                    editingId: idEditando,
                    captureSignature: capturarAssinatura,
                    generateId: gerarId,
                    uploadImage: _uploadImagemStorage
                });
                const _foAssinaturaBase64 = _foAssinatura.base64;
                const _foFolhaId = _foAssinatura.id;
                const _foAssinaturaPath = _foAssinatura.path;
"""
app = app[:start] + new + app[end:]

anchor = 'saveFormFolhaContext: true'
assert app.count(anchor) == 1, app.count(anchor)
app = app.replace(anchor, anchor + ', saveFormFolhaSignature: true', 1)

shell_anchor = "    saveFormFolhaContext: './assets/js/app-save-form-folha-context.js',\n"
assert shell.count(shell_anchor) == 1
shell = shell.replace(shell_anchor, shell_anchor + "    saveFormFolhaSignature: './assets/js/app-save-form-folha-signature.js',\n", 1)
load_anchor = "    if (options.saveFormFolhaContext === true) pedidos.push(MODULOS.saveFormFolhaContext);\n"
assert shell.count(load_anchor) == 1
shell = shell.replace(load_anchor, load_anchor + "    if (options.saveFormFolhaSignature === true) pedidos.push(MODULOS.saveFormFolhaSignature);\n", 1)

assert "const CACHE = 'totalgest-v54';" in sw
sw = sw.replace("const CACHE = 'totalgest-v54';", "const CACHE = 'totalgest-v55';", 1)
sw_anchor = "  './assets/js/app-save-form-folha-context.js',\n"
assert sw.count(sw_anchor) == 1
sw = sw.replace(sw_anchor, sw_anchor + "  './assets/js/app-save-form-folha-signature.js',\n", 1)

assert app.count('window.TotalGestSaveFormFolhaSignature.prepare({') == 1
new_end = app.index(end_token, start)
new_block = app[start:new_end]
for token in [
    "capturarAssinatura() || null",
    "await _uploadImagemStorage(`${_foAdminId}/folhas/${_foFolhaId}.png`",
    "let _foAssinaturaPath = null"
]:
    assert token not in new_block, token
assert shell.count('./assets/js/app-save-form-folha-signature.js') == 1
assert sw.count('./assets/js/app-save-form-folha-signature.js') == 1

APP.write_text(app, encoding='utf-8')
SHELL.write_text(shell, encoding='utf-8')
SW.write_text(sw, encoding='utf-8')
