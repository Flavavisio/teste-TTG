from pathlib import Path

APP = Path('app.html')
SHELL = Path('assets/js/app-shell.js')
SW = Path('sw.js')
MODULE = Path('assets/js/app-sync-orchestrator.js')

app = APP.read_text(encoding='utf-8')
shell = SHELL.read_text(encoding='utf-8')
sw = SW.read_text(encoding='utf-8')

marker = '        async function _sincronizar() {'
start = app.find(marker)
if start < 0:
    raise SystemExit('_sincronizar() não encontrada')

# Encontra o fim da função por contagem de chavetas.
pos = start + len(marker)
depth = 1
while pos < len(app) and depth:
    ch = app[pos]
    if ch == '{':
        depth += 1
    elif ch == '}':
        depth -= 1
    pos += 1
if depth != 0:
    raise SystemExit('Não foi possível determinar o fim de _sincronizar()')
old_function = app[start:pos]

required = [
    'navigator.onLine',
    'window.TotalGestSyncPrepare.repairInvalidEquipmentLocations',
    'window.TotalGestSyncFiles.migratePending',
    'window.TotalGestSyncCollections.run',
    'window.TotalGestSyncDelete.run',
    'window.TotalGestSyncFinalize.run'
]
for token in required:
    if token not in old_function:
        raise SystemExit(f'Dependência esperada não encontrada em _sincronizar(): {token}')

new_function = '''        async function _sincronizar() {
            await window.TotalGestSyncOrchestrator.run({
                isOnline: function () { return navigator.onLine; },
                showOfflineStatus: mostrarStatusOffline,
                data: dados,
                repairInvalidEquipmentLocations: window.TotalGestSyncPrepare.repairInvalidEquipmentLocations,
                migratePending: window.TotalGestSyncFiles.migratePending,
                fields: FICHEIRO_CAMPOS,
                uploadDataURL: uploadDataURL,
                runCollections: window.TotalGestSyncCollections.run,
                supabase: supa,
                order: ORDEM,
                metadata: M,
                snapshots: _snap,
                licenseSnapshot: _snapLic,
                junctionSnapshot: _snapJunc,
                changedRows: window.TotalGestSyncDiff.changedRows,
                runUpsert: window.TotalGestSyncUpsert.run,
                runLicenses: window.TotalGestSyncLicenses.run,
                runEncarregados: window.TotalGestSyncEncarregados.run,
                licenseToRow: licToRow,
                missingColumn: _colunaEmFalta,
                missingTable: _tabelaInexistente,
                runDelete: window.TotalGestSyncDelete.run,
                deletedIds: window.TotalGestSyncDiff.deletedIds,
                finalize: window.TotalGestSyncFinalize.run,
                showSyncStatus: mostrarStatusSync,
                saveCache: _guardarCacheLocal
            });
        }'''

app = app[:start] + new_function + app[pos:]

if app.count('window.TotalGestSyncOrchestrator.run({') != 1:
    raise SystemExit('A chamada ao orquestrador deveria existir exatamente uma vez')
if app.count('async function _sincronizar()') != 1:
    raise SystemExit('_sincronizar() deveria continuar exatamente uma vez')
for forbidden in [
    'const collectionsResult = await window.TotalGestSyncCollections.run',
    'const deleteResult = await window.TotalGestSyncDelete.run',
    'window.TotalGestSyncFinalize.run({\n                errors:'
]:
    if forbidden in app:
        raise SystemExit(f'Bloco antigo ainda presente: {forbidden}')

module_text = '''/* Total Gest — orquestração principal da sincronização
 * Coordena preparação, ficheiros, coleções, deletes e finalização sem alterar a lógica de cada módulo.
 */
(function () {
  'use strict';

  async function run(options) {
    const opts = options || {};
    const isOnline = opts.isOnline;
    const showOfflineStatus = opts.showOfflineStatus;
    const data = opts.data || {};
    const repairInvalidEquipmentLocations = opts.repairInvalidEquipmentLocations;
    const migratePending = opts.migratePending;
    const runCollections = opts.runCollections;
    const runDelete = opts.runDelete;
    const finalize = opts.finalize;

    if (typeof isOnline !== 'function' || typeof showOfflineStatus !== 'function' ||
        typeof repairInvalidEquipmentLocations !== 'function' || typeof migratePending !== 'function' ||
        typeof runCollections !== 'function' || typeof runDelete !== 'function' || typeof finalize !== 'function') {
      throw new Error('TotalGestSyncOrchestrator: dependencias invalidas');
    }

    if (!isOnline()) {
      showOfflineStatus();
      return;
    }

    repairInvalidEquipmentLocations(data);

    await migratePending({
      data: data,
      fields: opts.fields,
      uploadDataURL: opts.uploadDataURL
    });

    let errors = 0;
    let firstError = '';

    const collectionsResult = await runCollections({
      supabase: opts.supabase,
      order: opts.order,
      metadata: opts.metadata,
      data: data,
      snapshots: opts.snapshots,
      licenseSnapshot: opts.licenseSnapshot,
      junctionSnapshot: opts.junctionSnapshot,
      changedRows: opts.changedRows,
      runUpsert: opts.runUpsert,
      runLicenses: opts.runLicenses,
      runEncarregados: opts.runEncarregados,
      licenseToRow: opts.licenseToRow,
      missingColumn: opts.missingColumn,
      missingTable: opts.missingTable
    });
    errors += collectionsResult.errors;
    if (!firstError && collectionsResult.firstError) firstError = collectionsResult.firstError;

    const deleteResult = await runDelete({
      supabase: opts.supabase,
      order: opts.order,
      metadata: opts.metadata,
      data: data,
      snapshots: opts.snapshots,
      licenseSnapshot: opts.licenseSnapshot,
      junctionSnapshot: opts.junctionSnapshot,
      deletedIds: opts.deletedIds,
      missingTable: opts.missingTable
    });
    errors += deleteResult.errors;
    if (!firstError && deleteResult.firstError) firstError = deleteResult.firstError;

    finalize({
      errors: errors,
      firstError: firstError,
      showSyncStatus: opts.showSyncStatus,
      saveCache: opts.saveCache,
      showOfflineStatus: showOfflineStatus
    });
  }

  window.TotalGestSyncOrchestrator = { run: run };
})();
'''

if MODULE.exists():
    raise SystemExit(f'{MODULE} já existe')
MODULE.write_text(module_text, encoding='utf-8')

if shell.count("syncCollections: './assets/js/app-sync-collections.js',") != 1:
    raise SystemExit('Marcador syncCollections no shell inesperado')
shell = shell.replace(
    "    syncCollections: './assets/js/app-sync-collections.js',",
    "    syncCollections: './assets/js/app-sync-collections.js',\n    syncOrchestrator: './assets/js/app-sync-orchestrator.js',",
    1
)
if shell.count('if (options.syncCollections === true) pedidos.push(MODULOS.syncCollections);') != 1:
    raise SystemExit('Loader syncCollections inesperado')
shell = shell.replace(
    '    if (options.syncCollections === true) pedidos.push(MODULOS.syncCollections);',
    '    if (options.syncCollections === true) pedidos.push(MODULOS.syncCollections);\n    if (options.syncOrchestrator === true) pedidos.push(MODULOS.syncOrchestrator);',
    1
)

if app.count('syncCollections: true') != 1:
    raise SystemExit('Marcador syncCollections: true inesperado no init')
app = app.replace('syncCollections: true,', 'syncCollections: true, syncOrchestrator: true,', 1)
if app.count('syncOrchestrator: true') != 1:
    raise SystemExit('syncOrchestrator: true deveria existir exatamente uma vez')

if "const CACHE = 'totalgest-v33';" not in sw:
    raise SystemExit('Versão PWA esperada v33 não encontrada')
if sw.count("  './assets/js/app-sync-collections.js',") != 1:
    raise SystemExit('Marcador app-sync-collections.js no SW inesperado')
sw = sw.replace("const CACHE = 'totalgest-v33';", "const CACHE = 'totalgest-v34';", 1)
sw = sw.replace(
    "  './assets/js/app-sync-collections.js',",
    "  './assets/js/app-sync-collections.js',\n  './assets/js/app-sync-orchestrator.js',",
    1
)

APP.write_text(app, encoding='utf-8')
SHELL.write_text(shell, encoding='utf-8')
SW.write_text(sw, encoding='utf-8')
print('Extração da orquestração final preparada com sucesso.')
