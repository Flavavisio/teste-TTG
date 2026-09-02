from pathlib import Path

app_path = Path('app.html')
view_path = Path('assets/js/app-attendance-view.js')
sw_path = Path('sw.js')

app = app_path.read_text(encoding='utf-8')
view = view_path.read_text(encoding='utf-8')
sw = sw_path.read_text(encoding='utf-8')

def function_block(text, marker):
    s = text.index(marker)
    e = text.index('\n        function ', s + len(marker))
    return text[s:e]

services_marker = '        function renderizarServicos() {'
persist_marker = '        function _guardarEdicaoPontoRegisto(regId) {'
repair_marker = '        function _repararEntradasPresas() {'
services_before = function_block(app, services_marker)
persist_before = function_block(app, persist_marker)
repair_before = function_block(app, repair_marker)

point_marker = '        function renderizarPonto() {'
ps = app.index(point_marker)
pe = app.index('\n        function ', ps + len(point_marker))
point = app[ps:pe]
start_token = '                const personAttendance = window.TotalGestAttendanceView.preparePersonAttendanceRecords(porPessoa[fid]);'
start = point.index(start_token)
accordion_token = '                return window.TotalGestAttendanceView.attendanceAccordionItem({'
acc = point.index(accordion_token, start)
end = point.index('\n                });', acc) + len('\n                });')
old_person_block = point[start:end]
assert old_person_block.count('const _ausenciaHoje = _funcionarioAusenteEm(fid, _hojeSoP);') == 1
assert old_person_block.count('prepareAttendanceRecordRow(r, {') == 1
assert old_person_block.count('attendanceAccordionItem({') == 1

new_person_block = '''                const nomePessoa = (dados.administradores?.find(a => a.id === fid)?.nome) || obterNomeFuncionario(fid);
                const _ausenciaHoje = _funcionarioAusenteEm(fid, _hojeSoP);
                const personCard = window.TotalGestAttendanceView.prepareAttendanceAccordionPerson(porPessoa[fid], {
                    absence: _ausenciaHoje,
                    personName: nomePessoa,
                    nowTime: agoraHM,
                    selectedDateIsToday: _hojeSoP === getDataHoje(),
                    lateLimit: _limiteAtraso,
                    expectedTime: _horaEsperada,
                    toleranceMinutes: _tolerMin,
                    mode: _pontoNavModo,
                    calculateHours: calcularHoras,
                    formatHours: _fmtH,
                    getWorkDescription: obterDescricaoOS,
                    getClientName: obterNomeCliente,
                    escapeHtml: escapeHtmlSimples
                });
                return window.TotalGestAttendanceView.attendanceAccordionItem({
                    personId: fid,
                    nameHtml: escapeHtmlSimples(nomePessoa),
                    summaryHtml: personCard.summaryHtml,
                    rowsHtml: personCard.rowsHtml,
                    hasRecords: personCard.hasRecords,
                    mode: _pontoNavModo
                });'''
point_after = point[:start] + new_person_block + point[end:]
app = app[:ps] + point_after + app[pe:]

insert_marker = '  window.TotalGestAttendanceView = {'
assert view.count(insert_marker) == 1
helpers = '''  function prepareAttendancePersonState(records, options) {
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

'''
view = view.replace(insert_marker, helpers + insert_marker, 1)

old_exports = '''    missingAttendancePersonIds,
    addMissingAttendancePeople
  };'''
new_exports = '''    missingAttendancePersonIds,
    addMissingAttendancePeople,
    prepareAttendancePersonState,
    attendancePersonPresentation,
    attendancePersonRows,
    prepareAttendanceAccordionPerson
  };'''
assert view.count(old_exports) == 1, view.count(old_exports)
view = view.replace(old_exports, new_exports, 1)

assert "const CACHE = 'totalgest-v158';" in sw
sw = sw.replace("const CACHE = 'totalgest-v158';", "const CACHE = 'totalgest-v159';", 1)

app_path.write_text(app, encoding='utf-8')
view_path.write_text(view, encoding='utf-8')
sw_path.write_text(sw, encoding='utf-8')

app_after = app_path.read_text(encoding='utf-8')
assert function_block(app_after, services_marker) == services_before
assert function_block(app_after, persist_marker) == persist_before
assert function_block(app_after, repair_marker) == repair_before
point_final = function_block(app_after, point_marker)
assert point_final.count('prepareAttendanceAccordionPerson(porPessoa[fid], {') == 1
assert point_final.count('const _ausenciaHoje = _funcionarioAusenteEm(fid, _hojeSoP);') == 1
for item in ['preparePersonAttendanceRecords(porPessoa[fid])','calculateGeneralAttendanceState(regsGeral, agoraHM, calcularHoras)','applyAttendanceLunchDeduction(regsPessoa, {','isAttendanceBelowEightHours(geral, geralAberto, horasGeral)','isAttendanceLate({','attendanceAlertsHtml({','attendancePersonSummaryHtml({','prepareAttendanceRecordRow(r, {']:
    assert item not in point_final, item
print('SAFE_CUTS=4')
print('SERVICES_BLOCK_UNCHANGED=OK')
print('POINT_PERSISTENCE_UNCHANGED=OK')
print('POINT_REPAIR_UNCHANGED=OK')
print('POINT_ABSENCE_LOOKUP_PRESERVED=OK')
print('RENDER_PONTO_AFTER_CHARS=', len(point_final))
print('RENDER_PONTO_AFTER_LINES=', point_final.count('\n') + 1)
print('STRUCTURE=OK')
