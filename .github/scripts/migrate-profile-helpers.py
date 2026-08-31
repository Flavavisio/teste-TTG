from pathlib import Path

APP = Path('app.html')
SHELL = Path('assets/js/app-shell.js')
SW = Path('sw.js')
MODULE = Path('assets/js/app-profile-helpers.js')

app = APP.read_text(encoding='utf-8')
shell = SHELL.read_text(encoding='utf-8')
sw = SW.read_text(encoding='utf-8')

start_marker = '        function previewPerfilLogo(e) {'
end_marker = '        function salvarPerfil(e) {'
assert app.count(start_marker) == 1, app.count(start_marker)
assert app.count(end_marker) == 1, app.count(end_marker)
start = app.index(start_marker)
end = app.index(end_marker, start)
old = app[start:end]

for token in [
    'function previewPerfilLogo(e) {',
    'function previewPerfilFoto(e) {',
    'function fecharModalPerfil() {',
    'function _perfPreviewCertificadoraLogo(input) {'
]:
    assert old.count(token) == 1, (token, old.count(token))

module = """/* Total Gest — helpers UI do modal de perfil. */
(function () {
  'use strict';

  function previewPerfilLogo(e) {
    const file = e.target.files[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = function (ev) {
        const img = document.getElementById('perf_logo_img');
        const ph = document.getElementById('perf_logo_placeholder');
        if (img) { img.src = ev.target.result; img.style.display = ''; }
        if (ph) ph.style.display = 'none';
        const preview = document.getElementById('perf_logo_preview');
        if (preview && !img) preview.innerHTML = `<img src="${ev.target.result}" style="max-width:100px; max-height:100px; border-radius:8px;" />`;
      };
      reader.readAsDataURL(file);
    }
  }

  function previewPerfilFoto(e) {
    const file = e.target.files[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = function (ev) {
        const img = document.getElementById('perf_foto_img');
        const ph = document.getElementById('perf_foto_placeholder');
        if (img) { img.src = ev.target.result; img.style.display = ''; }
        if (ph) ph.style.display = 'none';
      };
      reader.readAsDataURL(file);
    }
  }

  function fecharModalPerfil() {
    document.getElementById('modalPerfilOverlay').classList.remove('open');
  }

  function perfPreviewCertificadoraLogo(input) {
    if (!input.files || !input.files[0]) return;
    const reader = new FileReader();
    reader.onload = function (ev) { window._perfCertificadoraLogoNova = ev.target.result; };
    reader.readAsDataURL(input.files[0]);
  }

  window.previewPerfilLogo = previewPerfilLogo;
  window.previewPerfilFoto = previewPerfilFoto;
  window.fecharModalPerfil = fecharModalPerfil;
  window._perfPreviewCertificadoraLogo = perfPreviewCertificadoraLogo;
})();
"""
MODULE.write_text(module, encoding='utf-8')

app = app[:start] + app[end:]

init_anchor = 'profileModal: true'
assert app.count(init_anchor) == 1, app.count(init_anchor)
app = app.replace(init_anchor, init_anchor + ', profileHelpers: true', 1)

module_anchor = "    profileModal: './assets/js/app-profile-modal.js',\n"
assert shell.count(module_anchor) == 1, shell.count(module_anchor)
shell = shell.replace(module_anchor, module_anchor + "    profileHelpers: './assets/js/app-profile-helpers.js',\n", 1)
load_anchor = "    if (options.profileModal === true) pedidos.push(MODULOS.profileModal);\n"
assert shell.count(load_anchor) == 1, shell.count(load_anchor)
shell = shell.replace(load_anchor, load_anchor + "    if (options.profileHelpers === true) pedidos.push(MODULOS.profileHelpers);\n", 1)

assert "const CACHE = 'totalgest-v86';" in sw
sw = sw.replace("const CACHE = 'totalgest-v86';", "const CACHE = 'totalgest-v87';", 1)
sw_anchor = "  './assets/js/app-profile-modal.js',\n"
assert sw.count(sw_anchor) == 1, sw.count(sw_anchor)
sw = sw.replace(sw_anchor, sw_anchor + "  './assets/js/app-profile-helpers.js',\n", 1)

for token in [
    'function previewPerfilLogo(e) {',
    'function previewPerfilFoto(e) {',
    'function fecharModalPerfil() {',
    'function _perfPreviewCertificadoraLogo(input) {'
]:
    assert token not in app, token
assert app.count('function salvarPerfil(e) {') == 1
assert shell.count('./assets/js/app-profile-helpers.js') == 1
assert sw.count('./assets/js/app-profile-helpers.js') == 1

APP.write_text(app, encoding='utf-8')
SHELL.write_text(shell, encoding='utf-8')
SW.write_text(sw, encoding='utf-8')
