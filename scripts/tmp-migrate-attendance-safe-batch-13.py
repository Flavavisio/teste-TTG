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

old_person = """                const regsPessoa = porPessoa[fid].sort((a, b) => (a.data || '').localeCompare(b.data || '') || (a.entrada || '').localeCompare(b.entrada || ''));
                const nomePessoa = (dados.administradores?.find(a => a.id === fid)?.nome) || obterNomeFuncionario(fid);
                // Só o registo GERAL (sem OS/obra ligada) conta para os alertas de horas/atraso — as entradas em OS/obra não.
                // Um dia pode ter vários segmentos gerais (ex: entrada → pausa almoço, depois retorno → saída),
                // por isso juntamos todos para calcular o total de horas e construir a linha entrada→...→saída.
                const regsGeral = regsPessoa.filter(r => !r.servicoId && !r.obraId).sort((a, b) => (a.entrada || '').localeCompare(b.entrada || ''));
                const geral = regsGeral[0] || null;
                let horasGeral = 0, geralAberto = false;
                regsGeral.forEach(r => {
                    if (r.entrada && r.saida) horasGeral += calcularHoras(r.entrada, r.saida);
                    else if (r.entrada && !r.saida) { horasGeral += calcularHoras(r.entrada, agoraHM); geralAberto = true; }
                });"""
new_person = """                const personAttendance = window.TotalGestAttendanceView.preparePersonAttendanceRecords(porPessoa[fid]);
                const regsPessoa = personAttendance.personRecords;
                const nomePessoa = (dados.administradores?.find(a => a.id === fid)?.nome) || obterNomeFuncionario(fid);
                // Só o registo GERAL (sem OS/obra ligada) conta para os alertas de horas/atraso — as entradas em OS/obra não.
                // Um dia pode ter vários segmentos gerais (ex: entrada → pausa almoço, depois retorno → saída).
                const regsGeral = personAttendance.generalRecords;
                const generalAttendance = window.TotalGestAttendanceView.calculateGeneralAttendanceState(regsGeral, agoraHM, calcularHoras);
                const geral = generalAttendance.generalRecord;
                let horasGeral = generalAttendance.generalHours;
                const geralAberto = generalAttendance.generalOpen;"""
assert app.count(old_person) == 1, app.count(old_person)
app = app.replace(old_person, new_person, 1)

old_lunch = """                const temPausaGeral = regsPessoa.some(r => r.pausaAlmoco && r.saida);
                let almocoDescontado = false;
                if (!temPausaGeral && !geralAberto && horasGeral > 6) {
                    horasGeral = Math.max(0, horasGeral - 1);
                    almocoDescontado = true;
                }
                const menosDe8h = geral && !geralAberto && horasGeral > 0 && horasGeral < 8;
                const _ausenciaHoje = _funcionarioAusenteEm(fid, _hojeSoP);
                const atrasado = _ausenciaHoje ? false : (geral ? (geral.entrada && geral.entrada > _limiteAtraso) : (_hojeSoP === getDataHoje() && regsPessoa.length === 0 && agoraHM > _limiteAtraso));"""
new_lunch = """                const lunchState = window.TotalGestAttendanceView.applyAttendanceLunchDeduction(regsPessoa, {
                    generalOpen: geralAberto,
                    generalHours: horasGeral
                });
                horasGeral = lunchState.generalHours;
                const almocoDescontado = lunchState.lunchDeducted;
                const menosDe8h = window.TotalGestAttendanceView.isAttendanceBelowEightHours(geral, geralAberto, horasGeral);
                const _ausenciaHoje = _funcionarioAusenteEm(fid, _hojeSoP);
                const atrasado = window.TotalGestAttendanceView.isAttendanceLate({
                    absence: _ausenciaHoje,
                    generalRecord: geral,
                    selectedDateIsToday: _hojeSoP === getDataHoje(),
                    recordsCount: regsPessoa.length,
                    nowTime: agoraHM,
                    lateLimit: _limiteAtraso
                });"""
assert app.count(old_lunch) == 1, app.count(old_lunch)
app = app.replace(old_lunch, new_lunch, 1)

insert_marker = '  window.TotalGestAttendanceView = {'
assert view.count(insert_marker) == 1
helpers = """  function preparePersonAttendanceRecords(records) {
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

"""
view = view.replace(insert_marker, helpers + insert_marker, 1)

old_exports = """    attendanceEditTitle,
    attendanceEntryExitHtml
  };"""
new_exports = """    attendanceEditTitle,
    attendanceEntryExitHtml,
    preparePersonAttendanceRecords,
    calculateGeneralAttendanceState,
    applyAttendanceLunchDeduction,
    isAttendanceBelowEightHours,
    isAttendanceLate
  };"""
assert view.count(old_exports) == 1, view.count(old_exports)
view = view.replace(old_exports, new_exports, 1)

assert "const CACHE = 'totalgest-v155';" in sw
sw = sw.replace("const CACHE = 'totalgest-v155';", "const CACHE = 'totalgest-v156';", 1)

app_path.write_text(app, encoding='utf-8')
view_path.write_text(view, encoding='utf-8')
sw_path.write_text(sw, encoding='utf-8')

app_after = app_path.read_text(encoding='utf-8')
assert function_block(app_after, services_marker) == services_before
assert function_block(app_after, persist_marker) == persist_before
assert function_block(app_after, repair_marker) == repair_before

point = function_block(app_after, '        function renderizarPonto() {')
for item in [
    'preparePersonAttendanceRecords(porPessoa[fid])',
    'calculateGeneralAttendanceState(regsGeral, agoraHM, calcularHoras)',
    'applyAttendanceLunchDeduction(regsPessoa, {',
    'isAttendanceBelowEightHours(geral, geralAberto, horasGeral)',
    'isAttendanceLate({'
]:
    assert point.count(item) == 1, (item, point.count(item))
for item in [
    "const regsPessoa = porPessoa[fid].sort((a, b) =>",
    "const regsGeral = regsPessoa.filter(r => !r.servicoId && !r.obraId)",
    'regsGeral.forEach(r => {',
    'const temPausaGeral = regsPessoa.some(r => r.pausaAlmoco && r.saida);',
    'const atrasado = _ausenciaHoje ? false :'
]:
    assert item not in point, item
assert point.count('const _ausenciaHoje = _funcionarioAusenteEm(fid, _hojeSoP);') == 1
assert point.index('isAttendanceBelowEightHours(') < point.index('const _ausenciaHoje = _funcionarioAusenteEm(fid, _hojeSoP);') < point.index('isAttendanceLate({')

print('SAFE_CUTS=5')
print('SERVICES_BLOCK_UNCHANGED=OK')
print('POINT_PERSISTENCE_UNCHANGED=OK')
print('POINT_REPAIR_UNCHANGED=OK')
print('POINT_ABSENCE_ORDER_PRESERVED=OK')
print('RENDER_PONTO_AFTER_CHARS=', len(point))
print('RENDER_PONTO_AFTER_LINES=', point.count('\n') + 1)
print('STRUCTURE=OK')
