from pathlib import Path

APP = Path('app.html')
SHELL = Path('assets/js/app-shell.js')
SW = Path('sw.js')

app = APP.read_text(encoding='utf-8')
shell = SHELL.read_text(encoding='utf-8')
sw = SW.read_text(encoding='utf-8')

func_start = app.index('async function _salvarFormularioInterno(')
start_token = '            let lista;\n'
end_token = "            if (ent === 'funcionario') dados.funcionarios = lista;\n"
start = app.index(start_token, func_start)
end = app.index(end_token, start)
old = app[start:end]
for token in [
    "if (ent === 'funcionario') lista = dados.funcionarios || [];",
    "else if (ent === 'cliente') lista = dados.clientes || [];",
    "else if (ent === 'servico') lista = dados.servicos || [];",
    "else if (ent === 'folha') lista = dados.folhasObra || [];",
    'let _servicoAntigo = null;',
    'let _funcAntesDeEditar = null;',
    'const idx = lista.findIndex(i => i.id === idEditando);',
    'lista[idx] = { ...lista[idx], ...obj };',
    'if (!obj.id) obj.id = gerarId();',
    'lista.push(obj);'
]:
    assert token in old, token

new = """            const _persistenciaFormulario = window.TotalGestSaveFormPersist.apply({
                entity: ent,
                data: dados,
                value: obj,
                isEdit: isEdit,
                editingId: idEditando,
                generateId: gerarId
            });
            if (!_persistenciaFormulario.ok) return;
            obj = _persistenciaFormulario.value;
            const lista = _persistenciaFormulario.list;
            let _servicoAntigo = _persistenciaFormulario.oldService;
            let _funcAntesDeEditar = _persistenciaFormulario.oldEmployee;
"""
app = app[:start] + new + app[end:]

anchor = 'saveFormServico: true'
assert app.count(anchor) == 1, app.count(anchor)
app = app.replace(anchor, anchor + ', saveFormPersist: true', 1)

shell_anchor = "    saveFormServico: './assets/js/app-save-form-servico.js',\n"
assert shell.count(shell_anchor) == 1, shell.count(shell_anchor)
shell = shell.replace(shell_anchor, shell_anchor + "    saveFormPersist: './assets/js/app-save-form-persist.js',\n", 1)
load_anchor = "    if (options.saveFormServico === true) pedidos.push(MODULOS.saveFormServico);\n"
assert shell.count(load_anchor) == 1, shell.count(load_anchor)
shell = shell.replace(load_anchor, load_anchor + "    if (options.saveFormPersist === true) pedidos.push(MODULOS.saveFormPersist);\n", 1)

assert "const CACHE = 'totalgest-v71';" in sw
sw = sw.replace("const CACHE = 'totalgest-v71';", "const CACHE = 'totalgest-v72';", 1)
sw_anchor = "  './assets/js/app-save-form-servico.js',\n"
assert sw.count(sw_anchor) == 1, sw.count(sw_anchor)
sw = sw.replace(sw_anchor, sw_anchor + "  './assets/js/app-save-form-persist.js',\n", 1)

func_end = app.index('function _emailFantasmaCliente(', func_start)
block = app[func_start:func_end]
assert block.count('window.TotalGestSaveFormPersist.apply({') == 1
for token in [
    'const idx = lista.findIndex(i => i.id === idEditando);',
    'lista[idx] = { ...lista[idx], ...obj };',
    'if (!obj.id) obj.id = gerarId();',
    'lista.push(obj);'
]:
    assert token not in block, token
assert shell.count('./assets/js/app-save-form-persist.js') == 1
assert sw.count('./assets/js/app-save-form-persist.js') == 1

APP.write_text(app, encoding='utf-8')
SHELL.write_text(shell, encoding='utf-8')
SW.write_text(sw, encoding='utf-8')
