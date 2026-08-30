from pathlib import Path

path = Path('app.html')
text = path.read_text(encoding='utf-8')

start_marker = "        // Traduz mensagens técnicas do servidor (Postgres/Supabase) para uma frase calma e\n"
end_marker = "        let _syncChain = Promise.resolve();"
old_init = "window.TotalGestApp.init({ pwa: true, toast: true, ui: true, dialogs: true, connectivity: true, bootstrap: true });"
new_init = "window.TotalGestApp.init({ pwa: true, toast: true, ui: true, dialogs: true, connectivity: true, syncStatus: true, bootstrap: true });"

if text.count(start_marker) != 1:
    raise SystemExit('inicio do bloco sync status inesperado')
if text.count(end_marker) != 1:
    raise SystemExit('fim do bloco sync status inesperado')
if text.count('        function _traduzirErroSync(detalheOriginal) {') != 1:
    raise SystemExit('_traduzirErroSync inesperado')
if text.count('        function mostrarStatusSync(erros, detalhe) {') != 1:
    raise SystemExit('mostrarStatusSync inesperado')
if text.count(old_init) != 1 or text.count(new_init) != 0:
    raise SystemExit('init modular inesperado')

start = text.index(start_marker)
end = text.index(end_marker, start)
text = text[:start] + end_marker + text[end + len(end_marker):]
text = text.replace(old_init, new_init, 1)

if '        function _traduzirErroSync(detalheOriginal) {' in text:
    raise SystemExit('_traduzirErroSync inline nao foi removido')
if '        function mostrarStatusSync(erros, detalhe) {' in text:
    raise SystemExit('mostrarStatusSync inline nao foi removido')
if text.count(end_marker) != 1:
    raise SystemExit('_syncChain foi alterado indevidamente')
if text.count('mostrarStatusSync(') < 2:
    raise SystemExit('chamadas legadas de mostrarStatusSync desapareceram')
if text.count(new_init) != 1:
    raise SystemExit('syncStatus nao foi ativado exatamente uma vez')

path.write_text(text, encoding='utf-8')
print('OK: mensagens de sincronizacao extraidas e modulo externo ativado.')
