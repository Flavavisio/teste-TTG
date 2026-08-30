/* Total Gest — shell modular da aplicação
 * Ponto de entrada para os módulos extraídos de app.html.
 * O ficheiro ainda não é carregado pelo app.html legado; não altera o runtime atual.
 */
(function () {
  'use strict';

  const MODULOS = [
    './assets/js/app-pwa.js'
  ];

  function carregarScript(src) {
    return new Promise(function (resolve, reject) {
      if (document.querySelector('script[data-tg-module="' + src + '"]')) {
        resolve();
        return;
      }

      const script = document.createElement('script');
      script.src = src;
      script.defer = true;
      script.dataset.tgModule = src;
      script.onload = resolve;
      script.onerror = reject;
      document.head.appendChild(script);
    });
  }

  async function iniciar() {
    for (const modulo of MODULOS) {
      await carregarScript(modulo);
    }

    if (window.TotalGestPwa && typeof window.TotalGestPwa.init === 'function') {
      window.TotalGestPwa.init();
    }
  }

  window.TotalGestApp = {
    init: iniciar,
    modules: MODULOS.slice()
  };
})();
