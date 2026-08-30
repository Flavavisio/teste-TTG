/* Total Gest — cache local offline
 * Mantém uma cópia dos dados e do snapshot confirmado para permitir arranque e trabalho offline.
 */
(function () {
  'use strict';

  let cacheLocalDesativada = false;

  function guardarCacheLocal() {
    if (cacheLocalDesativada) return;
    try {
      const snapPlano = {};
      for (const col of ORDEM) snapPlano[col] = Object.fromEntries(_snap[col] || new Map());
      localStorage.setItem('tg_cache_dados_v1', JSON.stringify(dados));
      localStorage.setItem('tg_cache_snap_v1', JSON.stringify({
        porColuna: snapPlano,
        lic: Object.fromEntries(_snapLic || new Map()),
        junc: Object.fromEntries(_snapJunc || new Map())
      }));
      localStorage.setItem('tg_cache_dados_v1_quando', String(Date.now()));
    } catch (e) {
      if (e && e.name === 'QuotaExceededError') {
        cacheLocalDesativada = true;
        console.warn('Cópia local offline desativada: dados demasiado grandes para o armazenamento do browser. A app continua a funcionar normalmente online.');
      } else {
        console.warn('cache local (guardar):', e);
      }
    }
  }

  function carregarCacheLocal() {
    try {
      const txt = localStorage.getItem('tg_cache_dados_v1');
      if (!txt) return null;
      return JSON.parse(txt);
    } catch (e) {
      console.warn('cache local (ler):', e);
      return null;
    }
  }

  function restaurarSnapshotDaCache() {
    try {
      const txt = localStorage.getItem('tg_cache_snap_v1');
      if (!txt) {
        _reconstruirSnapshots();
        return;
      }
      const s = JSON.parse(txt);
      _snap = {};
      for (const col of ORDEM) _snap[col] = new Map(Object.entries(s.porColuna?.[col] || {}));
      _snapLic = new Map(Object.entries(s.lic || {}));
      _snapJunc = new Map(Object.entries(s.junc || {}));
    } catch (e) {
      console.warn('restaurar snapshot da cache:', e);
      _reconstruirSnapshots();
    }
  }

  window._guardarCacheLocal = guardarCacheLocal;
  window._carregarCacheLocal = carregarCacheLocal;
  window._restaurarSnapshotDaCache = restaurarSnapshotDaCache;

  window.TotalGestCache = {
    save: guardarCacheLocal,
    load: carregarCacheLocal,
    restoreSnapshot: restaurarSnapshotDaCache
  };
})();
