from pathlib import Path
import re

app_path = Path('app.html')
shell_path = Path('assets/js/app-shell.js')
sw_path = Path('sw.js')
module_path = Path('assets/js/app-sync-upsert.js')

text = app_path.read_text(encoding='utf-8')
shell = shell_path.read_text(encoding='utf-8')
sw = sw_path.read_text(encoding='utf-8')

if module_path.exists() or 'app-sync-upsert.js' in shell or 'app-sync-upsert.js' in sw:
    raise SystemExit('app-sync-upsert ja presente; abortar para evitar duplicacao')

old_block = """                if (upserts.length) {
                    // Em lotes de 200 — um único pedido com centenas/milhares de linhas de
                    // uma vez (ex.: uma importação grande de clientes) pode ultrapassar o
                    // tempo limite da base de dados (\"statement timeout\") e falhar por
                    // inteiro. Em lotes mais pequenos, cada um tem tempo de sobra, e se um
                    // lote falhar os restantes continuam a tentar na mesma.
                    const TAMANHO_LOTE = 200;
                    let erroNesteTabela = null;
                    for (let i = 0; i < upserts.length; i += TAMANHO_LOTE) {
                        const loteRows = upserts.slice(i, i + TAMANHO_LOTE);
                        const loteJson = upsertsJson.slice(i, i + TAMANHO_LOTE);
                        // IMPORTANTE: pedimos sempre .select('id') de volta. O Supabase pode responder
                        // \"sem erro\" a um upsert que, por causa das permissões (RLS), na prática não
                        // escreveu nenhuma linha — sem o .select(), nunca saberíamos a diferença entre
                        // \"gravou tudo\" e \"não gravou nada\", e ficávamos a marcar coisas como
                        // sincronizadas quando não estavam.
                        const { data: linhasGravadas, error } = await supa.from(meta.tabela).upsert(loteRows, { onConflict: 'id' }).select('id');
                        if (error) {
                            console.error('upsert ' + meta.tabela + ' (lote ' + (i / TAMANHO_LOTE + 1) + '):', error.message);
                            const colunaFalta = _colunaEmFalta(error);
                            if (colunaFalta) {
                                // Repete o mesmo lote sem essa coluna — para não ficar preso a
                                // tentar os mesmos registos para sempre enquanto ela não existir.
                                console.warn('Coluna \"' + colunaFalta + '\" não existe em \"' + meta.tabela + '\" — a sincronizar sem ela por agora. Corre a query SQL correspondente para isto passar a gravar completo.');
                                const loteRowsSemColuna = loteRows.map(r => { const r2 = { ...r }; delete r2[colunaFalta]; return r2; });
                                const retry = await supa.from(meta.tabela).upsert(loteRowsSemColuna, { onConflict: 'id' }).select('id');
                                if (!retry.error && retry.data && retry.data.length >= loteRowsSemColuna.length) {
                                    loteJson.forEach(u => _snap[col].set(u.id, u.json));
                                    continue; // este lote já ficou tratado — não conta como erro
                                }
                            }
                            erroNesteTabela = error;
                            // continua a tentar os restantes lotes — não desiste ao primeiro que falhar
                        } else if (!linhasGravadas || linhasGravadas.length < loteRows.length) {
                            // Resposta \"sem erro\", mas confirmou menos linhas do que enviámos — as
                            // permissões (RLS) bloquearam algumas em silêncio. Só marca como
                            // sincronizado o que veio mesmo confirmado; o resto fica pendente e volta
                            // a tentar na próxima gravação, em vez de se perder para sempre.
                            const idsConfirmados = new Set((linhasGravadas || []).map(r => r.id));
                            loteJson.forEach(u => { if (idsConfirmados.has(u.id)) _snap[col].set(u.id, u.json); });
                            console.error('upsert ' + meta.tabela + ': enviadas ' + loteRows.length + ', confirmadas ' + (linhasGravadas?.length || 0) + ' — bloqueado por permissões (RLS)');
                            erroNesteTabela = { message: 'Algumas linhas de \"' + meta.tabela + '\" foram bloqueadas pelas permissões do servidor (RLS)' };
                        } else {
                            loteJson.forEach(u => _snap[col].set(u.id, u.json));
                        }
                    }
                    if (erroNesteTabela) {
                        if (!_tabelaInexistente(erroNesteTabela) && col !== 'auditoria') { erros++; if (!primeiroErro) primeiroErro = meta.tabela + ' — ' + (erroNesteTabela.message || erroNesteTabela.code || 'erro'); }
                        // As linhas cujo lote falhou não ficaram marcadas como sincronizadas — ficam pendentes para a próxima tentativa, nada se perde
                    }
                }
"""
new_block = """                if (upserts.length) {
                    const resultadoUpsert = await window.TotalGestSyncUpsert.run({
                        supabase: supa,
                        table: meta.tabela,
                        rows: upserts,
                        states: upsertsJson,
                        snapshot: _snap[col],
                        missingColumn: _colunaEmFalta
                    });
                    const erroNesteTabela = resultadoUpsert.error;
                    if (erroNesteTabela) {
                        if (!_tabelaInexistente(erroNesteTabela) && col !== 'auditoria') { erros++; if (!primeiroErro) primeiroErro = meta.tabela + ' — ' + (erroNesteTabela.message || erroNesteTabela.code || 'erro'); }
                        // As linhas cujo lote falhou não ficaram marcadas como sincronizadas — ficam pendentes para a próxima tentativa, nada se perde
                    }
                }
"""

if text.count(old_block) != 1:
    raise SystemExit(f'bloco upsert esperado nao encontrado uma vez: {text.count(old_block)}')
text = text.replace(old_block, new_block, 1)

marker = "    syncDiff: './assets/js/app-sync-diff.js',"
if shell.count(marker) != 1:
    raise SystemExit('marcador syncDiff no shell inesperado')
shell = shell.replace(marker, marker + "\n    syncUpsert: './assets/js/app-sync-upsert.js',", 1)

load_marker = '    if (options.syncDiff === true) pedidos.push(MODULOS.syncDiff);'
if shell.count(load_marker) != 1:
    raise SystemExit('loader syncDiff inesperado')
shell = shell.replace(load_marker, load_marker + "\n    if (options.syncUpsert === true) pedidos.push(MODULOS.syncUpsert);", 1)

init_re = re.compile(r"window\.TotalGestApp\.init\(\{([^}]*)\}\);")
matches = list(init_re.finditer(text))
if len(matches) != 1:
    raise SystemExit(f'init modular inesperado: {len(matches)}')
opts = matches[0].group(1)
if 'syncDiff: true' not in opts or 'saveQueue: true' not in opts:
    raise SystemExit('opcoes de init esperadas em falta')
if 'syncUpsert:' in opts:
    raise SystemExit('syncUpsert ja presente no init')
old_init = matches[0].group(0)
new_opts = opts.replace('saveQueue: true', 'syncUpsert: true, saveQueue: true', 1)
text = text.replace(old_init, f'window.TotalGestApp.init({{{new_opts}}});', 1)

module_path.write_text("""/* Total Gest — UPSERT genérico em lotes
 * Mantém a semântica legada de confirmação, retry por coluna em falta e snapshots.
 */
(function () {
  'use strict';

  async function run(options) {
    const opts = options || {};
    const supabase = opts.supabase;
    const table = opts.table;
    const rows = opts.rows || [];
    const states = opts.states || [];
    const snapshot = opts.snapshot;
    const missingColumn = opts.missingColumn;
    const batchSize = 200;
    let tableError = null;

    if (!supabase || !table || !snapshot || typeof missingColumn !== 'function') {
      throw new Error('TotalGestSyncUpsert: dependencias invalidas');
    }

    for (let i = 0; i < rows.length; i += batchSize) {
      const batchRows = rows.slice(i, i + batchSize);
      const batchStates = states.slice(i, i + batchSize);
      const result = await supabase.from(table).upsert(batchRows, { onConflict: 'id' }).select('id');
      const writtenRows = result.data;
      const error = result.error;

      if (error) {
        console.error('upsert ' + table + ' (lote ' + (i / batchSize + 1) + '):', error.message);
        const missing = missingColumn(error);
        if (missing) {
          console.warn('Coluna "' + missing + '" não existe em "' + table + '" — a sincronizar sem ela por agora. Corre a query SQL correspondente para isto passar a gravar completo.');
          const retryRows = batchRows.map(function (row) {
            const copy = { ...row };
            delete copy[missing];
            return copy;
          });
          const retry = await supabase.from(table).upsert(retryRows, { onConflict: 'id' }).select('id');
          if (!retry.error && retry.data && retry.data.length >= retryRows.length) {
            batchStates.forEach(function (state) { snapshot.set(state.id, state.json); });
            continue;
          }
        }
        tableError = error;
        continue;
      }

      if (!writtenRows || writtenRows.length < batchRows.length) {
        const confirmedIds = new Set((writtenRows || []).map(function (row) { return row.id; }));
        batchStates.forEach(function (state) {
          if (confirmedIds.has(state.id)) snapshot.set(state.id, state.json);
        });
        console.error('upsert ' + table + ': enviadas ' + batchRows.length + ', confirmadas ' + ((writtenRows && writtenRows.length) || 0) + ' — bloqueado por permissões (RLS)');
        tableError = { message: 'Algumas linhas de "' + table + '" foram bloqueadas pelas permissões do servidor (RLS)' };
      } else {
        batchStates.forEach(function (state) { snapshot.set(state.id, state.json); });
      }
    }

    return { error: tableError };
  }

  window.TotalGestSyncUpsert = { run: run };
})();
""", encoding='utf-8')

cache_marker = "  './assets/js/app-sync-diff.js',"
if sw.count(cache_marker) != 1:
    raise SystemExit('marcador syncDiff no service worker inesperado')
sw = sw.replace(cache_marker, cache_marker + "\n  './assets/js/app-sync-upsert.js',", 1)
cache_re = re.compile(r"const CACHE = 'totalgest-v(\d+)';")
m = cache_re.search(sw)
if not m:
    raise SystemExit('versao do cache PWA nao encontrada')
old_v = int(m.group(1))
sw = cache_re.sub(f"const CACHE = 'totalgest-v{old_v + 1}';", sw, count=1)

app_path.write_text(text, encoding='utf-8')
shell_path.write_text(shell, encoding='utf-8')
sw_path.write_text(sw, encoding='utf-8')

checks = {
    'syncUpsert no shell': shell.count("syncUpsert: './assets/js/app-sync-upsert.js'") == 1,
    'loader syncUpsert': shell.count('options.syncUpsert === true') == 1,
    'syncUpsert no init': text.count('syncUpsert: true') == 1,
    'chamada modulo': text.count('TotalGestSyncUpsert.run({') == 1,
    'upsert generico removido do app': ".upsert(loteRows, { onConflict: 'id' }).select('id')" not in text,
    'licencas preservadas': "supa.from('licencas').upsert(licUp" in text,
    'juncao preservada': "supa.from('encarregado_funcionarios').insert(rows)" in text,
    'deletes preservados': ".delete().in('id', remover)" in text,
    '_sincronizar preservada': text.count('async function _sincronizar()') == 1,
    'modulo no cache': sw.count("'./assets/js/app-sync-upsert.js'") == 1,
}
for name, ok in checks.items():
    print(name, 'OK' if ok else 'FALHOU')
    if not ok:
        raise SystemExit(1)
print(f'cache PWA: totalgest-v{old_v} -> totalgest-v{old_v + 1}')
