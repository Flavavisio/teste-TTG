from pathlib import Path
import re

app_path = Path('app.html')
shell_path = Path('assets/js/app-shell.js')
sw_path = Path('sw.js')
module_path = Path('assets/js/app-sync-encarregados.js')

text = app_path.read_text(encoding='utf-8')
shell = shell_path.read_text(encoding='utf-8')
sw = sw_path.read_text(encoding='utf-8')

if module_path.exists() or 'app-sync-encarregados.js' in shell or 'app-sync-encarregados.js' in sw:
    raise SystemExit('modulo de encarregados ja presente; abortar para evitar duplicacao')

marker = "    syncLicenses: './assets/js/app-sync-licenses.js',"
if shell.count(marker) != 1:
    raise SystemExit('marcador syncLicenses no shell inesperado')
shell = shell.replace(marker, marker + "\n    syncEncarregados: './assets/js/app-sync-encarregados.js',", 1)

load_marker = '    if (options.syncLicenses === true) pedidos.push(MODULOS.syncLicenses);'
if shell.count(load_marker) != 1:
    raise SystemExit('loader syncLicenses inesperado')
shell = shell.replace(load_marker, load_marker + "\n    if (options.syncEncarregados === true) pedidos.push(MODULOS.syncEncarregados);", 1)

init_re = re.compile(r"window\.TotalGestApp\.init\(\{([^}]*)\}\);")
matches = list(init_re.finditer(text))
if len(matches) != 1:
    raise SystemExit(f'init modular inesperado: {len(matches)}')
opts = matches[0].group(1)
if 'syncLicenses: true' not in opts or 'saveQueue: true' not in opts:
    raise SystemExit('opcoes esperadas do init em falta')
if 'syncEncarregados:' in opts:
    raise SystemExit('syncEncarregados ja aparece no init')
old_init = matches[0].group(0)
new_opts = opts.replace('syncLicenses: true', 'syncLicenses: true, syncEncarregados: true', 1)
text = text.replace(old_init, f'window.TotalGestApp.init({{{new_opts}}});', 1)

old_block = """                // junção encarregado_funcionarios (a seguir aos encarregados)
                if (col === 'encarregados') {
                    for (const e of lista) {
                        const ids = (e.funcionariosIds || []).slice().sort();
                        const json = JSON.stringify(ids);
                        if (_snapJunc.get(e.id) !== json) {
                            const { error: errDel } = await supa.from('encarregado_funcionarios').delete().eq('encarregado_id', e.id);
                            if (errDel && !_tabelaInexistente(errDel)) { erros++; if (!primeiroErro) primeiroErro = 'encarregado_funcionarios — ' + (errDel.message || errDel.code || 'erro'); continue; }
                            if (ids.length) {
                                const rows = ids.map(fid => ({ encarregado_id: e.id, funcionario_id: fid }));
                                const { error } = await supa.from('encarregado_funcionarios').insert(rows);
                                if (error) { console.error('junção encarregado:', error.message); if (!_tabelaInexistente(error)) { erros++; if (!primeiroErro) primeiroErro = 'encarregado_funcionarios — ' + (error.message || error.code || 'erro'); continue; } }
                            }
                            _snapJunc.set(e.id, json);
                        }
                    }
                }
"""
new_block = """                // junção encarregado_funcionarios (a seguir aos encarregados)
                if (col === 'encarregados') {
                    const juncResult = await window.TotalGestSyncEncarregados.run({
                        supabase: supa,
                        encarregados: lista,
                        snapshot: _snapJunc,
                        missingTable: _tabelaInexistente
                    });
                    erros += juncResult.errors;
                    if (!primeiroErro && juncResult.firstError) primeiroErro = juncResult.firstError;
                }
"""
if text.count(old_block) != 1:
    raise SystemExit(f'bloco encarregado_funcionarios inesperado: {text.count(old_block)}')
text = text.replace(old_block, new_block, 1)

module_path.write_text("""/* Total Gest — sincronizacao da juncao encarregado_funcionarios
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
""", encoding='utf-8')

cache_marker = "  './assets/js/app-sync-licenses.js',"
if sw.count(cache_marker) != 1:
    raise SystemExit('marcador syncLicenses no service worker inesperado')
sw = sw.replace(cache_marker, cache_marker + "\n  './assets/js/app-sync-encarregados.js',", 1)
cache_re = re.compile(r"const CACHE = 'totalgest-v(\d+)';")
m = cache_re.search(sw)
if not m:
    raise SystemExit('versao cache PWA nao encontrada')
old_v = int(m.group(1))
sw = cache_re.sub(f"const CACHE = 'totalgest-v{old_v + 1}';", sw, count=1)

app_path.write_text(text, encoding='utf-8')
shell_path.write_text(shell, encoding='utf-8')
sw_path.write_text(sw, encoding='utf-8')

checks = {
    'modulo no shell': shell.count("syncEncarregados: './assets/js/app-sync-encarregados.js'") == 1,
    'loader no shell': shell.count('options.syncEncarregados === true') == 1,
    'modulo no init': text.count('syncEncarregados: true') == 1,
    'chamada modular': text.count('TotalGestSyncEncarregados.run({') == 1,
    'delete inline removido': text.count("supa.from('encarregado_funcionarios').delete().eq('encarregado_id', e.id)") == 0,
    '_sincronizar preservada': text.count('async function _sincronizar()') == 1,
    'cache inclui modulo': sw.count("'./assets/js/app-sync-encarregados.js'") == 1,
}
for name, ok in checks.items():
    print(name, 'OK' if ok else 'FALHOU')
    if not ok:
        raise SystemExit(1)
print(f'cache PWA: totalgest-v{old_v} -> totalgest-v{old_v + 1}')
