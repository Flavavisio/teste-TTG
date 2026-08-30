/* Total Gest — PWA da aplicação
 * Extração incremental do bloco legado de app.html.
 * Mantém as funções globais necessárias ao aviso de atualização.
 * Ainda não substitui o bloco inline de app.html; será ligado apenas após validação.
 */

(function () {
  'use strict';

  let avisoNovaVersaoMostrado = false;

  function mostrarAvisoNovaVersao() {
    if (avisoNovaVersaoMostrado) return;
    avisoNovaVersaoMostrado = true;

    const div = document.createElement('div');
    div.style.cssText = 'position:fixed;left:16px;right:16px;bottom:16px;max-width:420px;margin:0 auto;background:#152a52;color:#fff;border-radius:12px;padding:14px 16px;box-shadow:0 10px 30px rgba(0,0,0,.3);z-index:999999;display:flex;align-items:center;gap:12px;font-family:inherit;';
    div.innerHTML = '<div style="flex:1;font-size:.88rem;"><strong>Nova versão disponível.</strong><br>Atualiza para veres as últimas melhorias.</div>' +
      '<button style="background:#f4520e;color:#fff;border:none;border-radius:8px;padding:8px 14px;font-weight:700;font-size:.85rem;cursor:pointer;white-space:nowrap;" type="button" data-tg-update-app>Atualizar</button>';

    const button = div.querySelector('[data-tg-update-app]');
    if (button) button.addEventListener('click', atualizarParaNovaVersao);
    document.body.appendChild(div);
  }

  async function atualizarParaNovaVersao() {
    try {
      const reg = await navigator.serviceWorker.getRegistration();
      if (reg && reg.waiting) {
        reg.waiting.postMessage('SKIP_WAITING');
        navigator.serviceWorker.addEventListener('controllerchange', function () {
          location.reload();
        }, { once: true });
        setTimeout(function () { location.reload(); }, 1500);
        return;
      }
    } catch (e) {}
    location.reload();
  }

  function registarPwa() {
    if (!('serviceWorker' in navigator)) return;

    window.addEventListener('load', function () {
      navigator.serviceWorker.register('sw.js').then(function (reg) {
        reg.addEventListener('updatefound', function () {
          const novoWorker = reg.installing;
          if (!novoWorker) return;

          novoWorker.addEventListener('statechange', function () {
            if (novoWorker.state === 'installed' && navigator.serviceWorker.controller) {
              mostrarAvisoNovaVersao();
            }
          });
        });

        setInterval(function () {
          reg.update().catch(function () {});
        }, 30 * 60 * 1000);
      }).catch(function (err) {
        console.warn('Service worker não registado (precisa de HTTPS):', err);
      });

      navigator.serviceWorker.addEventListener('message', function (ev) {
        if (ev.data && ev.data.type === 'SW_UPDATED') {
          mostrarAvisoNovaVersao();
        }
      });
    });
  }

  // Compatibilidade com chamadas globais do código legado durante a migração.
  window._mostrarAvisoNovaVersao = mostrarAvisoNovaVersao;
  window._atualizarParaNovaVersao = atualizarParaNovaVersao;
  window.TotalGestPwa = {
    init: registarPwa,
    mostrarAvisoNovaVersao: mostrarAvisoNovaVersao,
    atualizarParaNovaVersao: atualizarParaNovaVersao
  };
})();
