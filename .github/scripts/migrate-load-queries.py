from pathlib import Path
APP=Path('app.html'); SHELL=Path('assets/js/app-shell.js'); SW=Path('sw.js'); MOD=Path('assets/js/app-load-queries.js')
app=APP.read_text(encoding='utf-8'); shell=SHELL.read_text(encoding='utf-8'); sw=SW.read_text(encoding='utf-8')
start_token="            const TABELAS_PORTAL_CLIENTE = new Set(['administradores', 'clientes', 'locais', 'contratos', 'servicos', 'folhas_obra', 'relatorios_especialidade', 'obras', 'notificacoes']);\n"
start=app.index(start_token)
catch_token='            } catch (e) {'
catch=app.index(catch_token,start)
old=app[start:catch]
for token in ["Promise.all(tabelas.map(t => {", "t === 'ponto'", "t === 'servicos'", "t === 'folhas_obra'", "t === 'auditoria'", "t === 'referencias'", "encarregado_funcionarios"]:
    assert token in old, token
new="""            let resultados;
            try {
                resultados = await window.TotalGestLoadQueries.fetchAll({
                    supabase: supa,
                    tables: tabelas,
                    tenantId: tenantId,
                    superAdmin: ehSuperAdmin,
                    clienteId: clienteId,
                    pontoSince: _pontoCarregadoDesde,
                    servicesSince: _servicosCarregadoDesde,
                    sheetsSince: _folhasCarregadoDesde,
                    auditSince: _auditoriaCarregadaDesde
                });
"""
app=app[:start]+new+app[catch:]
assert app.count('loadContext: true')==1
app=app.replace('loadContext: true','loadContext: true, loadQueries: true',1)
MOD.write_text("""/* Total Gest — queries do carregamento inicial
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
""",encoding='utf-8')
needle="    loadContext: './assets/js/app-load-context.js',\n"; assert shell.count(needle)==1
shell=shell.replace(needle,needle+"    loadQueries: './assets/js/app-load-queries.js',\n",1)
needle="    if (options.loadContext === true) pedidos.push(MODULOS.loadContext);\n"; assert shell.count(needle)==1
shell=shell.replace(needle,needle+"    if (options.loadQueries === true) pedidos.push(MODULOS.loadQueries);\n",1)
assert "const CACHE = 'totalgest-v38';" in sw
sw=sw.replace("const CACHE = 'totalgest-v38';","const CACHE = 'totalgest-v39';",1)
needle="  './assets/js/app-load-context.js',\n"; assert sw.count(needle)==1
sw=sw.replace(needle,needle+"  './assets/js/app-load-queries.js',\n",1)
assert app.count('window.TotalGestLoadQueries.fetchAll({')==1
assert app.count('loadQueries: true')==1
APP.write_text(app,encoding='utf-8'); SHELL.write_text(shell,encoding='utf-8'); SW.write_text(sw,encoding='utf-8')
