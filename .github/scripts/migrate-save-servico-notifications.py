from pathlib import Path

APP = Path('app.html')
SHELL = Path('assets/js/app-shell.js')
SW = Path('sw.js')

app = APP.read_text(encoding='utf-8')
shell = SHELL.read_text(encoding='utf-8')
sw = SW.read_text(encoding='utf-8')

func_start = app.index('async function _salvarFormularioInterno(')
start_token = "            else if (ent === 'servico') {\n                dados.servicos = lista;\n"
end_token = "            }\n            else if (ent === 'folha') dados.folhasObra = lista;\n"
assert app.count(start_token) == 1, app.count(start_token)
start = app.index(start_token, func_start)
end = app.index(end_token, start)
old = app[start:end + len("            }\n")]
for token in [
    'const _destinatarios = [...new Set(',
    "'🧾 Nova Ordem de Serviço atribuída'",
    "'💶 Pagamento no local'",
    "'📅 Visita agendada'",
    'const _idsAntes = [...new Set(',
    "'📅 OS '",
    "'🚫 Retirado de uma OS'",
    "'✅ Pedido de assistência aceite'"
]:
    assert token in old, token

new = """            else if (ent === 'servico') {
                dados.servicos = lista;
                window.TotalGestSaveFormServicoNotifications.run({
                    value: obj,
                    oldService: _servicoAntigo,
                    data: dados,
                    isEdit: isEdit,
                    clientName: obterNomeCliente,
                    notify: _notificarFuncionario,
                    formatEuro: _finEur
                });
            }
"""
app = app[:start] + new + app[end + len("            }\n"):]

anchor = 'saveFormPersist: true'
assert app.count(anchor) == 1, app.count(anchor)
app = app.replace(anchor, anchor + ', saveFormServicoNotifications: true', 1)

shell_anchor = "    saveFormPersist: './assets/js/app-save-form-persist.js',\n"
assert shell.count(shell_anchor) == 1, shell.count(shell_anchor)
shell = shell.replace(shell_anchor, shell_anchor + "    saveFormServicoNotifications: './assets/js/app-save-form-servico-notifications.js',\n", 1)
load_anchor = "    if (options.saveFormPersist === true) pedidos.push(MODULOS.saveFormPersist);\n"
assert shell.count(load_anchor) == 1, shell.count(load_anchor)
shell = shell.replace(load_anchor, load_anchor + "    if (options.saveFormServicoNotifications === true) pedidos.push(MODULOS.saveFormServicoNotifications);\n", 1)

assert "const CACHE = 'totalgest-v72';" in sw
sw = sw.replace("const CACHE = 'totalgest-v72';", "const CACHE = 'totalgest-v73';", 1)
sw_anchor = "  './assets/js/app-save-form-persist.js',\n"
assert sw.count(sw_anchor) == 1, sw.count(sw_anchor)
sw = sw.replace(sw_anchor, sw_anchor + "  './assets/js/app-save-form-servico-notifications.js',\n", 1)

func_end = app.index('function _emailFantasmaCliente(', func_start)
block = app[func_start:func_end]
assert block.count('window.TotalGestSaveFormServicoNotifications.run({') == 1
for token in [
    'const _destinatarios = [...new Set(',
    'const _idsAntes = [...new Set(',
    "'🧾 Nova Ordem de Serviço atribuída'",
    "'🚫 Retirado de uma OS'"
]:
    assert token not in block, token
assert shell.count('./assets/js/app-save-form-servico-notifications.js') == 1
assert sw.count('./assets/js/app-save-form-servico-notifications.js') == 1

APP.write_text(app, encoding='utf-8')
SHELL.write_text(shell, encoding='utf-8')
SW.write_text(sw, encoding='utf-8')
