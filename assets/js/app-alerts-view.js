/* Total Gest — apresentação reutilizável de alertas */
(function () {
  'use strict';

  function icon(tipo) {
    if (tipo === 'danger') {
      return '<span class="alerta-ic danger"><i class="fas fa-triangle-exclamation"></i></span>';
    }
    if (tipo === 'warning') {
      return '<span class="alerta-ic warn"><i class="fas fa-exclamation-triangle"></i></span>';
    }
    return '<span class="alerta-ic info"><i class="fas fa-info"></i></span>';
  }

  function alertLines(alertas) {
    return (alertas || []).map(function (alerta) {
      return `<div class="alerta-linha ${alerta.tipo === 'danger' ? 'danger' : ''}" onclick="${alerta.acao}">
                    ${icon(alerta.tipo)}
                    <div class="alerta-txt"><div class="alerta-t">${alerta.titulo}</div><div class="alerta-s">${alerta.sub}</div></div>
                    <i class="fas fa-chevron-right alerta-chev"></i>
                </div>`;
    }).join('');
  }

  function alertsCard(options) {
    options = options || {};
    const linhasHtml = alertLines(options.alertas);

    if (options.mobile === true) {
      return `<div class="alertas-card">
                    <div class="alertas-h alertas-h--acordeao" onclick="this.closest('.alertas-card').classList.toggle('aberto')">
                        <span style="display:flex;align-items:center;gap:8px;"><i class="fas fa-bell"></i> Alertas e Pendências <span class="tgm-live-dot tgm-live-dot--vermelho"></span></span>
                        <i class="fas fa-chevron-down alertas-acordeao-seta"></i>
                    </div>
                    <div class="alertas-corpo">${linhasHtml}</div>
                </div>`;
    }

    return `<div class="alertas-card">
                    <div class="alertas-h"><i class="fas fa-bell"></i> Alertas e Pendências</div>
                    ${linhasHtml}
                </div>`;
  }

  window.TotalGestAlertsView = {
    alertsCard: alertsCard
  };
})();
