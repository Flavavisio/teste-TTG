/* Total Gest — preferências da interface
 * Tema, sidebar, zoom e branding interno. Mantém os nomes globais usados pelo HTML e pelo bootstrap legado.
 */
(function () {
  'use strict';

  function carregarTemaMarca() {
    if (document.querySelector('link[data-tg-brand-theme]')) return;
    const link = document.createElement('link');
    link.rel = 'stylesheet';
    link.href = './assets/css/brand-theme.css';
    link.dataset.tgBrandTheme = '1';
    document.head.appendChild(link);
    const meta = document.querySelector('meta[name="theme-color"]');
    if (meta) meta.setAttribute('content', '#243B8F');
  }

  const NIVEIS_ZOOM = [100, 90, 80];

  function alternarTema() {
    const ativo = document.body.classList.toggle('dark-mode');
    try { localStorage.setItem('tg_tema', ativo ? 'escuro' : 'claro'); } catch (e) {}
    const ic = document.getElementById('iconeTema');
    if (ic) {
      ic.classList.toggle('fa-moon', !ativo);
      ic.classList.toggle('fa-sun', ativo);
    }
  }

  function alternarSidebarEncolhida() {
    const ativo = document.body.classList.toggle('tg-sidebar-collapsed');
    try { localStorage.setItem('tg_sidebar_collapsed', ativo ? '1' : '0'); } catch (e) {}
  }

  function aplicarSidebarEncolhidaGuardada() {
    let guardado = null;
    try { guardado = localStorage.getItem('tg_sidebar_collapsed'); } catch (e) {}
    if (guardado === '1') document.body.classList.add('tg-sidebar-collapsed');
  }

  function aplicarZoom(nivel) {
    document.documentElement.style.zoom = nivel + '%';
    const lbl = document.getElementById('labelZoom');
    if (lbl) lbl.textContent = nivel + '%';

    // Compensa o efeito do CSS zoom em dimensões que precisam continuar a preencher o ecrã.
    const compensado = Math.round((100 / (nivel / 100)) * 100) / 100;
    document.documentElement.style.setProperty('--tg-zoom-compensa', compensado + '%');
  }

  function alternarZoom() {
    let atual = 100;
    try { atual = parseInt(localStorage.getItem('tg_zoom'), 10) || 100; } catch (e) {}
    const idxAtual = NIVEIS_ZOOM.indexOf(atual);
    const proximo = NIVEIS_ZOOM[(idxAtual + 1) % NIVEIS_ZOOM.length];
    aplicarZoom(proximo);
    try { localStorage.setItem('tg_zoom', String(proximo)); } catch (e) {}
  }

  function aplicarZoomGuardado() {
    let nivel = 100;
    try { nivel = parseInt(localStorage.getItem('tg_zoom'), 10) || 100; } catch (e) {}
    if (nivel !== 100) aplicarZoom(nivel);
  }

  function aplicarTemaGuardado() {
    let tema = null;
    try { tema = localStorage.getItem('tg_tema'); } catch (e) {}
    if (tema === 'escuro') {
      document.body.classList.add('dark-mode');
      const ic = document.getElementById('iconeTema');
      if (ic) {
        ic.classList.remove('fa-moon');
        ic.classList.add('fa-sun');
      }
    }
  }

  function aplicarBranding() {
    const logoSrc = 'logo-totalgest.png';
    document.querySelectorAll('.tg-logo-clone').forEach(function (img) {
      img.src = logoSrc;
    });
  }

  window.alternarTema = alternarTema;
  window.alternarSidebarEncolhida = alternarSidebarEncolhida;
  window._aplicarSidebarEncolhidaGuardada = aplicarSidebarEncolhidaGuardada;
  window.alternarZoom = alternarZoom;
  window._aplicarZoom = aplicarZoom;
  window._aplicarZoomGuardado = aplicarZoomGuardado;
  window._aplicarTemaGuardado = aplicarTemaGuardado;
  window._aplicarBrandingTotalGest = aplicarBranding;

  window.TotalGestUi = {
    toggleTheme: alternarTema,
    toggleSidebar: alternarSidebarEncolhida,
    toggleZoom: alternarZoom,
    applyStoredTheme: aplicarTemaGuardado,
    applyStoredSidebar: aplicarSidebarEncolhidaGuardada,
    applyStoredZoom: aplicarZoomGuardado,
    applyBranding: aplicarBranding
  };

  // O módulo é carregado no fim do body, quando os clones do logótipo já existem.
  carregarTemaMarca();
  aplicarBranding();
})();
