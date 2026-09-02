from pathlib import Path

app_path=Path('app.html'); view_path=Path('assets/js/app-attendance-view.js'); sw_path=Path('sw.js')
app=app_path.read_text(encoding='utf-8'); view=view_path.read_text(encoding='utf-8'); sw=sw_path.read_text(encoding='utf-8')

def block(text, marker):
    s=text.index(marker); e=text.index('\n        function ',s+len(marker)); return text[s:e]
services_before=block(app,'        function renderizarServicos() {')
persist_before=block(app,'        function _guardarEdicaoPontoRegisto(regId) {')
repair_before=block(app,'        function _repararEntradasPresas() {')

old='''            const totalHoras = window.TotalGestAttendanceView.calculateWeeklyAttendanceTotal(_registrosSemana, {
                today: getDataHoje(),
                nowTime: new Date().toTimeString().slice(0, 5),
                calculateHours: calcularHoras
            });
            const _alvoSem = window.TotalGestAttendanceView.attendanceWeeklyTarget(
                usuarioLogado,
                dados.funcionarios || [],
                dados.encarregados || []
            );
            document.getElementById('saldoHoras').textContent = window.TotalGestAttendanceView.attendanceWeeklyBalanceLabel(totalHoras, _alvoSem);

            // A partir daqui, mostra o dia (ou semana) selecionado nos filtros, organizado por
            // pessoa (acordeão) — antes era sempre fixo no dia de hoje.
            const navigationState = window.TotalGestAttendanceView.prepareAttendanceNavigation(registros, {
                selectedDate: _pontoNavData,
                today: getDataHoje(),
                mode: _pontoNavModo
            });
            _pontoNavData = navigationState.selectedDate;
            const _hojeSoP = navigationState.selectedDate;
            const contAcc = attendanceElements.accordion;
            const porPessoa = navigationState.groupedRecords;
            const agoraHM = new Date().toTimeString().slice(0, 5);
            const timingConfig = window.TotalGestAttendanceView.attendanceTimingConfig(adminAtual());
            const _horaEsperada = timingConfig.expectedTime;
            const _tolerMin = timingConfig.toleranceMinutes;
            const _limiteAtraso = timingConfig.lateLimit;'''
new='''            const attendanceViewState = window.TotalGestAttendanceView.prepareAttendanceViewState({
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
            });
            document.getElementById('saldoHoras').textContent = attendanceViewState.weeklyBalanceLabel;
            _pontoNavData = attendanceViewState.selectedDate;
            const _hojeSoP = attendanceViewState.selectedDate;
            const porPessoa = attendanceViewState.groupedRecords;
            const agoraHM = attendanceViewState.nowTime;
            const _horaEsperada = attendanceViewState.expectedTime;
            const _tolerMin = attendanceViewState.toleranceMinutes;
            const _limiteAtraso = attendanceViewState.lateLimit;'''
assert app.count(old)==1,app.count(old); app=app.replace(old,new,1)

marker='  window.TotalGestAttendanceView = {'
helper='''  function prepareAttendanceViewState(options) {
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
    return {
      weeklyBalanceLabel: attendanceWeeklyBalanceLabel(totalHours, weeklyTarget),
      selectedDate: navigation.selectedDate,
      groupedRecords: navigation.groupedRecords,
      nowTime,
      expectedTime: timing.expectedTime,
      toleranceMinutes: timing.toleranceMinutes,
      lateLimit: timing.lateLimit
    };
  }

'''
assert view.count(marker)==1; view=view.replace(marker,helper+marker,1)
oldexp='''    prepareAttendancePeriods,
    prepareAttendanceBaseState
  };'''
newexp='''    prepareAttendancePeriods,
    prepareAttendanceBaseState,
    prepareAttendanceViewState
  };'''
assert view.count(oldexp)==1; view=view.replace(oldexp,newexp,1)
assert "const CACHE = 'totalgest-v162';" in sw; sw=sw.replace("const CACHE = 'totalgest-v162';","const CACHE = 'totalgest-v163';",1)
app_path.write_text(app,encoding='utf-8'); view_path.write_text(view,encoding='utf-8'); sw_path.write_text(sw,encoding='utf-8')
assert block(app,'        function renderizarServicos() {')==services_before
assert block(app,'        function _guardarEdicaoPontoRegisto(regId) {')==persist_before
assert block(app,'        function _repararEntradasPresas() {')==repair_before
p=block(app,'        function renderizarPonto() {')
assert p.count('prepareAttendanceViewState({')==1
for x in ['calculateWeeklyAttendanceTotal(_registrosSemana, {','attendanceWeeklyTarget(','attendanceWeeklyBalanceLabel(totalHoras, _alvoSem)','prepareAttendanceNavigation(registros, {','attendanceTimingConfig(adminAtual())']:
    assert x not in p,x
assert p.count('const _ausenciaHoje = _funcionarioAusenteEm(fid, _hojeSoP);')==1
assert 'guardarDados(dados)' not in p
print('SAFE_CUTS=4'); print('SERVICES_BLOCK_UNCHANGED=OK'); print('POINT_PERSISTENCE_UNCHANGED=OK'); print('POINT_REPAIR_UNCHANGED=OK'); print('RENDER_PONTO_AFTER_CHARS=',len(p)); print('RENDER_PONTO_AFTER_LINES=',p.count('\n')+1); print('STRUCTURE=OK')
