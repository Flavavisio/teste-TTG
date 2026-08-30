from pathlib import Path
import re

path = Path('app.html')
text = path.read_text(encoding='utf-8')

start_marker = "        // Cópia local (offline-first): guarda o último estado conhecido para a app conseguir"
end_marker = "        // -------- sincronização por diferenças (substitui o antigo guardarDados) --------"

if text.count(start_marker) != 1:
    raise SystemExit('marcador inicial da cache inesperado')
if text.count(end_marker) != 1:
    raise SystemExit('marcador final da cache inesperado')
for fn in ('_guardarCacheLocal', '_carregarCacheLocal', '_restaurarSnapshotDaCache'):
    if text.count(f'function {fn}() {{') != 1:
        raise SystemExit(f'funcao inline {fn} inesperada')
if text.count('let _cacheLocalDesativada = false;') != 1:
    raise SystemExit('estado da cache local inesperado')

init_re = re.compile(r"window\.TotalGestApp\.init\(\{([^}]*)\}\);")
matches = list(init_re.finditer(text))
if len(matches) != 1:
    raise SystemExit('init modular inesperado')
opts = matches[0].group(1)
for required in ('pwa: true', 'toast: true', 'ui: true', 'dialogs: true', 'connectivity: true', 'syncStatus: true', 'bootstrap: true'):
    if required not in opts:
        raise SystemExit(f'opcao modular em falta: {required}')
if 'cache:' in opts:
    raise SystemExit('cache ja aparece no init')

start = text.index(start_marker)
end = text.index(end_marker, start)
text = text[:start] + text[end:]

old_init = matches[0].group(0)
new_opts = opts.replace('bootstrap: true', 'cache: true, bootstrap: true', 1)
new_init = f'window.TotalGestApp.init({{{new_opts}}});'
text = text.replace(old_init, new_init, 1)

for fn in ('_guardarCacheLocal', '_carregarCacheLocal', '_restaurarSnapshotDaCache'):
    if f'function {fn}() {{' in text:
        raise SystemExit(f'{fn} inline nao foi removida')
if 'let _cacheLocalDesativada = false;' in text:
    raise SystemExit('estado inline da cache nao foi removido')
if text.count('cache: true') != 1:
    raise SystemExit('cache modular nao foi ativada exatamente uma vez')
if text.count(end_marker) != 1:
    raise SystemExit('bloco de sincronizacao seguinte foi alterado')
if text.count('function guardarDados() {') != 1:
    raise SystemExit('guardarDados foi alterado indevidamente')

path.write_text(text, encoding='utf-8')
print('OK: cache local inline removida e modulo externo ativado; sincronizacao preservada.')
