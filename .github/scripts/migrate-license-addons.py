from pathlib import Path

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


contracts = """            const modBloco = window.TotalGestLicenseAddons.renderAddon({
                active: modAtivo,
                title: 'Contratos de Manutenção',
                plan: admin.contratosPlano,
                expiry: modExp,
                remainingDays: calcularDiasRestantes(admin.contratosExpiracao),
                pending: !!contratoPedidoPend,
                pendingInstructions: contratoPedidoPend ? blocoInstrucoesPagamento(contratoPedidoPend) : '',
                renewFunction: 'solicitarContratos',
                monthlyPrice: PRECO_CONTRATOS_MENSAL,
                annualPrice: PRECO_CONTRATOS_ANUAL,
                inactiveDescription: 'Ative o módulo para gerir contratos de manutenção. A ativação é feita pelo Super Admin após confirmação do pagamento.'
            });
"""
fleet = """            const frotaBloco = window.TotalGestLicenseAddons.renderAddon({
                active: frotaAtivo,
                title: 'Frota',
                plan: admin.frotaPlano,
                expiry: frotaExp,
                remainingDays: calcularDiasRestantes(admin.frotaExpiracao),
                pending: !!frotaPedidoPend,
                pendingInstructions: frotaPedidoPend ? blocoInstrucoesPagamento(frotaPedidoPend) : '',
                renewFunction: 'solicitarFrota',
                monthlyPrice: PRECO_FROTA_MENSAL,
                annualPrice: PRECO_FROTA_ANUAL,
                inactiveDescription: 'Ative o módulo para gerir a frota de veículos. A ativação é feita pelo Super Admin após confirmação do pagamento.'
            });
"""
warehouse = """            const armazemBloco = window.TotalGestLicenseAddons.renderAddon({
                active: armazemAtivo,
                title: 'Armazém / Stock / Gestão de Obras',
                plan: admin.armazemPlano,
                expiry: armazemExp,
                remainingDays: calcularDiasRestantes(admin.armazemExpiracao),
                pending: !!armazemPedidoPend,
                pendingInstructions: armazemPedidoPend ? blocoInstrucoesPagamento(armazemPedidoPend) : '',
                renewFunction: 'solicitarArmazem',
                monthlyPrice: PRECO_ARMAZEM_MENSAL,
                annualPrice: PRECO_ARMAZEM_ANUAL,
                inactiveDescription: 'Add-on de gestão de stock: artigos, fornecedores, obras, encomendas e planos de materiais. A ativação é feita pelo Super Admin após confirmação do pagamento.'
            });
"""
crm = """            const crmBloco = window.TotalGestLicenseAddons.renderAddon({
                active: crmAtivo,
                title: 'CRM Comercial + Assist',
                plan: admin.crmPlano,
                expiry: crmExp,
                remainingDays: calcularDiasRestantes(admin.crmExpiracao),
                pending: !!crmPedidoPend,
                pendingInstructions: crmPedidoPend ? blocoInstrucoesPagamento(crmPedidoPend) : '',
                renewFunction: 'solicitarCrm',
                monthlyPrice: PRECO_CRM_MENSAL,
                annualPrice: PRECO_CRM_ANUAL,
                inactiveBadgeStyle: 'background:#7c3aed;color:#fff;',
                inactiveDescription: 'Gestão do ciclo comercial completo — leads, pipeline, propostas, mapa de visitas e conversão automática em cliente/contrato assim que um negócio é ganho — mais o Total Gest Assist (pedidos de suporte e assistência técnica com criação direta de OS), incluído sem custo extra. A ativação é feita pelo Super Admin após confirmação do pagamento.'
            });
"""

app = replace_region(app, '            const modBloco = modAtivo', '            const frotaAtivo = moduloFrotaAtivo(admin);', contracts)
app = replace_region(app, '            const frotaBloco = frotaAtivo', '            const armazemAtivo = moduloArmazemAtivo(admin);', fleet)
app = replace_region(app, '            const armazemBloco = armazemAtivo', '            const portalBloco = ', warehouse)
app = replace_region(app, '            const crmBloco = crmAtivo', '            const erpBloco = ', crm)

init_anchor = 'dashboardAnalyticsMetrics: true, syncPrepare: true'
assert app.count(init_anchor) == 1, app.count(init_anchor)
app = app.replace(init_anchor, 'dashboardAnalyticsMetrics: true, licenseAddons: true, syncPrepare: true', 1)

module_anchor = "    dashboardAnalyticsMetrics: './assets/js/app-dashboard-analytics-metrics.js',\n"
assert shell.count(module_anchor) == 1, shell.count(module_anchor)
shell = shell.replace(module_anchor, module_anchor + "    licenseAddons: './assets/js/app-license-addons.js',\n", 1)

loader_anchor = '    if (options.dashboardAnalyticsMetrics === true) pedidos.push(MODULOS.dashboardAnalyticsMetrics);\n'
assert shell.count(loader_anchor) == 1, shell.count(loader_anchor)
shell = shell.replace(loader_anchor, loader_anchor + '    if (options.licenseAddons === true) pedidos.push(MODULOS.licenseAddons);\n', 1)

asset_anchor = "  './assets/js/app-dashboard-analytics-metrics.js',\n"
assert sw.count(asset_anchor) == 1, sw.count(asset_anchor)
sw = sw.replace(asset_anchor, asset_anchor + "  './assets/js/app-license-addons.js',\n", 1)
assert sw.count("const CACHE = 'totalgest-v112';") == 1
sw = sw.replace("const CACHE = 'totalgest-v112';", "const CACHE = 'totalgest-v113';", 1)

assert app.count('window.TotalGestLicenseAddons.renderAddon({') == 4
for old in ['const modBloco = modAtivo', 'const frotaBloco = frotaAtivo', 'const armazemBloco = armazemAtivo', 'const crmBloco = crmAtivo']:
    assert old not in app
assert app.count('function renderizarMinhaLicenca()') == 1
assert app.count('function renderizarDashboardAnalitico()') == 1
assert shell.count("licenseAddons: './assets/js/app-license-addons.js'") == 1
assert shell.count('options.licenseAddons === true') == 1
assert sw.count("'./assets/js/app-license-addons.js'") == 1
assert sw.count("const CACHE = 'totalgest-v113';") == 1

APP.write_text(app, encoding='utf-8')
SHELL.write_text(shell, encoding='utf-8')
SW.write_text(sw, encoding='utf-8')
print('MIGRATION_ASSERTIONS=OK')
