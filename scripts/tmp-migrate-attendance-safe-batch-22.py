from pathlib import Path

app_path=Path('app.html'); view_path=Path('assets/js/app-attendance-view.js'); sw_path=Path('sw.js')
app=app_path.read_text(encoding='utf-8'); view=view_path.read_text(encoding='utf-8'); sw=sw_path.read_text(encoding='utf-8')

def block(text, marker):
    s=text.index(marker); e=text.index('\n        function ',s+len(marker)); return text[s:e]
services_before=block(app,'        function renderizarServicos() {')
persist_before=block(app,'        function _guardarEdicaoPontoRegisto(regId) {')
repair_before=block(app,'        function _repararEntradasPresas() {')

old_call='''            const attendanceViewState = window.TotalGestAttendanceView.prepareAttendanceViewState({
                weekRecords: _registrosSemana,
                recentRecords: registros,
                user: usuarioLogado,
                employees: dados.funcionarios || [],
                managers: dados.encarregados || [],
                selectedDate: _pontoNavData,
                today: getDataHoje(),
                mode: _pontoNavModo,
                nowTime: new Date().toTimeString().slice(0, 5),
                admin: adminAtual(),
                calculateHours: calcularHoras
            });'''
new_call='''            const attendanceViewState = window.TotalGestAttendanceView.prepareAttendanceViewState({
                weekRecords: _registrosSemana,
                recentRecords: registros,
                user: usuarioLogado,
                role: usuarioLogado?.role || '',
                employees: dados.funcionarios || [],
                managers: dados.encarregados || [],
                tenantId: _tenantId(),
                selectedDate: _pontoNavData,
                today: getDataHoje(),
                mode: _pontoNavModo,
                nowTime: new Date().toTimeString().slice(0, 5),
                admin: adminAtual(),
                calculateHours: calcularHoras
            });'''
assert app.count(old_call)==1,app.count(old_call); app=app.replace(old_call,new_call,1)
old_missing='''            window.TotalGestAttendanceView.applyMissingAttendancePeople(porPessoa, {
                selectedDate: _hojeSoP,
                today: getDataHoje(),
                role: usuarioLogado?.role || '',
                nowTime: agoraHM,
                lateLimit: _limiteAtraso,
                employees: dados.funcionarios || [],
                managers: dados.encarregados || [],
                tenantId: _tenantId()
            });
'''
assert app.count(old_missing)==1,app.count(old_missing); app=app.replace(old_missing,'',1)

start=view.index('  function prepareAttendanceViewState(options) {')
end=view.index('\n  function prepareMissingAttendanceState(',start)
old_fn=view[start:end]
new_fn='''  function prepareAttendanceViewState(options) {
    const o = options || {};
    const nowTime = o.nowTime || new Date().toTimeString().slice(0, 5);
    const totalHours = calculateWeeklyAttendanceTotal(o.weekRecords, {
      today: o.today,
      nowTime,
      calculateHours: o.calculateHours
    });
    const weeklyTarget = attendanceWeeklyTarget(o.user, o.employees, o.managers);
    const navigation = prepareAttendanceNavigation(o.recentRecords, {
      selectedDate: o.selectedDate,
      today: o.today,
      mode: o.mode
    });
    const timing = attendanceTimingConfig(o.admin);
    const missingAttendanceState = applyMissingAttendancePeople(navigation.groupedRecords, {
      selectedDate: navigation.selectedDate,
      today: o.today,
      role: o.role,
      nowTime,
      lateLimit: timing.lateLimit,
      employees: o.employees,
      managers: o.managers,
      tenantId: o.tenantId
    });
    return {
      weeklyBalanceLabel: attendanceWeeklyBalanceLabel(totalHours, weeklyTarget),
      selectedDate: navigation.selectedDate,
      groupedRecords: navigation.groupedRecords,
      nowTime,
      expectedTime: timing.expectedTime,
      toleranceMinutes: timing.toleranceMinutes,
      lateLimit: timing.lateLimit,
      missingAttendanceState
    };
  }
'''
view=view[:start]+new_fn+view[end:]
assert "const CACHE = 'totalgest-v164';" in sw; sw=sw.replace("const CACHE = 'totalgest-v164';","const CACHE = 'totalgest-v165';",1)
app_path.write_text(app,encoding='utf-8'); view_path.write_text(view,encoding='utf-8'); sw_path.write_text(sw,encoding='utf-8')
assert block(app,'        function renderizarServicos() {')==services_before
assert block(app,'        function _guardarEdicaoPontoRegisto(regId) {')==persist_before
assert block(app,'        function _repararEntradasPresas() {')==repair_before
p=block(app,'        function renderizarPonto() {')
assert p.count('prepareAttendanceViewState({')==1
assert 'applyMissingAttendancePeople(porPessoa, {' not in p
assert p.count('const _ausenciaHoje = _funcionarioAusenteEm(fid, _hojeSoP);')==1
assert 'guardarDados(dados)' not in p
print('SAFE_CUTS=2'); print('SERVICES_BLOCK_UNCHANGED=OK'); print('POINT_PERSISTENCE_UNCHANGED=OK'); print('POINT_REPAIR_UNCHANGED=OK'); print('POINT_ABSENCE_LOOKUP_PRESERVED=OK'); print('RENDER_PONTO_AFTER_CHARS=',len(p)); print('RENDER_PONTO_AFTER_LINES=',p.count('\n')+1); print('STRUCTURE=OK')
