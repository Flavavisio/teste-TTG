/* Total Gest — transformação dos resultados do carregamento inicial
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
