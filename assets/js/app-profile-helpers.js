/* Total Gest — helpers UI do modal de perfil. */
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
