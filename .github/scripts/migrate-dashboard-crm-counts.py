from pathlib import Path

APP=Path('app.html'); MODULE=Path('assets/js/app-dashboard-counts.js'); SW=Path('sw.js')
app=APP.read_text(encoding='utf-8'); module=MODULE.read_text(encoding='utf-8'); sw=SW.read_text(encoding='utf-8')
fn=app.index('function atualizarContagens()')
start=app.index("            const elCountLeads = document.getElementById('countLeads');", fn)
end=app.index("            const elFrotaResumo = document.getElementById('frotaResumo');", start)
old=app[start:end]
assert old.count("document.getElementById('countLeads')")==1
assert old.count("document.getElementById('countOportunidades')")==1
assert old.count("document.getElementById('countPropostas')")==1
assert old.count("document.getElementById('countComissoes')")==1

new="""            const _crmCounts = window.TotalGestDashboardCounts.calculateCrmCounts({
                data: dados,
                user: usuarioLogado
            });
            const elCountLeads = document.getElementById('countLeads');
            if (elCountLeads) elCountLeads.textContent = _crmCounts.leads;
            const elCountOport = document.getElementById('countOportunidades');
            if (elCountOport) elCountOport.textContent = _crmCounts.oportunidades;
            const elCountProp = document.getElementById('countPropostas');
            if (elCountProp) elCountProp.textContent = _crmCounts.propostas;
            const elCountComissoes = document.getElementById('countComissoes');
            if (elCountComissoes) elCountComissoes.textContent = _crmCounts.comissoes;
"""
app=app[:start]+new+app[end:]
assert app.count('TotalGestDashboardCounts.calculateCrmCounts({')==1

marker='\n  window.TotalGestDashboardCounts = {'
assert module.count(marker)==1
crm_fn="""
  function calculateCrmCounts(options) {
    const opts = options || {};
    const data = opts.data || {};
    const user = opts.user;
    const adminId = user && user.role === 'admin' ? user.id : (user ? user.adminId : undefined);
    return {
      leads: (data.leads || []).filter(l => l.adminId === adminId && l.estado !== 'ganho' && l.estado !== 'perdido').length,
      oportunidades: (data.oportunidades || []).filter(o => o.adminId === adminId && o.estado !== 'ganho' && o.estado !== 'perdido').length,
      propostas: (data.propostas || []).filter(p => p.adminId === adminId && (p.estado === 'enviada' || p.estado === 'visualizada')).length,
      comissoes: (data.oportunidades || []).filter(o => o.adminId === adminId && o.estado === 'ganho' && o.comissaoPercentagem && !o.comissaoPaga).length
    };
  }
"""
module=module.replace(marker,crm_fn+marker,1)
old_export="  window.TotalGestDashboardCounts = { calculateRoleCounts: calculateRoleCounts, calculateStatusCounts: calculateStatusCounts };"
assert module.count(old_export)==1
module=module.replace(old_export,"  window.TotalGestDashboardCounts = { calculateRoleCounts: calculateRoleCounts, calculateStatusCounts: calculateStatusCounts, calculateCrmCounts: calculateCrmCounts };",1)
assert module.count('function calculateCrmCounts(')==1
assert module.count('calculateCrmCounts: calculateCrmCounts')==1
assert "const CACHE = 'totalgest-v109';" in sw
sw=sw.replace("const CACHE = 'totalgest-v109';","const CACHE = 'totalgest-v110';",1)
APP.write_text(app,encoding='utf-8'); MODULE.write_text(module,encoding='utf-8'); SW.write_text(sw,encoding='utf-8')
