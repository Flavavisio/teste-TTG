from pathlib import Path

APP = Path('app.html')
SHELL = Path('assets/js/app-shell.js')
SW = Path('sw.js')
MODULE = Path('assets/js/app-sync-files.js')

app = APP.read_text(encoding='utf-8')
shell = SHELL.read_text(encoding='utf-8')
sw = SW.read_text(encoding='utf-8')

old_function = """        async function migrarFicheirosPendentes() {\n            for (const col of Object.keys(FICHEIRO_CAMPOS)) {\n                for (const o of (dados[col] || [])) {\n                    for (const campo of FICHEIRO_CAMPOS[col]) {\n                        const v = o[campo];\n                        if (typeof v === 'string' && v.startsWith('data:')) {\n                            try { o[campo] = await uploadDataURL(v, col); }\n                            catch (e) { console.error('upload ' + col + '.' + campo + ':', e.message || e); } // mantém base64 como fallback\n                        }\n                    }\n                }\n            }\n        }\n"""

new_call = """            await window.TotalGestSyncFiles.migratePending({\n                data: dados,\n                fields: FICHEIRO_CAMPOS,\n                uploadDataURL: uploadDataURL\n            });"""

old_call = "            await migrarFicheirosPendentes();"

if app.count(old_function) != 1:
    raise SystemExit(f'Esperava 1 função migrarFicheirosPendentes, encontrei {app.count(old_function)}')
if app.count(old_call) != 1:
    raise SystemExit(f'Esperava 1 chamada migrarFicheirosPendentes, encontrei {app.count(old_call)}')
if app.count('syncPrepare: true') != 1:
    raise SystemExit('Marcador syncPrepare: true inesperado')

app = app.replace(old_function, '', 1)
app = app.replace(old_call, new_call, 1)
app = app.replace('                    syncPrepare: true,', '                    syncPrepare: true,\n                    syncFiles: true,', 1)

module_text = """/* Total Gest — migração de ficheiros pendentes antes da sincronização\n * Percorre campos configurados, delega o upload e mantém data URLs como fallback em caso de erro.\n */\n(function () {\n  'use strict';\n\n  async function migratePending(options) {\n    const opts = options || {};\n    const data = opts.data || {};\n    const fields = opts.fields || {};\n    const uploadDataURL = opts.uploadDataURL;\n\n    if (typeof uploadDataURL !== 'function') {\n      throw new Error('TotalGestSyncFiles: uploadDataURL invalido');\n    }\n\n    for (const collection of Object.keys(fields)) {\n      for (const item of (data[collection] || [])) {\n        for (const field of fields[collection]) {\n          const value = item[field];\n          if (typeof value === 'string' && value.startsWith('data:')) {\n            try {\n              item[field] = await uploadDataURL(value, collection);\n            } catch (error) {\n              console.error('upload ' + collection + '.' + field + ':', error.message || error);\n              // Mantém o data URL original como fallback, tal como no comportamento legado.\n            }\n          }\n        }\n      }\n    }\n  }\n\n  window.TotalGestSyncFiles = { migratePending: migratePending };\n})();\n"""

if MODULE.exists():
    raise SystemExit(f'{MODULE} já existe')
MODULE.write_text(module_text, encoding='utf-8')

if shell.count("syncPrepare: './assets/js/app-sync-prepare.js',") != 1:
    raise SystemExit('Marcador syncPrepare no shell inesperado')
if shell.count('if (options.syncPrepare === true) pedidos.push(MODULOS.syncPrepare);') != 1:
    raise SystemExit('Loader syncPrepare inesperado')
shell = shell.replace(
    "    syncPrepare: './assets/js/app-sync-prepare.js',",
    "    syncPrepare: './assets/js/app-sync-prepare.js',\n    syncFiles: './assets/js/app-sync-files.js',",
    1
)
shell = shell.replace(
    '    if (options.syncPrepare === true) pedidos.push(MODULOS.syncPrepare);',
    '    if (options.syncPrepare === true) pedidos.push(MODULOS.syncPrepare);\n    if (options.syncFiles === true) pedidos.push(MODULOS.syncFiles);',
    1
)

if "const CACHE = 'totalgest-v30';" not in sw:
    raise SystemExit('Versão PWA esperada v30 não encontrada')
if sw.count("  './assets/js/app-sync-prepare.js',") != 1:
    raise SystemExit('Marcador app-sync-prepare.js no SW inesperado')
sw = sw.replace("const CACHE = 'totalgest-v30';", "const CACHE = 'totalgest-v31';", 1)
sw = sw.replace(
    "  './assets/js/app-sync-prepare.js',",
    "  './assets/js/app-sync-prepare.js',\n  './assets/js/app-sync-files.js',",
    1
)

# Validações estruturais antes de gravar.
if 'function migrarFicheirosPendentes' in app or 'async function migrarFicheirosPendentes' in app:
    raise SystemExit('A função inline ainda existe')
if app.count('window.TotalGestSyncFiles.migratePending') != 1:
    raise SystemExit('A nova chamada deve existir exatamente uma vez')
if app.count('function uploadDataURL') + app.count('async function uploadDataURL') < 1:
    raise SystemExit('uploadDataURL deixou de existir no app.html')
if app.count('async function _sincronizar()') != 1:
    raise SystemExit('_sincronizar() deveria continuar a existir exatamente uma vez')
if app.count('syncFiles: true') != 1:
    raise SystemExit('syncFiles: true deveria existir exatamente uma vez')

APP.write_text(app, encoding='utf-8')
SHELL.write_text(shell, encoding='utf-8')
SW.write_text(sw, encoding='utf-8')

print('Extração de migrarFicheirosPendentes preparada com sucesso.')
