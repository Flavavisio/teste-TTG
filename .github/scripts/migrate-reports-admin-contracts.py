from pathlib import Path

APP=Path('app.html'); MODULE=Path('assets/js/app-reports-distributor-metrics.js'); SW=Path('sw.js')
app=APP.read_text(encoding='utf-8'); module=MODULE.read_text(encoding='utf-8'); sw=SW.read_text(encoding='utf-8')
start=app.index('function renderizarReports(')
old="""            const contratosAdmin = (dados.contratos || []).filter(c => c.adminId === admin.id);
            let ctEmDia = 0, ctAVencer = 0, ctVencidos = 0, ctValor = 0;
            contratosAdmin.forEach(c => {
                const ch = estadoManutencao(calcularProximaManutencao(c)).chave;
                if (ch === 'vencido') ctVencidos++; else if (ch === 'a_vencer') ctAVencer++; else if (ch === 'em_dia') ctEmDia++;
                ctValor += numOrd(c.valor);
            });
"""
assert app[start:].count(old)==1
new="""            const _adminContracts = window.TotalGestReportsDistributorMetrics.calculateAdminContracts({
                data: dados,
                adminId: admin.id,
                maintenanceState: estadoManutencao,
                nextMaintenance: calcularProximaManutencao,
                toNumber: numOrd
            });
            const contratosAdmin = _adminContracts.contracts;
            const ctEmDia = _adminContracts.emDia;
            const ctAVencer = _adminContracts.aVencer;
            const ctVencidos = _adminContracts.vencidos;
            const ctValor = _adminContracts.valor;
"""
app=app[:start]+app[start:].replace(old,new,1)
insert="""
  function calculateAdminContracts(options) {
    const opts = options || {};
    const data = opts.data || {};
    const contracts = (data.contratos || []).filter(c => c.adminId === opts.adminId);
    let emDia = 0, aVencer = 0, vencidos = 0, valor = 0;
    contracts.forEach(c => {
      const chave = opts.maintenanceState(opts.nextMaintenance(c)).chave;
      if (chave === 'vencido') vencidos++;
      else if (chave === 'a_vencer') aVencer++;
      else if (chave === 'em_dia') emDia++;
      valor += opts.toNumber(c.valor);
    });
    return { contracts: contracts, emDia: emDia, aVencer: aVencer, vencidos: vencidos, valor: valor };
  }
"""
marker='\n  window.TotalGestReportsDistributorMetrics = {'
assert module.count(marker)==1
module=module.replace(marker,insert+marker,1)
assert module.count('    calculateAdminOverview: calculateAdminOverview\n')==1
module=module.replace('    calculateAdminOverview: calculateAdminOverview\n','    calculateAdminOverview: calculateAdminOverview,\n    calculateAdminContracts: calculateAdminContracts\n',1)
assert app.count('TotalGestReportsDistributorMetrics.calculateAdminContracts({')==1
assert module.count('function calculateAdminContracts(')==1
assert module.count('calculateAdminContracts: calculateAdminContracts')==1
assert "const CACHE = 'totalgest-v105';" in sw
sw=sw.replace("const CACHE = 'totalgest-v105';","const CACHE = 'totalgest-v106';",1)
APP.write_text(app,encoding='utf-8'); MODULE.write_text(module,encoding='utf-8'); SW.write_text(sw,encoding='utf-8')
