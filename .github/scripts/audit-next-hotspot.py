from pathlib import Path

APP = Path('app.html')
SW = Path('sw.js')

app = APP.read_text(encoding='utf-8')
sw = SW.read_text(encoding='utf-8')

protected = {
    'bootstrapSupabase()': app.count('bootstrapSupabase()'),
    'supabase.auth': app.count('supabase.auth'),
    'function renderizarReports()': app.count('function renderizarReports()'),
    'window.TotalGestReportsSuperadminMetrics.calculateCompanySummary({': app.count('window.TotalGestReportsSuperadminMetrics.calculateCompanySummary({'),
    'window.TotalGestReportsDistributorMetrics.calculateClientSummary({': app.count('window.TotalGestReportsDistributorMetrics.calculateClientSummary({'),
    'window.TotalGestReportsView.superadminHeader({': app.count('window.TotalGestReportsView.superadminHeader({'),
    'window.TotalGestReportsView.distributorHeader({': app.count('window.TotalGestReportsView.distributorHeader({'),
    'window.TotalGestReportsView.adminOverviewCards({': app.count('window.TotalGestReportsView.adminOverviewCards({'),
}

start = app.index('        function renderizarReports() {')
end = app.index('\n        function ', start + 1)
block = app[start:end]

old_start_marker = '                // Licenças de Manutenção (módulo Contratos)\n'
old_end_marker = '                // Nota: o Total Gest Assist deixou de ter card/receita própria — vem sempre incluído\n'
assert block.count(old_start_marker) == 1
assert block.count(old_end_marker) == 1
old_start = block.index(old_start_marker)
old_end = block.index(old_end_marker)
old = block[old_start:old_end]
for needle in [
    'calculateContracts({',
    'calculateFleet({',
    'calculateWarehouse({',
    'calculateNotifications({',
    'calculateCrm({',
    'moduleLicenseCard({',
    'const receitaManut =',
    'const receitaFrota =',
    'const receitaArmazem =',
    'const receitaNotif =',
    'const receitaCrm ='
]:
    assert needle in old, needle

new = '''                const _moduleOverview = window.TotalGestReportsModuleMetrics.calculateOverview({\n                    admins: admins,\n                    warehouseActive: moduloArmazemAtivo,\n                    notificationsActive: moduloNotificacoesAtivo,\n                    crmActive: moduloCrmAtivo,\n                    contractsMonthlyPrice: PRECO_CONTRATOS_MENSAL,\n                    contractsAnnualPrice: PRECO_CONTRATOS_ANUAL,\n                    fleetMonthlyPrice: PRECO_FROTA_MENSAL,\n                    fleetAnnualPrice: PRECO_FROTA_ANUAL,\n                    warehouseMonthlyPrice: PRECO_ARMAZEM_MENSAL,\n                    warehouseAnnualPrice: PRECO_ARMAZEM_ANUAL,\n                    notificationsMonthlyPrice: PRECO_NOTIFICACOES_MENSAL,\n                    notificationsAnnualPrice: PRECO_NOTIFICACOES_ANUAL,\n                    crmMonthlyPrice: PRECO_CRM_MENSAL,\n                    crmAnnualPrice: PRECO_CRM_ANUAL\n                });\n                _moduleOverview.cards.forEach(card => {\n                    html += window.TotalGestReportsView.moduleLicenseCard(card);\n                });\n'''
block = block[:old_start] + new + block[old_end:]

replacements = {
    'contractsRevenue: receitaManut': 'contractsRevenue: _moduleOverview.revenues.contracts',
    'fleetRevenue: receitaFrota': 'fleetRevenue: _moduleOverview.revenues.fleet',
    'warehouseRevenue: receitaArmazem': 'warehouseRevenue: _moduleOverview.revenues.warehouse',
    'notificationsRevenue: receitaNotif': 'notificationsRevenue: _moduleOverview.revenues.notifications',
    'crmRevenue: receitaCrm': 'crmRevenue: _moduleOverview.revenues.crm',
}
for old_text, new_text in replacements.items():
    assert block.count(old_text) == 1, old_text
    block = block.replace(old_text, new_text, 1)

app = app[:start] + block + app[end:]

for needle, count in protected.items():
    assert app.count(needle) == count, (needle, count, app.count(needle))

new_block = app[start:start + len(block)]
assert new_block.count('window.TotalGestReportsModuleMetrics.calculateOverview({') == 1
assert new_block.count('window.TotalGestReportsView.moduleLicenseCard(card)') == 1
for needle in ['calculateContracts({','calculateFleet({','calculateWarehouse({','calculateNotifications({','calculateCrm({','const receitaManut =','const receitaFrota =','const receitaArmazem =','const receitaNotif =','const receitaCrm =']:
    assert needle not in new_block, needle

assert sw.count("const CACHE = 'totalgest-v123';") == 1
sw = sw.replace("const CACHE = 'totalgest-v123';", "const CACHE = 'totalgest-v124';", 1)

APP.write_text(app, encoding='utf-8')
SW.write_text(sw, encoding='utf-8')
print(f'RENDERIZAR_REPORTS_AFTER chars={len(new_block)} lines={len(new_block.splitlines())}')
print('REPORTS_MODULE_OVERVIEW_MIGRATION=OK')
