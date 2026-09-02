from pathlib import Path

app_path = Path('app.html')
view_path = Path('assets/js/app-attendance-view.js')
sw_path = Path('sw.js')

app = app_path.read_text(encoding='utf-8')
view = view_path.read_text(encoding='utf-8')
sw = sw_path.read_text(encoding='utf-8')

# Preserve protected areas byte-for-byte.
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

old_long = '''            const _longosComoRegistro = (dados.obraPontoLonga || []).map(x => {
                const _obraRec = dados.obras?.find(o => o.id === x.obraId);
                return { ...x, obraDescricao: _obraRec?.nome || 'Obra', clienteId: _obraRec?.clienteId || null, _ehObraLonga: true };
            });
            let registros = [...(dados.ponto || []), ..._longosComoRegistro];'''
new_long = '''            const _longosComoRegistro = window.TotalGestAttendanceView.buildLongWorkAttendanceRecords(
                dados.obraPontoLonga || [],
                dados.obras || []
            );
            let registros = [...(dados.ponto || []), ..._longosComoRegistro];'''
assert app.count(old_long) == 1, app.count(old_long)
app = app.replace(old_long, new_long, 1)

old_recent = '''            const _registrosSemana = registros.filter(p => { const d = p.data ? new Date(p.data + 'T00:00:00') : null; return d && d >= _wsP; });
            registros = registros.filter(p => { const d = p.data ? new Date(p.data + 'T00:00:00') : null; return d && d >= _msP; });'''
new_recent = '''            const _periodRecords = window.TotalGestAttendanceView.selectRecentAttendanceRecords(registros, {
                weekStart: _wsP,
                recentStart: _msP
            });
            const _registrosSemana = _periodRecords.weekRecords;
            registros = _periodRecords.recentRecords;'''
assert app.count(old_recent) == 1, app.count(old_recent)
app = app.replace(old_recent, new_recent, 1)

old_nav = '''            const registrosHoje = _pontoNavModo === 'semana'
                ? registros.filter(p => { const d = p.data ? new Date(p.data + 'T00:00:00') : null; const dp = new Date(_hojeSoP + 'T00:00:00'); const inicioSem = new Date(dp); inicioSem.setDate(dp.getDate() - dp.getDay() + (dp.getDay() === 0 ? -6 : 1)); const fimSem = new Date(inicioSem); fimSem.setDate(inicioSem.getDate() + 6); return d && d >= inicioSem && d <= fimSem; })
                : registros.filter(p => p.data === _hojeSoP);'''
new_nav = '''            const registrosHoje = window.TotalGestAttendanceView.selectAttendanceNavigationRecords(
                registros,
                _hojeSoP,
                _pontoNavModo
            );'''
assert app.count(old_nav) == 1, app.count(old_nav)
app = app.replace(old_nav, new_nav, 1)

old_group = '''            const porPessoa = {};
            registrosHoje.forEach(p => { (porPessoa[p.funcionarioId] = porPessoa[p.funcionarioId] || []).push(p); });'''
new_group = '''            const porPessoa = window.TotalGestAttendanceView.groupAttendanceByPerson(registrosHoje);'''
assert app.count(old_group) == 1, app.count(old_group)
app = app.replace(old_group, new_group, 1)

old_limit = '''            const _limiteAtraso = (() => { const [h, m] = _horaEsperada.split(':').map(Number); const total = h * 60 + m + _tolerMin; return String(Math.floor(total / 60)).padStart(2, '0') + ':' + String(total % 60).padStart(2, '0'); })();'''
new_limit = '''            const _limiteAtraso = window.TotalGestAttendanceView.attendanceLateLimit(_horaEsperada, _tolerMin);'''
assert app.count(old_limit) == 1, app.count(old_limit)
app = app.replace(old_limit, new_limit, 1)

insert_marker = '  window.TotalGestAttendanceView = {'
assert view.count(insert_marker) == 1
helpers = '''  function buildLongWorkAttendanceRecords(longRecords, works) {
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

'''
view = view.replace(insert_marker, helpers + insert_marker, 1)

old_exports = '''    attendanceNavigationLabel,
    isAttendanceNextDisabled'''
new_exports = '''    attendanceNavigationLabel,
    isAttendanceNextDisabled,
    buildLongWorkAttendanceRecords,
    selectRecentAttendanceRecords,
    selectAttendanceNavigationRecords,
    groupAttendanceByPerson,
    attendanceLateLimit'''
assert view.count(old_exports) == 1
view = view.replace(old_exports, new_exports, 1)

assert "const CACHE = 'totalgest-v152';" in sw
sw = sw.replace("const CACHE = 'totalgest-v152';", "const CACHE = 'totalgest-v153';", 1)

app_path.write_text(app, encoding='utf-8')
view_path.write_text(view, encoding='utf-8')
sw_path.write_text(sw, encoding='utf-8')

app_after = app_path.read_text(encoding='utf-8')
assert function_block(app_after, services_marker) == services_before
assert function_block(app_after, persist_marker) == persist_before
assert function_block(app_after, repair_marker) == repair_before

point = function_block(app_after, '        function renderizarPonto() {')
for item in [
    'buildLongWorkAttendanceRecords(',
    'selectRecentAttendanceRecords(registros, {',
    'selectAttendanceNavigationRecords(',
    'groupAttendanceByPerson(registrosHoje)',
    'attendanceLateLimit(_horaEsperada, _tolerMin)'
]:
    assert point.count(item) == 1, (item, point.count(item))
for item in [
    "(dados.obraPontoLonga || []).map(x => {",
    "const _registrosSemana = registros.filter(p =>",
    "const porPessoa = {};",
    "const _limiteAtraso = (() =>"
]:
    assert item not in point, item

print('SAFE_CUTS=5')
print('SERVICES_BLOCK_UNCHANGED=OK')
print('POINT_PERSISTENCE_UNCHANGED=OK')
print('POINT_REPAIR_UNCHANGED=OK')
print('RENDER_PONTO_AFTER_CHARS=', len(point))
print('RENDER_PONTO_AFTER_LINES=', point.count('\\n') + 1)
print('STRUCTURE=OK')
