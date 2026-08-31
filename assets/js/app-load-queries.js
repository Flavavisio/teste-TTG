/* Total Gest — queries do carregamento inicial
 * Constrói e executa as mesmas leituras por tabela, respeitando tenant e portal do cliente.
 */
(function () {
  'use strict';

  const CLIENT_PORTAL_TABLES = new Set([
    'administradores', 'clientes', 'locais', 'contratos', 'servicos',
    'folhas_obra', 'relatorios_especialidade', 'obras', 'notificacoes'
  ]);

  async function fetchAll(options) {
    const opts = options || {};
    return Promise.all((opts.tables || []).map(function (table) {
      if (opts.clienteId && !CLIENT_PORTAL_TABLES.has(table)) {
        return Promise.resolve({ data: [], error: null });
      }

      let query = opts.supabase.from(table).select('*');
      if (table === 'ponto') query = opts.supabase.from(table).select('*').gte('data', opts.pontoSince);
      else if (table === 'servicos') query = opts.supabase.from(table).select('*').or(`status.neq.concluído,data.gte.${opts.servicesSince}`);
      else if (table === 'folhas_obra') query = opts.supabase.from(table).select('*').or(`assinatura.is.null,data.gte.${opts.sheetsSince}`);
      else if (table === 'auditoria') query = opts.supabase.from(table).select('*').gte('data', opts.auditSince);

      if (opts.clienteId) {
        if (table === 'administradores') query = query.eq('id', opts.tenantId);
        else if (table === 'clientes') query = query.eq('id', opts.clienteId);
        else if (table === 'locais' || table === 'contratos' || table === 'servicos' || table === 'obras' || table === 'relatorios_especialidade') query = query.eq('cliente_id', opts.clienteId);
        else if (table === 'folhas_obra') query = query.eq('admin_id', opts.tenantId);
        else if (opts.tenantId) query = query.eq('admin_id', opts.tenantId);
      } else if (!opts.superAdmin && opts.tenantId && table !== 'encarregado_funcionarios') {
        if (table === 'administradores') query = query.eq('id', opts.tenantId);
        else if (table === 'referencias') query = query.eq('admin_referenciador_id', opts.tenantId);
        else query = query.eq('admin_id', opts.tenantId);
      }
      return query;
    }));
  }

  window.TotalGestLoadQueries = { fetchAll: fetchAll };
})();
