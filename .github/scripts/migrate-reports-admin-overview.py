from pathlib import Path

APP=Path('app.html')
MODULE=Path('assets/js/app-reports-distributor-metrics.js')
SW=Path('sw.js')
app=APP.read_text(encoding='utf-8')
module=MODULE.read_text(encoding='utf-8')
sw=SW.read_text(encoding='utf-8')
start=app.index('function renderizarReports(')

old="""            const totalFunc = dados.funcionarios ? dados.funcionarios.filter(f => f.adminId === admin.id && f.role !== 'admin')
                .length : 0;
            const totalCli = dados.clientes ? dados.clientes.filter(c => c.adminId === admin.id).length : 0;
            const totalOS = dados.servicos ? dados.servicos.filter(s => s.adminId === admin.id).length : 0;
            const osPend = dados.servicos ? dados.servicos.filter(s => s.adminId === admin.id && s.status === 'pendente')
                .length : 0;
            const totalPonto = dados.ponto ? dados.ponto.filter(p => p.adminId === admin.id).length : 0;
            const totalPedidos = dados.pedidos ? dados.pedidos.filter(p => p.adminId === admin.id).length : 0;
            const pedPend = dados.pedidos ? dados.pedidos.filter(p => p.adminId === admin.id && p.status === 'pendente_aprov')
                .length : 0;
            const totalFolhas = dados.folhasObra ? dados.folhasObra.filter(f => f.adminId === admin.id).length : 0;
            const totalReqs = dados.requisicoes ? dados.requisicoes.filter(r => r.adminId === admin.id).length : 0;
            const reqPend = dados.requisicoes ? dados.requisicoes.filter(r =>
                r.adminId === admin.id && r.status === 'pendente_aprov'
            ).length : 0;
            const totalEncarregados = dados.encarregados ? dados.encarregados.filter(e => e.adminId === admin.id).length : 0;
            const numOrd = (v) => (v === '' || v == null) ? 0 : (Number(v) || 0);
            const gastoFunc = (dados.funcionarios || [])
                .filter(f => f.adminId === admin.id && f.role === 'funcionario')
                .reduce((s, f) => s + numOrd(f.ordenadoBruto), 0);
            const gastoEnc = (dados.encarregados || [])
                .filter(e => e.adminId === admin.id)
                .reduce((s, e) => s + numOrd(e.ordenadoBruto), 0);
            const gastoTotal = gastoFunc + gastoEnc;
            const osList = (dados.servicos || []).filter(s => s.adminId === admin.id);
            const osPendentes = osList.filter(s => s.status === 'pendente').length;
            const osAndamento = osList.filter(s => s.status === 'em andamento' || s.status === 'em_andamento').length;
            const osConcluidas = osList.filter(s => (s.status || '').toLowerCase().includes('conclu')).length;
"""
assert app[start:].count(old)==1
new="""            const _adminOverview = window.TotalGestReportsDistributorMetrics.calculateAdminOverview({
                data: dados,
                adminId: admin.id
            });
            const totalFunc = _adminOverview.totalFunc;
            const totalCli = _adminOverview.totalCli;
            const totalOS = _adminOverview.totalOS;
            const osPend = _adminOverview.osPend;
            const totalPonto = _adminOverview.totalPonto;
            const totalPedidos = _adminOverview.totalPedidos;
            const pedPend = _adminOverview.pedPend;
            const totalFolhas = _adminOverview.totalFolhas;
            const totalReqs = _adminOverview.totalReqs;
            const reqPend = _adminOverview.reqPend;
            const totalEncarregados = _adminOverview.totalEncarregados;
            const numOrd = _adminOverview.numOrd;
            const gastoFunc = _adminOverview.gastoFunc;
            const gastoEnc = _adminOverview.gastoEnc;
            const gastoTotal = _adminOverview.gastoTotal;
            const osList = _adminOverview.osList;
            const osPendentes = _adminOverview.osPendentes;
            const osAndamento = _adminOverview.osAndamento;
            const osConcluidas = _adminOverview.osConcluidas;
"""
app=app[:start]+app[start:].replace(old,new,1)

insert="""
  function calculateAdminOverview(options) {
    const opts = options || {};
    const data = opts.data || {};
    const adminId = opts.adminId;
    const totalFunc = data.funcionarios ? data.funcionarios.filter(f => f.adminId === adminId && f.role !== 'admin').length : 0;
    const totalCli = data.clientes ? data.clientes.filter(c => c.adminId === adminId).length : 0;
    const totalOS = data.servicos ? data.servicos.filter(s => s.adminId === adminId).length : 0;
    const osPend = data.servicos ? data.servicos.filter(s => s.adminId === adminId && s.status === 'pendente').length : 0;
    const totalPonto = data.ponto ? data.ponto.filter(p => p.adminId === adminId).length : 0;
    const totalPedidos = data.pedidos ? data.pedidos.filter(p => p.adminId === adminId).length : 0;
    const pedPend = data.pedidos ? data.pedidos.filter(p => p.adminId === adminId && p.status === 'pendente_aprov').length : 0;
    const totalFolhas = data.folhasObra ? data.folhasObra.filter(f => f.adminId === adminId).length : 0;
    const totalReqs = data.requisicoes ? data.requisicoes.filter(r => r.adminId === adminId).length : 0;
    const reqPend = data.requisicoes ? data.requisicoes.filter(r => r.adminId === adminId && r.status === 'pendente_aprov').length : 0;
    const totalEncarregados = data.encarregados ? data.encarregados.filter(e => e.adminId === adminId).length : 0;
    const numOrd = (v) => (v === '' || v == null) ? 0 : (Number(v) || 0);
    const gastoFunc = (data.funcionarios || []).filter(f => f.adminId === adminId && f.role === 'funcionario').reduce((s, f) => s + numOrd(f.ordenadoBruto), 0);
    const gastoEnc = (data.encarregados || []).filter(e => e.adminId === adminId).reduce((s, e) => s + numOrd(e.ordenadoBruto), 0);
    const osList = (data.servicos || []).filter(s => s.adminId === adminId);
    return {
      totalFunc, totalCli, totalOS, osPend, totalPonto, totalPedidos, pedPend, totalFolhas, totalReqs, reqPend,
      totalEncarregados, numOrd, gastoFunc, gastoEnc, gastoTotal: gastoFunc + gastoEnc, osList,
      osPendentes: osList.filter(s => s.status === 'pendente').length,
      osAndamento: osList.filter(s => s.status === 'em andamento' || s.status === 'em_andamento').length,
      osConcluidas: osList.filter(s => (s.status || '').toLowerCase().includes('conclu')).length
    };
  }
"""
marker='\n  window.TotalGestReportsDistributorMetrics = {'
assert module.count(marker)==1
module=module.replace(marker,insert+marker,1)
module=module.replace('    calculateClient: calculateClient\n','    calculateClient: calculateClient,\n    calculateAdminOverview: calculateAdminOverview\n',1)
assert app.count('TotalGestReportsDistributorMetrics.calculateAdminOverview({')==1
assert module.count('calculateAdminOverview')==2
assert "const CACHE = 'totalgest-v104';" in sw
sw=sw.replace("const CACHE = 'totalgest-v104';","const CACHE = 'totalgest-v105';",1)
APP.write_text(app,encoding='utf-8')
MODULE.write_text(module,encoding='utf-8')
SW.write_text(sw,encoding='utf-8')
