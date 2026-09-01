from pathlib import Path

APP = Path('app.html')
METRICS = Path('assets/js/app-reports-distributor-metrics.js')
VIEW = Path('assets/js/app-reports-view.js')
SW = Path('sw.js')

app = APP.read_text(encoding='utf-8')
metrics = METRICS.read_text(encoding='utf-8')
view = VIEW.read_text(encoding='utf-8')
sw = SW.read_text(encoding='utf-8')

protected = {
    'bootstrapSupabase()': app.count('bootstrapSupabase()'),
    'supabase.auth': app.count('supabase.auth'),
    'function renderizarReports()': app.count('function renderizarReports()'),
    'window.TotalGestReportsSuperadminMetrics.calculateCompanySummary({': app.count('window.TotalGestReportsSuperadminMetrics.calculateCompanySummary({'),
    'window.TotalGestReportsDistributorMetrics.calculateClientSummary({': app.count('window.TotalGestReportsDistributorMetrics.calculateClientSummary({'),
    'window.TotalGestReportsModuleMetrics.calculateOverview({': app.count('window.TotalGestReportsModuleMetrics.calculateOverview({'),
}

# Compor as três métricas admin existentes, sem alterar as regras internas.
export_anchor = '  window.TotalGestReportsDistributorMetrics = {'
assert metrics.count(export_anchor) == 1
assert 'function calculateAdminSummary(options)' not in metrics
summary_fn = '''  function calculateAdminSummary(options) {\n    const opts = options || {};\n    const admin = opts.admin || {};\n    const overview = calculateAdminOverview({ data: opts.data, adminId: admin.id });\n    const contracts = calculateAdminContracts({\n      data: opts.data,\n      adminId: admin.id,\n      maintenanceState: opts.maintenanceState,\n      nextMaintenance: opts.nextMaintenance,\n      toNumber: overview.numOrd\n    });\n    const operations = calculateAdminOperations({\n      data: opts.data,\n      admin: admin,\n      contractsActive: opts.contractsActive,\n      countFleet: opts.countFleet\n    });\n\n    return {\n      totalFunc: overview.totalFunc,\n      totalEncarregados: overview.totalEncarregados,\n      totalCli: overview.totalCli,\n      gastoFunc: overview.gastoFunc,\n      gastoEnc: overview.gastoEnc,\n      gastoTotal: overview.gastoTotal,\n      totalOS: overview.totalOS,\n      osPendentes: overview.osPendentes,\n      osAndamento: overview.osAndamento,\n      osConcluidas: overview.osConcluidas,\n      totalPonto: overview.totalPonto,\n      totalPedidos: overview.totalPedidos,\n      pedPend: overview.pedPend,\n      totalFolhas: overview.totalFolhas,\n      folhasOT: operations.folhasOT,\n      totalReqs: overview.totalReqs,\n      reqPend: overview.reqPend,\n      moduloAtivoTxt: operations.moduloAtivoTxt,\n      contratosCount: contracts.contracts.length,\n      ctEmDia: contracts.emDia,\n      ctAVencer: contracts.aVencer,\n      ctVencidos: contracts.vencidos,\n      totalLocais: operations.totalLocais,\n      totalEquip: operations.totalEquip,\n      totalRegistos: operations.totalRegistos,\n      ctValor: contracts.valor,\n      frotaTotal: operations.frotaStats.total,\n      frotaEmDia: operations.frotaStats.emDia,\n      frotaAVencer: operations.frotaStats.aVencer,\n      frotaVencido: operations.frotaStats.vencido,\n      totalIntervencoes: operations.totalIntervencoes,\n      totalSinistros: operations.totalSinistros,\n      gastoVeiculos: operations.gastoVeiculos,\n      suporteTotal: operations.ajudasAdmin.length,\n      ajPend: operations.ajPend,\n      ajConcl: operations.ajConcl\n    };\n  }\n\n'''
metrics = metrics.replace(export_anchor, summary_fn + export_anchor, 1)
old_export = '    calculateAdminOperations: calculateAdminOperations\n'
assert metrics.count(old_export) == 1
metrics = metrics.replace(old_export, '    calculateAdminOperations: calculateAdminOperations,\n    calculateAdminSummary: calculateAdminSummary\n', 1)

# A formatação monetária pertence à camada visual.
view_anchor = "  function adminOverviewCards(options) {\n    options = options || {};\n    return `"
assert view.count(view_anchor) == 1
view = view.replace(view_anchor, "  function adminOverviewCards(options) {\n    options = options || {};\n    const eur = n => (Number(n) || 0).toLocaleString('pt-PT', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) + ' €';\n    return `", 1)
for field in ['gastoFunc', 'gastoEnc', 'gastoTotal', 'ctValor', 'gastoVeiculos']:
    old = '${options.' + field + '}'
    new = '${eur(options.' + field + ')}'
    assert view.count(old) == 1, field
    view = view.replace(old, new, 1)

# Reduzir apenas o ramo final Admin/Subadmin de renderizarReports().
start = app.index('        function renderizarReports() {')
end = app.index('\n        function ', start + 1)
block = app[start:end]
old_start = block.index('            const _adminOverview = window.TotalGestReportsDistributorMetrics.calculateAdminOverview({')
render_start = block.index('            container.innerHTML = window.TotalGestReportsView.adminOverviewCards({', old_start)
old_end = block.index('\n            });', render_start) + len('\n            });')
old = block[old_start:old_end]
for needle in [
    'calculateAdminOverview({',
    'calculateAdminContracts({',
    'calculateAdminOperations({',
    "const eur = (n) => n.toLocaleString('pt-PT'",
    'adminOverviewCards({'
]:
    assert needle in old, needle

new = '''            const _adminSummary = window.TotalGestReportsDistributorMetrics.calculateAdminSummary({\n                data: dados,\n                admin: admin,\n                maintenanceState: estadoManutencao,\n                nextMaintenance: calcularProximaManutencao,\n                contractsActive: moduloContratosAtivo,\n                countFleet: contarFrota\n            });\n            container.innerHTML = window.TotalGestReportsView.adminOverviewCards(_adminSummary);'''
block = block[:old_start] + new + block[old_end:]
app = app[:start] + block + app[end:]

for needle, count in protected.items():
    assert app.count(needle) == count, (needle, count, app.count(needle))

start = app.index('        function renderizarReports() {')
end = app.index('\n        function ', start + 1)
block = app[start:end]
assert block.count('window.TotalGestReportsDistributorMetrics.calculateAdminSummary({') == 1
assert block.count('window.TotalGestReportsView.adminOverviewCards(_adminSummary)') == 1
assert 'const _adminOverview =' not in block
assert 'const _adminContracts =' not in block
assert 'const _adminOperations =' not in block
assert "const eur = (n) =>" not in block

assert "const CACHE = 'totalgest-v124';" in sw
sw = sw.replace("const CACHE = 'totalgest-v124';", "const CACHE = 'totalgest-v125';", 1)

APP.write_text(app, encoding='utf-8')
METRICS.write_text(metrics, encoding='utf-8')
VIEW.write_text(view, encoding='utf-8')
SW.write_text(sw, encoding='utf-8')

start = app.index('        function renderizarReports() {')
end = app.index('\n        function ', start + 1)
block = app[start:end]
print(f'RENDERIZAR_REPORTS_AFTER chars={len(block)} lines={len(block.splitlines())}')
print('ADMIN_REPORT_SUMMARY_MIGRATION=OK')
