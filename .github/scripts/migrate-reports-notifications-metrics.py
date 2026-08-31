from pathlib import Path

APP=Path('app.html'); MODULE=Path('assets/js/app-reports-module-metrics.js'); SW=Path('sw.js')
app=APP.read_text(encoding='utf-8'); module=MODULE.read_text(encoding='utf-8'); sw=SW.read_text(encoding='utf-8')
fn='function renderizarReports('; assert app.count(fn)==1
start=app.index(fn)
old="""                const comNotif = admins.filter(a => a.id !== 'superadmin' && moduloNotificacoesAtivo(a));
                const notifMensais = comNotif.filter(a => a.notificacoesPlano === 'mensal').length;
                const notifAnuais = comNotif.filter(a => a.notificacoesPlano === 'anual').length;
                const notifDemos = comNotif.filter(a => a.notificacoesPlano === 'demo').length;
                const receitaNotif = notifMensais * PRECO_NOTIFICACOES_MENSAL + notifAnuais * PRECO_NOTIFICACOES_ANUAL;
"""
assert app[start:].count(old)==1
needle="""  window.TotalGestReportsModuleMetrics = {
    calculateContracts: calculateContracts,
    calculateFleet: calculateFleet,
    calculateWarehouse: calculateWarehouse
  };
"""
assert module.count(needle)==1
addition="""
  function calculateNotifications(options) {
    const opts = options || {};
    const admins = opts.admins || [];
    const isActive = opts.isActive;
    const active = admins.filter(a => a.id !== 'superadmin' && isActive(a));
    const monthly = active.filter(a => a.notificacoesPlano === 'mensal').length;
    const annual = active.filter(a => a.notificacoesPlano === 'anual').length;
    const demos = active.filter(a => a.notificacoesPlano === 'demo').length;
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
    calculateNotifications: calculateNotifications
  };
""",1)
new="""                const _notificationsMetrics = window.TotalGestReportsModuleMetrics.calculateNotifications({
                    admins: admins,
                    isActive: moduloNotificacoesAtivo,
                    monthlyPrice: PRECO_NOTIFICACOES_MENSAL,
                    annualPrice: PRECO_NOTIFICACOES_ANUAL
                });
                const comNotif = _notificationsMetrics.active;
                const notifMensais = _notificationsMetrics.monthly;
                const notifAnuais = _notificationsMetrics.annual;
                const notifDemos = _notificationsMetrics.demos;
                const receitaNotif = _notificationsMetrics.revenue;
"""
app=app[:start]+app[start:].replace(old,new,1)
assert "const CACHE = 'totalgest-v99';" in sw
sw=sw.replace("const CACHE = 'totalgest-v99';","const CACHE = 'totalgest-v100';",1)
assert app.count('window.TotalGestReportsModuleMetrics.calculateNotifications({')==1
assert app[start:].count("admins.filter(a => a.id !== 'superadmin' && moduloNotificacoesAtivo(a))")==0
assert module.count('function calculateNotifications(options) {')==1
APP.write_text(app,encoding='utf-8'); MODULE.write_text(module,encoding='utf-8'); SW.write_text(sw,encoding='utf-8')
