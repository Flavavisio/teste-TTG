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

old_base = '''            // _ehObraLonga: true marca estes registos como vindos do timer de obra (obraPontoLonga),
            // que corre em PARALELO ao ponto geral (não é um turno à parte) — por isso continuam a
            // aparecer na listagem (para se ver em que obra a pessoa esteve), mas não podem somar
            // por cima das horas do ponto geral, senão o mesmo período fica contado a dobrar.
            const _longosComoRegistro = window.TotalGestAttendanceView.buildLongWorkAttendanceRecords(
                dados.obraPontoLonga || [],
                dados.obras || []
            );
            let registros = [...(dados.ponto || []), ..._longosComoRegistro];

            registros = window.TotalGestAttendanceView.filterAttendanceRecordsForViewer(
                registros,
                usuarioLogado,
                _tenantId()
            );

            const _wsP = _inicioSemana();
            const _msP = window.TotalGestAttendanceView.attendanceRecentStart(new Date()); // início do mês ANTERIOR — mostra o mês corrente + o mês anterior
            const _periodRecords = window.TotalGestAttendanceView.selectRecentAttendanceRecords(registros, {
                weekStart: _wsP,
                recentStart: _msP
            });
            const _registrosSemana = _periodRecords.weekRecords;
            registros = _periodRecords.recentRecords;'''
new_base = '''            const attendanceBaseState = window.TotalGestAttendanceView.prepareAttendanceBaseState({
                pointRecords: dados.ponto || [],
                longWorkRecords: dados.obraPontoLonga || [],
                works: dados.obras || [],
                user: usuarioLogado,
                tenantId: _tenantId(),
                weekStart: _inicioSemana(),
                currentDate: new Date()
            });
            const _registrosSemana = attendanceBaseState.weekRecords;
            let registros = attendanceBaseState.recentRecords;'''
assert app.count(old_base) == 1, app.count(old_base)
app = app.replace(old_base, new_base, 1)

insert_marker = '  window.TotalGestAttendanceView = {'
assert view.count(insert_marker) == 1
helpers = '''  function mergeAttendanceRecords(pointRecords, longWorkRecords, works) {
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

'''
view = view.replace(insert_marker, helpers + insert_marker, 1)

old_exports = '''    applyAttendanceEmptyState,
    prepareAttendanceNavigation,
    attendanceTimingConfig,
    applyAttendanceAccordionState
  };'''
new_exports = '''    applyAttendanceEmptyState,
    prepareAttendanceNavigation,
    attendanceTimingConfig,
    applyAttendanceAccordionState,
    mergeAttendanceRecords,
    prepareAttendanceVisibleRecords,
    prepareAttendancePeriods,
    prepareAttendanceBaseState
  };'''
assert view.count(old_exports) == 1, view.count(old_exports)
view = view.replace(old_exports, new_exports, 1)

assert "const CACHE = 'totalgest-v161';" in sw
sw = sw.replace("const CACHE = 'totalgest-v161';", "const CACHE = 'totalgest-v162';", 1)

app_path.write_text(app, encoding='utf-8')
view_path.write_text(view, encoding='utf-8')
sw_path.write_text(sw, encoding='utf-8')

app_after = app_path.read_text(encoding='utf-8')
assert function_block(app_after, services_marker) == services_before
assert function_block(app_after, persist_marker) == persist_before
assert function_block(app_after, repair_marker) == repair_before
point = function_block(app_after, point_marker)
assert point.count('prepareAttendanceBaseState({') == 1
assert point.count('const _registrosSemana = attendanceBaseState.weekRecords;') == 1
assert point.count('let registros = attendanceBaseState.recentRecords;') == 1
for old in ['buildLongWorkAttendanceRecords(', 'filterAttendanceRecordsForViewer(', 'attendanceRecentStart(new Date())', 'selectRecentAttendanceRecords(registros, {']:
    assert old not in point, old
assert point.count('const _ausenciaHoje = _funcionarioAusenteEm(fid, _hojeSoP);') == 1
assert point.count('guardarDados(dados)') == 0
print('SAFE_CUTS=4')
print('SERVICES_BLOCK_UNCHANGED=OK')
print('POINT_PERSISTENCE_UNCHANGED=OK')
print('POINT_REPAIR_UNCHANGED=OK')
print('POINT_ABSENCE_LOOKUP_PRESERVED=OK')
print('RENDER_PONTO_AFTER_CHARS=', len(point))
print('RENDER_PONTO_AFTER_LINES=', point.count('\n') + 1)
print('STRUCTURE=OK')
