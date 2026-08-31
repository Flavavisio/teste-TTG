from pathlib import Path

APP = Path('app.html')
SHELL = Path('assets/js/app-shell.js')
SW = Path('sw.js')

app = APP.read_text(encoding='utf-8')
shell = SHELL.read_text(encoding='utf-8')
sw = SW.read_text(encoding='utf-8')

sig_token = "                const _foAssinaturaPath = _foAssinatura.path;\n"
start_token = "                obj = {\n"
end_token = "                // OS gerada a partir de uma Assistência (Total Gest Assist)"
assert app.count(sig_token) == 1, app.count(sig_token)
sig = app.index(sig_token)
start = app.index(start_token, sig)
end = app.index(end_token, start)
old = app[start:end]

for token in [
    "horasTrabalhadas: horas",
    "assinatura: _foAssinaturaPath ? '' : _foAssinaturaBase64",
    "if (!isEdit) obj.id = _foFolhaId;",
    "Indica se usaste materiais desta obra (Sim/Não).",
    "Funcionário não identificado."
]:
    assert token in old, token

new = """                const _foObjeto = window.TotalGestSaveFormFolhaObject.prepare({
                    document: document,
                    clientId: _foClienteId,
                    localId: _foLocalId,
                    workDescription: _foObraDescricao,
                    hours: horas,
                    employeeId: funcionarioId,
                    signatureBase64: _foAssinaturaBase64,
                    signaturePath: _foAssinaturaPath,
                    adminId: _foAdminId,
                    sheetId: _foFolhaId,
                    isEdit: isEdit,
                    showAlert: alert
                });
                if (!_foObjeto.ok) return;
                obj = _foObjeto.value;
"""
app = app[:start] + new + app[end:]

anchor = 'saveFormFolhaSignature: true'
assert app.count(anchor) == 1, app.count(anchor)
app = app.replace(anchor, anchor + ', saveFormFolhaObject: true', 1)

shell_anchor = "    saveFormFolhaSignature: './assets/js/app-save-form-folha-signature.js',\n"
assert shell.count(shell_anchor) == 1
shell = shell.replace(shell_anchor, shell_anchor + "    saveFormFolhaObject: './assets/js/app-save-form-folha-object.js',\n", 1)
load_anchor = "    if (options.saveFormFolhaSignature === true) pedidos.push(MODULOS.saveFormFolhaSignature);\n"
assert shell.count(load_anchor) == 1
shell = shell.replace(load_anchor, load_anchor + "    if (options.saveFormFolhaObject === true) pedidos.push(MODULOS.saveFormFolhaObject);\n", 1)

assert "const CACHE = 'totalgest-v55';" in sw
sw = sw.replace("const CACHE = 'totalgest-v55';", "const CACHE = 'totalgest-v56';", 1)
sw_anchor = "  './assets/js/app-save-form-folha-signature.js',\n"
assert sw.count(sw_anchor) == 1
sw = sw.replace(sw_anchor, sw_anchor + "  './assets/js/app-save-form-folha-object.js',\n", 1)

assert app.count('window.TotalGestSaveFormFolhaObject.prepare({') == 1
new_end = app.index(end_token, start)
new_block = app[start:new_end]
for token in [
    "horasTrabalhadas: horas",
    "assinatura: _foAssinaturaPath ? '' : _foAssinaturaBase64",
    "if (!isEdit) obj.id = _foFolhaId;",
    "Indica se usaste materiais desta obra (Sim/Não)."
]:
    assert token not in new_block, token
assert shell.count('./assets/js/app-save-form-folha-object.js') == 1
assert sw.count('./assets/js/app-save-form-folha-object.js') == 1

APP.write_text(app, encoding='utf-8')
SHELL.write_text(shell, encoding='utf-8')
SW.write_text(sw, encoding='utf-8')
