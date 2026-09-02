/* Total Gest — mensagens visuais de sincronização
 * Extraído de app.html sem alterar o comportamento ou os textos apresentados.
 */
(function () {
  'use strict';

  function traduzirErroSync(detalheOriginal) {
    const msg = (detalheOriginal || '').toLowerCase();
    if (msg.includes('duplicate key') || msg.includes('unique constraint') || msg.includes('já existe')) {
      return 'Este registo entrou em conflito com outro (talvez criado quase ao mesmo tempo, noutro aparelho). A app vai tentar corrigir sozinha.';
    }
    if (msg.includes('null value') || msg.includes('violates not-null') || msg.includes('not-null constraint')) {
      return 'Falta preencher um campo obrigatório neste registo antes de conseguir gravar.';
    }
    if (msg.includes('foreign key') || msg.includes('is not present in table') || msg.includes('violates foreign key')) {
      return 'Este registo está ligado a outro que entretanto foi eliminado (ex.: um cliente ou artigo apagado). Verifica essa ligação.';
    }
    if (msg.includes('permission denied') || msg.includes('row-level security') || msg.includes('rls') || msg.includes('new row violates row-level')) {
      return 'Não tens permissão para gravar esta alteração. Fala com o administrador da conta.';
    }
    if (msg.includes('failed to fetch') || msg.includes('network') || msg.includes('timeout') || msg.includes('load failed')) {
      return 'Não foi possível ligar ao servidor agora. Verifica a ligação à internet — a app vai continuar a tentar sozinha.';
    }
    if (msg.includes('does not exist') || msg.includes('schema cache') || msg.includes('could not find')) {
      return 'Esta funcionalidade ainda está a ser preparada do lado do servidor. A Total Gest já foi avisada — tenta novamente daqui a pouco.';
    }
    if (msg.includes('value too long') || msg.includes('out of range')) {
      return 'Um dos valores introduzidos é maior do que o permitido. Revê os campos preenchidos.';
    }
    return 'Não foi possível guardar esta alteração agora.';
  }

  function mostrarStatusSync(erros, detalhe) {
    let el = document.getElementById('syncToast');
    if (!erros) { if (el) el.style.display = 'none'; return; }
    if (!el) {
      el = document.createElement('div');
      el.id = 'syncToast';
      el.style.cssText = 'position:fixed; bottom:20px; right:20px; z-index:99999; background:#fee2e2; color:#991b1b; border:1px solid #fca5a5; padding:12px 16px; border-radius:10px; box-shadow:0 6px 20px rgba(0,0,0,.15); max-width:360px; font-size:14px;';
      document.body.appendChild(el);
    }
    const detOriginal = (detalhe || '').toString().replace(/[<>]/g, '').slice(0, 300);
    const mensagemAmigavel = traduzirErroSync(detOriginal);
    el.style.display = 'block';
    el.innerHTML = '<div style="display:flex; align-items:flex-start; gap:10px;"><i class="fas fa-exclamation-triangle" style="margin-top:2px;"></i><div style="flex:1;">'
      + mensagemAmigavel
      + (detOriginal ? '<div style="margin-top:6px;"><span onclick="this.nextElementSibling.style.display=this.nextElementSibling.style.display===\'none\'?\'block\':\'none\';" style="cursor:pointer;font-size:11px;text-decoration:underline;opacity:.75;">Detalhes técnicos</span><div style="display:none;font-size:11px; margin-top:4px; opacity:.7; word-break:break-word;">' + detOriginal + '</div></div>' : '')
      + '</div><button onclick="guardarDados()" style="background:#dc2626;color:#fff;border:none;border-radius:6px;padding:6px 10px;cursor:pointer;white-space:nowrap;">Tentar de novo</button></div>';
  }

  window._traduzirErroSync = traduzirErroSync;
  window.mostrarStatusSync = mostrarStatusSync;
  window.TotalGestSyncStatus = {
    translateError: traduzirErroSync,
    show: mostrarStatusSync
  };
})();
