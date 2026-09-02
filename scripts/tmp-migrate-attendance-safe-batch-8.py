from pathlib import Path

app_path = Path('app.html')
shell_path = Path('assets/js/app-shell.js')
view_path = Path('assets/js/app-attendance-view.js')
sw_path = Path('sw.js')

app = app_path.read_text(encoding='utf-8')
services_marker = '        function renderizarServicos() {'
services_start = app.index(services_marker)
services_end = app.index('\n        function ', services_start + len(services_marker))
services_before = app[services_start:services_end]

point_marker = '        function renderizarResumoPontoAdmin() {'
point_start = app.index(point_marker)
point_end = app.index('\n        // ---------- Navegador de picagens', point_start)
point_before = app[point_start:point_end]
controls_count_before = point_before.count('_pontoAccAtualizarControlos();')

module = r'''/* Total Gest — apresentação do resumo de registo de ponto */
(function () {
  'use strict';

  function startOfWeekMonday(value) {
    const x = value instanceof Date ? new Date(value.getTime()) : new Date();
    const dow = (x.getDay() + 6) % 7;
    x.setHours(0, 0, 0, 0);
    x.setDate(x.getDate() - dow);
    return x;
  }

  function formatHours(h) {
    if (!h || h <= 0) return '0h 0m';
    const hi = Math.floor(h);
    const mi = Math.round((h - hi) * 60);
    return `${hi}h ${mi}m`;
  }

  function teamSummaryRow(options) {
    const o = options || {};
    return `<tr>
                    <td>${o.name} <span style="color:#94a3b8;font-size:.8em;">(${o.type})</span></td>
                    <td>${o.appBadge}</td>
                    <td>${o.serviceBadge}</td>
                    <td>${o.workplace}</td>
                    <td>${formatHours(o.hoursToday)}</td>
                    <td>${formatHours(o.hoursWeek)} <span style="color:#94a3b8;font-size:.8em;">/ ${o.contractedHours}h</span></td>
                    <td style="font-weight:700;color:${o.balance >= 0 ? '#16a34a' : '#dc2626'};">${o.balanceText}</td>
                </tr>`;
  }

  function teamSummaryCard(options) {
    const o = options || {};
    const peopleCount = Number(o.peopleCount || 0);
    const inServiceCount = Number(o.inServiceCount || 0);
    return `
                <div class="report-card">
                    <h4><i class="fas fa-users"></i> Estado da equipa — ${inServiceCount} em serviço · ${peopleCount - inServiceCount} fora</h4>
                    ${peopleCount ? `<div class="table-wrapper"><table>
                        <thead><tr><th>Pessoa</th><th>Na app</th><th>Estado</th><th>Obra atual</th><th>Horas hoje</th><th>Esta semana</th><th>Saldo (semana)</th></tr></thead>
                        <tbody>${o.rowsHtml || ''}</tbody></table></div>
                        <p style="color:#94a3b8;font-size:.82rem;margin-top:8px;">Saldo = horas trabalhadas esta semana menos as horas semanais contratadas.</p>`
                      : '<p style="color:#64748b;">Sem funcionários ou encarregados.</p>'}
                </div>`;
  }

  window.TotalGestAttendanceView = {
    startOfWeekMonday,
    formatHours,
    teamSummaryRow,
    teamSummaryCard
  };
})();
'''
assert not view_path.exists(), 'attendance view already exists'
view_path.write_text(module, encoding='utf-8')

old_start_week = """        function _inicioSemana() {
            const x = new Date(); const dow = (x.getDay() + 6) % 7; // 0 = segunda
            x.setHours(0, 0, 0, 0); x.setDate(x.getDate() - dow); return x;
        }
"""
new_start_week = """        function _inicioSemana() {
            return window.TotalGestAttendanceView.startOfWeekMonday();
        }
"""
assert app.count(old_start_week) == 1
app = app.replace(old_start_week, new_start_week, 1)

old_fmt = """        function _fmtH(h) {
            if (!h || h <= 0) return '0h 0m';
            const hi = Math.floor(h); const mi = Math.round((h - hi) * 60);
            return `${hi}h ${mi}m`;
        }
"""
new_fmt = """        function _fmtH(h) {
            return window.TotalGestAttendanceView.formatHours(h);
        }
"""
assert app.count(old_fmt) == 1
app = app.replace(old_fmt, new_fmt, 1)

old_row = """                return `<tr>
                    <td>${p.nome} <span style=\"color:#94a3b8;font-size:.8em;\">(${p.tipo})</span></td>
                    <td>${appBadge}</td>
                    <td>${estadoBadge}</td>
                    <td>${obra}</td>
                    <td>${_fmtH(horasHoje)}</td>
                    <td>${_fmtH(horasSemana)} <span style=\"color:#94a3b8;font-size:.8em;\">/ ${p.horas || 0}h</span></td>
                    <td style=\"font-weight:700;color:${saldo >= 0 ? '#16a34a' : '#dc2626'};\">${saldoTxt}</td>
                </tr>`;
"""
new_row = """                return window.TotalGestAttendanceView.teamSummaryRow({
                    name: p.nome,
                    type: p.tipo,
                    appBadge,
                    serviceBadge: estadoBadge,
                    workplace: obra,
                    hoursToday: horasHoje,
                    hoursWeek: horasSemana,
                    contractedHours: p.horas || 0,
                    balance: saldo,
                    balanceText: saldoTxt
                });
"""
assert app.count(old_row) == 1
app = app.replace(old_row, new_row, 1)

old_card = """            cont.innerHTML = `
                <div class=\"report-card\">
                    <h4><i class=\"fas fa-users\"></i> Estado da equipa — ${emServicoN} em serviço · ${pessoas.length - emServicoN} fora</h4>
                    ${pessoas.length ? `<div class=\"table-wrapper\"><table>
                        <thead><tr><th>Pessoa</th><th>Na app</th><th>Estado</th><th>Obra atual</th><th>Horas hoje</th><th>Esta semana</th><th>Saldo (semana)</th></tr></thead>
                        <tbody>${linhas}</tbody></table></div>
                        <p style=\"color:#94a3b8;font-size:.82rem;margin-top:8px;\">Saldo = horas trabalhadas esta semana menos as horas semanais contratadas.</p>`
                      : '<p style=\"color:#64748b;\">Sem funcionários ou encarregados.</p>'}
                </div>`;
"""
new_card = """            cont.innerHTML = window.TotalGestAttendanceView.teamSummaryCard({
                inServiceCount: emServicoN,
                peopleCount: pessoas.length,
                rowsHtml: linhas
            });
"""
assert app.count(old_card) == 1
app = app.replace(old_card, new_card, 1)
app_path.write_text(app, encoding='utf-8')

shell = shell_path.read_text(encoding='utf-8')
shell_anchor = "    servicesView: './assets/js/app-services-view.js',\n"
assert shell.count(shell_anchor) == 1
assert 'app-attendance-view.js' not in shell
shell = shell.replace(shell_anchor, shell_anchor + "    attendanceView: './assets/js/app-attendance-view.js',\n", 1)
shell_path.write_text(shell, encoding='utf-8')

sw = sw_path.read_text(encoding='utf-8')
assert sw.count("const CACHE = 'totalgest-v150';") == 1
sw_anchor = "    './assets/js/app-services-view.js',\n"
assert sw.count(sw_anchor) == 1
assert 'app-attendance-view.js' not in sw
sw = sw.replace("const CACHE = 'totalgest-v150';", "const CACHE = 'totalgest-v151';", 1)
sw = sw.replace(sw_anchor, sw_anchor + "    './assets/js/app-attendance-view.js',\n", 1)
sw_path.write_text(sw, encoding='utf-8')

final = app_path.read_text(encoding='utf-8')
services_start = final.index(services_marker)
services_end = final.index('\n        function ', services_start + len(services_marker))
assert final[services_start:services_end] == services_before

point_start = final.index(point_marker)
point_end = final.index('\n        // ---------- Navegador de picagens', point_start)
point_after = final[point_start:point_end]
assert point_after.count('_pontoAccAtualizarControlos();') == controls_count_before
for item in [
    'window.TotalGestAttendanceView.startOfWeekMonday()',
    'window.TotalGestAttendanceView.formatHours(h)',
    'window.TotalGestAttendanceView.teamSummaryRow({',
    'window.TotalGestAttendanceView.teamSummaryCard({'
]:
    assert final.count(item) >= 1, (item, final.count(item))
for old in [
    'const x = new Date(); const dow = (x.getDay() + 6) % 7;',
    "const hi = Math.floor(h); const mi = Math.round((h - hi) * 60);",
    'return `<tr>\n                    <td>${p.nome}',
    'cont.innerHTML = `\n                <div class="report-card">'
]:
    assert old not in point_after and old not in final, old

# A lógica de cálculo de horas e presença continua no app.
for item in [
    'const contaParaTotal = x => x._ehObraLonga || (!x.servicoId && !x.obraId);',
    'if (x.entrada && x.saida) horasHoje += calcularHoras(x.entrada, x.saida);',
    'if (x.entrada && x.saida) horasSemana += calcularHoras(x.entrada, x.saida);',
    'const naApp = p.atividade && (Date.now() - p.atividade) < LIMITE_ONLINE_MS;'
]:
    assert point_after.count(item) == 1, (item, point_after.count(item))

print('SAFE_CUTS=4')
print('SERVICES_BLOCK_UNCHANGED=OK')
print('POINT_CALCULATION_UNCHANGED=OK')
print('STRUCTURE=OK')
