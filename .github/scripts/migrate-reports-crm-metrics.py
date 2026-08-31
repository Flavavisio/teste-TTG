from pathlib import Path

APP=Path('app.html'); MODULE=Path('assets/js/app-reports-module-metrics.js'); SW=Path('sw.js')
app=APP.read_text(encoding='utf-8'); module=MODULE.read_text(encoding='utf-8'); sw=SW.read_text(encoding='utf-8')
fn='function renderizarReports('; assert app.count(fn)==1
start=app.index(fn)
old="""                const comCrm = admins.filter(a => a.id !== 'superadmin' && moduloCrmAtivo(a));
                const crmMensais = comCrm.filter(a => a.crmPlano === 'mensal').length;
                const crmAnuais = comCrm.filter(a => a.crmPlano === 'anual').length;
                const crmDemos = comCrm.filter(a => a.crmPlano === 'demo').length;
                const receitaCrm = crmMensais * PRECO_CRM_MENSAL + crmAnuais * PRECO_CRM_ANUAL;
"""
assert app[start:].count(old)==1
needle="""  window.TotalGestReportsModuleMetrics = {
    calculateContracts: calculateContracts,
    calculateFleet: calculateFleet,
    calculateWarehouse: calculateWarehouse,
    calculateNotifications: calculateNotifications
  };
"""
assert module.count(needle)==1
addition="""
  function calculateCrm(options) {
    const opts = options || {};
    const admins = opts.admins || [];
    const isActive = opts.isActive;
    const active = admins.filter(a => a.id !== 'superadmin' && isActive(a));
    const monthly = active.filter(a => a.crmPlano === 'mensal').length;
    const annual = active.filter(a => a.crmPlano === 'anual').length;
    const demos = active.filter(a => a.crmPlano === 'demo').length;
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
    calculateWarehouse: calculateWarehouse,
    calculateNotifications: calculateNotifications,
    calculateCrm: calculateCrm
  };
""",1)
new="""                const _crmMetrics = window.TotalGestReportsModuleMetrics.calculateCrm({
                    admins: admins,
                    isActive: moduloCrmAtivo,
                    monthlyPrice: PRECO_CRM_MENSAL,
                    annualPrice: PRECO_CRM_ANUAL
                });
                const comCrm = _crmMetrics.active;
                const crmMensais = _crmMetrics.monthly;
                const crmAnuais = _crmMetrics.annual;
                const crmDemos = _crmMetrics.demos;
                const receitaCrm = _crmMetrics.revenue;
"""
app=app[:start]+app[start:].replace(old,new,1)
assert "const CACHE = 'totalgest-v100';" in sw
sw=sw.replace("const CACHE = 'totalgest-v100';","const CACHE = 'totalgest-v101';",1)
assert app.count('window.TotalGestReportsModuleMetrics.calculateCrm({')==1
assert app[start:].count("admins.filter(a => a.id !== 'superadmin' && moduloCrmAtivo(a))")==0
assert module.count('function calculateCrm(options) {')==1
APP.write_text(app,encoding='utf-8'); MODULE.write_text(module,encoding='utf-8'); SW.write_text(sw,encoding='utf-8')
