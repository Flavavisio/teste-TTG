from pathlib import Path

app_path = Path('app.html')
shell_path = Path('assets/js/app-shell.js')
sw_path = Path('sw.js')
module_path = Path('assets/js/app-sync-snapshots.js')

app = app_path.read_text(encoding='utf-8')
shell = shell_path.read_text(encoding='utf-8')
sw = sw_path.read_text(encoding='utf-8')

start_token = '        function _reconstruirSnapshots() {'
end_token = '\n\n        // -------- carregamento inicial --------'
assert app.count(start_token) == 1, 'Esperava uma única _reconstruirSnapshots()'
start = app.index(start_token)
end = app.index(end_token, start)
old_block = app[start:end]
assert 'for (const col of ORDEM)' in old_block
assert '_snapLic = new Map();' in old_block
assert '_snapJunc = new Map();' in old_block

new_block = '''        function _reconstruirSnapshots() {
            window.TotalGestSyncSnapshots.rebuild({
                data: dados,
                order: ORDEM,
                metadata: M,
                licenseToRow: licToRow,
                setSnapshots: value => { _snap = value; },
                setLicenseSnapshot: value => { _snapLic = value; },
                setJunctionSnapshot: value => { _snapJunc = value; }
            });
        }'''
app = app[:start] + new_block + app[end:]

module = '''/* Total Gest — reconstrução dos snapshots locais de sincronização
 * Reconstrói o último estado confirmado sem efetuar qualquer chamada de rede.
 */
(function () {
  'use strict';

  function rebuild(options) {
    const opts = options || {};
    const data = opts.data || {};
    const order = opts.order || [];
    const metadata = opts.metadata || {};
    const licenseToRow = opts.licenseToRow;
    const setSnapshots = opts.setSnapshots;
    const setLicenseSnapshot = opts.setLicenseSnapshot;
    const setJunctionSnapshot = opts.setJunctionSnapshot;

    if (typeof licenseToRow !== 'function' || typeof setSnapshots !== 'function' ||
        typeof setLicenseSnapshot !== 'function' || typeof setJunctionSnapshot !== 'function') {
      throw new Error('TotalGestSyncSnapshots: dependencias invalidas');
    }

    const snapshots = {};
    setSnapshots(snapshots);
    for (const collection of order) {
      const snapshot = new Map();
      for (const item of (data[collection] || [])) {
        snapshot.set(item.id, JSON.stringify(metadata[collection].to(item)));
      }
      snapshots[collection] = snapshot;
    }

    const licenseSnapshot = new Map();
    setLicenseSnapshot(licenseSnapshot);
    for (const admin of (data.administradores || [])) {
      if (admin.licenca) {
        licenseSnapshot.set(admin.id, JSON.stringify(licenseToRow(admin.id, admin.licenca)));
      }
    }

    const junctionSnapshot = new Map();
    setJunctionSnapshot(junctionSnapshot);
    for (const encarregado of (data.encarregados || [])) {
      junctionSnapshot.set(encarregado.id, JSON.stringify((encarregado.funcionariosIds || []).slice().sort()));
    }
  }

  window.TotalGestSyncSnapshots = { rebuild: rebuild };
})();
'''
assert not module_path.exists(), 'app-sync-snapshots.js já existe'
module_path.write_text(module, encoding='utf-8')

assert shell.count("syncDiff: './assets/js/app-sync-diff.js',") == 1
shell = shell.replace(
    "syncDiff: './assets/js/app-sync-diff.js',",
    "syncDiff: './assets/js/app-sync-diff.js',\n    syncSnapshots: './assets/js/app-sync-snapshots.js',",
    1
)
assert shell.count('if (options.syncDiff === true) pedidos.push(MODULOS.syncDiff);') == 1
shell = shell.replace(
    'if (options.syncDiff === true) pedidos.push(MODULOS.syncDiff);',
    'if (options.syncDiff === true) pedidos.push(MODULOS.syncDiff);\n    if (options.syncSnapshots === true) pedidos.push(MODULOS.syncSnapshots);',
    1
)

assert app.count('syncDiff: true,') == 1, 'syncDiff: true deveria existir exatamente uma vez'
app = app.replace('syncDiff: true,', 'syncDiff: true,\n                syncSnapshots: true,', 1)

assert "const CACHE = 'totalgest-v34';" in sw
sw = sw.replace("const CACHE = 'totalgest-v34';", "const CACHE = 'totalgest-v35';", 1)
assert sw.count("'./assets/js/app-sync-diff.js',") == 1
sw = sw.replace(
    "'./assets/js/app-sync-diff.js',",
    "'./assets/js/app-sync-diff.js',\n  './assets/js/app-sync-snapshots.js',",
    1
)

assert app.count('function _reconstruirSnapshots()') == 1
assert app.count('window.TotalGestSyncSnapshots.rebuild({') == 1
assert app.count('syncSnapshots: true') == 1
assert shell.count("syncSnapshots: './assets/js/app-sync-snapshots.js'") == 1
assert shell.count('options.syncSnapshots === true') == 1
assert sw.count("'./assets/js/app-sync-snapshots.js'") == 1

app_path.write_text(app, encoding='utf-8')
shell_path.write_text(shell, encoding='utf-8')
sw_path.write_text(sw, encoding='utf-8')
