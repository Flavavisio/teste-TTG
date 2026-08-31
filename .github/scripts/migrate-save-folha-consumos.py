from pathlib import Path

APP = Path('app.html')
SHELL = Path('assets/js/app-shell.js')
SW = Path('sw.js')

app = APP.read_text(encoding='utf-8')
shell = SHELL.read_text(encoding='utf-8')
sw = SW.read_text(encoding='utf-8')

old = """                _folhaConsumoPendente = Array.from(document.querySelectorAll('#fo_plano_materiais .fo-consumo')).map(inp => ({ artigoId: inp.getAttribute('data-artigo'), consumido: parseInt(inp.value,10) || 0 }));
                _folhaConsumoPendente.push(..._foMatExtra.map(x => ({ artigoId: x.artigoId, consumido: x.qtd })));
                _foMatExtra = [];
"""
assert app.count(old) == 1, app.count(old)
new = """                _folhaConsumoPendente = window.TotalGestSaveFormFolhaConsumos.prepare({
                    document: document,
                    extraMaterials: _foMatExtra
                });
                _foMatExtra = [];
"""
app = app.replace(old, new, 1)

anchor = 'saveFormFolhaAssist: true'
assert app.count(anchor) == 1, app.count(anchor)
app = app.replace(anchor, anchor + ', saveFormFolhaConsumos: true', 1)

shell_anchor = "    saveFormFolhaAssist: './assets/js/app-save-form-folha-assist.js',\n"
assert shell.count(shell_anchor) == 1
shell = shell.replace(shell_anchor, shell_anchor + "    saveFormFolhaConsumos: './assets/js/app-save-form-folha-consumos.js',\n", 1)
load_anchor = "    if (options.saveFormFolhaAssist === true) pedidos.push(MODULOS.saveFormFolhaAssist);\n"
assert shell.count(load_anchor) == 1
shell = shell.replace(load_anchor, load_anchor + "    if (options.saveFormFolhaConsumos === true) pedidos.push(MODULOS.saveFormFolhaConsumos);\n", 1)

assert "const CACHE = 'totalgest-v57';" in sw
sw = sw.replace("const CACHE = 'totalgest-v57';", "const CACHE = 'totalgest-v58';", 1)
sw_anchor = "  './assets/js/app-save-form-folha-assist.js',\n"
assert sw.count(sw_anchor) == 1
sw = sw.replace(sw_anchor, sw_anchor + "  './assets/js/app-save-form-folha-consumos.js',\n", 1)

assert app.count('window.TotalGestSaveFormFolhaConsumos.prepare({') == 1
assert shell.count('./assets/js/app-save-form-folha-consumos.js') == 1
assert sw.count('./assets/js/app-save-form-folha-consumos.js') == 1

APP.write_text(app, encoding='utf-8')
SHELL.write_text(shell, encoding='utf-8')
SW.write_text(sw, encoding='utf-8')
