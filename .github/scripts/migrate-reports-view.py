from pathlib import Path
import re

APP = Path('app.html')
SHELL = Path('assets/js/app-shell.js')
SW = Path('sw.js')

app = APP.read_text(encoding='utf-8')
shell = SHELL.read_text(encoding='utf-8')
sw = SW.read_text(encoding='utf-8')


def replace_region(text, start_marker, end_marker, replacement):
    assert text.count(start_marker) == 1, (start_marker, text.count(start_marker))
    assert text.count(end_marker) == 1, (end_marker, text.count(end_marker))
    start = text.index(start_marker)
    end = text.index(end_marker, start)
    assert end > start
    return text[:start] + replacement + text[end:]


# O helper KPI estava duplicado nas branches Super Admin e Distribuidor.
kpi_pattern = re.compile(r'(?m)^(\s*)const _kpi = \(lbl, val, cor, ic\) => `<div style="border:1px solid #e6eaf2;.*?`;$')
app, kpi_count = kpi_pattern.subn(r'\1const _kpi = window.TotalGestReportsView.kpi;', app)
assert kpi_count == 2, kpi_count

contracts = """                html += window.TotalGestReportsView.moduleLicenseCard({
                    icon: 'fa-file-signature',
                    title: 'Licenças de Contratos de Manutenção',
                    activeCount: comContratos.length,
                    monthly: mensais,
                    annual: anuais,
                    revenue: receitaManut
                });
"""
fleet = """                html += window.TotalGestReportsView.moduleLicenseCard({
                    icon: 'fa-car',
                    title: 'Licenças de Frota',
                    activeCount: comFrota.length,
                    monthly: frotaMensais,
                    annual: frotaAnuais,
                    revenue: receitaFrota
                });
"""
warehouse = """                html += window.TotalGestReportsView.moduleLicenseCard({
                    icon: 'fa-boxes',
                    title: 'Licenças de Armazém',
                    activeCount: comArmazem.length,
                    monthly: armMensais,
                    annual: armAnuais,
                    demos: armDemos,
                    revenue: receitaArmazem
                });
"""
notifications = """                html += window.TotalGestReportsView.moduleLicenseCard({
                    icon: 'fa-bell',
                    title: 'Licenças de Notificações',
                    activeCount: comNotif.length,
                    monthly: notifMensais,
                    annual: notifAnuais,
                    demos: notifDemos,
                    revenue: receitaNotif
                });
"""
crm = """                html += window.TotalGestReportsView.moduleLicenseCard({
                    icon: 'fa-bullseye',
                    title: 'Licenças de CRM Comercial + Assist',
                    activeCount: comCrm.length,
                    monthly: crmMensais,
                    annual: crmAnuais,
                    demos: crmDemos,
                    revenue: receitaCrm
                });
"""

app = replace_region(
    app,
    '                html += `<div class="report-card">\n                            <h4><i class="fas fa-file-signature"></i> Licenças de Contratos de Manutenção</h4>',
    '                // Licenças de Frota',
    contracts,
)
app = replace_region(
    app,
    '                html += `<div class="report-card">\n                            <h4><i class="fas fa-car"></i> Licenças de Frota</h4>',
    '                // Licenças de Armazém',
    fleet,
)
app = replace_region(
    app,
    '                html += `<div class="report-card">\n                            <h4><i class="fas fa-boxes"></i> Licenças de Armazém</h4>',
    '                // Licenças de Notificações',
    warehouse,
)
app = replace_region(
    app,
    '                html += `<div class="report-card">\n                            <h4><i class="fas fa-bell"></i> Licenças de Notificações</h4>',
    '                // Licenças de CRM Comercial + Assist',
    notifications,
)
app = replace_region(
    app,
    '                html += `<div class="report-card">\n                            <h4><i class="fas fa-bullseye"></i> Licenças de CRM Comercial + Assist</h4>',
    '                // Nota: o Total Gest Assist deixou de ter card/receita própria',
    crm,
)

bars_start = "                let barras = '';"
bars_end = '                html += `<div class="report-card"><h4><i class="fas fa-coins"></i> Receita por módulo</h4>'
app = replace_region(
    app,
    bars_start,
    bars_end,
    "                const barras = window.TotalGestReportsView.revenueBars({ modules: mods, maxModuleRevenue: maxMod });\n",
)

init_anchor = 'reportsDistributorMetrics: true, dashboardCounts: true'
assert app.count(init_anchor) == 1, app.count(init_anchor)
app = app.replace(init_anchor, 'reportsDistributorMetrics: true, reportsView: true, dashboardCounts: true', 1)

module_anchor = "    reportsDistributorMetrics: './assets/js/app-reports-distributor-metrics.js',\n"
assert shell.count(module_anchor) == 1, shell.count(module_anchor)
shell = shell.replace(module_anchor, module_anchor + "    reportsView: './assets/js/app-reports-view.js',\n", 1)

loader_anchor = '    if (options.reportsDistributorMetrics === true) pedidos.push(MODULOS.reportsDistributorMetrics);\n'
assert shell.count(loader_anchor) == 1, shell.count(loader_anchor)
shell = shell.replace(loader_anchor, loader_anchor + '    if (options.reportsView === true) pedidos.push(MODULOS.reportsView);\n', 1)

asset_anchor = "  './assets/js/app-reports-distributor-metrics.js',\n"
assert sw.count(asset_anchor) == 1, sw.count(asset_anchor)
sw = sw.replace(asset_anchor, asset_anchor + "  './assets/js/app-reports-view.js',\n", 1)
assert sw.count("const CACHE = 'totalgest-v113';") == 1
sw = sw.replace("const CACHE = 'totalgest-v113';", "const CACHE = 'totalgest-v114';", 1)

assert app.count('window.TotalGestReportsView.kpi;') == 2
assert app.count('window.TotalGestReportsView.moduleLicenseCard({') == 5
assert app.count('window.TotalGestReportsView.revenueBars({') == 1
assert app.count('function renderizarReports()') == 1
assert shell.count("reportsView: './assets/js/app-reports-view.js'") == 1
assert shell.count('options.reportsView === true') == 1
assert sw.count("'./assets/js/app-reports-view.js'") == 1
assert sw.count("const CACHE = 'totalgest-v114';") == 1

APP.write_text(app, encoding='utf-8')
SHELL.write_text(shell, encoding='utf-8')
SW.write_text(sw, encoding='utf-8')
print('REPORTS_VIEW_MIGRATION_ASSERTIONS=OK')
