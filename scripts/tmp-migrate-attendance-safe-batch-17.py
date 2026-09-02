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
point_marker = '        function renderizarPonto() {'
services_before = function_block(app, services_marker)
persist_before = function_block(app, persist_marker)
repair_before = function_block(app, repair_marker)

old_filter = '''            if (usuarioLogado && usuarioLogado.role === 'admin') {
                registros = registros.filter(p => p.adminId === _tenantId());
            } else if (usuarioLogado && (usuarioLogado.role === 'encarregado' || usuarioLogado.role === 'funcionario' || usuarioLogado.role === 'vendedor' || usuarioLogado.role === 'vigilante' || usuarioLogado.role === 'supervisor_vigilantes')) {
                registros = registros.filter(p => p.funcionarioId === usuarioLogado.id);
            } else {
                registros = [];
            }'''
new_filter = '''            registros = window.TotalGestAttendanceView.filterAttendanceRecordsForViewer(
                registros,
                usuarioLogado,
                _tenantId()
            );'''
assert app.count(old_filter) == 1, app.count(old_filter)
app = app.replace(old_filter, new_filter, 1)

old_recent = '''            const _wsP = _inicioSemana();
            const _hojeMes = new Date();
            const _msP = new Date(_hojeMes.getFullYear(), _hojeMes.getMonth() - 1, 1); // início do mês ANTERIOR — mostra o mês corrente + o mês anterior (antes só mostrava o corrente, e picar uma data de outro mês no calendário ficava sempre vazio)'''
new_recent = '''            const _wsP = _inicioSemana();
            const _msP = window.TotalGestAttendanceView.attendanceRecentStart(new Date()); // início do mês ANTERIOR — mostra o mês corrente + o mês anterior'''
assert app.count(old_recent) == 1, app.count(old_recent)
app = app.replace(old_recent, new_recent, 1)

old_week = '''            let totalHoras = 0;
            const _hojeP = getDataHoje();
            const _agoraP = new Date().toTimeString().slice(0, 5);
            // As picagens "geral" (sem OS/obra associada) e as de obra de longa duração (_ehObraLonga)
            // contam para o total de horas. As picagens de OS dentro de dados.ponto (com servicoId)
            // são visitas pontuais registadas DENTRO do mesmo período da picagem geral (nested) —
            // somá-las também duplicava o tempo já contado na geral, tal como já estava corrigido
            // no relatório de Assiduidade.
            _registrosSemana.forEach(p => {
                // NOTA: "pausaAlmoco: true" não significa "não contar" — marca que a SAÍDA deste
                // registo foi para ir almoçar. O intervalo entrada→saída continua a ser trabalho
                // real (ex: a manhã toda, 08:02→12:00) e tem de ser contado, tal como já é feito
                // no resumo do admin. Excluí-lo aqui estava a descontar a manhã inteira a quem já
                // tinha ido almoçar — só neste ecrã do próprio funcionário, nunca no do admin.
                if (!(p._ehObraLonga || (!p.servicoId && !p.obraId))) return;
                if (p.entrada && p.saida) totalHoras += calcularHoras(p.entrada, p.saida);
                else if (p.data === _hojeP && p.entrada && !p.saida) totalHoras += calcularHoras(p.entrada, _agoraP);
            });
            const horasInt = Math.floor(totalHoras);
            const minutos = Math.round((totalHoras - horasInt) * 60);
            let _alvoSem = null;
            if (usuarioLogado?.role === 'funcionario' || usuarioLogado?.role === 'vendedor') { const _f = dados.funcionarios?.find(x => x.id === usuarioLogado.id); _alvoSem = (_f?.horasSemanais) || 40; }
            else if (usuarioLogado?.role === 'encarregado') { const _e = dados.encarregados?.find(x => x.id === usuarioLogado.id); _alvoSem = (_e?.horasSemanais) || 40; }
            document.getElementById('saldoHoras').textContent = _alvoSem != null
                ? `Horas esta semana: ${horasInt}h ${minutos}m / ${_alvoSem}h`
                : `Horas esta semana: ${horasInt}h ${minutos}m`;'''
new_week = '''            const totalHoras = window.TotalGestAttendanceView.calculateWeeklyAttendanceTotal(_registrosSemana, {
                today: getDataHoje(),
                nowTime: new Date().toTimeString().slice(0, 5),
                calculateHours: calcularHoras
            });
            const _alvoSem = window.TotalGestAttendanceView.attendanceWeeklyTarget(
                usuarioLogado,
                dados.funcionarios || [],
                dados.encarregados || []
            );
            document.getElementById('saldoHoras').textContent = window.TotalGestAttendanceView.attendanceWeeklyBalanceLabel(totalHoras, _alvoSem);'''
assert app.count(old_week) == 1, app.count(old_week)
app = app.replace(old_week, new_week, 1)

insert_marker = '  window.TotalGestAttendanceView = {'
assert view.count(insert_marker) == 1
helpers = '''  function filterAttendanceRecordsForViewer(records, user, tenantId) {
    const list = Array.isArray(records) ? records : [];
    if (user && user.role === 'admin') {
      return list.filter(function (record) { return record.adminId === tenantId; });
    }
    if (user && ['encarregado', 'funcionario', 'vendedor', 'vigilante', 'supervisor_vigilantes'].includes(user.role)) {
      return list.filter(function (record) { return record.funcionarioId === user.id; });
    }
    return [];
  }

  function attendanceRecentStart(value) {
    const date = value instanceof Date ? value : new Date(value);
    return new Date(date.getFullYear(), date.getMonth() - 1, 1);
  }

  function calculateWeeklyAttendanceTotal(records, options) {
    const o = options || {};
    const calculate = typeof o.calculateHours === 'function' ? o.calculateHours : function () { return 0; };
    return (Array.isArray(records) ? records : []).reduce(function (total, record) {
      if (!(record && (record._ehObraLonga || (!record.servicoId && !record.obraId)))) return total;
      if (record.entrada && record.saida) return total + calculate(record.entrada, record.saida);
      if (record.data === o.today && record.entrada && !record.saida) return total + calculate(record.entrada, o.nowTime);
      return total;
    }, 0);
  }

  function attendanceWeeklyTarget(user, employees, managers) {
    if (!user) return null;
    if (user.role === 'funcionario' || user.role === 'vendedor') {
      const person = (Array.isArray(employees) ? employees : []).find(function (item) { return item.id === user.id; });
      return (person && person.horasSemanais) || 40;
    }
    if (user.role === 'encarregado') {
      const person = (Array.isArray(managers) ? managers : []).find(function (item) { return item.id === user.id; });
      return (person && person.horasSemanais) || 40;
    }
    return null;
  }

  function attendanceWeeklyBalanceLabel(totalHours, weeklyTarget) {
    const total = Number(totalHours || 0);
    const hours = Math.floor(total);
    const minutes = Math.round((total - hours) * 60);
    return weeklyTarget != null
      ? `Horas esta semana: ${hours}h ${minutes}m / ${weeklyTarget}h`
      : `Horas esta semana: ${hours}h ${minutes}m`;
  }

'''
view = view.replace(insert_marker, helpers + insert_marker, 1)

old_exports = '''    attendancePersonPresentation,
    attendancePersonRows,
    prepareAttendanceAccordionPerson
  };'''
new_exports = '''    attendancePersonPresentation,
    attendancePersonRows,
    prepareAttendanceAccordionPerson,
    filterAttendanceRecordsForViewer,
    attendanceRecentStart,
    calculateWeeklyAttendanceTotal,
    attendanceWeeklyTarget,
    attendanceWeeklyBalanceLabel
  };'''
assert view.count(old_exports) == 1, view.count(old_exports)
view = view.replace(old_exports, new_exports, 1)

assert "const CACHE = 'totalgest-v159';" in sw
sw = sw.replace("const CACHE = 'totalgest-v159';", "const CACHE = 'totalgest-v160';", 1)

app_path.write_text(app, encoding='utf-8')
view_path.write_text(view, encoding='utf-8')
sw_path.write_text(sw, encoding='utf-8')

app_after = app_path.read_text(encoding='utf-8')
assert function_block(app_after, services_marker) == services_before
assert function_block(app_after, persist_marker) == persist_before
assert function_block(app_after, repair_marker) == repair_before
point = function_block(app_after, point_marker)
for item in ['filterAttendanceRecordsForViewer(','attendanceRecentStart(new Date())','calculateWeeklyAttendanceTotal(_registrosSemana, {','attendanceWeeklyTarget(','attendanceWeeklyBalanceLabel(totalHoras, _alvoSem)']:
    assert point.count(item) == 1, (item, point.count(item))
for old in ["registros = registros.filter(p => p.adminId === _tenantId());","const _hojeMes = new Date();","let totalHoras = 0;","_registrosSemana.forEach(p => {","const horasInt = Math.floor(totalHoras);","let _alvoSem = null;"]:
    assert old not in point, old
assert point.count('const _ausenciaHoje = _funcionarioAusenteEm(fid, _hojeSoP);') == 1
print('SAFE_CUTS=5')
print('SERVICES_BLOCK_UNCHANGED=OK')
print('POINT_PERSISTENCE_UNCHANGED=OK')
print('POINT_REPAIR_UNCHANGED=OK')
print('POINT_ABSENCE_LOOKUP_PRESERVED=OK')
print('RENDER_PONTO_AFTER_CHARS=', len(point))
print('RENDER_PONTO_AFTER_LINES=', point.count('\n') + 1)
print('STRUCTURE=OK')
