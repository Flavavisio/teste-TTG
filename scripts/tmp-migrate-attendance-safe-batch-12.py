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

old_alert = '''                const alertaHtml = (menosDe8h ? ` <i class="fas fa-triangle-exclamation" title="Ainda não completou as 8 horas diárias" style="color:#dc2626;"></i>` : '')
                    + (atrasado ? ` <i class="fas fa-clock" title="${geral ? 'Entrada depois das ' + _limiteAtraso : 'Ainda não picou (esperado ' + _horaEsperada + ' + ' + _tolerMin + 'min de tolerância)'}" style="color:#d97706;"></i>` : '')
                    + (almocoDescontado ? ` <i class="fas fa-utensils" title="Não picou saída/regresso do almoço — foi descontada 1h automaticamente" style="color:#d97706;"></i>` : '');'''
new_alert = '''                const alertaHtml = window.TotalGestAttendanceView.attendanceAlertsHtml({
                    lessThanEightHours: menosDe8h,
                    late: atrasado,
                    hasGeneralRecord: !!geral,
                    lateLimit: _limiteAtraso,
                    expectedTime: _horaEsperada,
                    toleranceMinutes: _tolerMin,
                    lunchDeducted: almocoDescontado
                });'''
assert app.count(old_alert) == 1, app.count(old_alert)
app = app.replace(old_alert, new_alert, 1)

old_summary = '''                let resumoGeral;
                if (_ausenciaHoje) {
                    resumoGeral = `<span style="color:${_ausenciaHoje.cor};font-weight:600;"><i class="fas ${_ausenciaHoje.icon}"></i> ${nomePessoa} está de ${_ausenciaHoje.label}</span>`;
                } else if (geral) {
                    const ultimoGeral = regsGeral[regsGeral.length - 1];
                    const partes = [geral.entrada || '--:--'];
                    regsGeral.forEach(r => {
                        if (r.pausaAlmoco && r.saida) {
                            partes.push(`<i class="fas fa-utensils" title="Pausa almoço" style="color:#d97706;"></i> ${r.saida}`);
                            const retomaReg = regsGeral.find(x => !x.pausaAlmoco && x.entrada && x.entrada > r.saida);
                            partes.push(retomaReg ? retomaReg.entrada : '<span style="color:#d97706;">ainda em pausa</span>');
                        }
                    });
                    partes.push(geralAberto ? '<span style="color:#16a34a;font-weight:700;">em serviço</span>' : (ultimoGeral?.saida || '--:--'));
                    resumoGeral = `${partes.join(' → ')} <span style="color:#64748b;">(${_fmtH(horasGeral)})</span>${alertaHtml}`;
                } else {
                    resumoGeral = `<span style="color:#94a3b8;">${regsPessoa.length === 0 ? (_hojeSoP === getDataHoje() ? 'ainda não picou hoje' : 'sem picagens neste dia') : 'sem picagem geral'}</span>${alertaHtml}`;
                }'''
new_summary = '''                const resumoGeral = window.TotalGestAttendanceView.attendancePersonSummaryHtml({
                    absence: _ausenciaHoje,
                    personName: nomePessoa,
                    generalRecord: geral,
                    generalRecords: regsGeral,
                    generalOpen: geralAberto,
                    generalHoursText: _fmtH(horasGeral),
                    alertsHtml: alertaHtml,
                    recordsCount: regsPessoa.length,
                    isToday: _hojeSoP === getDataHoje()
                });'''
assert app.count(old_summary) == 1, app.count(old_summary)
app = app.replace(old_summary, new_summary, 1)

old_edit = '''                    const foiEditado = !!(r.editadoPor && r.editadoEm);
                    const tituloEdicao = foiEditado ? `Alterado por ${escapeHtmlSimples(r.editadoPor)} em ${new Date(r.editadoEm).toLocaleString('pt-PT')} — Motivo: ${escapeHtmlSimples(r.motivoEdicao || '—')}` : '';
                    const entradaTxt = foiEditado ? `<span style="color:#0ea5e9;" title="${tituloEdicao}">${r.entrada || '--:--'} <i class="fas fa-pen" style="font-size:.65em;"></i></span>` : (r.entrada || '--:--');
                    const saidaTxtBase = r.pausaAlmoco ? `<span style="color:#d97706;"><i class="fas fa-utensils" title="Pausa almoço"></i> ${r.saida || '--:--'}</span>` : (r.saidaAutomatica ? `${r.saida} <i class="fas fa-triangle-exclamation" title="Saída automática após 12h" style="color:#d97706;"></i>` : (r.saida || '--:--'));
                    const saidaTxt = (foiEditado && !r.pausaAlmoco) ? `<span style="color:#0ea5e9;" title="${tituloEdicao}">${saidaTxtBase} <i class="fas fa-pen" style="font-size:.65em;"></i></span>` : saidaTxtBase;'''
new_edit = '''                    const tituloEdicao = window.TotalGestAttendanceView.attendanceEditTitle(r, escapeHtmlSimples);
                    const timePresentation = window.TotalGestAttendanceView.attendanceEntryExitHtml(r, tituloEdicao);
                    const entradaTxt = timePresentation.entryHtml;
                    const saidaTxt = timePresentation.exitHtml;'''
assert app.count(old_edit) == 1, app.count(old_edit)
app = app.replace(old_edit, new_edit, 1)

insert_marker = '  window.TotalGestAttendanceView = {'
assert view.count(insert_marker) == 1
helpers = '''  function attendanceAlertsHtml(options) {
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

'''
view = view.replace(insert_marker, helpers + insert_marker, 1)

old_exports = '''    attendanceDateCell,
    attendanceRecordRow,
    attendanceAccordionItem'''
new_exports = '''    attendanceDateCell,
    attendanceRecordRow,
    attendanceAccordionItem,
    attendanceAlertsHtml,
    attendancePersonSummaryHtml,
    attendanceEditTitle,
    attendanceEntryExitHtml'''
assert view.count(old_exports) == 1
view = view.replace(old_exports, new_exports, 1)

assert "const CACHE = 'totalgest-v154';" in sw
sw = sw.replace("const CACHE = 'totalgest-v154';", "const CACHE = 'totalgest-v155';", 1)

app_path.write_text(app, encoding='utf-8')
view_path.write_text(view, encoding='utf-8')
sw_path.write_text(sw, encoding='utf-8')

app_after = app_path.read_text(encoding='utf-8')
assert function_block(app_after, services_marker) == services_before
assert function_block(app_after, persist_marker) == persist_before
assert function_block(app_after, repair_marker) == repair_before

point = function_block(app_after, '        function renderizarPonto() {')
for item in ['attendanceAlertsHtml({','attendancePersonSummaryHtml({','attendanceEditTitle(r, escapeHtmlSimples)','attendanceEntryExitHtml(r, tituloEdicao)']:
    assert point.count(item) == 1, (item, point.count(item))
for item in ['const alertaHtml = (menosDe8h ?', 'let resumoGeral;', 'const foiEditado = !!(r.editadoPor && r.editadoEm);', 'const saidaTxtBase = r.pausaAlmoco ?']:
    assert item not in point, item
for protected in [
    'const menosDe8h = geral && !geralAberto && horasGeral > 0 && horasGeral < 8;',
    'const _ausenciaHoje = _funcionarioAusenteEm(fid, _hojeSoP);',
    'const atrasado = _ausenciaHoje ? false :',
    'if (!temPausaGeral && !geralAberto && horasGeral > 6) {'
]:
    assert point.count(protected) == 1, protected

print('SAFE_CUTS=4')
print('SERVICES_BLOCK_UNCHANGED=OK')
print('POINT_PERSISTENCE_UNCHANGED=OK')
print('POINT_REPAIR_UNCHANGED=OK')
print('POINT_RULES_PRESERVED=OK')
print('RENDER_PONTO_AFTER_CHARS=', len(point))
print('RENDER_PONTO_AFTER_LINES=', point.count('\n') + 1)
print('STRUCTURE=OK')
