/* Total Gest — diálogos globais da aplicação
 * Extração do sistema legado de app.html.
 * Mantém as APIs globais tgAlert, tgConfirm, tgPrompt e tgEscolher.
 * O override de window.alert só é ativado por TotalGestDialogs.init().
 */
(function () {
  'use strict';

  var fila = [];
  var aMostrar = false;
  var iniciado = false;

  function elementos() {
    return {
      overlay: document.getElementById('tgAlertOverlay'),
      icone: document.getElementById('tgAlertIcone'),
      titulo: document.getElementById('tgAlertTitulo'),
      texto: document.getElementById('tgAlertTexto'),
      cancelar: document.getElementById('tgAlertBtnCancelar'),
      ok: document.getElementById('tgAlertBtnOk'),
      input: document.getElementById('tgAlertInput'),
      escolhas: document.getElementById('tgAlertEscolhas')
    };
  }

  function processarFila() {
    if (aMostrar || !fila.length) return;

    var els = elementos();
    if (!els.overlay || !els.icone || !els.titulo || !els.texto || !els.cancelar || !els.ok || !els.input || !els.escolhas) {
      var pendente = fila.shift();
      if (pendente) pendente.resolve(pendente.ehPrompt || pendente.ehEscolha ? null : false);
      setTimeout(processarFila, 0);
      return;
    }

    aMostrar = true;
    var item = fila.shift();
    var mensagem = item.mensagem;
    var opts = item.opts || {};
    var resolve = item.resolve;
    var ehConfirm = !!item.ehConfirm;
    var ehPrompt = !!item.ehPrompt;
    var ehEscolha = !!item.ehEscolha;

    els.icone.className = opts.tipo || (ehConfirm ? 'aviso' : '');
    els.icone.innerHTML = '<i class="fas ' + (opts.icone || (ehConfirm ? 'fa-circle-question' : (opts.tipo === 'erro' ? 'fa-circle-exclamation' : opts.tipo === 'aviso' ? 'fa-triangle-exclamation' : opts.tipo === 'sucesso' ? 'fa-circle-check' : 'fa-circle-info'))) + '"></i>';
    els.titulo.textContent = opts.titulo || (ehConfirm ? 'Confirmar' : 'Total Gest');
    els.texto.textContent = mensagem;
    els.input.style.display = ehPrompt ? 'block' : 'none';
    els.input.value = opts.valorInicial || '';
    els.escolhas.style.display = ehEscolha ? 'flex' : 'none';
    els.escolhas.innerHTML = '';
    els.cancelar.style.display = (ehConfirm || ehPrompt) ? 'inline-block' : 'none';
    els.cancelar.textContent = opts.textoCancelar || 'Cancelar';
    els.ok.style.display = ehEscolha ? 'none' : 'inline-block';
    els.ok.textContent = opts.textoOk || (ehConfirm ? 'Confirmar' : 'OK');
    els.overlay.classList.add('aberto');

    function fechar(resultado) {
      els.overlay.classList.remove('aberto');
      aMostrar = false;
      resolve(resultado);
      setTimeout(processarFila, 200);
    }

    if (ehEscolha) {
      (opts.opcoes || []).forEach(function (op) {
        var b = document.createElement('button');
        b.type = 'button';
        b.textContent = op.rotulo;
        b.style.cssText = 'width:100%;padding:12px 16px;border-radius:10px;border:1.5px solid #d1d9e6;background:#fafcff;color:#152a52;font-weight:600;cursor:pointer;text-align:left;transition:.15s;';
        b.onmouseenter = function () {
          b.style.borderColor = '#1a5f7a';
          b.style.background = '#eef6f8';
        };
        b.onmouseleave = function () {
          b.style.borderColor = '#d1d9e6';
          b.style.background = '#fafcff';
        };
        b.onclick = function () { fechar(op.valor); };
        els.escolhas.appendChild(b);
      });

      if (opts.permiteCancelar !== false) {
        var bc = document.createElement('button');
        bc.type = 'button';
        bc.textContent = 'Cancelar';
        bc.style.cssText = 'width:100%;padding:10px 16px;border-radius:10px;border:none;background:none;color:#94a3b8;font-weight:600;cursor:pointer;';
        bc.onclick = function () { fechar(null); };
        els.escolhas.appendChild(bc);
      }
    } else {
      els.ok.onclick = function () { fechar(ehPrompt ? els.input.value : true); };
      els.cancelar.onclick = function () { fechar(ehPrompt ? null : false); };
    }

    if (ehPrompt) setTimeout(function () { els.input.focus(); }, 150);
  }

  function tgAlert(mensagem, opts) {
    opts = opts || {};
    return new Promise(function (resolve) {
      fila.push({ mensagem: mensagem, opts: opts, resolve: resolve, ehConfirm: false });
      processarFila();
    });
  }

  function tgConfirm(mensagem, opts) {
    opts = opts || {};
    return new Promise(function (resolve) {
      fila.push({ mensagem: mensagem, opts: opts, resolve: resolve, ehConfirm: true });
      processarFila();
    });
  }

  function tgPrompt(mensagem, opts) {
    opts = opts || {};
    return new Promise(function (resolve) {
      fila.push({ mensagem: mensagem, opts: opts, resolve: resolve, ehPrompt: true });
      processarFila();
    });
  }

  function tgEscolher(mensagem, opcoes, opts) {
    opts = opts || {};
    opts.opcoes = opcoes;
    return new Promise(function (resolve) {
      fila.push({ mensagem: mensagem, opts: opts, resolve: resolve, ehEscolha: true });
      processarFila();
    });
  }

  function init() {
    if (iniciado) return;
    iniciado = true;
    window.alert = function (mensagem) { tgAlert(mensagem); };
  }

  window.tgAlert = tgAlert;
  window.tgConfirm = tgConfirm;
  window.tgPrompt = tgPrompt;
  window.tgEscolher = tgEscolher;
  window.TotalGestDialogs = {
    init: init,
    alert: tgAlert,
    confirm: tgConfirm,
    prompt: tgPrompt,
    escolher: tgEscolher
  };
})();
