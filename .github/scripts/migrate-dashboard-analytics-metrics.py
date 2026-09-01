from pathlib import Path
APP=Path('app.html'); SHELL=Path('assets/js/app-shell.js'); SW=Path('sw.js'); MOD=Path('assets/js/app-dashboard-analytics-metrics.js')
app=APP.read_text(encoding='utf-8'); shell=SHELL.read_text(encoding='utf-8'); sw=SW.read_text(encoding='utf-8')
fn=app.index('function renderizarDashboardAnalitico()')
start=app.index('            const tecnicos = ',fn)
end=app.index('            cont.innerHTML = `',start)
old=app[start:end]
for token in ['const tecnicos =','const statsTec =','const topClientes =','const geofencePeriodo =','const porMes =','const maxObrasMes =']:
    assert old.count(token)==1, token
new="""            const _analytics = window.TotalGestDashboardAnalyticsMetrics.calculate({
                data: dados,
                adminId: adminId,
                startDate: ini,
                endDate: fim,
                worksYear: _danAnoObras,
                calculateHours: calcularHoras,
                businessDays: _danDiasUteis,
                clientName: obterNomeCliente
            });
            const statsTec = _analytics.technicians;
            const maxOS = _analytics.maxOS;
            const totalOS = _analytics.totalOS;
            const taxaConclusao = _analytics.completionRate;
            const topClientes = _analytics.topClients;
            const geofencePeriodo = _analytics.geofenceAlerts;
            const nomesMeses = _analytics.monthNames;
            const porMes = _analytics.worksByMonth;
            const maxObrasMes = _analytics.maxWorksMonth;

"""
app=app[:start]+new+app[end:]
assert app.count('TotalGestDashboardAnalyticsMetrics.calculate({')==1
module="""/* Total Gest — métricas puras do dashboard analítico. */
(function () {
  'use strict';

  function calculate(options) {
    const opts = options || {};
    const data = opts.data || {};
    const adminId = opts.adminId;
    const ini = opts.startDate;
    const fim = opts.endDate;
    const tecnicos = [...(data.funcionarios || []).filter(f => f.adminId === adminId && f.role !== 'admin'), ...(data.encarregados || []).filter(e => e.adminId === adminId)];
    const osPeriodo = (data.servicos || []).filter(s => s.adminId === adminId && s.data && s.data >= ini && s.data <= fim);
    const statsTec = tecnicos.map(t => {
      const osT = osPeriodo.filter(s => s.funcionarioId === t.id);
      const regsPonto = (data.ponto || []).filter(p => p.funcionarioId === t.id && p.entrada && p.saida && p.servicoId && osT.some(s => s.id === p.servicoId));
      const totalHoras = regsPonto.reduce((s, p) => s + opts.calculateHours(p.entrada, p.saida), 0);
      const tempoMedio = regsPonto.length ? (totalHoras / regsPonto.length) : 0;
      const diasComPonto = new Set((data.ponto || []).filter(p => p.funcionarioId === t.id && p.entrada && p.saida && p.data >= ini && p.data <= fim).map(p => p.data)).size;
      const diasUteis = opts.businessDays(ini, fim) || 1;
      const assiduidade = Math.min(100, Math.round((diasComPonto / diasUteis) * 100));
      return { nome: t.nome, nOS: osT.length, tempoMedio: tempoMedio, assiduidade: assiduidade };
    }).sort((a, b) => b.nOS - a.nOS);
    const maxOS = Math.max(1, ...statsTec.map(t => t.nOS));
    const totalOS = osPeriodo.length;
    const osConcluidas = osPeriodo.filter(s => s.status === 'concluído').length;
    const taxaConclusao = totalOS ? Math.round((osConcluidas / totalOS) * 100) : 0;
    const porCliente = {};
    osPeriodo.forEach(s => { if (s.clienteId) porCliente[s.clienteId] = (porCliente[s.clienteId] || 0) + 1; });
    const topClientes = Object.entries(porCliente).sort((a, b) => b[1] - a[1]).slice(0, 5).map(([cid, n]) => ({ nome: opts.clientName(cid) || '—', n: n }));
    const geofencePeriodo = (data.alertasGeofence || []).filter(g => g.adminId === adminId && g.dataCriacao >= new Date(ini).getTime() && g.dataCriacao <= new Date(fim + 'T23:59:59').getTime()).length;
    const nomesMeses = ['Jan','Fev','Mar','Abr','Mai','Jun','Jul','Ago','Set','Out','Nov','Dez'];
    const obrasAdmin = (data.obras || []).filter(o => o.adminId === adminId && o.estado === 'concluida' && o.dataConclusao);
    const porMes = [1,2,3,4,5,6,7,8,9,10,11,12].map(m => {
      const mm = String(m).padStart(2, '0');
      const obrasMes = obrasAdmin.filter(o => o.dataConclusao && o.dataConclusao.startsWith(opts.worksYear + '-' + mm));
      const valores = obrasMes.map(o => (data.servicos || []).filter(s => s.obraId === o.id).reduce((s, x) => s + (Number(x.valor) || 0), 0));
      const valorMedio = valores.length ? (valores.reduce((a, b) => a + b, 0) / valores.length) : 0;
      return { n: obrasMes.length, valorMedio: valorMedio };
    });
    return { technicians: statsTec, maxOS: maxOS, totalOS: totalOS, completionRate: taxaConclusao, topClients: topClientes, geofenceAlerts: geofencePeriodo, monthNames: nomesMeses, worksByMonth: porMes, maxWorksMonth: Math.max(1, ...porMes.map(x => x.n)) };
  }

  window.TotalGestDashboardAnalyticsMetrics = { calculate: calculate };
})();
"""
assert not MOD.exists()
# shell wiring
needle="    dashboardCounts: './assets/js/app-dashboard-counts.js',\n"
assert shell.count(needle)==1
shell=shell.replace(needle,needle+"    dashboardAnalyticsMetrics: './assets/js/app-dashboard-analytics-metrics.js',\n",1)
needle2="    if (options.dashboardCounts === true) pedidos.push(MODULOS.dashboardCounts);\n"
assert shell.count(needle2)==1
shell=shell.replace(needle2,needle2+"    if (options.dashboardAnalyticsMetrics === true) pedidos.push(MODULOS.dashboardAnalyticsMetrics);\n",1)
# app loader option
assert app.count('dashboardCounts: true')==1
app=app.replace('dashboardCounts: true','dashboardCounts: true,\n                dashboardAnalyticsMetrics: true',1)
assert "const CACHE = 'totalgest-v111';" in sw
sw=sw.replace("const CACHE = 'totalgest-v111';","const CACHE = 'totalgest-v112';",1)
asset="  './assets/js/app-dashboard-counts.js',\n"
assert sw.count(asset)==1
sw=sw.replace(asset,asset+"  './assets/js/app-dashboard-analytics-metrics.js',\n",1)
APP.write_text(app,encoding='utf-8'); SHELL.write_text(shell,encoding='utf-8'); SW.write_text(sw,encoding='utf-8'); MOD.write_text(module,encoding='utf-8')
