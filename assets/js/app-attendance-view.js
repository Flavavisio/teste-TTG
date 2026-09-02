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

  function attendanceRecordHours(record, calculateHours, formatHoursFn) {
    const r = record || {};
    if (!r.saida) return '';
    const calc = typeof calculateHours === 'function' ? calculateHours : function () { return 0; };
    const format = typeof formatHoursFn === 'function' ? formatHoursFn : formatHours;
    return format(calc(r.entrada, r.saida));
  }

  function attendanceRecordWorkplace(record, options) {
    const r = record || {}, o = options || {};
    const getWorkDescription = typeof o.getWorkDescription === 'function' ? o.getWorkDescription : function () { return ''; };
    const getClientName = typeof o.getClientName === 'function' ? o.getClientName : function () { return '-'; };
    const escape = typeof o.escapeHtml === 'function' ? o.escapeHtml : function (value) { return String(value == null ? '' : value); };
    const work = escape(r.servicoId ? getWorkDescription(r.servicoId) : (r.obraDescricao || (r.obraId ? 'Obra' : 'Escritório/Exterior')));
    const clientName = r.clienteId ? (getClientName(r.clienteId) || '-') : '-';
    return { workHtml: work, clientName };
  }

  function attendanceRecordMedia(record, mode) {
    const r = record || {};
    return {
      photoHtml: attendancePhotoHtml(r.foto),
      gpsEntryHtml: attendanceGpsHtml(r.lat, r.lng),
      gpsExitHtml: attendanceGpsHtml(r.latSaida, r.lngSaida),
      dateHtml: attendanceDateCell(r.data, mode)
    };
  }

  function prepareAttendanceRecordRow(record, options) {
    const r = record || {}, o = options || {};
    const editTitle = attendanceEditTitle(r, o.escapeHtml);
    const times = attendanceEntryExitHtml(r, editTitle);
    const workplace = attendanceRecordWorkplace(r, o);
    const media = attendanceRecordMedia(r, o.mode);
    return {
      dateHtml: media.dateHtml,
      entryHtml: times.entryHtml,
      exitHtml: times.exitHtml,
      hoursHtml: attendanceRecordHours(r, o.calculateHours, o.formatHours),
      clientName: workplace.clientName,
      workHtml: workplace.workHtml,
      photoHtml: media.photoHtml,
      gpsEntryHtml: media.gpsEntryHtml,
      gpsExitHtml: media.gpsExitHtml,
      recordId: r.id
    };
  }

  function shouldIncludeMissingAttendancePeople(options) {
    const o = options || {};
    return o.selectedDate === o.today
      && (o.role === 'admin' || o.role === 'subadmin')
      && o.nowTime > o.lateLimit;
  }

  function eligibleAttendancePersonIds(employees, managers, tenantId) {
    const employeeIds = (Array.isArray(employees) ? employees : [])
      .filter(function (person) {
        return person.adminId === tenantId
          && person.role !== 'admin'
          && person.role !== 'superadmin'
          && !person.suspenso;
      })
      .map(function (person) { return person.id; });
    const managerIds = (Array.isArray(managers) ? managers : [])
      .filter(function (person) { return person.adminId === tenantId && !person.suspenso; })
      .map(function (person) { return person.id; });
    return employeeIds.concat(managerIds);
  }

  function missingAttendancePersonIds(groupedRecords, candidateIds) {
    const grouped = groupedRecords || {};
    return (Array.isArray(candidateIds) ? candidateIds : []).filter(function (id) { return !grouped[id]; });
  }

  function addMissingAttendancePeople(groupedRecords, missingIds) {
    const grouped = groupedRecords || {};
    (Array.isArray(missingIds) ? missingIds : []).forEach(function (id) { grouped[id] = []; });
    return grouped;
  }

  function prepareAttendancePersonState(records, options) {
    const o = options || {};
    const prepared = preparePersonAttendanceRecords(records);
    const personRecords = prepared.personRecords;
    const generalRecords = prepared.generalRecords;
    const general = calculateGeneralAttendanceState(generalRecords, o.nowTime, o.calculateHours);
    const lunch = applyAttendanceLunchDeduction(personRecords, {
      generalOpen: general.generalOpen,
      generalHours: general.generalHours
    });
    const generalHours = lunch.generalHours;
    return {
      personRecords,
      generalRecords,
      generalRecord: general.generalRecord,
      generalOpen: general.generalOpen,
      generalHours,
      lunchDeducted: lunch.lunchDeducted,
      lessThanEightHours: isAttendanceBelowEightHours(general.generalRecord, general.generalOpen, generalHours),
      late: isAttendanceLate({
        absence: o.absence,
        generalRecord: general.generalRecord,
        selectedDateIsToday: o.selectedDateIsToday,
        recordsCount: personRecords.length,
        nowTime: o.nowTime,
        lateLimit: o.lateLimit
      })
    };
  }

  function attendancePersonPresentation(state, options) {
    const s = state || {}, o = options || {};
    const alertsHtml = attendanceAlertsHtml({
      lessThanEightHours: s.lessThanEightHours,
      late: s.late,
      hasGeneralRecord: !!s.generalRecord,
      lateLimit: o.lateLimit,
      expectedTime: o.expectedTime,
      toleranceMinutes: o.toleranceMinutes,
      lunchDeducted: s.lunchDeducted
    });
    return attendancePersonSummaryHtml({
      absence: o.absence,
      personName: o.personName,
      generalRecord: s.generalRecord,
      generalRecords: s.generalRecords,
      generalOpen: s.generalOpen,
      generalHoursText: (typeof o.formatHours === 'function' ? o.formatHours : formatHours)(s.generalHours),
      alertsHtml,
      recordsCount: s.personRecords.length,
      isToday: o.selectedDateIsToday
    });
  }

  function attendancePersonRows(records, options) {
    const o = options || {};
    return (Array.isArray(records) ? records : []).map(function (record) {
      return attendanceRecordRow(prepareAttendanceRecordRow(record, o));
    }).join('');
  }

  function prepareAttendanceAccordionPerson(records, options) {
    const o = options || {};
    const state = prepareAttendancePersonState(records, o);
    return {
      summaryHtml: attendancePersonPresentation(state, o),
      rowsHtml: attendancePersonRows(state.personRecords, o),
      hasRecords: state.personRecords.length > 0,
      state
    };
  }

  function filterAttendanceRecordsForViewer(records, user, tenantId) {
    const list = Array.isArray(records) ? records : [];
    if (user && user.role === 'admin') {
      return list.filter(function (record) { return record.adminId === tenantId; });
    }
    if (user && ['encarregado', 'funcionario', 'vendedor', 'vigilante', 'supervisor_vigilantes'].includes(user.role)) {
      return list.filter(function (record) { return record.funcionarioId === user.id; });
    }
    return [];
  }

  function attendanceRecentStart(value) {
    const date = value instanceof Date ? value : new Date(value);
    return new Date(date.getFullYear(), date.getMonth() - 1, 1);
  }

  function calculateWeeklyAttendanceTotal(records, options) {
    const o = options || {};
    const calculate = typeof o.calculateHours === 'function' ? o.calculateHours : function () { return 0; };
    return (Array.isArray(records) ? records : []).reduce(function (total, record) {
      if (!(record && (record._ehObraLonga || (!record.servicoId && !record.obraId)))) return total;
      if (record.entrada && record.saida) return total + calculate(record.entrada, record.saida);
      if (record.data === o.today && record.entrada && !record.saida) return total + calculate(record.entrada, o.nowTime);
      return total;
    }, 0);
  }

  function attendanceWeeklyTarget(user, employees, managers) {
    if (!user) return null;
    if (user.role === 'funcionario' || user.role === 'vendedor') {
      const person = (Array.isArray(employees) ? employees : []).find(function (item) { return item.id === user.id; });
      return (person && person.horasSemanais) || 40;
    }
    if (user.role === 'encarregado') {
      const person = (Array.isArray(managers) ? managers : []).find(function (item) { return item.id === user.id; });
      return (person && person.horasSemanais) || 40;
    }
    return null;
  }

  function attendanceWeeklyBalanceLabel(totalHours, weeklyTarget) {
    const total = Number(totalHours || 0);
    const hours = Math.floor(total);
    const minutes = Math.round((total - hours) * 60);
    return weeklyTarget != null
      ? `Horas esta semana: ${hours}h ${minutes}m / ${weeklyTarget}h`
      : `Horas esta semana: ${hours}h ${minutes}m`;
  }

  function attendanceViewElements(doc) {
    const d = doc || document;
    return {
      empty: d.getElementById('emptyPonto'),
      accordion: d.getElementById('pontoAcordeao'),
      weeklyBalance: d.getElementById('saldoHoras')
    };
  }

  function applyAttendanceEmptyState(elements, isEmpty) {
    const e = elements || {};
    if (isEmpty) {
      if (e.accordion) e.accordion.innerHTML = '';
      if (e.empty) e.empty.style.display = 'block';
      if (e.weeklyBalance) e.weeklyBalance.textContent = 'Horas esta semana: 0h 0m';
      return true;
    }
    if (e.empty) e.empty.style.display = 'none';
    return false;
  }

  function prepareAttendanceNavigation(records, options) {
    const o = options || {};
    const selectedDate = o.selectedDate || o.today;
    const selectedRecords = selectAttendanceNavigationRecords(records, selectedDate, o.mode);
    return {
      selectedDate,
      selectedRecords,
      groupedRecords: groupAttendanceByPerson(selectedRecords)
    };
  }

  function attendanceTimingConfig(adminConfig) {
    const cfg = adminConfig || {};
    const expectedTime = cfg.horaEntradaHabitual || '09:00';
    const toleranceMinutes = cfg.toleranciaAtrasoMin != null ? cfg.toleranciaAtrasoMin : 15;
    return {
      expectedTime,
      toleranceMinutes,
      lateLimit: attendanceLateLimit(expectedTime, toleranceMinutes)
    };
  }

  function applyAttendanceAccordionState(elements, html, peopleCount) {
    const e = elements || {};
    if (!Number(peopleCount || 0)) {
      if (e.accordion) e.accordion.innerHTML = '';
      if (e.empty) e.empty.style.display = 'block';
      return false;
    }
    if (e.accordion) e.accordion.innerHTML = html || '';
    if (e.empty) e.empty.style.display = 'none';
    return true;
  }

  function mergeAttendanceRecords(pointRecords, longWorkRecords, works) {
    return [
      ...(Array.isArray(pointRecords) ? pointRecords : []),
      ...buildLongWorkAttendanceRecords(longWorkRecords, works)
    ];
  }

  function prepareAttendanceVisibleRecords(options) {
    const o = options || {};
    return filterAttendanceRecordsForViewer(
      mergeAttendanceRecords(o.pointRecords, o.longWorkRecords, o.works),
      o.user,
      o.tenantId
    );
  }

  function prepareAttendancePeriods(records, options) {
    const o = options || {};
    return selectRecentAttendanceRecords(records, {
      weekStart: o.weekStart,
      recentStart: o.recentStart || attendanceRecentStart(o.currentDate || new Date())
    });
  }

  function prepareAttendanceBaseState(options) {
    const o = options || {};
    const visibleRecords = prepareAttendanceVisibleRecords(o);
    const periods = prepareAttendancePeriods(visibleRecords, o);
    return {
      visibleRecords,
      weekRecords: periods.weekRecords,
      recentRecords: periods.recentRecords
    };
  }

  function prepareAttendanceViewState(options) {
    const o = options || {};
    const nowTime = o.nowTime || new Date().toTimeString().slice(0, 5);
    const totalHours = calculateWeeklyAttendanceTotal(o.weekRecords, {
      today: o.today,
      nowTime,
      calculateHours: o.calculateHours
    });
    const weeklyTarget = attendanceWeeklyTarget(o.user, o.employees, o.managers);
    const navigation = prepareAttendanceNavigation(o.recentRecords, {
      selectedDate: o.selectedDate,
      today: o.today,
      mode: o.mode
    });
    const timing = attendanceTimingConfig(o.admin);
    const missingAttendanceState = applyMissingAttendancePeople(navigation.groupedRecords, {
      selectedDate: navigation.selectedDate,
      today: o.today,
      role: o.role,
      nowTime,
      lateLimit: timing.lateLimit,
      employees: o.employees,
      managers: o.managers,
      tenantId: o.tenantId
    });
    return {
      weeklyBalanceLabel: attendanceWeeklyBalanceLabel(totalHours, weeklyTarget),
      selectedDate: navigation.selectedDate,
      groupedRecords: navigation.groupedRecords,
      nowTime,
      expectedTime: timing.expectedTime,
      toleranceMinutes: timing.toleranceMinutes,
      lateLimit: timing.lateLimit,
      missingAttendanceState
    };
  }

  function prepareMissingAttendanceState(groupedRecords, options) {
    const o = options || {};
    if (!shouldIncludeMissingAttendancePeople(o)) return { shouldApply: false, missingIds: [] };
    const eligibleIds = eligibleAttendancePersonIds(o.employees, o.managers, o.tenantId);
    return {
      shouldApply: true,
      missingIds: missingAttendancePersonIds(groupedRecords, eligibleIds)
    };
  }

  function applyMissingAttendancePeople(groupedRecords, options) {
    const state = prepareMissingAttendanceState(groupedRecords, options);
    if (state.shouldApply) addMissingAttendancePeople(groupedRecords, state.missingIds);
    return state;
  }

  function attendancePersonName(personId, administrators, getEmployeeName) {
    const admin = (Array.isArray(administrators) ? administrators : []).find(function (item) { return item.id === personId; });
    if (admin && admin.nome) return admin.nome;
    return typeof getEmployeeName === 'function' ? getEmployeeName(personId) : '';
  }

  function prepareAttendancePersonAccordionItem(personId, records, options) {
    const o = options || {};
    const card = prepareAttendanceAccordionPerson(records, o);
    const escapeHtml = typeof o.escapeHtml === 'function' ? o.escapeHtml : function (value) { return String(value == null ? '' : value); };
    return attendanceAccordionItem({
      personId,
      nameHtml: escapeHtml(o.personName || ''),
      summaryHtml: card.summaryHtml,
      rowsHtml: card.rowsHtml,
      hasRecords: card.hasRecords,
      mode: o.mode
    });
  }

  function createAttendancePersonRenderer(options) {
    const o = options || {};
    const viewState = o.viewState || {};
    return function (personId, records, personOptions) {
      const p = personOptions || {};
      return prepareAttendancePersonAccordionItem(personId, records, {
        absence: p.absence,
        personName: p.personName,
        nowTime: viewState.nowTime,
        selectedDateIsToday: o.selectedDateIsToday,
        lateLimit: viewState.lateLimit,
        expectedTime: viewState.expectedTime,
        toleranceMinutes: viewState.toleranceMinutes,
        mode: o.mode,
        calculateHours: o.calculateHours,
        formatHours: o.formatHours,
        getWorkDescription: o.getWorkDescription,
        getClientName: o.getClientName,
        escapeHtml: o.escapeHtml
      });
    };
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
    isAttendanceLate,
    attendanceRecordHours,
    attendanceRecordWorkplace,
    attendanceRecordMedia,
    prepareAttendanceRecordRow,
    shouldIncludeMissingAttendancePeople,
    eligibleAttendancePersonIds,
    missingAttendancePersonIds,
    addMissingAttendancePeople,
    prepareAttendancePersonState,
    attendancePersonPresentation,
    attendancePersonRows,
    prepareAttendanceAccordionPerson,
    filterAttendanceRecordsForViewer,
    attendanceRecentStart,
    calculateWeeklyAttendanceTotal,
    attendanceWeeklyTarget,
    attendanceWeeklyBalanceLabel,
    attendanceViewElements,
    applyAttendanceEmptyState,
    prepareAttendanceNavigation,
    attendanceTimingConfig,
    applyAttendanceAccordionState,
    mergeAttendanceRecords,
    prepareAttendanceVisibleRecords,
    prepareAttendancePeriods,
    prepareAttendanceBaseState,
    prepareAttendanceViewState,
    prepareMissingAttendanceState,
    applyMissingAttendancePeople,
    attendancePersonName,
    prepareAttendancePersonAccordionItem,
    createAttendancePersonRenderer
  };
})();
