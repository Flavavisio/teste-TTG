from pathlib import Path

app_path=Path('app.html'); view_path=Path('assets/js/app-attendance-view.js'); sw_path=Path('sw.js')
app=app_path.read_text(encoding='utf-8'); view=view_path.read_text(encoding='utf-8'); sw=sw_path.read_text(encoding='utf-8')

def block(text, marker):
    s=text.index(marker); e=text.index('\n        function ',s+len(marker)); return text[s:e]
services_before=block(app,'        function renderizarServicos() {')
persist_before=block(app,'        function _guardarEdicaoPontoRegisto(regId) {')
repair_before=block(app,'        function _repararEntradasPresas() {')

old_alias='''            const _hojeSoP = attendanceViewState.selectedDate;
            const porPessoa = attendanceViewState.groupedRecords;
            const agoraHM = attendanceViewState.nowTime;
            const _horaEsperada = attendanceViewState.expectedTime;
            const _tolerMin = attendanceViewState.toleranceMinutes;
            const _limiteAtraso = attendanceViewState.lateLimit;
            const htmlAcc = Object.keys(porPessoa).map(fid => {'''
new_alias='''            const _hojeSoP = attendanceViewState.selectedDate;
            const porPessoa = attendanceViewState.groupedRecords;
            const renderAttendancePerson = window.TotalGestAttendanceView.createAttendancePersonRenderer({
                viewState: attendanceViewState,
                selectedDateIsToday: _hojeSoP === getDataHoje(),
                mode: _pontoNavModo,
                calculateHours: calcularHoras,
                formatHours: _fmtH,
                getWorkDescription: obterDescricaoOS,
                getClientName: obterNomeCliente,
                escapeHtml: escapeHtmlSimples
            });
            const htmlAcc = Object.keys(porPessoa).map(fid => {'''
assert app.count(old_alias)==1,app.count(old_alias); app=app.replace(old_alias,new_alias,1)
old_return='''                return window.TotalGestAttendanceView.prepareAttendancePersonAccordionItem(fid, porPessoa[fid], {
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
                });'''
new_return='''                return renderAttendancePerson(fid, porPessoa[fid], {
                    absence: _ausenciaHoje,
                    personName: nomePessoa
                });'''
assert app.count(old_return)==1,app.count(old_return); app=app.replace(old_return,new_return,1)

marker='  window.TotalGestAttendanceView = {'
helper='''  function createAttendancePersonRenderer(options) {
    const o = options || {};
    const viewState = o.viewState || {};
    return function (personId, records, personOptions) {
      const p = personOptions || {};
      return prepareAttendancePersonAccordionItem(personId, records, {
        absence: p.absence,
        personName: p.personName,
        nowTime: viewState.nowTime,
        selectedDateIsToday: o.selectedDateIsToday,
        lateLimit: viewState.lateLimit,
        expectedTime: viewState.expectedTime,
        toleranceMinutes: viewState.toleranceMinutes,
        mode: o.mode,
        calculateHours: o.calculateHours,
        formatHours: o.formatHours,
        getWorkDescription: o.getWorkDescription,
        getClientName: o.getClientName,
        escapeHtml: o.escapeHtml
      });
    };
  }

'''
assert view.count(marker)==1; view=view.replace(marker,helper+marker,1)
oldexp='''    attendancePersonName,
    prepareAttendancePersonAccordionItem
  };'''
newexp='''    attendancePersonName,
    prepareAttendancePersonAccordionItem,
    createAttendancePersonRenderer
  };'''
assert view.count(oldexp)==1; view=view.replace(oldexp,newexp,1)
assert "const CACHE = 'totalgest-v165';" in sw; sw=sw.replace("const CACHE = 'totalgest-v165';","const CACHE = 'totalgest-v166';",1)
app_path.write_text(app,encoding='utf-8'); view_path.write_text(view,encoding='utf-8'); sw_path.write_text(sw,encoding='utf-8')
assert block(app,'        function renderizarServicos() {')==services_before
assert block(app,'        function _guardarEdicaoPontoRegisto(regId) {')==persist_before
assert block(app,'        function _repararEntradasPresas() {')==repair_before
p=block(app,'        function renderizarPonto() {')
assert p.count('createAttendancePersonRenderer({')==1
assert p.count('renderAttendancePerson(fid, porPessoa[fid], {')==1
for x in ['const agoraHM = attendanceViewState.nowTime;','const _horaEsperada = attendanceViewState.expectedTime;','const _tolerMin = attendanceViewState.toleranceMinutes;','const _limiteAtraso = attendanceViewState.lateLimit;','prepareAttendancePersonAccordionItem(fid, porPessoa[fid], {']:
    assert x not in p,x
assert p.count('const _ausenciaHoje = _funcionarioAusenteEm(fid, _hojeSoP);')==1
assert 'guardarDados(dados)' not in p
print('SAFE_CUTS=2'); print('SERVICES_BLOCK_UNCHANGED=OK'); print('POINT_PERSISTENCE_UNCHANGED=OK'); print('POINT_REPAIR_UNCHANGED=OK'); print('POINT_ABSENCE_LOOKUP_PRESERVED=OK'); print('RENDER_PONTO_AFTER_CHARS=',len(p)); print('RENDER_PONTO_AFTER_LINES=',p.count('\n')+1); print('STRUCTURE=OK')
