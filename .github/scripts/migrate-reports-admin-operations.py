from pathlib import Path
APP=Path('app.html'); MODULE=Path('assets/js/app-reports-distributor-metrics.js'); SW=Path('sw.js')
app=APP.read_text(encoding='utf-8'); module=MODULE.read_text(encoding='utf-8'); sw=SW.read_text(encoding='utf-8')
start=app.index('function renderizarReports(')
old="""            const totalLocais = (dados.locais || []).filter(l => l.adminId === admin.id).length;
            const totalEquip = (dados.equipamentos || []).filter(e => e.adminId === admin.id).length;
            const totalRegistos = (dados.registosManutencao || []).filter(r => r.adminId === admin.id).length;
            const moduloAtivoTxt = moduloContratosAtivo(admin) ? ('Ativo (' + (admin.contratosPlano === 'demo' ? 'Demo' : admin.contratosPlano === 'anual' ? 'Anual' : 'Mensal') + ')') : 'Inativo';
            const folhasOT = (dados.folhasObra || []).filter(f => f.adminId === admin.id && f.contratoId).length;
            const frotaStats = contarFrota((dados.veiculos || []).filter(v => v.adminId === admin.id));
            const totalIntervencoes = (dados.veiculoIntervencoes || []).filter(i => i.adminId === admin.id).length;
            const gastoVeiculos = (dados.veiculoIntervencoes || []).filter(i => i.adminId === admin.id).reduce((s, i) => s + (Number(i.custo) || 0), 0);
            const totalSinistros = (dados.veiculoSinistros || []).filter(s => s.adminId === admin.id).length;
            const ajudasAdmin = (dados.ajudas || []).filter(a => a.adminId === admin.id);
            const ajPend = ajudasAdmin.filter(a => a.status === 'pendente').length;
            const ajConcl = ajudasAdmin.filter(a => (a.status || '').toLowerCase().includes('conclu')).length;
"""
assert app[start:].count(old)==1
new="""            const _adminOperations = window.TotalGestReportsDistributorMetrics.calculateAdminOperations({
                data: dados,
                admin: admin,
                contractsActive: moduloContratosAtivo,
                countFleet: contarFrota
            });
            const totalLocais = _adminOperations.totalLocais;
            const totalEquip = _adminOperations.totalEquip;
            const totalRegistos = _adminOperations.totalRegistos;
            const moduloAtivoTxt = _adminOperations.moduloAtivoTxt;
            const folhasOT = _adminOperations.folhasOT;
            const frotaStats = _adminOperations.frotaStats;
            const totalIntervencoes = _adminOperations.totalIntervencoes;
            const gastoVeiculos = _adminOperations.gastoVeiculos;
            const totalSinistros = _adminOperations.totalSinistros;
            const ajudasAdmin = _adminOperations.ajudasAdmin;
            const ajPend = _adminOperations.ajPend;
            const ajConcl = _adminOperations.ajConcl;
"""
app=app[:start]+app[start:].replace(old,new,1)
insert="""
  function calculateAdminOperations(options) {
    const opts = options || {}, data = opts.data || {}, admin = opts.admin || {}, adminId = admin.id;
    const totalLocais = (data.locais || []).filter(l => l.adminId === adminId).length;
    const totalEquip = (data.equipamentos || []).filter(e => e.adminId === adminId).length;
    const totalRegistos = (data.registosManutencao || []).filter(r => r.adminId === adminId).length;
    const moduloAtivoTxt = opts.contractsActive(admin) ? ('Ativo (' + (admin.contratosPlano === 'demo' ? 'Demo' : admin.contratosPlano === 'anual' ? 'Anual' : 'Mensal') + ')') : 'Inativo';
    const folhasOT = (data.folhasObra || []).filter(f => f.adminId === adminId && f.contratoId).length;
    const frotaStats = opts.countFleet((data.veiculos || []).filter(v => v.adminId === adminId));
    const intervencoes = (data.veiculoIntervencoes || []).filter(i => i.adminId === adminId);
    const totalIntervencoes = intervencoes.length;
    const gastoVeiculos = intervencoes.reduce((s, i) => s + (Number(i.custo) || 0), 0);
    const totalSinistros = (data.veiculoSinistros || []).filter(s => s.adminId === adminId).length;
    const ajudasAdmin = (data.ajudas || []).filter(a => a.adminId === adminId);
    return { totalLocais,totalEquip,totalRegistos,moduloAtivoTxt,folhasOT,frotaStats,totalIntervencoes,gastoVeiculos,totalSinistros,ajudasAdmin,ajPend:ajudasAdmin.filter(a=>a.status==='pendente').length,ajConcl:ajudasAdmin.filter(a=>(a.status||'').toLowerCase().includes('conclu')).length };
  }
"""
marker='\n  window.TotalGestReportsDistributorMetrics = {'
assert module.count(marker)==1
module=module.replace(marker,insert+marker,1)
assert module.count('    calculateAdminContracts: calculateAdminContracts\n')==1
module=module.replace('    calculateAdminContracts: calculateAdminContracts\n','    calculateAdminContracts: calculateAdminContracts,\n    calculateAdminOperations: calculateAdminOperations\n',1)
assert app.count('TotalGestReportsDistributorMetrics.calculateAdminOperations({')==1
assert module.count('function calculateAdminOperations(')==1
assert "const CACHE = 'totalgest-v106';" in sw
sw=sw.replace("const CACHE = 'totalgest-v106';","const CACHE = 'totalgest-v107';",1)
APP.write_text(app,encoding='utf-8'); MODULE.write_text(module,encoding='utf-8'); SW.write_text(sw,encoding='utf-8')
