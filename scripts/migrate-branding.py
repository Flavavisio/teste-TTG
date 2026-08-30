from pathlib import Path

path = Path('app.html')
text = path.read_text(encoding='utf-8')

block = """<script>
// Branding da aplicação privada — independente da landing pública.
(function () {
    const logoSrc = 'logo-totalgest.png';
    document.querySelectorAll('.tg-logo-clone').forEach(img => { img.src = logoSrc; });
})();
</script>
"""

if text.count(block) != 1:
    raise SystemExit('bloco inline de branding inesperado')
if text.count('<script src="./assets/js/app-shell.js"></script>') != 1:
    raise SystemExit('app-shell inesperado')
if text.count('window.TotalGestApp.init({ pwa: true, toast: true, ui: true, dialogs: true, connectivity: true, bootstrap: true });') != 1:
    raise SystemExit('init modular inesperado')

text = text.replace(block, '', 1)

if 'Branding da aplicação privada — independente da landing pública.' in text:
    raise SystemExit('branding inline nao foi removido')
if text.count('<script src="./assets/js/app-shell.js"></script>') != 1:
    raise SystemExit('app-shell foi alterado indevidamente')
if text.count('window.TotalGestApp.init({ pwa: true, toast: true, ui: true, dialogs: true, connectivity: true, bootstrap: true });') != 1:
    raise SystemExit('init modular foi alterado indevidamente')

path.write_text(text, encoding='utf-8')
print('OK: branding inline removido; app-shell e init preservados.')
