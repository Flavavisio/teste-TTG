from pathlib import Path

APP = Path('app.html')
SHELL = Path('assets/js/app-shell.js')
SW = Path('sw.js')
MODULE = Path('assets/js/app-sync-collections.js')

app = APP.read_text(encoding='utf-8')
shell = SHELL.read_text(encoding='utf-8')
sw = SW.read_text(encoding='utf-8')

start_marker = "            // 1) UPSERTS na ordem das FKs\n"
end_marker = "            // 2) DELETES na ordem inversa\n"

if app.count(start_marker) != 1:
    raise SystemExit(f'Marcador inicial inesperado: {app.count(start_marker)}')
if app.count(end_marker) != 1:
    raise SystemExit(f'Marcador final inesperado: {app.count(end_marker)}')

start = app.index(start_marker)
end = app.index(end_marker, start)
old_block = app[start:end]

required = [
    'for (const col of ORDEM)',
    'window.TotalGestSyncDiff.changedRows',
    'window.TotalGestSyncUpsert.run',
    'window.TotalGestSyncLicenses.run',
    'window.TotalGestSyncEncarregados.run',
    "col === 'obraPontoLonga'",
]
for item in required:
    if item not in old_block:
        raise SystemExit(f'Dependência esperada não encontrada no ciclo: {item}')

new_block = """            // 1) sincronizar coleções na ordem das FKs\n            const collectionsResult = await window.TotalGestSyncCollections.run({\n                supabase: supa,\n                order: ORDEM,\n                metadata: M,\n                data: dados,\n                snapshots: _snap,\n                licenseSnapshot: _snapLic,\n                junctionSnapshot: _snapJunc,\n                changedRows: window.TotalGestSyncDiff.changedRows,\n                runUpsert: window.TotalGestSyncUpsert.run,\n                runLicenses: window.TotalGestSyncLicenses.run,\n                runEncarregados: window.TotalGestSyncEncarregados.run,\n                licenseToRow: licToRow,\n                missingColumn: _colunaEmFalta,\n                missingTable: _tabelaInexistente\n            });\n            erros += collectionsResult.errors;\n            if (!primeiroErro && collectionsResult.firstError) primeiroErro = collectionsResult.firstError;\n"""

app = app[:start] + new_block + app[end:]

if app.count('syncFiles: true') != 1:
    raise SystemExit('syncFiles: true deveria existir exatamente uma vez')
app = app.replace('syncFiles: true,', 'syncFiles: true, syncCollections: true,', 1)

module_text = """/* Total Gest — orquestração da sincronização das coleções\n * Mantém a ordem das FKs e delega cada responsabilidade nos módulos já extraídos.\n */\n(function () {\n  'use strict';\n\n  async function run(options) {\n    const opts = options || {};\n    const supabase = opts.supabase;\n    const order = opts.order || [];\n    const metadata = opts.metadata || {};\n    const data = opts.data || {};\n    const snapshots = opts.snapshots || {};\n    const licenseSnapshot = opts.licenseSnapshot;\n    const junctionSnapshot = opts.junctionSnapshot;\n    const changedRows = opts.changedRows;\n    const runUpsert = opts.runUpsert;\n    const runLicenses = opts.runLicenses;\n    const runEncarregados = opts.runEncarregados;\n    const licenseToRow = opts.licenseToRow;\n    const missingColumn = opts.missingColumn;\n    const missingTable = opts.missingTable;\n    let errors = 0;\n    let firstError = '';\n\n    if (!supabase || typeof changedRows !== 'function' || typeof runUpsert !== 'function' ||\n        typeof runLicenses !== 'function' || typeof runEncarregados !== 'function' ||\n        typeof licenseToRow !== 'function' || typeof missingColumn !== 'function' ||\n        typeof missingTable !== 'function') {\n      throw new Error('TotalGestSyncCollections: dependencias invalidas');\n    }\n\n    for (const collection of order) {\n      const meta = metadata[collection];\n      const list = data[collection] || [];\n      const diff = changedRows(list, meta.to, snapshots[collection]);\n      const rows = diff.rows;\n      const states = diff.states;\n\n      if (collection === 'obraPontoLonga' && list.length) {\n        console.log('[obraPontoLonga] a sincronizar:', rows.length, 'de', list.length, 'registo(s) local(is)');\n      }\n\n      if (rows.length) {\n        const upsertResult = await runUpsert({\n          supabase: supabase,\n          table: meta.tabela,\n          rows: rows,\n          states: states,\n          snapshot: snapshots[collection],\n          missingColumn: missingColumn\n        });\n        const tableError = upsertResult.error;\n        if (tableError && !missingTable(tableError) && collection !== 'auditoria') {\n          errors++;\n          if (!firstError) firstError = meta.tabela + ' — ' + (tableError.message || tableError.code || 'erro');\n        }\n      }\n\n      if (collection === 'administradores') {\n        const licenseResult = await runLicenses({\n          supabase: supabase,\n          admins: list,\n          snapshot: licenseSnapshot,\n          toRow: licenseToRow\n        });\n        if (licenseResult.error && !missingTable(licenseResult.error)) {\n          errors++;\n          if (!firstError) firstError = 'licencas — ' + (licenseResult.error.message || licenseResult.error.code || 'erro');\n        }\n      }\n\n      if (collection === 'encarregados') {\n        const junctionResult = await runEncarregados({\n          supabase: supabase,\n          encarregados: list,\n          snapshot: junctionSnapshot,\n          missingTable: missingTable\n        });\n        errors += junctionResult.errors;\n        if (!firstError && junctionResult.firstError) firstError = junctionResult.firstError;\n      }\n    }\n\n    return { errors: errors, firstError: firstError };\n  }\n\n  window.TotalGestSyncCollections = { run: run };\n})();\n"""

if MODULE.exists():
    raise SystemExit(f'{MODULE} já existe')
MODULE.write_text(module_text, encoding='utf-8')

shell_marker = "    syncFiles: './assets/js/app-sync-files.js',"
loader_marker = '    if (options.syncFiles === true) pedidos.push(MODULOS.syncFiles);'
if shell.count(shell_marker) != 1 or shell.count(loader_marker) != 1:
    raise SystemExit('Marcadores syncFiles no shell inesperados')
shell = shell.replace(shell_marker, shell_marker + "\n    syncCollections: './assets/js/app-sync-collections.js',", 1)
shell = shell.replace(loader_marker, loader_marker + '\n    if (options.syncCollections === true) pedidos.push(MODULOS.syncCollections);', 1)

if "const CACHE = 'totalgest-v32';" not in sw:
    raise SystemExit('Versão PWA esperada v32 não encontrada')
sw_marker = "  './assets/js/app-sync-files.js',"
if sw.count(sw_marker) != 1:
    raise SystemExit('Marcador app-sync-files.js no SW inesperado')
sw = sw.replace("const CACHE = 'totalgest-v32';", "const CACHE = 'totalgest-v33';", 1)
sw = sw.replace(sw_marker, sw_marker + "\n  './assets/js/app-sync-collections.js',", 1)

# Validações estruturais.
if app.count('window.TotalGestSyncCollections.run(') != 1:
    raise SystemExit('Nova chamada sync collections deveria existir exatamente uma vez')
if 'for (const col of ORDEM)' in app[start:start + len(new_block) + 1000]:
    raise SystemExit('O ciclo inline de ORDEM ainda parece existir na zona migrada')
if app.count('window.TotalGestSyncUpsert.run(') != 0:
    raise SystemExit('A chamada direta a SyncUpsert deveria ter saído de app.html')
if app.count('window.TotalGestSyncLicenses.run(') != 0:
    raise SystemExit('A chamada direta a SyncLicenses deveria ter saído de app.html')
if app.count('window.TotalGestSyncEncarregados.run(') != 0:
    raise SystemExit('A chamada direta a SyncEncarregados deveria ter saído de app.html')
if app.count('async function _sincronizar()') != 1:
    raise SystemExit('_sincronizar() deveria continuar a existir exatamente uma vez')
if app.count('window.TotalGestSyncDelete.run(') != 1:
    raise SystemExit('SyncDelete deveria continuar exatamente uma vez')
if app.count('window.TotalGestSyncFinalize.run(') != 1:
    raise SystemExit('SyncFinalize deveria continuar exatamente uma vez')
if app.count('syncCollections: true') != 1:
    raise SystemExit('syncCollections: true deveria existir exatamente uma vez')

APP.write_text(app, encoding='utf-8')
SHELL.write_text(shell, encoding='utf-8')
SW.write_text(sw, encoding='utf-8')
print('Extração do ciclo de coleções preparada com sucesso.')
