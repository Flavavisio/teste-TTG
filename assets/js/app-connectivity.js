/* Total Gest — estado de conectividade e sincronização visual.
 * Mantém os nomes globais usados pelo código legado durante a migração incremental.
 */
(function () {
  'use strict';

  let iniciado = false;
  let intervalo = null;

  function mostrarStatusOffline(erroPersistente) {
    let el = document.getElementById('offlineToast');
    const offline = !navigator.onLine;
    const pendentes = _contarAlteracoesPendentes();
    if (!offline && !pendentes) {
      if (el) el.style.display = 'none';
      return;
    }
    if (!el) {
      el = document.createElement('div');
      el.id = 'offlineToast';
      el.style.cssText = 'position:fixed; bottom:20px; left:20px; z-index:99998; background:#0b3b5c; color:#fff; padding:12px 16px; border-radius:10px; box-shadow:0 6px 20px rgba(0,0,0,.2); max-width:320px; font-size:13.5px;';
      document.body.appendChild(el);
    }
    el.style.display = 'block';
    if (offline) {
      el.innerHTML = `<div style="display:flex;align-items:center;gap:8px;"><i class="fas fa-wifi-slash"></i><div>Sem ligação — a trabalhar offline.${pendentes ? '<br><span style="opacity:.8;">' + pendentes + ' alteração(ões) por sincronizar.' : ''}</span></div></div>`;
    } else if (erroPersistente) {
      el.style.background = '#7c2d12';
      el.innerHTML = `<div style="display:flex;align-items:center;gap:8px;"><i class="fas fa-triangle-exclamation"></i><div>${pendentes} alteração(ões) por sincronizar — houve um erro.<br><a href="#" onclick="guardarDados(); return false;" style="color:#fdba74;">Tentar novamente</a></div></div>`;
    } else {
      el.style.background = '#0b3b5c';
      el.innerHTML = `<div style="display:flex;align-items:center;gap:8px;"><i class="fas fa-cloud-arrow-up fa-spin"></i><div>A sincronizar ${pendentes} alteração(ões)…</div></div>`;
    }
  }

  function _atualizarIndicadorLigacao() {
    const dot = document.getElementById('ligacaoDot');
    const txt = document.getElementById('ligacaoTexto');
    const wrap = document.getElementById('ligacaoIndicador');
    if (!dot || !txt || !wrap) return;
    const offline = !navigator.onLine;
    const pendentes = _contarAlteracoesPendentes();
    if (offline) {
      dot.style.background = '#dc2626';
      txt.textContent = 'Offline';
      wrap.title = 'Sem ligação — a trabalhar offline.' + (pendentes ? ' ' + pendentes + ' alteração(ões) por sincronizar.' : '');
    } else if (pendentes) {
      dot.style.background = '#d97706';
      txt.textContent = 'A sincronizar';
      wrap.title = pendentes + ' alteração(ões) por sincronizar…';
    } else {
      dot.style.background = '#16a34a';
      txt.textContent = 'Online';
      wrap.title = 'Ligado e sincronizado.';
    }
  }

  function iniciar() {
    if (iniciado) return;
    iniciado = true;

    window.addEventListener('offline', function () {
      mostrarStatusOffline();
      _atualizarIndicadorLigacao();
    });
    window.addEventListener('online', function () {
      mostrarStatusOffline();
      guardarDados();
      _atualizarIndicadorLigacao();
    });

    intervalo = setInterval(_atualizarIndicadorLigacao, 4000);
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', _atualizarIndicadorLigacao, { once: true });
    } else {
      _atualizarIndicadorLigacao();
    }
  }

  window.mostrarStatusOffline = mostrarStatusOffline;
  window._atualizarIndicadorLigacao = _atualizarIndicadorLigacao;
  window.TotalGestConnectivity = {
    init: iniciar,
    refresh: _atualizarIndicadorLigacao,
    isStarted: function () { return iniciado; },
    interval: function () { return intervalo; }
  };
})();
