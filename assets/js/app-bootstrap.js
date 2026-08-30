/* Total Gest — arranque da aplicação
 * Extraído de app.html para permitir a migração incremental.
 * Não arranca automaticamente: o shell chama init() apenas quando o bootstrap inline legado for removido.
 */
(function () {
  'use strict';

  let iniciado = false;
  let promessa = null;

  async function iniciarAplicacao() {
    if (iniciado) return promessa;
    iniciado = true;

    promessa = (async function () {
      _aplicarTemaGuardado();
      _aplicarSidebarEncolhidaGuardada();
      _aplicarZoomGuardado();

      await bootstrapSupabase();
      inicializar();

      if (_verificarLinkRenovacao()) {
        if (relogioInterval) clearInterval(relogioInterval);
        relogioInterval = setInterval(atualizarRelogio, 1000);
        return;
      }

      await restaurarSessaoAuth();
      _tratarRegressoOAuthTOConline();

      if (relogioInterval) clearInterval(relogioInterval);
      relogioInterval = setInterval(atualizarRelogio, 1000);
    })();

    try {
      return await promessa;
    } catch (erro) {
      iniciado = false;
      promessa = null;
      throw erro;
    }
  }

  window.TotalGestBootstrap = {
    init: iniciarAplicacao,
    isStarted: function () { return iniciado; }
  };
})();
