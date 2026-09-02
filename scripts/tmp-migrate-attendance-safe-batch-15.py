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

old_missing = '''            // Para o admin/sub-admin: mostra também quem ainda não picou nada, se já passou da
            // tolerância — só faz sentido aplicar isto a "hoje", nunca a dias passados/futuros.
            let idsSemPicagem = [];
            if (_hojeSoP === getDataHoje() && (usuarioLogado?.role === 'admin' || usuarioLogado?.role === 'subadmin') && agoraHM > _limiteAtraso) {
                const _todosIds = [
                    ...(dados.funcionarios || []).filter(f => f.adminId === _tenantId() && f.role !== 'admin' && f.role !== 'superadmin' && !f.suspenso).map(f => f.id),
                    ...(dados.encarregados || []).filter(e => e.adminId === _tenantId() && !e.suspenso).map(e => e.id)
                ];
                idsSemPicagem = _todosIds.filter(id => !porPessoa[id]);
                idsSemPicagem.forEach(id => { porPessoa[id] = []; });
            }'''
new_missing = '''            // Para o admin/sub-admin: mostra também quem ainda não picou nada, se já passou da
            // tolerância — só faz sentido aplicar isto a "hoje", nunca a dias passados/futuros.
            if (window.TotalGestAttendanceView.shouldIncludeMissingAttendancePeople({
                selectedDate: _hojeSoP,
                today: getDataHoje(),
                role: usuarioLogado?.role || '',
                nowTime: agoraHM,
                lateLimit: _limiteAtraso
            })) {
                const _todosIds = window.TotalGestAttendanceView.eligibleAttendancePersonIds(
                    dados.funcionarios || [],
                    dados.encarregados || [],
                    _tenantId()
                );
                const idsSemPicagem = window.TotalGestAttendanceView.missingAttendancePersonIds(porPessoa, _todosIds);
                window.TotalGestAttendanceView.addMissingAttendancePeople(porPessoa, idsSemPicagem);
            }'''
assert app.count(old_missing) == 1, app.count(old_missing)
app = app.replace(old_missing, new_missing, 1)

insert_marker = '  window.TotalGestAttendanceView = {'
assert view.count(insert_marker) == 1
helpers = '''  function shouldIncludeMissingAttendancePeople(options) {
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

'''
view = view.replace(insert_marker, helpers + insert_marker, 1)

old_exports = '''    attendanceRecordMedia,
    prepareAttendanceRecordRow
  };'''
new_exports = '''    attendanceRecordMedia,
    prepareAttendanceRecordRow,
    shouldIncludeMissingAttendancePeople,
    eligibleAttendancePersonIds,
    missingAttendancePersonIds,
    addMissingAttendancePeople
  };'''
assert view.count(old_exports) == 1, view.count(old_exports)
view = view.replace(old_exports, new_exports, 1)

assert "const CACHE = 'totalgest-v157';" in sw
sw = sw.replace("const CACHE = 'totalgest-v157';", "const CACHE = 'totalgest-v158';", 1)

app_path.write_text(app, encoding='utf-8')
view_path.write_text(view, encoding='utf-8')
sw_path.write_text(sw, encoding='utf-8')

app_after = app_path.read_text(encoding='utf-8')
assert function_block(app_after, services_marker) == services_before
assert function_block(app_after, persist_marker) == persist_before
assert function_block(app_after, repair_marker) == repair_before
point = function_block(app_after, '        function renderizarPonto() {')
for item in ['shouldIncludeMissingAttendancePeople({','eligibleAttendancePersonIds(','missingAttendancePersonIds(porPessoa, _todosIds)','addMissingAttendancePeople(porPessoa, idsSemPicagem)']:
    assert point.count(item) == 1, (item, point.count(item))
for item in ['let idsSemPicagem = [];', '...(dados.funcionarios || []).filter(f =>', 'idsSemPicagem = _todosIds.filter(id => !porPessoa[id]);', 'idsSemPicagem.forEach(id => { porPessoa[id] = []; });']:
    assert item not in point, item
print('SAFE_CUTS=4')
print('SERVICES_BLOCK_UNCHANGED=OK')
print('POINT_PERSISTENCE_UNCHANGED=OK')
print('POINT_REPAIR_UNCHANGED=OK')
print('RENDER_PONTO_AFTER_CHARS=', len(point))
print('RENDER_PONTO_AFTER_LINES=', point.count('\n') + 1)
print('STRUCTURE=OK')
