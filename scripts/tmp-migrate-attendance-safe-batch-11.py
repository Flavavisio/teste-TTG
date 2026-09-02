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

old_media = '''                    const fotoHtml = r.foto ? `<img src="${r.foto}" alt="foto" class="foto-miniatura" onclick="window.open('${r.foto}','_blank')" />` : '';
                    const gpsEntradaHtml = (r.lat && r.lng) ? `<a href="https://www.google.com/maps?q=${r.lat},${r.lng}" target="_blank" title="Ver no mapa"><i class="fas fa-map-pin gps-icon"></i></a>` : '<span style="color:#cbd5e1;">—</span>';
                    const gpsSaidaHtml = (r.latSaida && r.lngSaida) ? `<a href="https://www.google.com/maps?q=${r.latSaida},${r.lngSaida}" target="_blank" title="Ver no mapa"><i class="fas fa-map-pin gps-icon"></i></a>` : '<span style="color:#cbd5e1;">—</span>';
                    const dataHtml = _pontoNavModo === 'semana'
                        ? `<span style="min-width:78px;font-weight:600;color:#1a5f7a;text-transform:capitalize;">${r.data ? new Date(r.data + 'T00:00:00').toLocaleDateString('pt-PT', { weekday: 'short', day: '2-digit', month: '2-digit' }) : '—'}</span>`
                        : '';'''
new_media = '''                    const fotoHtml = window.TotalGestAttendanceView.attendancePhotoHtml(r.foto);
                    const gpsEntradaHtml = window.TotalGestAttendanceView.attendanceGpsHtml(r.lat, r.lng);
                    const gpsSaidaHtml = window.TotalGestAttendanceView.attendanceGpsHtml(r.latSaida, r.lngSaida);
                    const dataHtml = window.TotalGestAttendanceView.attendanceDateCell(r.data, _pontoNavModo);'''
assert app.count(old_media) == 1, app.count(old_media)
app = app.replace(old_media, new_media, 1)

old_row = '''                    return `<div class="ponto-acc-sub-row">
                        ${dataHtml}
                        <span style="min-width:60px;font-weight:600;">${entradaTxt}</span>
                        <span style="min-width:60px;font-weight:600;">${saidaTxt}</span>
                        <span style="min-width:60px;">${horas != null ? _fmtH(horas) : ''}</span>
                        <span style="flex:1;min-width:160px;color:#334155;">${clienteNome !== '-' ? clienteNome + ' — ' : ''}${obra}${fotoHtml}</span>
                        <span style="min-width:26px;text-align:center;">${gpsEntradaHtml}</span>
                        <span style="min-width:26px;text-align:center;">${gpsSaidaHtml}</span>
                        <span style="min-width:26px;text-align:center;"><button type="button" class="btn btn-sm btn-outline" style="padding:2px 6px;" title="Editar picagem" onclick="event.stopPropagation();_abrirEdicaoPontoRegisto('${r.id}')"><i class="fas fa-pen"></i></button></span>
                    </div>`;'''
new_row = '''                    return window.TotalGestAttendanceView.attendanceRecordRow({
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
                    });'''
assert app.count(old_row) == 1, app.count(old_row)
app = app.replace(old_row, new_row, 1)

old_item = '''                const cabecalho = `<div class="ponto-acc-sub-row" style="font-size:.68rem;font-weight:700;text-transform:uppercase;letter-spacing:.03em;color:#94a3b8;border-bottom:1px solid #e6eaf2;">
                        ${_pontoNavModo === 'semana' ? '<span style="min-width:78px;">Dia</span>' : ''}
                        <span style="min-width:60px;">Entrada</span>
                        <span style="min-width:60px;">Saída</span>
                        <span style="min-width:60px;">Total</span>
                        <span style="flex:1;min-width:160px;">Local</span>
                        <span style="min-width:26px;text-align:center;" title="GPS na entrada">GPS ent.</span>
                        <span style="min-width:26px;text-align:center;" title="GPS na saída">GPS saí.</span>
                        <span style="min-width:26px;text-align:center;"></span>
                    </div>`;
                return `<div class="ponto-acc-item" id="ponto-acc-${fid}">
                    <div class="ponto-acc-head" onclick="document.getElementById('ponto-acc-${fid}').classList.toggle('aberto')">
                        <span class="nome">${escapeHtmlSimples(nomePessoa)}</span>
                        <span>${resumoGeral}</span>
                        <i class="fas fa-chevron-right chevron"></i>
                    </div>
                    <div class="ponto-acc-body">${regsPessoa.length ? cabecalho + corpo : '<span style="color:#94a3b8;">Sem picagens hoje.</span>'}</div>
                </div>`;'''
new_item = '''                return window.TotalGestAttendanceView.attendanceAccordionItem({
                    personId: fid,
                    nameHtml: escapeHtmlSimples(nomePessoa),
                    summaryHtml: resumoGeral,
                    rowsHtml: corpo,
                    hasRecords: regsPessoa.length > 0,
                    mode: _pontoNavModo
                });'''
assert app.count(old_item) == 1, app.count(old_item)
app = app.replace(old_item, new_item, 1)

insert_marker = '  window.TotalGestAttendanceView = {'
assert view.count(insert_marker) == 1
helpers = '''  function attendancePhotoHtml(url) {
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

'''
view = view.replace(insert_marker, helpers + insert_marker, 1)

old_exports = '''    groupAttendanceByPerson,
    attendanceLateLimit'''
new_exports = '''    groupAttendanceByPerson,
    attendanceLateLimit,
    attendancePhotoHtml,
    attendanceGpsHtml,
    attendanceDateCell,
    attendanceRecordRow,
    attendanceAccordionItem'''
assert view.count(old_exports) == 1
view = view.replace(old_exports, new_exports, 1)

assert "const CACHE = 'totalgest-v153';" in sw
sw = sw.replace("const CACHE = 'totalgest-v153';", "const CACHE = 'totalgest-v154';", 1)

app_path.write_text(app, encoding='utf-8')
view_path.write_text(view, encoding='utf-8')
sw_path.write_text(sw, encoding='utf-8')

app_after = app_path.read_text(encoding='utf-8')
assert function_block(app_after, services_marker) == services_before
assert function_block(app_after, persist_marker) == persist_before
assert function_block(app_after, repair_marker) == repair_before

point = function_block(app_after, '        function renderizarPonto() {')
for item in [
    'attendancePhotoHtml(r.foto)',
    'attendanceGpsHtml(r.lat, r.lng)',
    'attendanceGpsHtml(r.latSaida, r.lngSaida)',
    'attendanceDateCell(r.data, _pontoNavModo)',
    'attendanceRecordRow({',
    'attendanceAccordionItem({'
]:
    assert point.count(item) == 1, (item, point.count(item))
for item in ['const cabecalho = `<div class="ponto-acc-sub-row"', 'return `<div class="ponto-acc-sub-row">', 'const fotoHtml = r.foto ?', 'const gpsEntradaHtml = (r.lat && r.lng) ?']:
    assert item not in point, item

for protected in [
    'const temPausaGeral = regsPessoa.some(r => r.pausaAlmoco && r.saida);',
    'if (!temPausaGeral && !geralAberto && horasGeral > 6) {',
    'const _ausenciaHoje = _funcionarioAusenteEm(fid, _hojeSoP);',
    'const atrasado = _ausenciaHoje ? false :'
]:
    assert point.count(protected) == 1, protected

print('SAFE_CUTS=5')
print('SERVICES_BLOCK_UNCHANGED=OK')
print('POINT_PERSISTENCE_UNCHANGED=OK')
print('POINT_REPAIR_UNCHANGED=OK')
print('POINT_RULES_PRESERVED=OK')
print('RENDER_PONTO_AFTER_CHARS=', len(point))
print('RENDER_PONTO_AFTER_LINES=', point.count('\n') + 1)
print('STRUCTURE=OK')
