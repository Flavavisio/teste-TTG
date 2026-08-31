from pathlib import Path

APP=Path('app.html'); MODULE=Path('assets/js/app-reports-module-metrics.js'); SW=Path('sw.js')
app=APP.read_text(encoding='utf-8'); module=MODULE.read_text(encoding='utf-8'); sw=SW.read_text(encoding='utf-8')
fn='function renderizarReports('; assert app.count(fn)==1
start=app.index(fn)
old="""                const comArmazem = admins.filter(a => a.id !== 'superadmin' && moduloArmazemAtivo(a));
                const armMensais = comArmazem.filter(a => a.armazemPlano === 'mensal').length;
                const armAnuais = comArmazem.filter(a => a.armazemPlano === 'anual').length;
                const armDemos = comArmazem.filter(a => a.armazemPlano === 'demo').length;
                const receitaArmazem = armMensais * PRECO_ARMAZEM_MENSAL + armAnuais * PRECO_ARMAZEM_ANUAL;
"""
assert app[start:].count(old)==1
needle="""  window.TotalGestReportsModuleMetrics = {
    calculateContracts: calculateContracts,
    calculateFleet: calculateFleet
  };
"""
assert module.count(needle)==1
addition="""
  function calculateWarehouse(options) {
    const opts = options || {};
    const admins = opts.admins || [];
    const isActive = opts.isActive;
    const active = admins.filter(a => a.id !== 'superadmin' && isActive(a));
    const monthly = active.filter(a => a.armazemPlano === 'mensal').length;
    const annual = active.filter(a => a.armazemPlano === 'anual').length;
    const demos = active.filter(a => a.armazemPlano === 'demo').length;
    return {
      active: active,
      monthly: monthly,
      annual: annual,
      demos: demos,
      revenue: monthly * opts.monthlyPrice + annual * opts.annualPrice
    };
  }

"""
module=module.replace(needle,addition+"""  window.TotalGestReportsModuleMetrics = {
    calculateContracts: calculateContracts,
    calculateFleet: calculateFleet,
    calculateWarehouse: calculateWarehouse
  };
""",1)
new="""                const _warehouseMetrics = window.TotalGestReportsModuleMetrics.calculateWarehouse({
                    admins: admins,
                    isActive: moduloArmazemAtivo,
                    monthlyPrice: PRECO_ARMAZEM_MENSAL,
                    annualPrice: PRECO_ARMAZEM_ANUAL
                });
                const comArmazem = _warehouseMetrics.active;
                const armMensais = _warehouseMetrics.monthly;
                const armAnuais = _warehouseMetrics.annual;
                const armDemos = _warehouseMetrics.demos;
                const receitaArmazem = _warehouseMetrics.revenue;
"""
app=app[:start]+app[start:].replace(old,new,1)
assert "const CACHE = 'totalgest-v98';" in sw
sw=sw.replace("const CACHE = 'totalgest-v98';","const CACHE = 'totalgest-v99';",1)
assert app.count('window.TotalGestReportsModuleMetrics.calculateWarehouse({')==1
assert app[start:].count("admins.filter(a => a.id !== 'superadmin' && moduloArmazemAtivo(a))")==0
assert module.count('function calculateWarehouse(options) {')==1
APP.write_text(app,encoding='utf-8'); MODULE.write_text(module,encoding='utf-8'); SW.write_text(sw,encoding='utf-8')
