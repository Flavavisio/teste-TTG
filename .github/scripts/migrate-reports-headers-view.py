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
    'window.TotalGestReportsSuperadminMetrics.calculate({': app.count('window.TotalGestReportsSuperadminMetrics.calculate({'),
    'window.TotalGestReportsSuperadminMetrics.calculateCompanySummary({': app.count('window.TotalGestReportsSuperadminMetrics.calculateCompanySummary({'),
    'window.TotalGestReportsDistributorMetrics.calculateOverview({': app.count('window.TotalGestReportsDistributorMetrics.calculateOverview({'),
    'window.TotalGestReportsDistributorMetrics.calculateClientSummary({': app.count('window.TotalGestReportsDistributorMetrics.calculateClientSummary({'),
    'window.TotalGestReportsDistributorMetrics.calculateAdminOverview({': app.count('window.TotalGestReportsDistributorMetrics.calculateAdminOverview({'),
}

start, end, reports = reports_region(app)

super_start = '                const _kpi = window.TotalGestReportsView.kpi;\n'
super_end = '                const _companySummary = window.TotalGestReportsSuperadminMetrics.calculateCompanySummary({' 
assert reports.count(super_start) == 2, reports.count(super_start)
assert reports.count(super_end) == 1
s1 = reports.index(super_start)
e1 = reports.index(super_end, s1)
super_old = reports[s1:e1]
assert 'relSuperAdminPDF()' in super_old
assert "_kpi('Empresas'" in super_old
assert "_kpi('Receita recorrente'" in super_old
super_new = '''                let html = window.TotalGestReportsView.superadminHeader({\n                    empresas: _emp.length,\n                    empresasAtivas: _empAtivas,\n                    totalUtilizadores: _totFunc + _totEnc,\n                    addonsAtivos: _addons,\n                    expiramEm10Dias: _expira,\n                    receitaRecorrente: _recT\n                });\n'''
reports = reports[:s1] + super_new + reports[e1:]

# localizar a segunda declaração _kpi, agora pertencente ao distribuidor
assert reports.count(super_start) == 1
s2 = reports.index(super_start)
client_anchor = '                const _clientSummary = window.TotalGestReportsDistributorMetrics.calculateClientSummary({' 
e2 = reports.index(client_anchor, s2)
dist_old = reports[s2:e2]
assert "_kpi('Clientes'" in dist_old
assert 'meusClientes.length' in dist_old
assert 'ativos.length' in dist_old
dist_new = '''                let html = window.TotalGestReportsView.distributorHeader({\n                    clientes: meusClientes.length,\n                    clientesAtivos: ativos.length\n                });\n'''
reports = reports[:s2] + dist_new + reports[e2:]
app = app[:start] + reports + app[end:]

view_anchor = '  function moduleLicenseCard(options) {'
assert view.count(view_anchor) == 1
assert 'function superadminHeader(options)' not in view
assert 'function distributorHeader(options)' not in view
view_functions = '''  function superadminHeader(options) {\n    options = options || {};\n    const empresas = Number(options.empresas) || 0;\n    const empresasAtivas = Number(options.empresasAtivas) || 0;\n    const expiram = Number(options.expiramEm10Dias) || 0;\n    const receita = Number(options.receitaRecorrente) || 0;\n    let html = `<div style="display:flex;justify-content:flex-end;margin-bottom:10px;"><button class="btn btn-outline" onclick="relSuperAdminPDF()"><i class="fas fa-file-pdf"></i> Exportar PDF</button></div>`;\n    html += `<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(155px,1fr));gap:12px;margin-bottom:16px;">\n      ${kpi('Empresas', empresas + ` <span style="font-size:.7rem;color:#16a34a;">(${empresasAtivas} ativas)</span>`, '#2563eb', 'fa-building')}\n      ${kpi('Utilizadores', String(Number(options.totalUtilizadores) || 0), '#0e7490', 'fa-users')}\n      ${kpi('Add-ons ativos', String(Number(options.addonsAtivos) || 0), '#b45309', 'fa-puzzle-piece')}\n      ${kpi('A expirar (≤10d)', String(expiram), expiram ? '#dc2626' : '#16a34a', 'fa-hourglass-half')}\n      ${kpi('Receita recorrente', receita.toLocaleString('pt-PT', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) + ' €', '#16a34a', 'fa-euro-sign')}\n    </div>`;\n    return html;\n  }\n\n  function distributorHeader(options) {\n    options = options || {};\n    const clientes = Number(options.clientes) || 0;\n    const ativos = Number(options.clientesAtivos) || 0;\n    return `<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(155px,1fr));gap:12px;margin-bottom:16px;">\n      ${kpi('Clientes', clientes + ` <span style="font-size:.7rem;color:#16a34a;">(${ativos} ativos)</span>`, '#7c3aed', 'fa-user-tie')}\n    </div>`;\n  }\n\n'''
view = view.replace(view_anchor, view_functions + view_anchor, 1)

export_anchor = '  window.TotalGestReportsView = {\n    kpi: kpi,\n'
assert view.count(export_anchor) == 1
view = view.replace(export_anchor, '  window.TotalGestReportsView = {\n    kpi: kpi,\n    superadminHeader: superadminHeader,\n    distributorHeader: distributorHeader,\n', 1)

assert sw.count("const CACHE = 'totalgest-v120';") == 1
sw = sw.replace("const CACHE = 'totalgest-v120';", "const CACHE = 'totalgest-v121';", 1)

for needle, before in protected.items():
    assert app.count(needle) == before, (needle, before, app.count(needle))

_, _, after = reports_region(app)
assert after.count('window.TotalGestReportsView.superadminHeader({') == 1
assert after.count('window.TotalGestReportsView.distributorHeader({') == 1
assert 'const _kpi = window.TotalGestReportsView.kpi;' not in after
assert 'relSuperAdminPDF()' not in after
assert "_kpi('Clientes'" not in after
assert view.count('function superadminHeader(options)') == 1
assert view.count('function distributorHeader(options)') == 1
assert view.count('superadminHeader: superadminHeader') == 1
assert view.count('distributorHeader: distributorHeader') == 1
assert sw.count("const CACHE = 'totalgest-v121';") == 1

APP.write_text(app, encoding='utf-8')
VIEW.write_text(view, encoding='utf-8')
SW.write_text(sw, encoding='utf-8')
print(f'RENDERIZAR_REPORTS_AFTER chars={len(after)} lines={after.count(chr(10)) + 1}')
print('REPORTS_HEADERS_VIEW_MIGRATION=OK')
