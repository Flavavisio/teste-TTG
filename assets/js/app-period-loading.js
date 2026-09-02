/* Total Gest — carregamento incremental por períodos
 * Centraliza cálculos de corte e carregamentos históricos sem alterar filtros ou queries existentes.
 */
(function () {
  'use strict';

  function cutoffMonths(months) {
    const date = new Date();
    date.setMonth(date.getMonth() - months);
    return date.toISOString().slice(0, 10);
  }

  function monthsSinceCutoff(cutoff) {
    if (!cutoff) return 0;
    const today = new Date();
    const date = new Date(cutoff + 'T00:00:00');
    return Math.max(0, Math.round((today - date) / (30.44 * 24 * 60 * 60 * 1000)));
  }

  async function ensurePoint(options) {
    const opts = options || {};
    if (!opts.desde || !opts.currentSince || opts.desde >= opts.currentSince) return;
    const result = await opts.supabase.from('ponto').select('*').gte('data', opts.desde).lt('data', opts.currentSince);
    if (result.error) {
      console.error('carregar ponto mais antigo:', result.error.message);
      return;
    }
    const incoming = (result.data || []).map(opts.fromRow);
    const existingIds = new Set((opts.data.ponto || []).map(item => item.id));
    opts.data.ponto = [...(opts.data.ponto || []), ...incoming.filter(item => !existingIds.has(item.id))];
    opts.setSince(opts.desde);
  }

  async function ensureSheets(options) {
    const opts = options || {};
    if (!opts.desde || !opts.currentSince || opts.desde >= opts.currentSince) return 0;
    const result = await opts.supabase.from('folhas_obra').select('*')
      .not('assinatura', 'is', null)
      .gte('data', opts.desde)
      .lt('data', opts.currentSince);
    if (result.error) {
      console.error('carregar folhas mais antigas:', result.error.message);
      opts.setSince(opts.desde);
      return 0;
    }
    const incoming = (result.data || []).map(opts.fromRow);
    const existingIds = new Set((opts.data.folhasObra || []).map(item => item.id));
    const additions = incoming.filter(item => !existingIds.has(item.id));
    opts.data.folhasObra = [...(opts.data.folhasObra || []), ...additions];
    opts.setSince(opts.desde);
    return additions.length;
  }

  async function ensureServices(options) {
    const opts = options || {};
    if (!opts.desde || !opts.currentSince || opts.desde >= opts.currentSince) return 0;
    const result = await opts.supabase.from('servicos').select('*')
      .eq('status', 'concluído')
      .gte('data', opts.desde)
      .lt('data', opts.currentSince);
    if (result.error) {
      console.error('carregar OS mais antigas:', result.error.message);
      opts.setSince(opts.desde);
      return 0;
    }
    const incoming = (result.data || []).map(opts.fromRow);
    const existingIds = new Set((opts.data.servicos || []).map(item => item.id));
    const additions = incoming.filter(item => !existingIds.has(item.id));
    opts.data.servicos = [...(opts.data.servicos || []), ...additions];
    opts.setSince(opts.desde);
    return additions.length;
  }

  window.TotalGestPeriodLoading = {
    cutoffMonths: cutoffMonths,
    monthsSinceCutoff: monthsSinceCutoff,
    ensurePoint: ensurePoint,
    ensureSheets: ensureSheets,
    ensureServices: ensureServices
  };
})();
