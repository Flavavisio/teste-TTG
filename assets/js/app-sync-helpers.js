/* Total Gest — helpers de sincronização
 * Classifica erros de tabela/coluna sem alterar dados nem executar pedidos.
 */
(function () {
  'use strict';

  function tabelaInexistente(e) {
    const m = (e && (e.message || e.msg || '')) + '';
    const c = (e && e.code || '') + '';
    return /does not exist|schema cache|find the table|relation .* does not/i.test(m) || ['42P01','PGRST205','PGRST204','PGRST202'].includes(c);
  }

  function colunaEmFalta(e) {
    const m = (e && (e.message || e.msg || '')) + '';
    const c = (e && e.code || '') + '';

    // Formato PostgREST/Supabase: "Could not find the 'X' column ... in the schema cache".
    let match = m.match(/Could not find the ['\"]?([a-z0-9_]+)['\"]? column/i);
    if (match) return match[1];

    // Formato PostgreSQL puro: "column X does not exist".
    if (c === '42703' || /column .* does not exist/i.test(m)) {
      match = m.match(/column ["']?([a-z0-9_]+)["']?/i);
      return match ? match[1] : null;
    }
    return null;
  }

  window._tabelaInexistente = tabelaInexistente;
  window._colunaEmFalta = colunaEmFalta;

  window.TotalGestSyncHelpers = {
    missingTable: tabelaInexistente,
    missingColumn: colunaEmFalta
  };
})();
