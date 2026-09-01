from pathlib import Path

APP = Path('app.html')
VIEW = Path('assets/js/app-reports-view.js')
SW = Path('sw.js')

app = APP.read_text(encoding='utf-8')
view = VIEW.read_text(encoding='utf-8')
sw = SW.read_text(encoding='utf-8')


def reports_region(text):
    start = text.index('        function renderizarReports() {')
    end = text.index('\n        function ', start + 1)
    return start, end, text[start:end]


protected = {
    'bootstrapSupabase()': app.count('bootstrapSupabase()'),
    'supabase.auth': app.count('supabase.auth'),
    'window.TotalGestReportsDistributorMetrics.calculateAdminOverview({': app.count('window.TotalGestReportsDistributorMetrics.calculateAdminOverview({'),
    'window.TotalGestReportsDistributorMetrics.calculateAdminContracts({': app.count('window.TotalGestReportsDistributorMetrics.calculateAdminContracts({'),
    'window.TotalGestReportsDistributorMetrics.calculateAdminOperations({': app.count('window.TotalGestReportsDistributorMetrics.calculateAdminOperations({'),
}

start, end, reports = reports_region(app)
template_start = '''            container.innerHTML = `
                    <div class="report-card">
                        <h4><i class="fas fa-users"></i> Recursos Humanos</h4>'''
template_end = '''                `;'''
assert reports.count(template_start) == 1, reports.count(template_start)
start_rel = reports.index(template_start)
end_rel = reports.index(template_end, start_rel) + len(template_end)
old_template = reports[start_rel:end_rel]
assert old_template.count('<div class="report-card">') == 9, old_template.count('<div class="report-card">')
assert 'Suporte Técnico' in old_template

replacement = '''            container.innerHTML = window.TotalGestReportsView.adminOverviewCards({
                totalFunc: totalFunc,
                totalEncarregados: totalEncarregados,
                totalCli: totalCli,
                gastoFunc: eur(gastoFunc),
                gastoEnc: eur(gastoEnc),
                gastoTotal: eur(gastoTotal),
                totalOS: totalOS,
                osPendentes: osPendentes,
                osAndamento: osAndamento,
                osConcluidas: osConcluidas,
                totalPonto: totalPonto,
                totalPedidos: totalPedidos,
                pedPend: pedPend,
                totalFolhas: totalFolhas,
                folhasOT: folhasOT,
                totalReqs: totalReqs,
                reqPend: reqPend,
                moduloAtivoTxt: moduloAtivoTxt,
                contratosCount: contratosAdmin.length,
                ctEmDia: ctEmDia,
                ctAVencer: ctAVencer,
                ctVencidos: ctVencidos,
                totalLocais: totalLocais,
                totalEquip: totalEquip,
                totalRegistos: totalRegistos,
                ctValor: eur(ctValor),
                frotaTotal: frotaStats.total,
                frotaEmDia: frotaStats.emDia,
                frotaAVencer: frotaStats.aVencer,
                frotaVencido: frotaStats.vencido,
                totalIntervencoes: totalIntervencoes,
                totalSinistros: totalSinistros,
                gastoVeiculos: eur(gastoVeiculos),
                suporteTotal: ajudasAdmin.length,
                ajPend: ajPend,
                ajConcl: ajConcl
            });'''

reports = reports[:start_rel] + replacement + reports[end_rel:]
app = app[:start] + reports + app[end:]

view_anchor = '  window.TotalGestReportsView = {\n'
assert view.count(view_anchor) == 1
admin_view = '''  function adminOverviewCards(options) {
    options = options || {};
    return `
                    <div class="report-card">
                        <h4><i class="fas fa-users"></i> Recursos Humanos</h4>
                        <div class="report-item"><span>Total de Funcionários</span><span>${options.totalFunc}</span></div>
                        <div class="report-item"><span>Total de Encarregados</span><span>${options.totalEncarregados}</span></div>
                        <div class="report-item"><span>Total de Clientes</span><span>${options.totalCli}</span></div>
                        <div class="report-item"><span>Gasto com Funcionários (bruto)</span><span>${options.gastoFunc}</span></div>
                        <div class="report-item"><span>Gasto com Encarregados (bruto)</span><span>${options.gastoEnc}</span></div>
                        <div class="report-item" style="font-weight:bold; border-top:1px solid #e2e8f0; padding-top:8px;"><span>Gasto Total com Pessoal</span><span>${options.gastoTotal}</span></div>
                    </div>
                    <div class="report-card">
                        <h4><i class="fas fa-tools"></i> Ordens de Serviço</h4>
                        <div class="report-item"><span>Total</span><span>${options.totalOS}</span></div>
                        <div class="report-item"><span>Pendentes</span><span>${options.osPendentes}</span></div>
                        <div class="report-item"><span>Em andamento</span><span>${options.osAndamento}</span></div>
                        <div class="report-item"><span>Concluídas</span><span>${options.osConcluidas}</span></div>
                    </div>
                    <div class="report-card">
                        <h4><i class="fas fa-clock"></i> Assiduidade</h4>
                        <div class="report-item"><span>Total de registos de ponto</span><span>${options.totalPonto}</span></div>
                    </div>
                    <div class="report-card">
                        <h4><i class="fas fa-calendar-check"></i> Férias / Faltas</h4>
                        <div class="report-item"><span>Total de pedidos</span><span>${options.totalPedidos}</span></div>
                        <div class="report-item"><span>Pendentes</span><span>${options.pedPend}</span></div>
                    </div>
                    <div class="report-card">
                        <h4><i class="fas fa-clipboard-list"></i> Folhas de Obra</h4>
                        <div class="report-item"><span>Total</span><span>${options.totalFolhas}</span></div>
                        <div class="report-item"><span>Ordens de trabalho de manutenção</span><span>${options.folhasOT}</span></div>
                    </div>
                    <div class="report-card">
                        <h4><i class="fas fa-boxes"></i> Requisições</h4>
                        <div class="report-item"><span>Total</span><span>${options.totalReqs}</span></div>
                        <div class="report-item"><span>Pendentes</span><span>${options.reqPend}</span></div>
                    </div>
                    <div class="report-card">
                        <h4><i class="fas fa-file-signature"></i> Contratos de Manutenção</h4>
                        <div class="report-item"><span>Módulo</span><span>${options.moduloAtivoTxt}</span></div>
                        <div class="report-item"><span>Total de contratos</span><span>${options.contratosCount}</span></div>
                        <div class="report-item"><span>Em dia</span><span style="color:#16a34a;">${options.ctEmDia}</span></div>
                        <div class="report-item"><span>A vencer (≤30d)</span><span style="color:#f59e0b;">${options.ctAVencer}</span></div>
                        <div class="report-item"><span>Vencidos</span><span style="color:#dc2626;">${options.ctVencidos}</span></div>
                        <div class="report-item"><span>Locais / Equipamentos</span><span>${options.totalLocais} / ${options.totalEquip}</span></div>
                        <div class="report-item"><span>Manutenções realizadas</span><span>${options.totalRegistos}</span></div>
                        <div class="report-item" style="font-weight:bold; border-top:1px solid #e2e8f0; padding-top:8px;"><span>Valor anual contratado</span><span>${options.ctValor}</span></div>
                    </div>
                    <div class="report-card">
                        <h4><i class="fas fa-car"></i> Frota</h4>
                        <div class="report-item"><span>Total de veículos</span><span>${options.frotaTotal}</span></div>
                        <div class="report-item"><span>Em dia</span><span style="color:#16a34a;">${options.frotaEmDia}</span></div>
                        <div class="report-item"><span>A vencer</span><span style="color:#f59e0b;">${options.frotaAVencer}</span></div>
                        <div class="report-item"><span>Vencidos</span><span style="color:#dc2626;">${options.frotaVencido}</span></div>
                        <div class="report-item"><span>Intervenções registadas</span><span>${options.totalIntervencoes}</span></div>
                        <div class="report-item"><span>Sinistros</span><span>${options.totalSinistros}</span></div>
                        <div class="report-item" style="font-weight:bold; border-top:1px solid #e2e8f0; padding-top:8px;"><span>Valor gasto (manutenção/inspeção)</span><span>${options.gastoVeiculos}</span></div>
                    </div>
                    <div class="report-card">
                        <h4><i class="fas fa-headset"></i> Suporte Técnico</h4>
                        <div class="report-item"><span>Total</span><span>${options.suporteTotal}</span></div>
                        <div class="report-item"><span>Pendentes</span><span>${options.ajPend}</span></div>
                        <div class="report-item"><span>Concluídas</span><span>${options.ajConcl}</span></div>
                    </div>
                `;
  }

'''
view = view.replace(view_anchor, admin_view + view_anchor, 1)
export_anchor = '    distributorClientSummary: distributorClientSummary\n'
assert view.count(export_anchor) == 1
view = view.replace(export_anchor, '    distributorClientSummary: distributorClientSummary,\n    adminOverviewCards: adminOverviewCards\n', 1)

assert sw.count("const CACHE = 'totalgest-v116';") == 1
sw = sw.replace("const CACHE = 'totalgest-v116';", "const CACHE = 'totalgest-v117';", 1)

for needle, count in protected.items():
    assert app.count(needle) == count, (needle, count, app.count(needle))
_, _, after_reports = reports_region(app)
assert after_reports.count('window.TotalGestReportsView.adminOverviewCards({') == 1
assert 'container.innerHTML = `\n                    <div class="report-card">\n                        <h4><i class="fas fa-users"></i> Recursos Humanos</h4>' not in after_reports
assert view.count('function adminOverviewCards(options)') == 1
assert view.count('adminOverviewCards: adminOverviewCards') == 1
assert sw.count("const CACHE = 'totalgest-v117';") == 1

APP.write_text(app, encoding='utf-8')
VIEW.write_text(view, encoding='utf-8')
SW.write_text(sw, encoding='utf-8')
print(f'RENDERIZAR_REPORTS_AFTER chars={len(after_reports)} lines={after_reports.count(chr(10))+1}')
print('REPORTS_ADMIN_VIEW_MIGRATION=OK')
