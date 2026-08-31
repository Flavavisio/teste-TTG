from pathlib import Path
import re

app_path = Path('app.html')
shell_path = Path('assets/js/app-shell.js')
sw_path = Path('sw.js')
module_path = Path('assets/js/app-sync-diff.js')

text = app_path.read_text(encoding='utf-8')
shell = shell_path.read_text(encoding='utf-8')
sw = sw_path.read_text(encoding='utf-8')

if module_path.exists() or 'app-sync-diff.js' in shell or 'app-sync-diff.js' in sw:
    raise SystemExit('app-sync-diff ja presente; abortar para evitar duplicacao')

# 1) Registar o helper puro no shell modular.
marker = "    syncHelpers: './assets/js/app-sync-helpers.js',"
if shell.count(marker) != 1:
    raise SystemExit('marcador syncHelpers no app-shell inesperado')
shell = shell.replace(marker, marker + "\n    syncDiff: './assets/js/app-sync-diff.js',", 1)

load_marker = '    if (options.syncHelpers === true) pedidos.push(MODULOS.syncHelpers);'
if shell.count(load_marker) != 1:
    raise SystemExit('carregamento syncHelpers no app-shell inesperado')
shell = shell.replace(load_marker, load_marker + "\n    if (options.syncDiff === true) pedidos.push(MODULOS.syncDiff);", 1)

# 2) Ativar syncDiff no init modular de app.html.
init_re = re.compile(r"window\.TotalGestApp\.init\(\{([^}]*)\}\);")
matches = list(init_re.finditer(text))
if len(matches) != 1:
    raise SystemExit(f'init modular inesperado: {len(matches)}')
opts = matches[0].group(1)
if 'syncHelpers: true' not in opts or 'saveQueue: true' not in opts or 'bootstrap: true' not in opts:
    raise SystemExit('opcoes esperadas do init em falta')
if 'syncDiff:' in opts:
    raise SystemExit('syncDiff ja aparece no init')
old_init = matches[0].group(0)
new_opts = opts.replace('saveQueue: true', 'syncDiff: true, saveQueue: true', 1)
text = text.replace(old_init, f'window.TotalGestApp.init({{{new_opts}}});', 1)

# 3) Substituir apenas o cálculo local de UPSERTs.
old_upsert = """                const upserts = [];
                const upsertsJson = [];
                const idsAtuais = new Set();
                for (const o of lista) {
                    idsAtuais.add(o.id);
                    const row = meta.to(o);
                    const json = JSON.stringify(row);
                    if (_snap[col].get(o.id) !== json) { upserts.push(row); upsertsJson.push({ id: o.id, json }); }
                }
"""
new_upsert = """                const diffUpsert = window.TotalGestSyncDiff.changedRows(lista, meta.to, _snap[col]);
                const upserts = diffUpsert.rows;
                const upsertsJson = diffUpsert.states;
"""
if text.count(old_upsert) != 1:
    raise SystemExit(f'bloco de cálculo de upserts inesperado: {text.count(old_upsert)}')
text = text.replace(old_upsert, new_upsert, 1)

# 4) Substituir apenas o cálculo local dos IDs removidos.
old_delete = """                const idsAtuais = new Set((dados[col] || []).map(o => o.id));
                const remover = [];
                for (const id of _snap[col].keys()) if (!idsAtuais.has(id)) remover.push(id);
"""
new_delete = """                const remover = window.TotalGestSyncDiff.deletedIds(dados[col] || [], _snap[col]);
"""
if text.count(old_delete) != 1:
    raise SystemExit(f'bloco de cálculo de deletes inesperado: {text.count(old_delete)}')
text = text.replace(old_delete, new_delete, 1)

# 5) Criar módulo puro: sem Supabase, sem DOM e sem estado global da aplicação.
module_path.write_text("""/* Total Gest — cálculo puro das diferenças de sincronização
 * Não faz pedidos ao Supabase e não altera snapshots; apenas calcula o que mudou.
 */
(function () {
  'use strict';

  function changedRows(list, toRow, snapshot) {
    const rows = [];
    const states = [];
    const source = list || [];

    for (const item of source) {
      const row = toRow(item);
      const json = JSON.stringify(row);
      if (snapshot.get(item.id) !== json) {
        rows.push(row);
        states.push({ id: item.id, json: json });
      }
    }

    return { rows: rows, states: states };
  }

  function deletedIds(list, snapshot) {
    const currentIds = new Set((list || []).map(function (item) { return item.id; }));
    const removed = [];
    for (const id of snapshot.keys()) {
      if (!currentIds.has(id)) removed.push(id);
    }
    return removed;
  }

  window.TotalGestSyncDiff = {
    changedRows: changedRows,
    deletedIds: deletedIds
  };
})();
""", encoding='utf-8')

# 6) Cache PWA.
cache_marker = "  './assets/js/app-sync-helpers.js',"
if sw.count(cache_marker) != 1:
    raise SystemExit('marcador syncHelpers no service worker inesperado')
sw = sw.replace(cache_marker, cache_marker + "\n  './assets/js/app-sync-diff.js',", 1)
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
    'syncDiff no shell': shell.count("syncDiff: './assets/js/app-sync-diff.js'") == 1,
    'loader syncDiff': shell.count('options.syncDiff === true') == 1,
    'syncDiff no init': text.count('syncDiff: true') == 1,
    'changedRows usado': text.count('TotalGestSyncDiff.changedRows(') == 1,
    'deletedIds usado': text.count('TotalGestSyncDiff.deletedIds(') == 1,
    '_sincronizar preservada': text.count('async function _sincronizar()') == 1,
    'upsert Supabase preservado': '.upsert(loteRows' in text,
    'delete Supabase preservado': ".delete().in('id', remover)" in text,
    'modulo em cache': sw.count("'./assets/js/app-sync-diff.js'") == 1,
}
for name, ok in checks.items():
    print(name, 'OK' if ok else 'FALHOU')
    if not ok:
        raise SystemExit(1)
print(f'cache PWA: totalgest-v{old_v} -> totalgest-v{old_v + 1}')
