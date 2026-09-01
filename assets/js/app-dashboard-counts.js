/* Total Gest — contagens do dashboard por perfil. */
(function () {
  'use strict';

  function calculateRoleCounts(options) {
    const opts = options || {};
    const data = opts.data || {};
    const user = opts.user;
    let countFunc = 0;
    let countCli = 0;
    let osPend = 0;
    let osAndamento = 0;
    let countPonto = 0;
    let countPedidos = 0;
    let countFolhas = 0;
    let countReqs = 0;
    let countEncarregados = 0;

    if (user && (user.role === 'admin' || user.role === 'subadmin')) {
      const adminId = user.role === 'admin' ? user.id : user.adminId;
      countFunc = data.funcionarios ? data.funcionarios.filter(f => f.adminId === adminId && f.role !== 'admin' && f.role !== 'superadmin').length : 0;
      countEncarregados = data.encarregados ? data.encarregados.filter(e => e.adminId === adminId).length : 0;
      countCli = data.clientes ? data.clientes.filter(c => c.adminId === adminId).length : 0;
      osPend = data.servicos ? data.servicos.filter(s => s.adminId === adminId && s.status === 'pendente').length : 0;
      osAndamento = data.servicos ? data.servicos.filter(s => s.adminId === adminId && s.status === 'em andamento').length : 0;
      countPonto = data.ponto ? data.ponto.filter(p => p.adminId === adminId).length : 0;
      countPedidos = data.pedidos ? data.pedidos.filter(p => p.adminId === adminId && p.status === 'pendente_aprov').length : 0;
      countFolhas = data.folhasObra ? data.folhasObra.filter(f => f.adminId === adminId).length : 0;
      countReqs = data.requisicoes ? data.requisicoes.filter(r => r.adminId === adminId && (r.status === 'pendente_aprov' || r.status === 'em_andamento' || r.status === 'aguarda_validacao')).length : 0;
    } else if (user && user.role === 'encarregado') {
      const encarregado = data.encarregados ? data.encarregados.find(e => e.id === user.id) : undefined;
      if (encarregado) {
        countFunc = data.funcionarios ? data.funcionarios.filter(f => encarregado.funcionariosIds?.includes(f.id) && f.role !== 'admin' && f.role !== 'superadmin').length : 0;
        countPonto = data.ponto ? data.ponto.filter(p => p.funcionarioId === user.id).length : 0;
        countPedidos = data.pedidos ? data.pedidos.filter(p => p.funcionarioId === user.id && p.status === 'pendente_aprov').length : 0;
        countReqs = data.requisicoes ? data.requisicoes.filter(r => r.funcionarioId === user.id && (r.status === 'pendente_aprov' || r.status === 'em_andamento' || r.status === 'aguarda_validacao')).length : 0;
        countFolhas = data.folhasObra ? data.folhasObra.filter(f => f.funcionarioId === user.id).length : 0;
        osPend = data.servicos ? data.servicos.filter(s => {
          const atribuidos = (s.funcionariosIds && s.funcionariosIds.length) ? s.funcionariosIds : [s.funcionarioId].filter(Boolean);
          return s.adminId === encarregado.adminId && (s.funcionarioId === null || atribuidos.includes(user.id) || atribuidos.some(fid => encarregado.funcionariosIds?.includes(fid))) && s.status === 'pendente';
        }).length : 0;
        osAndamento = data.servicos ? data.servicos.filter(s => {
          const atribuidos = (s.funcionariosIds && s.funcionariosIds.length) ? s.funcionariosIds : [s.funcionarioId].filter(Boolean);
          return s.adminId === encarregado.adminId && (s.funcionarioId === null || atribuidos.includes(user.id) || atribuidos.some(fid => encarregado.funcionariosIds?.includes(fid))) && s.status === 'em andamento';
        }).length : 0;
      }
    } else if (user && user.role === 'funcionario') {
      const funcObj = data.funcionarios ? data.funcionarios.find(f => f.id === user.id) : undefined;
      const adminId = funcObj?.adminId;
      if (adminId) {
        osPend = data.servicos ? data.servicos.filter(s => {
          const atribuidos = (s.funcionariosIds && s.funcionariosIds.length) ? s.funcionariosIds : [s.funcionarioId].filter(Boolean);
          return s.adminId === adminId && (s.funcionarioId === null || atribuidos.includes(user.id)) && s.status === 'pendente';
        }).length : 0;
        osAndamento = data.servicos ? data.servicos.filter(s => {
          const atribuidos = (s.funcionariosIds && s.funcionariosIds.length) ? s.funcionariosIds : [s.funcionarioId].filter(Boolean);
          return s.adminId === adminId && (s.funcionarioId === null || atribuidos.includes(user.id)) && s.status === 'em andamento';
        }).length : 0;
      }
      countPonto = data.ponto ? data.ponto.filter(p => p.funcionarioId === user.id).length : 0;
      countPedidos = data.pedidos ? data.pedidos.filter(p => p.funcionarioId === user.id && p.status === 'pendente_aprov').length : 0;
      countReqs = data.requisicoes ? data.requisicoes.filter(r => r.funcionarioId === user.id && (r.status === 'pendente_aprov' || r.status === 'em_andamento' || r.status === 'aguarda_validacao')).length : 0;
      countFolhas = data.folhasObra ? data.folhasObra.filter(f => f.funcionarioId === user.id).length : 0;
    }

    return { countFunc, countCli, osPend, osAndamento, countPonto, countPedidos, countFolhas, countReqs, countEncarregados };
  }

  function calculateStatusCounts(options) {
    const opts = options || {};
    const admins = opts.admins || [];
    const renewalRequests = opts.renewalRequests || [];
    const helps = opts.helps || [];
    const user = opts.user;
    const licencasAtivas = admins.filter(a => a.ativo && a.licenca && opts.isLicenseValid(a.licenca.dataExpiracao)).length;
    const aVencer = admins.filter(a => a.ativo && a.licenca && opts.isLicenseValid(a.licenca.dataExpiracao) && opts.daysRemaining(a.licenca.dataExpiracao) <= 5).length;
    const pedidosPendentes = renewalRequests.filter(p => p.status === 'pendente').length;
    let ajudasRelevantes = [];
    if (user) {
      if (user.role === 'admin' || user.role === 'encarregado') {
        ajudasRelevantes = helps.filter(a => a.remetenteId === user.id);
      } else if (user.role === 'superadmin') {
        ajudasRelevantes = helps;
      }
    }
    return {
      licencasAtivas: licencasAtivas,
      aVencer: aVencer,
      pedidosPendentes: pedidosPendentes,
      ajudasPendentes: ajudasRelevantes.filter(a => a.status === 'pendente').length,
      ajudasAnalise: ajudasRelevantes.filter(a => a.status === 'analise').length,
      ajudasConcluido: ajudasRelevantes.filter(a => a.status === 'concluido').length
    };
  }

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

  window.TotalGestDashboardCounts = { calculateRoleCounts: calculateRoleCounts, calculateStatusCounts: calculateStatusCounts, calculateCrmCounts: calculateCrmCounts };
})();
