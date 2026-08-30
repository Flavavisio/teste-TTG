from pathlib import Path

path = Path('app.html')
text = path.read_text(encoding='utf-8')

start_marker = "        function mostrarStatusOffline(erroPersistente) {"
end_marker = "        if (document.readyState !== 'loading') _atualizarIndicadorLigacao();\n\n        function guardarDados() {"
old_init = "window.TotalGestApp.init({ pwa: true, toast: true, ui: true, dialogs: true, bootstrap: true });"
new_init = "window.TotalGestApp.init({ pwa: true, toast: true, ui: true, dialogs: true, connectivity: true, bootstrap: true });"

if text.count(start_marker) != 1:
    raise SystemExit('marcador inicial de conectividade inesperado')
if text.count(end_marker) != 1:
    raise SystemExit('marcador final de conectividade inesperado')
if text.count(old_init) != 1 or text.count(new_init) != 0:
    raise SystemExit('estado do init modular inesperado')
if text.count('        function guardarDados() {') != 1:
    raise SystemExit('guardarDados inesperado antes da migracao')
if text.count('        function _contarAlteracoesPendentes() {') != 1:
    raise SystemExit('_contarAlteracoesPendentes inesperado antes da migracao')

start = text.index(start_marker)
end = text.index(end_marker, start)
replacement = "        function guardarDados() {"
text = text[:start] + replacement + text[end + len(end_marker):]
text = text.replace(old_init, new_init, 1)

if start_marker in text:
    raise SystemExit('mostrarStatusOffline inline nao foi removido')
if '        function _atualizarIndicadorLigacao() {' in text:
    raise SystemExit('_atualizarIndicadorLigacao inline nao foi removido')
if text.count('        function guardarDados() {') != 1:
    raise SystemExit('guardarDados foi alterado indevidamente')
if text.count('        function _contarAlteracoesPendentes() {') != 1:
    raise SystemExit('_contarAlteracoesPendentes foi alterado indevidamente')
if text.count(new_init) != 1:
    raise SystemExit('connectivity nao foi ativado exatamente uma vez')
if text.count('mostrarStatusOffline();') < 3:
    raise SystemExit('chamadas legadas de mostrarStatusOffline desapareceram inesperadamente')

path.write_text(text, encoding='utf-8')
print('OK: conectividade inline removida; helpers de dados preservados; modulo externo ativado.')
