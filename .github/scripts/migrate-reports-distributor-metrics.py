from pathlib import Path

APP = Path('app.html')
SHELL = Path('assets/js/app-shell.js')
SW = Path('sw.js')

app = APP.read_text(encoding='utf-8')
shell = SHELL.read_text(encoding='utf-8')
sw = SW.read_text(encoding='utf-8')

start = app.index('function renderizarReports(')

old_overview = """                const meusClientes = (dados.administradores || []).filter(a => a.distribuidorId === admin.id);
                const _kpi = (lbl, val, cor, ic) => `<div style=\"border:1px solid #e6eaf2;border-left:4px solid ${cor};border-radius:10px;padding:12px 14px;background:#fff;\"><div style=\"font-size:.78rem;color:#64748b;\"><i class=\"fas ${ic}\" style=\"color:${cor};\"></i> ${lbl}</div><div style=\"font-size:1.2rem;font-weight:800;color:#0f172a;margin-top:4px;\">${val}</div></div>`;
                const ativos = meusClientes.filter(c => c.licenca && c.ativo !== false && isLicencaValida(c.licenca.dataExpiracao));
"""
assert app[start:].count(old_overview) == 1
new_overview = """                const _distributorOverview = window.TotalGestReportsDistributorMetrics.calculateOverview({
                    admins: dados.administradores || [],
                    distributorId: admin.id,
                    isLicenseValid: isLicencaValida
                });
                const meusClientes = _distributorOverview.clients;
                const _kpi = (lbl, val, cor, ic) => `<div style=\"border:1px solid #e6eaf2;border-left:4px solid ${cor};border-radius:10px;padding:12px 14px;background:#fff;\"><div style=\"font-size:.78rem;color:#64748b;\"><i class=\"fas ${ic}\" style=\"color:${cor};\"></i> ${lbl}</div><div style=\"font-size:1.2rem;font-weight:800;color:#0f172a;margin-top:4px;\">${val}</div></div>`;
                const ativos = _distributorOverview.active;
"""
app = app[:start] + app[start:].replace(old_overview, new_overview, 1)

old_client = """                        const funcs = (dados.funcionarios || []).filter(f => f.adminId === c.id && f.role !== 'admin' && f.role !== 'superadmin').length;
                        const temContratos = moduloContratosAtivo(c), temFrota = moduloFrotaAtivo(c), temArmazem = moduloArmazemAtivo(c), temCrm = moduloCrmAtivo(c);
                        const valorBase = c.precoDistribuidorCobrado != null ? c.precoDistribuidorCobrado : (c.licenca ? parseFloat(getValorPlano(c.licenca.plano)) : 0);
                        const valorAddons = (temContratos ? (c.contratosPlano === 'anual' ? PRECO_CONTRATOS_ANUAL / 12 : PRECO_CONTRATOS_MENSAL) : 0) + (temFrota ? (c.frotaPlano === 'anual' ? PRECO_FROTA_ANUAL / 12 : PRECO_FROTA_MENSAL) : 0) + (temArmazem ? (c.armazemPlano === 'anual' ? PRECO_ARMAZEM_ANUAL / 12 : PRECO_ARMAZEM_MENSAL) : 0) + (temCrm ? (c.crmPlano === 'anual' ? PRECO_CRM_ANUAL / 12 : PRECO_CRM_MENSAL) : 0);
                        const valorCliente = valorBase + valorAddons;
"""
assert app[start:].count(old_client) == 1
new_client = """                        const _clientMetrics = window.TotalGestReportsDistributorMetrics.calculateClient({
                            client: c,
                            data: dados,
                            contractsActive: moduloContratosAtivo,
                            fleetActive: moduloFrotaAtivo,
                            warehouseActive: moduloArmazemAtivo,
                            crmActive: moduloCrmAtivo,
                            getPlanValue: getValorPlano,
                            contractsAnnualPrice: PRECO_CONTRATOS_ANUAL,
                            contractsMonthlyPrice: PRECO_CONTRATOS_MENSAL,
                            fleetAnnualPrice: PRECO_FROTA_ANUAL,
                            fleetMonthlyPrice: PRECO_FROTA_MENSAL,
                            warehouseAnnualPrice: PRECO_ARMAZEM_ANUAL,
                            warehouseMonthlyPrice: PRECO_ARMAZEM_MENSAL,
                            crmAnnualPrice: PRECO_CRM_ANUAL,
                            crmMonthlyPrice: PRECO_CRM_MENSAL
                        });
                        const funcs = _clientMetrics.funcionarios;
                        const temContratos = _clientMetrics.temContratos;
                        const temFrota = _clientMetrics.temFrota;
                        const temArmazem = _clientMetrics.temArmazem;
                        const temCrm = _clientMetrics.temCrm;
                        const valorCliente = _clientMetrics.valorCliente;
"""
app = app[:start] + app[start:].replace(old_client, new_client, 1)

shell_module = "    reportsModuleMetrics: './assets/js/app-reports-module-metrics.js',\n"
assert shell.count(shell_module) == 1
shell = shell.replace(shell_module, shell_module + "    reportsDistributorMetrics: './assets/js/app-reports-distributor-metrics.js',\n", 1)

shell_loader = "    if (options.reportsModuleMetrics === true) pedidos.push(MODULOS.reportsModuleMetrics);\n"
assert shell.count(shell_loader) == 1
shell = shell.replace(shell_loader, shell_loader + "    if (options.reportsDistributorMetrics === true) pedidos.push(MODULOS.reportsDistributorMetrics);\n", 1)

init_token = 'reportsSuperadminMetrics: true, reportsModuleMetrics: true, syncPrepare: true'
assert app.count(init_token) == 1
app = app.replace(init_token, 'reportsSuperadminMetrics: true, reportsModuleMetrics: true, reportsDistributorMetrics: true, syncPrepare: true', 1)

asset_token = "  './assets/js/app-reports-module-metrics.js',\n"
assert sw.count(asset_token) == 1
sw = sw.replace(asset_token, asset_token + "  './assets/js/app-reports-distributor-metrics.js',\n", 1)
assert "const CACHE = 'totalgest-v103';" in sw
sw = sw.replace("const CACHE = 'totalgest-v103';", "const CACHE = 'totalgest-v104';", 1)

assert app.count('window.TotalGestReportsDistributorMetrics.calculateOverview({') == 1
assert app.count('window.TotalGestReportsDistributorMetrics.calculateClient({') == 1
assert app[start:].count("const valorAddons = (temContratos ?") == 0
assert shell.count('reportsDistributorMetrics') == 2
assert sw.count("./assets/js/app-reports-distributor-metrics.js") == 1

APP.write_text(app, encoding='utf-8')
SHELL.write_text(shell, encoding='utf-8')
SW.write_text(sw, encoding='utf-8')
