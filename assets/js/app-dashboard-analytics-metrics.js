/* Total Gest — métricas puras do dashboard analítico. */
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
