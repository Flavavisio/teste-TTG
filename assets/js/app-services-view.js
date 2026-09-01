/* Total Gest — apresentação da área de Ordens de Serviço */
(function () {
  'use strict';

  function specialtyAndHistoryNotice(options) {
    const opts = options || {};
    const pending = Array.isArray(opts.pendingServices) ? opts.pendingServices : [];
    const canSeePending = opts.canSeePending === true;
    const loadedSinceLabel = opts.loadedSinceLabel || '—';

    let html = '';

    if (canSeePending && pending.length) {
      const preview = pending.slice(0, 4).map(item => {
        const number = item.number || '';
        const types = Array.isArray(item.types) ? item.types.join(', ') : '';
        return `${number} (${types})`;
      }).join(' · ');

      html += `<div style="background:#fef3c7;border:1px solid #f59e0b;color:#92400e;border-radius:8px;padding:10px 14px;margin-bottom:10px;font-size:.85rem;">
        <i class="fas fa-triangle-exclamation"></i> <strong>${pending.length}</strong> OS já dada(s) como concluída(s) ainda tem(êm) relatório(s) de especialidade por preencher: ${preview}${pending.length > 4 ? ' ...' : ''}
      </div>`;
    }

    html += `<div style="margin-bottom:10px;">
      <button class="btn btn-sm" id="btn-carregar-os-antigas" style="background:#f1f5f9;color:#334155;" onclick="carregarOSMaisAntigo()"><i class="fas fa-clock-rotate-left"></i> Carregar OS mais antigas (+3 meses)</button>
      <span style="font-size:.75rem;color:#94a3b8;margin-left:8px;">A mostrar concluídas desde ${loadedSinceLabel}. Pendentes/em andamento aparecem sempre, seja qual for a idade.</span>
    </div>`;

    return html;
  }

  window.TotalGestServicesView = {
    specialtyAndHistoryNotice
  };
})();
