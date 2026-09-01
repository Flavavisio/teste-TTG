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
    'function renderizarReports()': app.count('function renderizarReports()'),
    'window.TotalGestReportsView.superadminCompanySummary({': app.count('window.TotalGestReportsView.superadminCompanySummary({'),
}

start, end, body = reports_region(app)
block_start = '                const _companyRows = [];\n'
block_end = '\n\n                // Licenças de Manutenção (módulo Contratos)'
assert body.count(block_start) == 1, body.count(block_start)
assert body.count(block_end) == 1, body.count(block_end)
start_rel = body.index(block_start)
end_rel = body.index(block_end, start_rel)
old = body[start_rel:end_rel]
assert 'admins.forEach(admin => {' in old
assert 'window.TotalGestReportsSuperadminMetrics.calculateCompany({' in old
assert '_companyRows.push({' in old
assert 'totalReceitaGlobal += valorEmpresa;' in old
assert 'html += window.TotalGestReportsView.superadminCompanySummary({' in old

replacement = '''                const _companySummary = window.TotalGestReportsSuperadminMetrics.calculateCompanySummary({\n                    admins: admins,\n                    data: dados,\n                    baseValueCharged: valorBaseCobradoDe,\n                    contractsActive: moduloContratosAtivo,\n                    fleetActive: moduloFrotaAtivo,\n                    warehouseActive: moduloArmazemAtivo,\n                    crmActive: moduloCrmAtivo,\n                    erpActive: moduloErpAtivo,\n                    roundsActive: moduloRondasAtivo,\n                    contractsAnnualPrice: PRECO_CONTRATOS_ANUAL,\n                    contractsMonthlyPrice: PRECO_CONTRATOS_MENSAL,\n                    fleetAnnualPrice: PRECO_FROTA_ANUAL,\n                    fleetMonthlyPrice: PRECO_FROTA_MENSAL,\n                    warehouseAnnualPrice: PRECO_ARMAZEM_ANUAL,\n                    warehouseMonthlyPrice: PRECO_ARMAZEM_MENSAL,\n                    crmAnnualPrice: PRECO_CRM_ANUAL,\n                    crmMonthlyPrice: PRECO_CRM_MENSAL,\n                    erpAnnualPrice: PRECO_ERP_ANUAL,\n                    erpMonthlyPrice: PRECO_ERP_MENSAL,\n                    roundsAnnualPrice: PRECO_RONDAS_ANUAL,\n                    roundsMonthlyPrice: PRECO_RONDAS_MENSAL,\n                    planLabel: admin => admin.licenca ? PLANOS[admin.licenca.plano]?.label || admin.licenca.plano : 'Sem licença',\n                    expiryLabel: admin => admin.licenca ? new Date(admin.licenca.dataExpiracao).toLocaleDateString('pt-PT') : '-'\n                });\n                html += window.TotalGestReportsView.superadminCompanySummary(_companySummary);'''

body = body[:start_rel] + replacement + body[end_rel:]
app = app[:start] + body + app[end:]

assert sw.count("const CACHE = 'totalgest-v118';") == 1
sw = sw.replace("const CACHE = 'totalgest-v118';", "const CACHE = 'totalgest-v119';", 1)

for needle, before in protected.items():
    if needle == 'window.TotalGestReportsView.superadminCompanySummary({':
        continue
    assert app.count(needle) == before, (needle, before, app.count(needle))

_, _, after = reports_region(app)
assert after.count('window.TotalGestReportsSuperadminMetrics.calculateCompanySummary({') == 1
assert after.count('window.TotalGestReportsView.superadminCompanySummary(_companySummary)') == 1
assert 'const _companyRows = [];' not in after
assert 'totalReceitaGlobal' not in after
assert 'totalFuncGlobal' not in after
assert 'window.TotalGestReportsSuperadminMetrics.calculateCompany({' not in after
assert sw.count("const CACHE = 'totalgest-v119';") == 1

APP.write_text(app, encoding='utf-8')
SW.write_text(sw, encoding='utf-8')
print(f'RENDERIZAR_REPORTS_AFTER chars={len(after)} lines={after.count(chr(10))+1}')
print('SUPERADMIN_COMPANY_SUMMARY_MIGRATION=OK')
