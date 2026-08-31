from pathlib import Path
APP=Path('app.html'); SHELL=Path('assets/js/app-shell.js'); SW=Path('sw.js'); MOD=Path('assets/js/app-load-orchestrator.js')
app=APP.read_text(encoding='utf-8'); shell=SHELL.read_text(encoding='utf-8'); sw=SW.read_text(encoding='utf-8')
start_token='        async function carregarDados(tenantIdParam, superAdminParam, clienteIdParam) {\n'
end_token='        function registarAuditoria('
start=app.index(start_token); end=app.index(end_token,start)
old=app[start:end]
for token in ['_guardarDadosQueue.waitForIdle()', 'window.TotalGestLoadContext.resolve({', 'window.TotalGestLoadQueries.fetchAll({', 'window.TotalGestLoadTransform.apply({', '_reconstruirSnapshots()', '_guardarCacheLocal()', '_restaurarSnapshotDaCache()']:
    assert token in old, token
new="""        async function carregarDados(tenantIdParam, superAdminParam, clienteIdParam) {
            return window.TotalGestLoadOrchestrator.run({
                tenantIdParam: tenantIdParam,
                superAdminParam: superAdminParam,
                clienteIdParam: clienteIdParam,
                user: usuarioLogado,
                waitForIdle: () => _guardarDadosQueue.waitForIdle(),
                isOnline: () => navigator.onLine,
                loadCache: _carregarCacheLocal,
                restoreSnapshot: _restaurarSnapshotDaCache,
                showOffline: mostrarStatusOffline,
                setData: value => { dados = value; },
                emptyData: dadosVazios,
                order: ORDEM,
                metadata: M,
                cutoffMonths: _dataCorteMeses,
                setPointSince: value => { _pontoCarregadoDesde = value; },
                setServicesSince: value => { _servicosCarregadoDesde = value; },
                setSheetsSince: value => { _folhasCarregadoDesde = value; },
                resolveContext: window.TotalGestLoadContext.resolve,
                fetchAll: window.TotalGestLoadQueries.fetchAll,
                transform: window.TotalGestLoadTransform.apply,
                supabase: supa,
                licenseFromRow: licFromRow,
                rebuildSnapshots: _reconstruirSnapshots,
                saveCache: _guardarCacheLocal
            });
        }

"""
app=app[:start]+new+app[end:]
assert app.count('loadTransform: true')==1
app=app.replace('loadTransform: true','loadTransform: true, loadOrchestrator: true',1)
MOD.write_text("""/* Total Gest — orquestração do carregamento inicial
 * Coordena cache offline, contexto, queries, transformação, snapshots e cache final.
 */
(function () {
  'use strict';

  async function run(options) {
    const opts = options || {};
    await opts.waitForIdle();

    if (!opts.isOnline()) {
      const cached = opts.loadCache();
      if (cached) {
        opts.setData(cached);
        opts.restoreSnapshot();
        opts.showOffline();
        return cached;
      }
    }

    const target = opts.emptyData();
    const tables = opts.order.map(function (collection) { return opts.metadata[collection].tabela; })
      .concat(['licencas', 'encarregado_funcionarios']);

    const pointSince = opts.cutoffMonths(6);
    const servicesSince = opts.cutoffMonths(3);
    const sheetsSince = opts.cutoffMonths(3);
    const auditSince = opts.cutoffMonths(6);
    opts.setPointSince(pointSince);
    opts.setServicesSince(servicesSince);
    opts.setSheetsSince(sheetsSince);

    const context = opts.resolveContext({
      tenantIdParam: opts.tenantIdParam,
      superAdminParam: opts.superAdminParam,
      clienteIdParam: opts.clienteIdParam,
      user: opts.user
    });

    let results;
    try {
      results = await opts.fetchAll({
        supabase: opts.supabase,
        tables: tables,
        tenantId: context.tenantId,
        superAdmin: context.superAdmin,
        clienteId: context.clienteId,
        pontoSince: pointSince,
        servicesSince: servicesSince,
        sheetsSince: sheetsSince,
        auditSince: auditSince
      });
    } catch (error) {
      const cached = opts.loadCache();
      if (cached) {
        opts.setData(cached);
        opts.restoreSnapshot();
        opts.showOffline();
        return cached;
      }
      throw error;
    }

    opts.transform({
      tables: tables,
      results: results,
      order: opts.order,
      metadata: opts.metadata,
      target: target,
      licenseFromRow: opts.licenseFromRow
    });

    opts.setData(target);
    opts.rebuildSnapshots();
    opts.saveCache();
    return target;
  }

  window.TotalGestLoadOrchestrator = { run: run };
})();
""",encoding='utf-8')
needle="    loadTransform: './assets/js/app-load-transform.js',\n"; assert shell.count(needle)==1
shell=shell.replace(needle,needle+"    loadOrchestrator: './assets/js/app-load-orchestrator.js',\n",1)
needle="    if (options.loadTransform === true) pedidos.push(MODULOS.loadTransform);\n"; assert shell.count(needle)==1
shell=shell.replace(needle,needle+"    if (options.loadOrchestrator === true) pedidos.push(MODULOS.loadOrchestrator);\n",1)
assert "const CACHE = 'totalgest-v40';" in sw
sw=sw.replace("const CACHE = 'totalgest-v40';","const CACHE = 'totalgest-v41';",1)
needle="  './assets/js/app-load-transform.js',\n"; assert sw.count(needle)==1
sw=sw.replace(needle,needle+"  './assets/js/app-load-orchestrator.js',\n",1)
assert app.count('async function carregarDados(')==1
assert app.count('window.TotalGestLoadOrchestrator.run({')==1
assert app.count('loadOrchestrator: true')==1
for obsolete in ['window.TotalGestLoadContext.resolve({','window.TotalGestLoadQueries.fetchAll({','window.TotalGestLoadTransform.apply({']:
    assert app.count(obsolete)==0,(obsolete,app.count(obsolete))
APP.write_text(app,encoding='utf-8'); SHELL.write_text(shell,encoding='utf-8'); SW.write_text(sw,encoding='utf-8')
