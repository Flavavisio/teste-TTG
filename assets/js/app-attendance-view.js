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

  function attendancePhotoHtml(url) {
    return url ? `<img src="${url}" alt="foto" class="foto-miniatura" onclick="window.open('${url}','_blank')" />` : '';
  }

  function attendanceGpsHtml(lat, lng) {
    return (lat && lng)
      ? `<a href="https://www.google.com/maps?q=${lat},${lng}" target="_blank" title="Ver no mapa"><i class="fas fa-map-pin gps-icon"></i></a>`
      : '<span style="color:#cbd5e1;">—</span>';
  }

  function attendanceDateCell(value, mode) {
    if (mode !== 'semana') return '';
    const label = value
      ? new Date(value + 'T00:00:00').toLocaleDateString('pt-PT', { weekday: 'short', day: '2-digit', month: '2-digit' })
      : '—';
    return `<span style="min-width:78px;font-weight:600;color:#1a5f7a;text-transform:capitalize;">${label}</span>`;
  }

  function attendanceRecordRow(options) {
    const o = options || {};
    return `<div class="ponto-acc-sub-row">
                        ${o.dateHtml || ''}
                        <span style="min-width:60px;font-weight:600;">${o.entryHtml || ''}</span>
                        <span style="min-width:60px;font-weight:600;">${o.exitHtml || ''}</span>
                        <span style="min-width:60px;">${o.hoursHtml || ''}</span>
                        <span style="flex:1;min-width:160px;color:#334155;">${o.clientName !== '-' ? o.clientName + ' — ' : ''}${o.workHtml || ''}${o.photoHtml || ''}</span>
                        <span style="min-width:26px;text-align:center;">${o.gpsEntryHtml || ''}</span>
                        <span style="min-width:26px;text-align:center;">${o.gpsExitHtml || ''}</span>
                        <span style="min-width:26px;text-align:center;"><button type="button" class="btn btn-sm btn-outline" style="padding:2px 6px;" title="Editar picagem" onclick="event.stopPropagation();_abrirEdicaoPontoRegisto('${o.recordId || ''}')"><i class="fas fa-pen"></i></button></span>
                    </div>`;
  }

  function attendanceAccordionItem(options) {
    const o = options || {};
    const header = `<div class="ponto-acc-sub-row" style="font-size:.68rem;font-weight:700;text-transform:uppercase;letter-spacing:.03em;color:#94a3b8;border-bottom:1px solid #e6eaf2;">
                        ${o.mode === 'semana' ? '<span style="min-width:78px;">Dia</span>' : ''}
                        <span style="min-width:60px;">Entrada</span>
                        <span style="min-width:60px;">Saída</span>
                        <span style="min-width:60px;">Total</span>
                        <span style="flex:1;min-width:160px;">Local</span>
                        <span style="min-width:26px;text-align:center;" title="GPS na entrada">GPS ent.</span>
                        <span style="min-width:26px;text-align:center;" title="GPS na saída">GPS saí.</span>
                        <span style="min-width:26px;text-align:center;"></span>
                    </div>`;
    const body = o.hasRecords ? header + (o.rowsHtml || '') : '<span style="color:#94a3b8;">Sem picagens hoje.</span>';
    return `<div class="ponto-acc-item" id="ponto-acc-${o.personId || ''}">
                    <div class="ponto-acc-head" onclick="document.getElementById('ponto-acc-${o.personId || ''}').classList.toggle('aberto')">
                        <span class="nome">${o.nameHtml || ''}</span>
                        <span>${o.summaryHtml || ''}</span>
                        <i class="fas fa-chevron-right chevron"></i>
                    </div>
                    <div class="ponto-acc-body">${body}</div>
                </div>`;
  }

  function attendanceAlertsHtml(options) {
    const o = options || {};
    return (o.lessThanEightHours ? ` <i class="fas fa-triangle-exclamation" title="Ainda não completou as 8 horas diárias" style="color:#dc2626;"></i>` : '')
      + (o.late ? ` <i class="fas fa-clock" title="${o.hasGeneralRecord ? 'Entrada depois das ' + o.lateLimit : 'Ainda não picou (esperado ' + o.expectedTime + ' + ' + o.toleranceMinutes + 'min de tolerância)'}" style="color:#d97706;"></i>` : '')
      + (o.lunchDeducted ? ` <i class="fas fa-utensils" title="Não picou saída/regresso do almoço — foi descontada 1h automaticamente" style="color:#d97706;"></i>` : '');
  }

  function attendancePersonSummaryHtml(options) {
    const o = options || {};
    if (o.absence) {
      return `<span style="color:${o.absence.cor};font-weight:600;"><i class="fas ${o.absence.icon}"></i> ${o.personName} está de ${o.absence.label}</span>`;
    }
    if (o.generalRecord) {
      const records = Array.isArray(o.generalRecords) ? o.generalRecords : [];
      const last = records[records.length - 1];
      const parts = [o.generalRecord.entrada || '--:--'];
      records.forEach(function (record) {
        if (record.pausaAlmoco && record.saida) {
          parts.push(`<i class="fas fa-utensils" title="Pausa almoço" style="color:#d97706;"></i> ${record.saida}`);
          const resume = records.find(function (item) { return !item.pausaAlmoco && item.entrada && item.entrada > record.saida; });
          parts.push(resume ? resume.entrada : '<span style="color:#d97706;">ainda em pausa</span>');
        }
      });
      parts.push(o.generalOpen ? '<span style="color:#16a34a;font-weight:700;">em serviço</span>' : ((last && last.saida) || '--:--'));
      return `${parts.join(' → ')} <span style="color:#64748b;">(${o.generalHoursText || '0h 0m'})</span>${o.alertsHtml || ''}`;
    }
    const emptyLabel = Number(o.recordsCount || 0) === 0 ? (o.isToday ? 'ainda não picou hoje' : 'sem picagens neste dia') : 'sem picagem geral';
    return `<span style="color:#94a3b8;">${emptyLabel}</span>${o.alertsHtml || ''}`;
  }

  function attendanceEditTitle(record, escapeHtml) {
    const r = record || {};
    if (!(r.editadoPor && r.editadoEm)) return '';
    const escape = typeof escapeHtml === 'function' ? escapeHtml : function (value) { return String(value == null ? '' : value); };
    return `Alterado por ${escape(r.editadoPor)} em ${new Date(r.editadoEm).toLocaleString('pt-PT')} — Motivo: ${escape(r.motivoEdicao || '—')}`;
  }

  function attendanceEntryExitHtml(record, editTitle) {
    const r = record || {};
    const edited = !!(r.editadoPor && r.editadoEm);
    const entryHtml = edited ? `<span style="color:#0ea5e9;" title="${editTitle || ''}">${r.entrada || '--:--'} <i class="fas fa-pen" style="font-size:.65em;"></i></span>` : (r.entrada || '--:--');
    const exitBase = r.pausaAlmoco
      ? `<span style="color:#d97706;"><i class="fas fa-utensils" title="Pausa almoço"></i> ${r.saida || '--:--'}</span>`
      : (r.saidaAutomatica ? `${r.saida} <i class="fas fa-triangle-exclamation" title="Saída automática após 12h" style="color:#d97706;"></i>` : (r.saida || '--:--'));
    const exitHtml = (edited && !r.pausaAlmoco) ? `<span style="color:#0ea5e9;" title="${editTitle || ''}">${exitBase} <i class="fas fa-pen" style="font-size:.65em;"></i></span>` : exitBase;
    return { entryHtml, exitHtml };
  }

  function preparePersonAttendanceRecords(records) {
    const personRecords = Array.isArray(records) ? records : [];
    personRecords.sort(function (a, b) {
      return (a.data || '').localeCompare(b.data || '') || (a.entrada || '').localeCompare(b.entrada || '');
    });
    const generalRecords = personRecords
      .filter(function (record) { return !record.servicoId && !record.obraId; })
      .sort(function (a, b) { return (a.entrada || '').localeCompare(b.entrada || ''); });
    return { personRecords, generalRecords };
  }

  function calculateGeneralAttendanceState(generalRecords, nowTime, calculateHours) {
    const records = Array.isArray(generalRecords) ? generalRecords : [];
    const calc = typeof calculateHours === 'function' ? calculateHours : function () { return 0; };
    let generalHours = 0;
    let generalOpen = false;
    records.forEach(function (record) {
      if (record.entrada && record.saida) generalHours += calc(record.entrada, record.saida);
      else if (record.entrada && !record.saida) {
        generalHours += calc(record.entrada, nowTime);
        generalOpen = true;
      }
    });
    return {
      generalRecord: records[0] || null,
      generalHours,
      generalOpen
    };
  }

  function applyAttendanceLunchDeduction(personRecords, options) {
    const records = Array.isArray(personRecords) ? personRecords : [];
    const o = options || {};
    const hasLunchBreak = records.some(function (record) { return record.pausaAlmoco && record.saida; });
    let generalHours = Number(o.generalHours || 0);
    let lunchDeducted = false;
    if (!hasLunchBreak && !o.generalOpen && generalHours > 6) {
      generalHours = Math.max(0, generalHours - 1);
      lunchDeducted = true;
    }
    return { generalHours, lunchDeducted };
  }

  function isAttendanceBelowEightHours(generalRecord, generalOpen, generalHours) {
    return !!(generalRecord && !generalOpen && generalHours > 0 && generalHours < 8);
  }

  function isAttendanceLate(options) {
    const o = options || {};
    if (o.absence) return false;
    if (o.generalRecord) return !!(o.generalRecord.entrada && o.generalRecord.entrada > o.lateLimit);
    return !!(o.selectedDateIsToday && Number(o.recordsCount || 0) === 0 && o.nowTime > o.lateLimit);
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
    attendanceLateLimit,
    attendancePhotoHtml,
    attendanceGpsHtml,
    attendanceDateCell,
    attendanceRecordRow,
    attendanceAccordionItem,
    attendanceAlertsHtml,
    attendancePersonSummaryHtml,
    attendanceEditTitle,
    attendanceEntryExitHtml,
    preparePersonAttendanceRecords,
    calculateGeneralAttendanceState,
    applyAttendanceLunchDeduction,
    isAttendanceBelowEightHours,
    isAttendanceLate
  };
})();
