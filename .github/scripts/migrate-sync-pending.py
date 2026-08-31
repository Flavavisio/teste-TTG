from pathlib import Path

APP = Path('app.html')
SHELL = Path('assets/js/app-shell.js')
SW = Path('sw.js')
MODULE = Path('assets/js/app-sync-pending.js')

app = APP.read_text(encoding='utf-8')
shell = SHELL.read_text(encoding='utf-8')
sw = SW.read_text(encoding='utf-8')

old = """        function _contarAlteracoesPendentes() {
            let n = 0;
            ORDEM.forEach(col => {
                (dados[col] || []).forEach(o => {
                    const json = JSON.stringify(M[col].to(o));
                    if (_snap[col].get(o.id) !== json) n++;
                });
                for (const id of _snap[col].keys()) {
                    if (!(dados[col] || []).some(o => o.id === id)) n++;
                }
            });
            return n;
        }
"""
new = """        function _contarAlteracoesPendentes() {
            return window.TotalGestSyncPending.count({
                order: ORDEM,
                data: dados,
                metadata: M,
                snapshots: _snap
            });
        }
"""
if app.count(old) != 1:
    raise SystemExit(f'Bloco _contarAlteracoesPendentes esperado 1 vez, encontrado {app.count(old)}')
app = app.replace(old, new, 1)

if app.count('syncSnapshots: true') != 1:
    raise SystemExit('syncSnapshots: true deve existir exatamente uma vez')
app = app.replace('syncSnapshots: true', 'syncSnapshots: true,\n            syncPending: true', 1)

module_src = """/* Total Gest — contagem de alterações locais pendentes
 * Compara os dados atuais com os snapshots confirmados sem efetuar chamadas de rede.
 */
(function () {
  'use strict';

  function count(options) {
    const opts = options || {};
    const order = opts.order || [];
    const data = opts.data || {};
    const metadata = opts.metadata || {};
    const snapshots = opts.snapshots || {};
    let total = 0;

    for (const collection of order) {
      const list = data[collection] || [];
      for (const item of list) {
        const json = JSON.stringify(metadata[collection].to(item));
        if (snapshots[collection].get(item.id) !== json) total++;
      }
      for (const id of snapshots[collection].keys()) {
        if (!list.some(item => item.id === id)) total++;
      }
    }

    return total;
  }

  window.TotalGestSyncPending = { count: count };
})();
"""
MODULE.write_text(module_src, encoding='utf-8')

needle = "    syncSnapshots: './assets/js/app-sync-snapshots.js',\n"
if shell.count(needle) != 1:
    raise SystemExit('Registo syncSnapshots inesperado no shell')
shell = shell.replace(needle, needle + "    syncPending: './assets/js/app-sync-pending.js',\n", 1)

needle = "    if (options.syncSnapshots === true) pedidos.push(MODULOS.syncSnapshots);\n"
if shell.count(needle) != 1:
    raise SystemExit('Loader syncSnapshots inesperado no shell')
shell = shell.replace(needle, needle + "    if (options.syncPending === true) pedidos.push(MODULOS.syncPending);\n", 1)

if "const CACHE = 'totalgest-v35';" not in sw:
    raise SystemExit('Versão PWA esperada totalgest-v35 não encontrada')
sw = sw.replace("const CACHE = 'totalgest-v35';", "const CACHE = 'totalgest-v36';", 1)
needle = "  './assets/js/app-sync-snapshots.js',\n"
if sw.count(needle) != 1:
    raise SystemExit('Entrada app-sync-snapshots.js inesperada no SW')
sw = sw.replace(needle, needle + "  './assets/js/app-sync-pending.js',\n", 1)

# Invariantes simples após a transformação.
if app.count('function _contarAlteracoesPendentes()') != 1:
    raise SystemExit('Wrapper _contarAlteracoesPendentes deve existir exatamente uma vez')
if app.count('window.TotalGestSyncPending.count({') != 1:
    raise SystemExit('Nova chamada ao módulo pending deve existir exatamente uma vez')
if app.count('syncPending: true') != 1:
    raise SystemExit('syncPending: true deve existir exatamente uma vez')

APP.write_text(app, encoding='utf-8')
SHELL.write_text(shell, encoding='utf-8')
SW.write_text(sw, encoding='utf-8')
