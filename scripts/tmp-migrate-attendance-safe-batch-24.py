from pathlib import Path

app_path=Path('app.html'); view_path=Path('assets/js/app-attendance-view.js'); sw_path=Path('sw.js')
app=app_path.read_text(encoding='utf-8'); view=view_path.read_text(encoding='utf-8'); sw=sw_path.read_text(encoding='utf-8')

def block(text, marker):
    s=text.index(marker); e=text.index('\n        function ',s+len(marker)); return text[s:e]
services_before=block(app,'        function renderizarServicos() {')
persist_before=block(app,'        function _guardarEdicaoPontoRegisto(regId) {')
repair_before=block(app,'        function _repararEntradasPresas() {')

old_renderer='''            const renderAttendancePerson = window.TotalGestAttendanceView.createAttendancePersonRenderer({
                viewState: attendanceViewState,
                selectedDateIsToday: _hojeSoP === getDataHoje(),
                mode: _pontoNavModo,
                calculateHours: calcularHoras,
                formatHours: _fmtH,
                getWorkDescription: obterDescricaoOS,
                getClientName: obterNomeCliente,
                escapeHtml: escapeHtmlSimples
            });
            const htmlAcc = Object.keys(porPessoa).map(fid => {
                const nomePessoa = window.TotalGestAttendanceView.attendancePersonName(
                    fid,
                    dados.administradores || [],
                    obterNomeFuncionario
                );
                const _ausenciaHoje = _funcionarioAusenteEm(fid, _hojeSoP);
                return renderAttendancePerson(fid, porPessoa[fid], {
                    absence: _ausenciaHoje,
                    personName: nomePessoa
                });
            }).join('');'''
new_renderer='''            const renderAttendancePersonEntry = window.TotalGestAttendanceView.createAttendancePersonEntryRenderer({
                administrators: dados.administradores || [],
                getEmployeeName: obterNomeFuncionario,
                viewState: attendanceViewState,
                selectedDateIsToday: _hojeSoP === getDataHoje(),
                mode: _pontoNavModo,
                calculateHours: calcularHoras,
                formatHours: _fmtH,
                getWorkDescription: obterDescricaoOS,
                getClientName: obterNomeCliente,
                escapeHtml: escapeHtmlSimples
            });
            const htmlAcc = Object.keys(porPessoa).map(fid => {
                const _ausenciaHoje = _funcionarioAusenteEm(fid, _hojeSoP);
                return renderAttendancePersonEntry(fid, porPessoa[fid], _ausenciaHoje);
            }).join('');'''
assert app.count(old_renderer)==1,app.count(old_renderer); app=app.replace(old_renderer,new_renderer,1)

marker='  window.TotalGestAttendanceView = {'
helper='''  function createAttendancePersonEntryRenderer(options) {
    const o = options || {};
    const renderPerson = createAttendancePersonRenderer(o);
    return function (personId, records, absence) {
      return renderPerson(personId, records, {
        absence,
        personName: attendancePersonName(personId, o.administrators, o.getEmployeeName)
      });
    };
  }

'''
assert view.count(marker)==1; view=view.replace(marker,helper+marker,1)
oldexp='''    prepareAttendancePersonAccordionItem,
    createAttendancePersonRenderer
  };'''
newexp='''    prepareAttendancePersonAccordionItem,
    createAttendancePersonRenderer,
    createAttendancePersonEntryRenderer
  };'''
assert view.count(oldexp)==1; view=view.replace(oldexp,newexp,1)
assert "const CACHE = 'totalgest-v166';" in sw; sw=sw.replace("const CACHE = 'totalgest-v166';","const CACHE = 'totalgest-v167';",1)
app_path.write_text(app,encoding='utf-8'); view_path.write_text(view,encoding='utf-8'); sw_path.write_text(sw,encoding='utf-8')
assert block(app,'        function renderizarServicos() {')==services_before
assert block(app,'        function _guardarEdicaoPontoRegisto(regId) {')==persist_before
assert block(app,'        function _repararEntradasPresas() {')==repair_before
p=block(app,'        function renderizarPonto() {')
assert p.count('createAttendancePersonEntryRenderer({')==1
assert p.count('renderAttendancePersonEntry(fid, porPessoa[fid], _ausenciaHoje)')==1
for x in ['attendancePersonName(','renderAttendancePerson(fid, porPessoa[fid], {']:
    assert x not in p,x
assert p.count('const _ausenciaHoje = _funcionarioAusenteEm(fid, _hojeSoP);')==1
assert 'guardarDados(dados)' not in p
print('SAFE_CUTS=2'); print('SERVICES_BLOCK_UNCHANGED=OK'); print('POINT_PERSISTENCE_UNCHANGED=OK'); print('POINT_REPAIR_UNCHANGED=OK'); print('POINT_ABSENCE_LOOKUP_PRESERVED=OK'); print('RENDER_PONTO_AFTER_CHARS=',len(p)); print('RENDER_PONTO_AFTER_LINES=',p.count('\n')+1); print('STRUCTURE=OK')
