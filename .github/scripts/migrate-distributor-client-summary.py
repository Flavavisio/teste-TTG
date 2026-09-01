from pathlib import Path

APP = Path('app.html')
SW = Path('sw.js')

app = APP.read_text(encoding='utf-8')
sw = SW.read_text(encoding='utf-8')


def reports_region(text):
    start = text.index('        function renderizarReports() {')
    end = text.index('\n        function ', start + 1)
    return start, end, text[start:end]

protected = {
    'bootstrapSupabase()': app.count('bootstrapSupabase()'),
    'supabase.auth': app.count('supabase.auth'),
    'window.TotalGestReportsSuperadminMetrics.calculateCompanySummary({': app.count('window.TotalGestReportsSuperadminMetrics.calculateCompanySummary({'),
    'window.TotalGestReportsDistributorMetrics.calculateOverview({': app.count('window.TotalGestReportsDistributorMetrics.calculateOverview({'),
    'window.TotalGestReportsDistributorMetrics.calculateAdminOverview({': app.count('window.TotalGestReportsDistributorMetrics.calculateAdminOverview({'),
    'window.TotalGestReportsDistributorMetrics.calculateAdminContracts({': app.count('window.TotalGestReportsDistributorMetrics.calculateAdminContracts({'),
    'window.TotalGestReportsDistributorMetrics.calculateAdminOperations({': app.count('window.TotalGestReportsDistributorMetrics.calculateAdminOperations({'),
}

start, end, reports = reports_region(app)
block_start = '                const _clientRows = [];\n'
block_end = '''                html += window.TotalGestReportsView.distributorClientSummary({\n                    rows: _clientRows,\n                    totalCobrado: totalCobradoGlobal\n                });'''
assert reports.count(block_start) == 1, reports.count(block_start)
assert reports.count(block_end) == 1, reports.count(block_end)
start_rel = reports.index(block_start)
end_rel = reports.index(block_end, start_rel) + len(block_end)
old = reports[start_rel:end_rel]
assert 'meusClientes.forEach(c => {' in old
assert 'window.TotalGestReportsDistributorMetrics.calculateClient({' in old
assert 'totalCobradoGlobal += valorCliente;' in old
assert '_clientRows.push({' in old

replacement = '''                const _clientSummary = window.TotalGestReportsDistributorMetrics.calculateClientSummary({\n                    clients: meusClientes,\n                    data: dados,\n                    contractsActive: moduloContratosAtivo,\n                    fleetActive: moduloFrotaAtivo,\n                    warehouseActive: moduloArmazemAtivo,\n                    crmActive: moduloCrmAtivo,\n                    getPlanValue: getValorPlano,\n                    contractsAnnualPrice: PRECO_CONTRATOS_ANUAL,\n                    contractsMonthlyPrice: PRECO_CONTRATOS_MENSAL,\n                    fleetAnnualPrice: PRECO_FROTA_ANUAL,\n                    fleetMonthlyPrice: PRECO_FROTA_MENSAL,\n                    warehouseAnnualPrice: PRECO_ARMAZEM_ANUAL,\n                    warehouseMonthlyPrice: PRECO_ARMAZEM_MENSAL,\n                    crmAnnualPrice: PRECO_CRM_ANUAL,\n                    crmMonthlyPrice: PRECO_CRM_MENSAL,\n                    planLabel: client => client.licenca ? PLANOS[client.licenca.plano]?.label || client.licenca.plano : 'Sem licença',\n                    expiryLabel: client => client.licenca ? new Date(client.licenca.dataExpiracao).toLocaleDateString('pt-PT') : '-'\n                });\n                html += window.TotalGestReportsView.distributorClientSummary(_clientSummary);'''

reports = reports[:start_rel] + replacement + reports[end_rel:]
app = app[:start] + reports + app[end:]

assert sw.count("const CACHE = 'totalgest-v119';") == 1
sw = sw.replace("const CACHE = 'totalgest-v119';", "const CACHE = 'totalgest-v120';", 1)

for needle, before in protected.items():
    assert app.count(needle) == before, (needle, before, app.count(needle))

_, _, after = reports_region(app)
assert after.count('window.TotalGestReportsDistributorMetrics.calculateClientSummary({') == 1
assert after.count('window.TotalGestReportsView.distributorClientSummary(_clientSummary)') == 1
assert 'const _clientRows = [];' not in after
assert 'totalCobradoGlobal' not in after
assert 'window.TotalGestReportsDistributorMetrics.calculateClient({' not in after
assert sw.count("const CACHE = 'totalgest-v120';") == 1

APP.write_text(app, encoding='utf-8')
SW.write_text(sw, encoding='utf-8')
print(f'RENDERIZAR_REPORTS_AFTER chars={len(after)} lines={after.count(chr(10)) + 1}')
print('DISTRIBUTOR_CLIENT_SUMMARY_MIGRATION=OK')
