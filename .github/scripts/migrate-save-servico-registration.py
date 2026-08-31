from pathlib import Path

APP = Path('app.html')
SHELL = Path('assets/js/app-shell.js')
SW = Path('sw.js')

app = APP.read_text(encoding='utf-8')
shell = SHELL.read_text(encoding='utf-8')
sw = SW.read_text(encoding='utf-8')

old = """                if (!isEdit) {
                    obj.numeroRegisto = await gerarNumeroRegistoServidor();
                }
"""
assert app.count(old) == 1, app.count(old)
new = """                obj = await window.TotalGestSaveFormServicoRegistration.apply({
                    value: obj,
                    isEdit: isEdit,
                    generateRegistrationNumber: gerarNumeroRegistoServidor
                });
"""
app = app.replace(old, new, 1)

anchor = 'saveFormServicoConflicts: true'
assert app.count(anchor) == 1, app.count(anchor)
app = app.replace(anchor, anchor + ', saveFormServicoRegistration: true', 1)

shell_anchor = "    saveFormServicoConflicts: './assets/js/app-save-form-servico-conflicts.js',\n"
assert shell.count(shell_anchor) == 1, shell.count(shell_anchor)
shell = shell.replace(shell_anchor, shell_anchor + "    saveFormServicoRegistration: './assets/js/app-save-form-servico-registration.js',\n", 1)
load_anchor = "    if (options.saveFormServicoConflicts === true) pedidos.push(MODULOS.saveFormServicoConflicts);\n"
assert shell.count(load_anchor) == 1, shell.count(load_anchor)
shell = shell.replace(load_anchor, load_anchor + "    if (options.saveFormServicoRegistration === true) pedidos.push(MODULOS.saveFormServicoRegistration);\n", 1)

assert "const CACHE = 'totalgest-v69';" in sw
sw = sw.replace("const CACHE = 'totalgest-v69';", "const CACHE = 'totalgest-v70';", 1)
sw_anchor = "  './assets/js/app-save-form-servico-conflicts.js',\n"
assert sw.count(sw_anchor) == 1, sw.count(sw_anchor)
sw = sw.replace(sw_anchor, sw_anchor + "  './assets/js/app-save-form-servico-registration.js',\n", 1)

assert app.count('window.TotalGestSaveFormServicoRegistration.apply({') == 1
assert app.count('gerarNumeroRegistoServidor();') == 0
assert shell.count('./assets/js/app-save-form-servico-registration.js') == 1
assert sw.count('./assets/js/app-save-form-servico-registration.js') == 1

APP.write_text(app, encoding='utf-8')
SHELL.write_text(shell, encoding='utf-8')
SW.write_text(sw, encoding='utf-8')
