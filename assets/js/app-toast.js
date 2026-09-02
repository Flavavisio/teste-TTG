/* Total Gest — notificações toast
 * Mantém mostrarToast() global para compatibilidade com o código legado da aplicação.
 * Não substitui window.alert: os diálogos modulares são a camada final de alertas.
 */
(function () {
  'use strict';

  const alertNativo = window.alert.bind(window);
  const icones = {
    sucesso: 'fa-circle-check',
    erro: 'fa-circle-exclamation',
    aviso: 'fa-triangle-exclamation',
    info: 'fa-circle-info'
  };

  function classificar(msg) {
    const m = String(msg || '');
    if (/✅|sucesso|criad[oa] com sucesso|atualizad[oa] com sucesso|guardad[oa] com sucesso|aprovad[oa]|gravad[oa]/i.test(m)) return 'sucesso';
    if (/❌|erro|falhou|falha|não foi possível|nao foi possivel|inválid|invalido/i.test(m)) return 'erro';
    if (/⚠️|atenção|atencao|aviso|cuidado/i.test(m)) return 'aviso';
    return 'info';
  }

  function mostrarToast(mensagem, tipoForcado) {
    const cont = document.getElementById('tgToastContainer');
    if (!cont) {
      alertNativo(mensagem);
      return;
    }

    const tipo = tipoForcado || classificar(mensagem);
    const el = document.createElement('div');
    el.className = 'tg-toast tg-' + tipo;
    el.innerHTML = '<i class="fas ' + icones[tipo] + ' tg-toast-ic"></i>' +
      '<div class="tg-toast-msg"></div>' +
      '<button type="button" class="tg-toast-fechar" aria-label="Fechar"><i class="fas fa-xmark"></i></button>';
    el.querySelector('.tg-toast-msg').textContent = mensagem;

    const remover = function () {
      el.classList.add('tg-toast-saindo');
      setTimeout(function () { el.remove(); }, 220);
    };

    el.querySelector('.tg-toast-fechar').onclick = remover;
    cont.appendChild(el);
    setTimeout(remover, tipo === 'erro' ? 7000 : 4500);
  }

  window.mostrarToast = mostrarToast;
  window.TotalGestToast = {
    show: mostrarToast,
    classify: classificar
  };
})();
