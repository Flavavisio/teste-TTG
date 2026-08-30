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

      // Os links especiais de renovação continuam a ser tratados antes da exigência
      // de sessão, exatamente como no arranque legado.
      if (_verificarLinkRenovacao()) {
        if (relogioInterval) clearInterval(relogioInterval);
        relogioInterval = setInterval(atualizarRelogio, 1000);
        return;
      }

      // app.html passou a ser uma área privada. O login público vive em login.html;
      // se não existir uma sessão persistida, não deixamos a app num estado vazio nem
      // voltamos a mostrar a landing/login legados que ainda estão a ser removidos.
      const { data: estadoSessao } = await supa.auth.getSession();
      if (!estadoSessao || !estadoSessao.session || !estadoSessao.session.user) {
        window.location.replace('./login.html');
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
