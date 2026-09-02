/* Total Gest — sincronizacao da juncao encarregado_funcionarios
 * Mantem a sequencia legada: apagar associacoes, inserir as atuais e so depois atualizar snapshot.
 */
(function () {
  'use strict';

  async function run(options) {
    const opts = options || {};
    const supabase = opts.supabase;
    const encarregados = opts.encarregados || [];
    const snapshot = opts.snapshot;
    const missingTable = opts.missingTable;
    let errors = 0;
    let firstError = '';

    if (!supabase || !snapshot || typeof missingTable !== 'function') {
      throw new Error('TotalGestSyncEncarregados: dependencias invalidas');
    }

    for (const encarregado of encarregados) {
      const ids = (encarregado.funcionariosIds || []).slice().sort();
      const json = JSON.stringify(ids);
      if (snapshot.get(encarregado.id) === json) continue;

      const delResult = await supabase
        .from('encarregado_funcionarios')
        .delete()
        .eq('encarregado_id', encarregado.id);
      const deleteError = delResult.error;
      if (deleteError && !missingTable(deleteError)) {
        errors++;
        if (!firstError) firstError = 'encarregado_funcionarios — ' + (deleteError.message || deleteError.code || 'erro');
        continue;
      }

      if (ids.length) {
        const rows = ids.map(function (funcionarioId) {
          return { encarregado_id: encarregado.id, funcionario_id: funcionarioId };
        });
        const insertResult = await supabase.from('encarregado_funcionarios').insert(rows);
        const insertError = insertResult.error;
        if (insertError) {
          console.error('junção encarregado:', insertError.message);
          if (!missingTable(insertError)) {
            errors++;
            if (!firstError) firstError = 'encarregado_funcionarios — ' + (insertError.message || insertError.code || 'erro');
            continue;
          }
        }
      }

      snapshot.set(encarregado.id, json);
    }

    return { errors: errors, firstError: firstError };
  }

  window.TotalGestSyncEncarregados = { run: run };
})();
