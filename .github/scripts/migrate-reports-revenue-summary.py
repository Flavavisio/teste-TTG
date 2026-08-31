from pathlib import Path
APP=Path('app.html'); MOD=Path('assets/js/app-reports-superadmin-metrics.js'); SW=Path('sw.js')
app=APP.read_text(encoding='utf-8'); mod=MOD.read_text(encoding='utf-8'); sw=SW.read_text(encoding='utf-8')
start=app.index('function renderizarReports(')
bs=app.index("                const _adm = admins.filter(a => a.id !== 'superadmin');",start)
be=app.index("                let barras = '';",bs)
old=app[bs:be]
assert old.count('let recBase = 0;')==1 and old.count('const mods =')==1 and old.count('const recTot =')==1
new="""                const _revenueSummary = window.TotalGestReportsSuperadminMetrics.calculateRevenueSummary({
                    admins: admins,
                    baseValueCharged: valorBaseCobradoDe,
                    contractsRevenue: receitaManut,
                    fleetRevenue: receitaFrota,
                    warehouseRevenue: receitaArmazem,
                    notificationsRevenue: receitaNotif,
                    crmRevenue: receitaCrm
                });
                const mods = _revenueSummary.modules;
                const maxMod = _revenueSummary.maxModuleRevenue;
                const recTot = _revenueSummary.totalRevenue;
"""
app=app[:bs]+new+app[be:]
needle='  window.TotalGestReportsSuperadminMetrics = { calculate: calculate, calculateCompany: calculateCompany };\n'
assert mod.count(needle)==1
addition="""
  function calculateRevenueSummary(options) {
    const opts = options || {};
    const admins = (opts.admins || []).filter(a => a.id !== 'superadmin');
    let baseRevenue = 0;
    admins.forEach(a => {
      if (a.licenca && a.ativo !== false && a.licenca.dataExpiracao > Date.now()) baseRevenue += opts.baseValueCharged(a);
    });
    const modules = [
      { l: 'Licenças base', v: baseRevenue, c: '#2563eb' },
      { l: 'Contratos', v: opts.contractsRevenue, c: '#16a34a' },
      { l: 'Frota', v: opts.fleetRevenue, c: '#0ea5e9' },
      { l: 'Armazém', v: opts.warehouseRevenue, c: '#b45309' },
      { l: 'Notificações', v: opts.notificationsRevenue, c: '#e11d48' },
      { l: 'CRM + Assist', v: opts.crmRevenue, c: '#7c3aed' }
    ];
    return {
      modules: modules,
      maxModuleRevenue: Math.max(1, ...modules.map(m => m.v)),
      totalRevenue: baseRevenue + opts.contractsRevenue + opts.fleetRevenue + opts.warehouseRevenue + opts.notificationsRevenue + opts.crmRevenue
    };
  }

"""
mod=mod.replace(needle,addition+'  window.TotalGestReportsSuperadminMetrics = { calculate: calculate, calculateCompany: calculateCompany, calculateRevenueSummary: calculateRevenueSummary };\n',1)
assert app.count('TotalGestReportsSuperadminMetrics.calculateRevenueSummary({')==1
assert "const CACHE = 'totalgest-v102';" in sw
sw=sw.replace("const CACHE = 'totalgest-v102';","const CACHE = 'totalgest-v103';",1)
APP.write_text(app,encoding='utf-8'); MOD.write_text(mod,encoding='utf-8'); SW.write_text(sw,encoding='utf-8')
