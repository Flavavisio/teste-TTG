from pathlib import Path

app_path = Path('app.html')
view_path = Path('assets/js/app-attendance-view.js')
sw_path = Path('sw.js')

app = app_path.read_text(encoding='utf-8')
view = view_path.read_text(encoding='utf-8')
sw = sw_path.read_text(encoding='utf-8')

services_marker = '        function renderizarServicos() {'
services_start = app.index(services_marker)
services_end = app.index('\n        function ', services_start + len(services_marker))
services_before = app[services_start:services_end]

point_marker = '        function renderizarPonto() {'
point_start = app.index(point_marker)
point_end = app.index('\n        function ', point_start + len(point_marker))
point_before = app[point_start:point_end]

persist_marker = '        function _guardarEdicaoPontoRegisto(regId) {'
persist_start = app.index(persist_marker)
persist_end = app.index('\n        function ', persist_start + len(persist_marker))
persist_before = app[persist_start:persist_end]

repair_marker = '        function _repararEntradasPresas() {'
repair_start = app.index(repair_marker)
repair_end = app.index('\n        function ', repair_start + len(repair_marker))
repair_before = app[repair_start:repair_end]

old_move = '''        function _pontoAccMover(direcao) {
            if (!_pontoNavData) _pontoNavData = getDataHoje();
            const [a, m, d] = _pontoNavData.split('-').map(Number);
            const dt = new Date(Date.UTC(a, m - 1, d));
            dt.setUTCDate(dt.getUTCDate() + direcao * (_pontoNavModo === 'semana' ? 7 : 1));
            const novaData = dt.getUTCFullYear() + '-' + String(dt.getUTCMonth() + 1).padStart(2, '0') + '-' + String(dt.getUTCDate()).padStart(2, '0');
            if (direcao > 0 && novaData > getDataHoje()) return; // nunca avança para o futuro
            _pontoNavData = novaData;
            renderizarPonto();
        }'''
new_move = '''        function _pontoAccMover(direcao) {
            if (!_pontoNavData) _pontoNavData = getDataHoje();
            const novaData = window.TotalGestAttendanceView.moveNavigationDate({
                value: _pontoNavData,
                direction: direcao,
                mode: _pontoNavModo,
                today: getDataHoje()
            });
            if (!novaData) return;
            _pontoNavData = novaData;
            renderizarPonto();
        }'''
assert app.count(old_move) == 1
app = app.replace(old_move, new_move, 1)

old_controls = '''        function _pontoAccAtualizarControlos() {
            const wrap = document.getElementById('pontoAccNavControlos');
            if (!wrap) return;
            // Estes controlos (Dia/Semana, avançar/recuar) já eram exclusivos do admin/subadmin,
            // mas o funcionário/encarregado/vendedor também deve poder navegar dia a dia pelo seu
            // PRÓPRIO histórico mensal — os dados já vêm filtrados só à pessoa mais acima nesta
            // função (renderizarPonto), por isso é seguro mostrar isto a todos os papéis que picam ponto.
            const _rNav = usuarioLogado?.role;
            if (!['admin', 'subadmin', 'funcionario', 'encarregado', 'vendedor'].includes(_rNav)) { wrap.style.display = 'none'; return; }
            wrap.style.display = 'flex';
            if (!_pontoNavData) _pontoNavData = getDataHoje();
            document.getElementById('pontoNavBtnDia')?.classList.toggle('ativo', _pontoNavModo !== 'semana');
            document.getElementById('pontoNavBtnSemana')?.classList.toggle('ativo', _pontoNavModo === 'semana');
            const lbl = document.getElementById('pontoNavLabel');
            if (lbl) {
                const [a, m, d] = _pontoNavData.split('-').map(Number);
                const dt = new Date(Date.UTC(a, m - 1, d));
                if (_pontoNavModo === 'semana') {
                    const inicioSem = new Date(dt); inicioSem.setUTCDate(dt.getUTCDate() - (dt.getUTCDay() === 0 ? 6 : dt.getUTCDay() - 1));
                    const fimSem = new Date(inicioSem); fimSem.setUTCDate(inicioSem.getUTCDate() + 6);
                    lbl.textContent = `${inicioSem.getUTCDate()}/${inicioSem.getUTCMonth() + 1} a ${fimSem.getUTCDate()}/${fimSem.getUTCMonth() + 1}`;
                } else {
                    lbl.textContent = dt.toLocaleDateString('pt-PT', { weekday: 'long', day: '2-digit', month: '2-digit', year: 'numeric', timeZone: 'UTC' });
                }
            }
            const btnSeg = document.getElementById('pontoNavBtnSeguinte');
            if (btnSeg) btnSeg.disabled = _pontoNavData >= getDataHoje();
        }'''
new_controls = '''        function _pontoAccAtualizarControlos() {
            const wrap = document.getElementById('pontoAccNavControlos');
            if (!wrap) return;
            // Estes controlos (Dia/Semana, avançar/recuar) já eram exclusivos do admin/subadmin,
            // mas o funcionário/encarregado/vendedor também deve poder navegar dia a dia pelo seu
            // PRÓPRIO histórico mensal — os dados já vêm filtrados só à pessoa mais acima nesta
            // função (renderizarPonto), por isso é seguro mostrar isto a todos os papéis que picam ponto.
            const _rNav = usuarioLogado?.role;
            if (!window.TotalGestAttendanceView.canNavigateAttendance(_rNav)) { wrap.style.display = 'none'; return; }
            wrap.style.display = 'flex';
            if (!_pontoNavData) _pontoNavData = getDataHoje();
            document.getElementById('pontoNavBtnDia')?.classList.toggle('ativo', _pontoNavModo !== 'semana');
            document.getElementById('pontoNavBtnSemana')?.classList.toggle('ativo', _pontoNavModo === 'semana');
            const lbl = document.getElementById('pontoNavLabel');
            if (lbl) lbl.textContent = window.TotalGestAttendanceView.attendanceNavigationLabel(_pontoNavData, _pontoNavModo);
            const btnSeg = document.getElementById('pontoNavBtnSeguinte');
            if (btnSeg) btnSeg.disabled = window.TotalGestAttendanceView.isAttendanceNextDisabled(_pontoNavData, getDataHoje());
        }'''
assert app.count(old_controls) == 1
app = app.replace(old_controls, new_controls, 1)

insert_marker = '  window.TotalGestAttendanceView = {'
assert view.count(insert_marker) == 1
helpers = '''  function moveNavigationDate(options) {
    const o = options || {};
    const value = o.value || o.today;
    if (!value) return null;
    const parts = String(value).split('-').map(Number);
    const dt = new Date(Date.UTC(parts[0], parts[1] - 1, parts[2]));
    dt.setUTCDate(dt.getUTCDate() + Number(o.direction || 0) * (o.mode === 'semana' ? 7 : 1));
    const next = dt.getUTCFullYear() + '-' + String(dt.getUTCMonth() + 1).padStart(2, '0') + '-' + String(dt.getUTCDate()).padStart(2, '0');
    if (Number(o.direction || 0) > 0 && o.today && next > o.today) return null;
    return next;
  }

  function canNavigateAttendance(role) {
    return ['admin', 'subadmin', 'funcionario', 'encarregado', 'vendedor'].includes(role);
  }

  function attendanceNavigationLabel(value, mode) {
    const parts = String(value || '').split('-').map(Number);
    const dt = new Date(Date.UTC(parts[0], parts[1] - 1, parts[2]));
    if (mode === 'semana') {
      const start = new Date(dt);
      start.setUTCDate(dt.getUTCDate() - (dt.getUTCDay() === 0 ? 6 : dt.getUTCDay() - 1));
      const end = new Date(start);
      end.setUTCDate(start.getUTCDate() + 6);
      return `${start.getUTCDate()}/${start.getUTCMonth() + 1} a ${end.getUTCDate()}/${end.getUTCMonth() + 1}`;
    }
    return dt.toLocaleDateString('pt-PT', { weekday: 'long', day: '2-digit', month: '2-digit', year: 'numeric', timeZone: 'UTC' });
  }

  function isAttendanceNextDisabled(value, today) {
    return String(value || '') >= String(today || '');
  }

'''
view = view.replace(insert_marker, helpers + insert_marker, 1)

old_exports = '''    startOfWeekMonday,
    formatHours,
    teamSummaryRow,
    teamSummaryCard'''
new_exports = '''    startOfWeekMonday,
    formatHours,
    teamSummaryRow,
    teamSummaryCard,
    moveNavigationDate,
    canNavigateAttendance,
    attendanceNavigationLabel,
    isAttendanceNextDisabled'''
assert view.count(old_exports) == 1
view = view.replace(old_exports, new_exports, 1)

assert "const CACHE = 'totalgest-v151';" in sw
sw = sw.replace("const CACHE = 'totalgest-v151';", "const CACHE = 'totalgest-v152';", 1)

app_path.write_text(app, encoding='utf-8')
view_path.write_text(view, encoding='utf-8')
sw_path.write_text(sw, encoding='utf-8')

app_after = app_path.read_text(encoding='utf-8')
services_start_after = app_after.index(services_marker)
services_end_after = app_after.index('\n        function ', services_start_after + len(services_marker))
assert app_after[services_start_after:services_end_after] == services_before
point_start_after = app_after.index(point_marker)
point_end_after = app_after.index('\n        function ', point_start_after + len(point_marker))
assert app_after[point_start_after:point_end_after] == point_before
persist_start_after = app_after.index(persist_marker)
persist_end_after = app_after.index('\n        function ', persist_start_after + len(persist_marker))
assert app_after[persist_start_after:persist_end_after] == persist_before
repair_start_after = app_after.index(repair_marker)
repair_end_after = app_after.index('\n        function ', repair_start_after + len(repair_marker))
assert app_after[repair_start_after:repair_end_after] == repair_before

print('SAFE_CUTS=4')
print('SERVICES_BLOCK_UNCHANGED=OK')
print('RENDER_PONTO_UNCHANGED=OK')
print('POINT_PERSISTENCE_UNCHANGED=OK')
print('POINT_REPAIR_UNCHANGED=OK')
print('STRUCTURE=OK')
