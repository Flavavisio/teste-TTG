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

old_rows = '''                const corpo = regsPessoa.map(r => {
                    const horas = r.saida ? calcularHoras(r.entrada, r.saida) : null;
                    const obra = escapeHtmlSimples(r.servicoId ? obterDescricaoOS(r.servicoId) : (r.obraDescricao || (r.obraId ? 'Obra' : 'Escritório/Exterior')));
                    const clienteNome = r.clienteId ? (obterNomeCliente(r.clienteId) || '-') : '-';
                    const tituloEdicao = window.TotalGestAttendanceView.attendanceEditTitle(r, escapeHtmlSimples);
                    const timePresentation = window.TotalGestAttendanceView.attendanceEntryExitHtml(r, tituloEdicao);
                    const entradaTxt = timePresentation.entryHtml;
                    const saidaTxt = timePresentation.exitHtml;
                    const fotoHtml = window.TotalGestAttendanceView.attendancePhotoHtml(r.foto);
                    const gpsEntradaHtml = window.TotalGestAttendanceView.attendanceGpsHtml(r.lat, r.lng);
                    const gpsSaidaHtml = window.TotalGestAttendanceView.attendanceGpsHtml(r.latSaida, r.lngSaida);
                    const dataHtml = window.TotalGestAttendanceView.attendanceDateCell(r.data, _pontoNavModo);
                    return window.TotalGestAttendanceView.attendanceRecordRow({
                        dateHtml: dataHtml,
                        entryHtml: entradaTxt,
                        exitHtml: saidaTxt,
                        hoursHtml: horas != null ? _fmtH(horas) : '',
                        clientName: clienteNome,
                        workHtml: obra,
                        photoHtml: fotoHtml,
                        gpsEntryHtml: gpsEntradaHtml,
                        gpsExitHtml: gpsSaidaHtml,
                        recordId: r.id
                    });
                }).join('');'''
new_rows = '''                const corpo = regsPessoa.map(r => window.TotalGestAttendanceView.attendanceRecordRow(
                    window.TotalGestAttendanceView.prepareAttendanceRecordRow(r, {
                        mode: _pontoNavModo,
                        calculateHours: calcularHoras,
                        formatHours: _fmtH,
                        getWorkDescription: obterDescricaoOS,
                        getClientName: obterNomeCliente,
                        escapeHtml: escapeHtmlSimples
                    })
                )).join('');'''
assert app.count(old_rows) == 1, app.count(old_rows)
app = app.replace(old_rows, new_rows, 1)

insert_marker = '  window.TotalGestAttendanceView = {'
assert view.count(insert_marker) == 1
helpers = '''  function attendanceRecordHours(record, calculateHours, formatHoursFn) {
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

'''
view = view.replace(insert_marker, helpers + insert_marker, 1)

old_exports = '''    applyAttendanceLunchDeduction,
    isAttendanceBelowEightHours,
    isAttendanceLate
  };'''
new_exports = '''    applyAttendanceLunchDeduction,
    isAttendanceBelowEightHours,
    isAttendanceLate,
    attendanceRecordHours,
    attendanceRecordWorkplace,
    attendanceRecordMedia,
    prepareAttendanceRecordRow
  };'''
assert view.count(old_exports) == 1, view.count(old_exports)
view = view.replace(old_exports, new_exports, 1)

assert "const CACHE = 'totalgest-v156';" in sw
sw = sw.replace("const CACHE = 'totalgest-v156';", "const CACHE = 'totalgest-v157';", 1)

app_path.write_text(app, encoding='utf-8')
view_path.write_text(view, encoding='utf-8')
sw_path.write_text(sw, encoding='utf-8')

app_after = app_path.read_text(encoding='utf-8')
assert function_block(app_after, services_marker) == services_before
assert function_block(app_after, persist_marker) == persist_before
assert function_block(app_after, repair_marker) == repair_before
point = function_block(app_after, '        function renderizarPonto() {')
assert point.count('prepareAttendanceRecordRow(r, {') == 1
assert point.count('attendanceRecordRow(') == 1
for item in ['const horas = r.saida ? calcularHoras(r.entrada, r.saida) : null;', 'const obra = escapeHtmlSimples(', 'const clienteNome = r.clienteId ?', 'attendanceEditTitle(r, escapeHtmlSimples)', 'attendancePhotoHtml(r.foto)', 'attendanceGpsHtml(r.lat, r.lng)', 'attendanceDateCell(r.data, _pontoNavModo)']:
    assert item not in point, item
print('SAFE_CUTS=4')
print('SERVICES_BLOCK_UNCHANGED=OK')
print('POINT_PERSISTENCE_UNCHANGED=OK')
print('POINT_REPAIR_UNCHANGED=OK')
print('RENDER_PONTO_AFTER_CHARS=', len(point))
print('RENDER_PONTO_AFTER_LINES=', point.count('\n') + 1)
print('STRUCTURE=OK')
