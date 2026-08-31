from pathlib import Path

APP=Path('app.html'); SHELL=Path('assets/js/app-shell.js'); SW=Path('sw.js'); MODULE=Path('assets/js/app-reports-module-metrics.js')
app=APP.read_text(encoding='utf-8'); shell=SHELL.read_text(encoding='utf-8'); sw=SW.read_text(encoding='utf-8')
fn='function renderizarReports('; assert app.count(fn)==1
start=app.index(fn)
old="""                const comContratos = admins.filter(a => a.contratosPlano && a.contratosExpiracao && a.contratosExpiracao > Date.now());
                const mensais = comContratos.filter(a => a.contratosPlano === 'mensal').length;
                const anuais = comContratos.filter(a => a.contratosPlano === 'anual').length;
                const receitaManut = mensais * PRECO_CONTRATOS_MENSAL + anuais * PRECO_CONTRATOS_ANUAL;
"""
assert app[start:].count(old)==1
module="""/* Total Gest — métricas dos módulos para Relatórios. */
(function () {
  'use strict';

  function calculateContracts(options) {
    const opts = options || {};
    const admins = opts.admins || [];
    const now = Date.now();
    const active = admins.filter(a => a.contratosPlano && a.contratosExpiracao && a.contratosExpiracao > now);
    const monthly = active.filter(a => a.contratosPlano === 'mensal').length;
    const annual = active.filter(a => a.contratosPlano === 'anual').length;
    return {
      active: active,
      monthly: monthly,
      annual: annual,
      revenue: monthly * opts.monthlyPrice + annual * opts.annualPrice
    };
  }

  window.TotalGestReportsModuleMetrics = {
    calculateContracts: calculateContracts
  };
})();
"""
MODULE.write_text(module,encoding='utf-8')
new="""                const _contratosMetrics = window.TotalGestReportsModuleMetrics.calculateContracts({
                    admins: admins,
                    monthlyPrice: PRECO_CONTRATOS_MENSAL,
                    annualPrice: PRECO_CONTRATOS_ANUAL
                });
                const comContratos = _contratosMetrics.active;
                const mensais = _contratosMetrics.monthly;
                const anuais = _contratosMetrics.annual;
                const receitaManut = _contratosMetrics.revenue;
"""
app=app[:start]+app[start:].replace(old,new,1)
init='reportsSuperadminMetrics: true'; assert app.count(init)==1; app=app.replace(init,init+', reportsModuleMetrics: true',1)
sa="    reportsSuperadminMetrics: './assets/js/app-reports-superadmin-metrics.js',\n"; assert shell.count(sa)==1; shell=shell.replace(sa,sa+"    reportsModuleMetrics: './assets/js/app-reports-module-metrics.js',\n",1)
la="    if (options.reportsSuperadminMetrics === true) pedidos.push(MODULOS.reportsSuperadminMetrics);\n"; assert shell.count(la)==1; shell=shell.replace(la,la+"    if (options.reportsModuleMetrics === true) pedidos.push(MODULOS.reportsModuleMetrics);\n",1)
assert "const CACHE = 'totalgest-v96';" in sw; sw=sw.replace("const CACHE = 'totalgest-v96';","const CACHE = 'totalgest-v97';",1)
swa="  './assets/js/app-reports-superadmin-metrics.js',\n"; assert sw.count(swa)==1; sw=sw.replace(swa,swa+"  './assets/js/app-reports-module-metrics.js',\n",1)
assert app.count('window.TotalGestReportsModuleMetrics.calculateContracts({')==1
assert app[start:].count("admins.filter(a => a.contratosPlano && a.contratosExpiracao && a.contratosExpiracao > Date.now())")==0
assert shell.count('./assets/js/app-reports-module-metrics.js')==1
assert sw.count('./assets/js/app-reports-module-metrics.js')==1
APP.write_text(app,encoding='utf-8'); SHELL.write_text(shell,encoding='utf-8'); SW.write_text(sw,encoding='utf-8')
