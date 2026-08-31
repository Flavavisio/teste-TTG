from pathlib import Path

APP = Path('app.html')
SHELL = Path('assets/js/app-shell.js')
SW = Path('sw.js')

app = APP.read_text(encoding='utf-8')
shell = SHELL.read_text(encoding='utf-8')
sw = SW.read_text(encoding='utf-8')

function_start = app.index('async function _salvarFormularioInterno(e)')
start_token = "            // Validação de formato — telefone (indicativo + 9 dígitos) e código postal (0000-000),\n"
end_token = "            if (ent === 'funcionario') {\n"
start = app.index(start_token, function_start)
end = app.index(end_token, start)
old = app[start:end]
for token in [
    "for (const idCp of ['f_cp', 'c_cp'])",
    'codigoPostalValido(elCp.value)',
    "for (const idTel of ['f_telefone', 'c_telefone'])",
    'telefoneValido(elTel.value)',
    "mostrarErro('Código postal inválido. Usa o formato 0000-000.');",
    "mostrarErro('Telefone inválido. O número (sem o indicativo) deve ter 9 dígitos.');"
]:
    assert token in old, token

new = """            const _contactosValidos = window.TotalGestSaveFormContactValidation.validate({
                document: document,
                postalCodeValid: codigoPostalValido,
                phoneValid: telefoneValido,
                showError: mostrarErro
            });
            if (!_contactosValidos) return;

"""
app = app[:start] + new + app[end:]

anchor = 'saveFormAuth: true'
assert app.count(anchor) == 1, app.count(anchor)
app = app.replace(anchor, anchor + ', saveFormContactValidation: true', 1)

shell_anchor = "    saveFormAuth: './assets/js/app-save-form-auth.js',\n"
assert shell.count(shell_anchor) == 1, shell.count(shell_anchor)
shell = shell.replace(shell_anchor, shell_anchor + "    saveFormContactValidation: './assets/js/app-save-form-contact-validation.js',\n", 1)
load_anchor = "    if (options.saveFormAuth === true) pedidos.push(MODULOS.saveFormAuth);\n"
assert shell.count(load_anchor) == 1, shell.count(load_anchor)
shell = shell.replace(load_anchor, load_anchor + "    if (options.saveFormContactValidation === true) pedidos.push(MODULOS.saveFormContactValidation);\n", 1)

assert "const CACHE = 'totalgest-v78';" in sw
sw = sw.replace("const CACHE = 'totalgest-v78';", "const CACHE = 'totalgest-v79';", 1)
sw_anchor = "  './assets/js/app-save-form-auth.js',\n"
assert sw.count(sw_anchor) == 1, sw.count(sw_anchor)
sw = sw.replace(sw_anchor, sw_anchor + "  './assets/js/app-save-form-contact-validation.js',\n", 1)

assert app.count('window.TotalGestSaveFormContactValidation.validate({') == 1
new_end = app.index(end_token, start)
new_block = app[start:new_end]
assert "for (const idCp of ['f_cp', 'c_cp'])" not in new_block
assert "for (const idTel of ['f_telefone', 'c_telefone'])" not in new_block
assert shell.count('./assets/js/app-save-form-contact-validation.js') == 1
assert sw.count('./assets/js/app-save-form-contact-validation.js') == 1

APP.write_text(app, encoding='utf-8')
SHELL.write_text(shell, encoding='utf-8')
SW.write_text(sw, encoding='utf-8')
