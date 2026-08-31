from pathlib import Path
APP=Path('app.html'); MOD=Path('assets/js/app-reports-module-metrics.js'); SW=Path('sw.js')
app=APP.read_text(encoding='utf-8'); mod=MOD.read_text(encoding='utf-8'); sw=SW.read_text(encoding='utf-8')
start=app.index('function renderizarReports(')
old_erp="""                const comErp = admins.filter(a => a.id !== 'superadmin' && moduloErpAtivo(a));
                const erpMensais = comErp.filter(a => a.erpPlano === 'mensal').length;
                const erpAnuais = comErp.filter(a => a.erpPlano === 'anual').length;
                const erpDemos = comErp.filter(a => a.erpPlano === 'demo').length;
                const receitaErp = erpMensais * PRECO_ERP_MENSAL + erpAnuais * PRECO_ERP_ANUAL;
"""
old_rounds="""                const comRondas = admins.filter(a => a.id !== 'superadmin' && moduloRondasAtivo(a));
                const rondasMensais = comRondas.filter(a => a.rondasPlano === 'mensal').length;
                const rondasAnuais = comRondas.filter(a => a.rondasPlano === 'anual').length;
                const rondasDemos = comRondas.filter(a => a.rondasPlano === 'demo').length;
                const receitaRondas = rondasMensais * PRECO_RONDAS_MENSAL + rondasAnuais * PRECO_RONDAS_ANUAL;
"""
assert app[start:].count(old_erp)==1, 'ERP block mismatch'
assert app[start:].count(old_rounds)==1, 'Rondas block mismatch'
needle="""  window.TotalGestReportsModuleMetrics = {
    calculateContracts: calculateContracts,
    calculateFleet: calculateFleet,
    calculateWarehouse: calculateWarehouse,
    calculateNotifications: calculateNotifications,
    calculateCrm: calculateCrm
  };
"""
assert mod.count(needle)==1
addition="""
  function calculatePlanModule(options, planField) {
    const opts = options || {};
    const admins = opts.admins || [];
    const isActive = opts.isActive;
    const active = admins.filter(a => a.id !== 'superadmin' && isActive(a));
    const monthly = active.filter(a => a[planField] === 'mensal').length;
    const annual = active.filter(a => a[planField] === 'anual').length;
    const demos = active.filter(a => a[planField] === 'demo').length;
    return { active: active, monthly: monthly, annual: annual, demos: demos,
      revenue: monthly * opts.monthlyPrice + annual * opts.annualPrice };
  }

  function calculateErp(options) { return calculatePlanModule(options, 'erpPlano'); }
  function calculateRounds(options) { return calculatePlanModule(options, 'rondasPlano'); }

"""
mod=mod.replace(needle,addition+"""  window.TotalGestReportsModuleMetrics = {
    calculateContracts: calculateContracts,
    calculateFleet: calculateFleet,
    calculateWarehouse: calculateWarehouse,
    calculateNotifications: calculateNotifications,
    calculateCrm: calculateCrm,
    calculateErp: calculateErp,
    calculateRounds: calculateRounds
  };
""",1)
new_erp="""                const _erpMetrics = window.TotalGestReportsModuleMetrics.calculateErp({
                    admins: admins, isActive: moduloErpAtivo,
                    monthlyPrice: PRECO_ERP_MENSAL, annualPrice: PRECO_ERP_ANUAL
                });
                const comErp = _erpMetrics.active;
                const erpMensais = _erpMetrics.monthly;
                const erpAnuais = _erpMetrics.annual;
                const erpDemos = _erpMetrics.demos;
                const receitaErp = _erpMetrics.revenue;
"""
new_rounds="""                const _roundsMetrics = window.TotalGestReportsModuleMetrics.calculateRounds({
                    admins: admins, isActive: moduloRondasAtivo,
                    monthlyPrice: PRECO_RONDAS_MENSAL, annualPrice: PRECO_RONDAS_ANUAL
                });
                const comRondas = _roundsMetrics.active;
                const rondasMensais = _roundsMetrics.monthly;
                const rondasAnuais = _roundsMetrics.annual;
                const rondasDemos = _roundsMetrics.demos;
                const receitaRondas = _roundsMetrics.revenue;
"""
app=app[:start]+app[start:].replace(old_erp,new_erp,1).replace(old_rounds,new_rounds,1)
assert "const CACHE = 'totalgest-v101';" in sw
sw=sw.replace("const CACHE = 'totalgest-v101';","const CACHE = 'totalgest-v102';",1)
assert app.count('calculateErp({')==1 and app.count('calculateRounds({')==1
assert mod.count('function calculateErp(options)')==1 and mod.count('function calculateRounds(options)')==1
APP.write_text(app,encoding='utf-8'); MOD.write_text(mod,encoding='utf-8'); SW.write_text(sw,encoding='utf-8')
