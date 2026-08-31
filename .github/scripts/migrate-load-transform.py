from pathlib import Path
APP=Path('app.html'); SHELL=Path('assets/js/app-shell.js'); SW=Path('sw.js'); MOD=Path('assets/js/app-load-transform.js')
app=APP.read_text(encoding='utf-8'); shell=SHELL.read_text(encoding='utf-8'); sw=SW.read_text(encoding='utf-8')
start_token='            const map = {};\n'
end_token='            dados = novos;\n'
start=app.index(start_token); end=app.index(end_token,start)
old=app[start:end]
for token in ["resultados[i].error", "map[M[col].tabela].map(M[col].from)", "map['licencas']", "map['encarregado_funcionarios']"]:
    assert token in old,token
new="""            window.TotalGestLoadTransform.apply({
                tables: tabelas,
                results: resultados,
                order: ORDEM,
                metadata: M,
                target: novos,
                licenseFromRow: licFromRow
            });
"""
app=app[:start]+new+app[end:]
assert app.count('loadQueries: true')==1
app=app.replace('loadQueries: true','loadQueries: true, loadTransform: true',1)
MOD.write_text("""/* Total Gest — transformação dos resultados do carregamento inicial
 * Converte linhas, embute licenças e recompõe relações locais sem chamadas de rede.
 */
(function () {
  'use strict';

  function apply(options) {
    const opts = options || {};
    const tables = opts.tables || [];
    const results = opts.results || [];
    const order = opts.order || [];
    const metadata = opts.metadata || {};
    const target = opts.target || {};
    const map = {};

    tables.forEach(function (table, index) {
      const result = results[index] || { data: [], error: null };
      if (result.error) console.error('carregar ' + table + ':', result.error.message);
      map[table] = result.data || [];
    });

    for (const collection of order) {
      target[collection] = map[metadata[collection].tabela].map(metadata[collection].from);
    }

    const licensesById = {};
    for (const row of map.licencas) licensesById[row.admin_id] = opts.licenseFromRow(row);
    for (const admin of target.administradores) admin.licenca = licensesById[admin.id] || null;

    const junctionByManager = {};
    for (const row of map.encarregado_funcionarios) {
      (junctionByManager[row.encarregado_id] = junctionByManager[row.encarregado_id] || []).push(row.funcionario_id);
    }
    for (const manager of target.encarregados) manager.funcionariosIds = junctionByManager[manager.id] || [];

    return target;
  }

  window.TotalGestLoadTransform = { apply: apply };
})();
""",encoding='utf-8')
needle="    loadQueries: './assets/js/app-load-queries.js',\n"; assert shell.count(needle)==1
shell=shell.replace(needle,needle+"    loadTransform: './assets/js/app-load-transform.js',\n",1)
needle="    if (options.loadQueries === true) pedidos.push(MODULOS.loadQueries);\n"; assert shell.count(needle)==1
shell=shell.replace(needle,needle+"    if (options.loadTransform === true) pedidos.push(MODULOS.loadTransform);\n",1)
assert "const CACHE = 'totalgest-v39';" in sw
sw=sw.replace("const CACHE = 'totalgest-v39';","const CACHE = 'totalgest-v40';",1)
needle="  './assets/js/app-load-queries.js',\n"; assert sw.count(needle)==1
sw=sw.replace(needle,needle+"  './assets/js/app-load-transform.js',\n",1)
assert app.count('window.TotalGestLoadTransform.apply({')==1
assert app.count('loadTransform: true')==1
APP.write_text(app,encoding='utf-8'); SHELL.write_text(shell,encoding='utf-8'); SW.write_text(sw,encoding='utf-8')
