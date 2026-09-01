from pathlib import Path

APP=Path('app.html'); MODULE=Path('assets/js/app-dashboard-counts.js'); SW=Path('sw.js')
app=APP.read_text(encoding='utf-8'); module=MODULE.read_text(encoding='utf-8'); sw=SW.read_text(encoding='utf-8')
fn=app.index('function atualizarContagens()')
start=app.index("                    const cts = (dados.contratos || []).filter(c => c.adminId === aId);", fn)
end=app.index("                    elCtResumo.innerHTML = `", start)
calc=app[start:end]
assert calc.count('const cts =')==1
assert calc.count('let ed = 0, av = 0, vc = 0;')==1
assert calc.count('estadoManutencao(calcularProximaManutencao(c)).chave')==1
new="""                    const _contractSummary = window.TotalGestDashboardCounts.calculateContractSummary({
                        contracts: dados.contratos,
                        adminId: aId,
                        getNextMaintenance: calcularProximaManutencao,
                        maintenanceState: estadoManutencao
                    });
"""
app=app[:start]+new+app[end:]
old_html="""                    elCtResumo.innerHTML = `<span class="count">${cts.length}</span> total · <span style="color:#16a34a;">${ed}</span> em dia · <span style="color:#f59e0b;">${av}</span> a vencer · <span style="color:#dc2626;">${vc}</span> venc.`;"""
assert app.count(old_html)==1
new_html="""                    elCtResumo.innerHTML = `<span class="count">${_contractSummary.total}</span> total · <span style="color:#16a34a;">${_contractSummary.emDia}</span> em dia · <span style="color:#f59e0b;">${_contractSummary.aVencer}</span> a vencer · <span style="color:#dc2626;">${_contractSummary.vencido}</span> venc.`;"""
app=app.replace(old_html,new_html,1)
assert app.count('TotalGestDashboardCounts.calculateContractSummary({')==1

marker='\n  window.TotalGestDashboardCounts = {'
assert module.count(marker)==1
fn_text="""
  function calculateContractSummary(options) {
    const opts = options || {};
    const contracts = (opts.contracts || []).filter(c => c.adminId === opts.adminId);
    let emDia = 0;
    let aVencer = 0;
    let vencido = 0;
    contracts.forEach(c => {
      const chave = opts.maintenanceState(opts.getNextMaintenance(c)).chave;
      if (chave === 'vencido') vencido++;
      else if (chave === 'a_vencer') aVencer++;
      else if (chave === 'em_dia') emDia++;
    });
    return { total: contracts.length, emDia: emDia, aVencer: aVencer, vencido: vencido };
  }
"""
module=module.replace(marker,fn_text+marker,1)
old_export="  window.TotalGestDashboardCounts = { calculateRoleCounts: calculateRoleCounts, calculateStatusCounts: calculateStatusCounts, calculateCrmCounts: calculateCrmCounts };"
assert module.count(old_export)==1
module=module.replace(old_export,"  window.TotalGestDashboardCounts = { calculateRoleCounts: calculateRoleCounts, calculateStatusCounts: calculateStatusCounts, calculateCrmCounts: calculateCrmCounts, calculateContractSummary: calculateContractSummary };",1)
assert module.count('function calculateContractSummary(')==1
assert module.count('calculateContractSummary: calculateContractSummary')==1
assert "const CACHE = 'totalgest-v110';" in sw
sw=sw.replace("const CACHE = 'totalgest-v110';","const CACHE = 'totalgest-v111';",1)
APP.write_text(app,encoding='utf-8'); MODULE.write_text(module,encoding='utf-8'); SW.write_text(sw,encoding='utf-8')
