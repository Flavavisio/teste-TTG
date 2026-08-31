from pathlib import Path

APP=Path('app.html'); MODULE=Path('assets/js/app-reports-module-metrics.js'); SW=Path('sw.js')
app=APP.read_text(encoding='utf-8'); module=MODULE.read_text(encoding='utf-8'); sw=SW.read_text(encoding='utf-8')
fn='function renderizarReports('; assert app.count(fn)==1
start=app.index(fn)
old="""                const comFrota = admins.filter(a => a.frotaPlano && a.frotaExpiracao && a.frotaExpiracao > Date.now());
                const frotaMensais = comFrota.filter(a => a.frotaPlano === 'mensal').length;
                const frotaAnuais = comFrota.filter(a => a.frotaPlano === 'anual').length;
                const receitaFrota = frotaMensais * PRECO_FROTA_MENSAL + frotaAnuais * PRECO_FROTA_ANUAL;
"""
assert app[start:].count(old)==1
needle="""  window.TotalGestReportsModuleMetrics = {
    calculateContracts: calculateContracts
  };
"""
assert module.count(needle)==1
addition="""
  function calculateFleet(options) {
    const opts = options || {};
    const admins = opts.admins || [];
    const now = Date.now();
    const active = admins.filter(a => a.frotaPlano && a.frotaExpiracao && a.frotaExpiracao > now);
    const monthly = active.filter(a => a.frotaPlano === 'mensal').length;
    const annual = active.filter(a => a.frotaPlano === 'anual').length;
    return {
      active: active,
      monthly: monthly,
      annual: annual,
      revenue: monthly * opts.monthlyPrice + annual * opts.annualPrice
    };
  }

"""
module=module.replace(needle,addition+"""  window.TotalGestReportsModuleMetrics = {
    calculateContracts: calculateContracts,
    calculateFleet: calculateFleet
  };
""",1)
new="""                const _frotaMetrics = window.TotalGestReportsModuleMetrics.calculateFleet({
                    admins: admins,
                    monthlyPrice: PRECO_FROTA_MENSAL,
                    annualPrice: PRECO_FROTA_ANUAL
                });
                const comFrota = _frotaMetrics.active;
                const frotaMensais = _frotaMetrics.monthly;
                const frotaAnuais = _frotaMetrics.annual;
                const receitaFrota = _frotaMetrics.revenue;
"""
app=app[:start]+app[start:].replace(old,new,1)
assert "const CACHE = 'totalgest-v97';" in sw
sw=sw.replace("const CACHE = 'totalgest-v97';","const CACHE = 'totalgest-v98';",1)
assert app.count('window.TotalGestReportsModuleMetrics.calculateFleet({')==1
assert app[start:].count("admins.filter(a => a.frotaPlano && a.frotaExpiracao && a.frotaExpiracao > Date.now())")==0
assert module.count('function calculateFleet(options) {')==1
APP.write_text(app,encoding='utf-8'); MODULE.write_text(module,encoding='utf-8'); SW.write_text(sw,encoding='utf-8')
