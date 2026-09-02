from pathlib import Path

app_path=Path('app.html'); view_path=Path('assets/js/app-attendance-view.js'); sw_path=Path('sw.js')
app=app_path.read_text(encoding='utf-8'); view=view_path.read_text(encoding='utf-8'); sw=sw_path.read_text(encoding='utf-8')

def block(text, marker):
    s=text.index(marker); e=text.index('\n        function ',s+len(marker)); return text[s:e]
services_before=block(app,'        function renderizarServicos() {')
persist_before=block(app,'        function _guardarEdicaoPontoRegisto(regId) {')
repair_before=block(app,'        function _repararEntradasPresas() {')

old_missing='''            // Para o admin/sub-admin: mostra também quem ainda não picou nada, se já passou da
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
new_missing='''            window.TotalGestAttendanceView.applyMissingAttendancePeople(porPessoa, {
                selectedDate: _hojeSoP,
                today: getDataHoje(),
                role: usuarioLogado?.role || '',
                nowTime: agoraHM,
                lateLimit: _limiteAtraso,
                employees: dados.funcionarios || [],
                managers: dados.encarregados || [],
                tenantId: _tenantId()
            });'''
assert app.count(old_missing)==1,app.count(old_missing); app=app.replace(old_missing,new_missing,1)

old_map='''            const htmlAcc = Object.keys(porPessoa).map(fid => {
                const nomePessoa = (dados.administradores?.find(a => a.id === fid)?.nome) || obterNomeFuncionario(fid);
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
                });
            }).join('');'''
new_map='''            const htmlAcc = Object.keys(porPessoa).map(fid => {
                const nomePessoa = window.TotalGestAttendanceView.attendancePersonName(
                    fid,
                    dados.administradores || [],
                    obterNomeFuncionario
                );
                const _ausenciaHoje = _funcionarioAusenteEm(fid, _hojeSoP);
                return window.TotalGestAttendanceView.prepareAttendancePersonAccordionItem(fid, porPessoa[fid], {
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
            }).join('');'''
assert app.count(old_map)==1,app.count(old_map); app=app.replace(old_map,new_map,1)

marker='  window.TotalGestAttendanceView = {'
helpers='''  function prepareMissingAttendanceState(groupedRecords, options) {
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

'''
assert view.count(marker)==1; view=view.replace(marker,helpers+marker,1)
oldexp='''    prepareAttendanceBaseState,
    prepareAttendanceViewState
  };'''
newexp='''    prepareAttendanceBaseState,
    prepareAttendanceViewState,
    prepareMissingAttendanceState,
    applyMissingAttendancePeople,
    attendancePersonName,
    prepareAttendancePersonAccordionItem
  };'''
assert view.count(oldexp)==1; view=view.replace(oldexp,newexp,1)
assert "const CACHE = 'totalgest-v163';" in sw; sw=sw.replace("const CACHE = 'totalgest-v163';","const CACHE = 'totalgest-v164';",1)
app_path.write_text(app,encoding='utf-8'); view_path.write_text(view,encoding='utf-8'); sw_path.write_text(sw,encoding='utf-8')
assert block(app,'        function renderizarServicos() {')==services_before
assert block(app,'        function _guardarEdicaoPontoRegisto(regId) {')==persist_before
assert block(app,'        function _repararEntradasPresas() {')==repair_before
p=block(app,'        function renderizarPonto() {')
for x in ['applyMissingAttendancePeople(porPessoa, {','attendancePersonName(','prepareAttendancePersonAccordionItem(fid, porPessoa[fid], {']:
    assert p.count(x)==1,(x,p.count(x))
for x in ['shouldIncludeMissingAttendancePeople({','eligibleAttendancePersonIds(','missingAttendancePersonIds(porPessoa, _todosIds)','addMissingAttendancePeople(porPessoa, idsSemPicagem)','prepareAttendanceAccordionPerson(porPessoa[fid], {','attendanceAccordionItem({']:
    assert x not in p,x
assert p.count('const _ausenciaHoje = _funcionarioAusenteEm(fid, _hojeSoP);')==1
assert 'guardarDados(dados)' not in p
print('SAFE_CUTS=4'); print('SERVICES_BLOCK_UNCHANGED=OK'); print('POINT_PERSISTENCE_UNCHANGED=OK'); print('POINT_REPAIR_UNCHANGED=OK'); print('POINT_ABSENCE_LOOKUP_PRESERVED=OK'); print('RENDER_PONTO_AFTER_CHARS=',len(p)); print('RENDER_PONTO_AFTER_LINES=',p.count('\n')+1); print('STRUCTURE=OK')
