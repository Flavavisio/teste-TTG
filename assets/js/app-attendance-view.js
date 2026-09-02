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

  function moveNavigationDate(options) {
    const o = options || {};
    const value = o.value || o.today;
    if (!value) return null;
    const parts = String(value).split('-').map(Number);
    const dt = new Date(Date.UTC(parts[0], parts[1] - 1, parts[2]));
    dt.setUTCDate(dt.getUTCDate() + Number(o.direction || 0) * (o.mode === 'semana' ? 7 : 1));
    const next = dt.getUTCFullYear() + '-' + String(dt.getUTCMonth() + 1).padStart(2, '0') + '-' + String(dt.getUTCDate()).padStart(2, '0');
    if (Number(o.direction || 0) > 0 && o.today && next > o.today) return null;
    return next;
  }

  function canNavigateAttendance(role) {
    return ['admin', 'subadmin', 'funcionario', 'encarregado', 'vendedor'].includes(role);
  }

  function attendanceNavigationLabel(value, mode) {
    const parts = String(value || '').split('-').map(Number);
    const dt = new Date(Date.UTC(parts[0], parts[1] - 1, parts[2]));
    if (mode === 'semana') {
      const start = new Date(dt);
      start.setUTCDate(dt.getUTCDate() - (dt.getUTCDay() === 0 ? 6 : dt.getUTCDay() - 1));
      const end = new Date(start);
      end.setUTCDate(start.getUTCDate() + 6);
      return `${start.getUTCDate()}/${start.getUTCMonth() + 1} a ${end.getUTCDate()}/${end.getUTCMonth() + 1}`;
    }
    return dt.toLocaleDateString('pt-PT', { weekday: 'long', day: '2-digit', month: '2-digit', year: 'numeric', timeZone: 'UTC' });
  }

  function isAttendanceNextDisabled(value, today) {
    return String(value || '') >= String(today || '');
  }

  function buildLongWorkAttendanceRecords(longRecords, works) {
    const workList = Array.isArray(works) ? works : [];
    return (Array.isArray(longRecords) ? longRecords : []).map(function (record) {
      const work = workList.find(function (item) { return item && item.id === record.obraId; });
      return Object.assign({}, record, {
        obraDescricao: work && work.nome ? work.nome : 'Obra',
        clienteId: work && work.clienteId ? work.clienteId : null,
        _ehObraLonga: true
      });
    });
  }

  function selectRecentAttendanceRecords(records, options) {
    const list = Array.isArray(records) ? records : [];
    const o = options || {};
    const asDate = function (record) { return record && record.data ? new Date(record.data + 'T00:00:00') : null; };
    return {
      weekRecords: list.filter(function (record) { const date = asDate(record); return date && date >= o.weekStart; }),
      recentRecords: list.filter(function (record) { const date = asDate(record); return date && date >= o.recentStart; })
    };
  }

  function selectAttendanceNavigationRecords(records, selectedDate, mode) {
    const list = Array.isArray(records) ? records : [];
    if (mode !== 'semana') return list.filter(function (record) { return record && record.data === selectedDate; });
    const selected = new Date(String(selectedDate || '') + 'T00:00:00');
    const start = new Date(selected);
    start.setDate(selected.getDate() - selected.getDay() + (selected.getDay() === 0 ? -6 : 1));
    const end = new Date(start);
    end.setDate(start.getDate() + 6);
    return list.filter(function (record) {
      const date = record && record.data ? new Date(record.data + 'T00:00:00') : null;
      return date && date >= start && date <= end;
    });
  }

  function groupAttendanceByPerson(records) {
    const grouped = {};
    (Array.isArray(records) ? records : []).forEach(function (record) {
      const id = record && record.funcionarioId;
      (grouped[id] = grouped[id] || []).push(record);
    });
    return grouped;
  }

  function attendanceLateLimit(expectedTime, toleranceMinutes) {
    const parts = String(expectedTime || '09:00').split(':').map(Number);
    const total = parts[0] * 60 + parts[1] + Number(toleranceMinutes || 0);
    return String(Math.floor(total / 60)).padStart(2, '0') + ':' + String(total % 60).padStart(2, '0');
  }

  window.TotalGestAttendanceView = {
    startOfWeekMonday,
    formatHours,
    teamSummaryRow,
    teamSummaryCard,
    moveNavigationDate,
    canNavigateAttendance,
    attendanceNavigationLabel,
    isAttendanceNextDisabled,
    buildLongWorkAttendanceRecords,
    selectRecentAttendanceRecords,
    selectAttendanceNavigationRecords,
    groupAttendanceByPerson,
    attendanceLateLimit
  };
})();
