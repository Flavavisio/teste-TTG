from pathlib import Path
import re

path = Path('app.html')
text = path.read_text(encoding='utf-8')

start_marker = "        function _tabelaInexistente(e) {"
end_marker = "        async function _sincronizar() {"

if text.count(start_marker) != 1:
    raise SystemExit('marcador _tabelaInexistente inesperado')
if text.count('        function _colunaEmFalta(e) {') != 1:
    raise SystemExit('marcador _colunaEmFalta inesperado')
if text.count(end_marker) != 1:
    raise SystemExit('marcador _sincronizar inesperado')
if text.index(start_marker) > text.index(end_marker):
    raise SystemExit('ordem dos blocos de sincronizacao inesperada')

init_re = re.compile(r"window\.TotalGestApp\.init\(\{([^}]*)\}\);")
matches = list(init_re.finditer(text))
if len(matches) != 1:
    raise SystemExit('init modular inesperado')
opts = matches[0].group(1)
for required in ('pwa: true', 'toast: true', 'ui: true', 'dialogs: true', 'cache: true', 'connectivity: true', 'syncStatus: true', 'bootstrap: true'):
    if required not in opts:
        raise SystemExit(f'opcao modular em falta: {required}')
if 'syncHelpers:' in opts:
    raise SystemExit('syncHelpers ja aparece no init')

start = text.index(start_marker)
end = text.index(end_marker, start)
removed = text[start:end]
if 'function _tabelaInexistente(e)' not in removed or 'function _colunaEmFalta(e)' not in removed:
    raise SystemExit('bloco dos helpers incompleto')
if 'async function _sincronizar()' in removed:
    raise SystemExit('_sincronizar entrou indevidamente no bloco a remover')

text = text[:start] + text[end:]
old_init = matches[0].group(0)
new_opts = opts.replace('bootstrap: true', 'syncHelpers: true, bootstrap: true', 1)
new_init = f'window.TotalGestApp.init({{{new_opts}}});'
text = text.replace(old_init, new_init, 1)

if 'function _tabelaInexistente(e)' in text:
    raise SystemExit('_tabelaInexistente inline nao foi removida')
if 'function _colunaEmFalta(e)' in text:
    raise SystemExit('_colunaEmFalta inline nao foi removida')
if text.count(end_marker) != 1:
    raise SystemExit('_sincronizar foi alterado indevidamente')
if text.count('syncHelpers: true') != 1:
    raise SystemExit('syncHelpers nao foi ativado exatamente uma vez')
if text.count('function guardarDados() {') != 1:
    raise SystemExit('guardarDados foi alterado indevidamente')

path.write_text(text, encoding='utf-8')
print('OK: helpers de erro extraidos; _sincronizar e guardarDados preservados.')
