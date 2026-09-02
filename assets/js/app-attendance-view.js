/* Total Gest — apresentação do resumo de registo de ponto */
(function () {
  'use strict';

  function startOfWeekMonday(value) {
    const x = value instanceof Date ? new Date(value.getTime()) : new Date();
    const dow = (x.getDay() + 6) % 7;
    x.setHours(0, 0, 0, 0);
    x.setDate(x.getDate() - dow);
    return x;
  }

  function formatHours(h) {
    if (!h || h <= 0) return '0h 0m';
    const hi = Math.floor(h);
    const mi = Math.round((h - hi) * 60);
    return `${hi}h ${mi}m`;
  }

  function teamSummaryRow(options) {
    const o = options || {};
    return `<tr>
                    <td>${o.name} <span style="color:#94a3b8;font-size:.8em;">(${o.type})</span></td>
                    <td>${o.appBadge}</td>
                    <td>${o.serviceBadge}</td>
                    <td>${o.workplace}</td>
                    <td>${formatHours(o.hoursToday)}</td>
                    <td>${formatHours(o.hoursWeek)} <span style="color:#94a3b8;font-size:.8em;">/ ${o.contractedHours}h</span></td>
                    <td style="font-weight:700;color:${o.balance >= 0 ? '#16a34a' : '#dc2626'};">${o.balanceText}</td>
                </tr>`;
  }

  function teamSummaryCard(options) {
    const o = options || {};
    const peopleCount = Number(o.peopleCount || 0);
    const inServiceCount = Number(o.inServiceCount || 0);
    return `
                <div class="report-card">
                    <h4><i class="fas fa-users"></i> Estado da equipa — ${inServiceCount} em serviço · ${peopleCount - inServiceCount} fora</h4>
                    ${peopleCount ? `<div class="table-wrapper"><table>
                        <thead><tr><th>Pessoa</th><th>Na app</th><th>Estado</th><th>Obra atual</th><th>Horas hoje</th><th>Esta semana</th><th>Saldo (semana)</th></tr></thead>
                        <tbody>${o.rowsHtml || ''}</tbody></table></div>
                        <p style="color:#94a3b8;font-size:.82rem;margin-top:8px;">Saldo = horas trabalhadas esta semana menos as horas semanais contratadas.</p>`
                      : '<p style="color:#64748b;">Sem funcionários ou encarregados.</p>'}
                </div>`;
  }

  window.TotalGestAttendanceView = {
    startOfWeekMonday,
    formatHours,
    teamSummaryRow,
    teamSummaryCard
  };
})();
