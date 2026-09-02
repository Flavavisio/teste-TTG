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
point_marker = '        function renderizarPonto() {'
services_before = function_block(app, services_marker)
persist_before = function_block(app, persist_marker)
repair_before = function_block(app, repair_marker)

old_dom = """            const empty = document.getElementById('emptyPonto');"""
new_dom = """            const attendanceElements = window.TotalGestAttendanceView.attendanceViewElements(document);
            const empty = attendanceElements.empty;"""
assert app.count(old_dom) == 1, app.count(old_dom)
app = app.replace(old_dom, new_dom, 1)

old_empty = """            if (registros.length === 0) {
                const contAccVazio = document.getElementById('pontoAcordeao'); if (contAccVazio) contAccVazio.innerHTML = '';
                empty.style.display = 'block';
                document.getElementById('saldoHoras').textContent = 'Horas esta semana: 0h 0m';
                return;
            }
            empty.style.display = 'none';"""
new_empty = """            if (window.TotalGestAttendanceView.applyAttendanceEmptyState(attendanceElements, registros.length === 0)) return;"""
assert app.count(old_empty) == 1, app.count(old_empty)
app = app.replace(old_empty, new_empty, 1)

old_nav = """            if (!_pontoNavData) _pontoNavData = getDataHoje();
            const _hojeSoP = _pontoNavData;
            const registrosHoje = window.TotalGestAttendanceView.selectAttendanceNavigationRecords(
                registros,
                _hojeSoP,
                _pontoNavModo
            );
            const contAcc = document.getElementById('pontoAcordeao');
            empty.style.display = 'none';
            const porPessoa = window.TotalGestAttendanceView.groupAttendanceByPerson(registrosHoje);"""
new_nav = """            const navigationState = window.TotalGestAttendanceView.prepareAttendanceNavigation(registros, {
                selectedDate: _pontoNavData,
                today: getDataHoje(),
                mode: _pontoNavModo
            });
            _pontoNavData = navigationState.selectedDate;
            const _hojeSoP = navigationState.selectedDate;
            const contAcc = attendanceElements.accordion;
            const porPessoa = navigationState.groupedRecords;"""
assert app.count(old_nav) == 1, app.count(old_nav)
app = app.replace(old_nav, new_nav, 1)

old_timing = """            const agoraHM = new Date().toTimeString().slice(0, 5);
            const _adminCfg = adminAtual();
            const _horaEsperada = _adminCfg?.horaEntradaHabitual || '09:00';
            const _tolerMin = _adminCfg?.toleranciaAtrasoMin != null ? _adminCfg.toleranciaAtrasoMin : 15;
            const _limiteAtraso = window.TotalGestAttendanceView.attendanceLateLimit(_horaEsperada, _tolerMin);"""
new_timing = """            const agoraHM = new Date().toTimeString().slice(0, 5);
            const timingConfig = window.TotalGestAttendanceView.attendanceTimingConfig(adminAtual());
            const _horaEsperada = timingConfig.expectedTime;
            const _tolerMin = timingConfig.toleranceMinutes;
            const _limiteAtraso = timingConfig.lateLimit;"""
assert app.count(old_timing) == 1, app.count(old_timing)
app = app.replace(old_timing, new_timing, 1)

old_final = """            if (!Object.keys(porPessoa).length) { if (contAcc) contAcc.innerHTML = ''; empty.style.display = 'block'; return; }
            if (contAcc) contAcc.innerHTML = htmlAcc;"""
new_final = """            if (!window.TotalGestAttendanceView.applyAttendanceAccordionState(attendanceElements, htmlAcc, Object.keys(porPessoa).length)) return;"""
assert app.count(old_final) == 1, app.count(old_final)
app = app.replace(old_final, new_final, 1)

insert_marker = '  window.TotalGestAttendanceView = {'
assert view.count(insert_marker) == 1
helpers = '''  function attendanceViewElements(doc) {
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

'''
view = view.replace(insert_marker, helpers + insert_marker, 1)

old_exports = '''    calculateWeeklyAttendanceTotal,
    attendanceWeeklyTarget,
    attendanceWeeklyBalanceLabel
  };'''
new_exports = '''    calculateWeeklyAttendanceTotal,
    attendanceWeeklyTarget,
    attendanceWeeklyBalanceLabel,
    attendanceViewElements,
    applyAttendanceEmptyState,
    prepareAttendanceNavigation,
    attendanceTimingConfig,
    applyAttendanceAccordionState
  };'''
assert view.count(old_exports) == 1, view.count(old_exports)
view = view.replace(old_exports, new_exports, 1)

assert "const CACHE = 'totalgest-v160';" in sw
sw = sw.replace("const CACHE = 'totalgest-v160';", "const CACHE = 'totalgest-v161';", 1)

app_path.write_text(app, encoding='utf-8')
view_path.write_text(view, encoding='utf-8')
sw_path.write_text(sw, encoding='utf-8')

app_after = app_path.read_text(encoding='utf-8')
assert function_block(app_after, services_marker) == services_before
assert function_block(app_after, persist_marker) == persist_before
assert function_block(app_after, repair_marker) == repair_before
point = function_block(app_after, point_marker)
for item in ['attendanceViewElements(document)','applyAttendanceEmptyState(attendanceElements, registros.length === 0)','prepareAttendanceNavigation(registros, {','attendanceTimingConfig(adminAtual())','applyAttendanceAccordionState(attendanceElements, htmlAcc, Object.keys(porPessoa).length)']:
    assert point.count(item) == 1, (item, point.count(item))
for old in ["document.getElementById('emptyPonto')","document.getElementById('pontoAcordeao')","if (!_pontoNavData) _pontoNavData = getDataHoje();","const _adminCfg = adminAtual();","if (!Object.keys(porPessoa).length) { if (contAcc) contAcc.innerHTML = ''; empty.style.display = 'block'; return; }"]:
    assert old not in point, old
assert point.count('const _ausenciaHoje = _funcionarioAusenteEm(fid, _hojeSoP);') == 1
assert point.count('guardarDados(dados)') == 0
print('SAFE_CUTS=5')
print('SERVICES_BLOCK_UNCHANGED=OK')
print('POINT_PERSISTENCE_UNCHANGED=OK')
print('POINT_REPAIR_UNCHANGED=OK')
print('POINT_ABSENCE_LOOKUP_PRESERVED=OK')
print('RENDER_PONTO_AFTER_CHARS=', len(point))
print('RENDER_PONTO_AFTER_LINES=', point.count('\\n') + 1)
print('STRUCTURE=OK')
