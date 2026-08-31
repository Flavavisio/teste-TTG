from pathlib import Path

APP = Path('app.html')
SHELL = Path('assets/js/app-shell.js')
SW = Path('sw.js')
MODULE = Path('assets/js/app-sync-finalize.js')

app = APP.read_text(encoding='utf-8')
shell = SHELL.read_text(encoding='utf-8')
sw = SW.read_text(encoding='utf-8')

old_block = """            mostrarStatusSync(erros, primeiroErro);\n            _guardarCacheLocal(); // mantém a cópia local a par do que já foi confirmado no servidor\n            mostrarStatusOffline(erros > 0); // atualiza sempre o aviso (limpa se já sincronizado, ou mostra o erro real se falhou)\n            // IMPORTANTE: sem isto, quem chama guardarDados(dados) e usa try/catch para saber se a\n            // gravação foi mesmo confirmada (ex: antes de mostrar \"sucesso\" a alguém) nunca ficava a\n            // saber que algo falhou — esta função só registava o erro num contador interno e seguia\n            // em frente sem avisar ninguém. Agora, se alguma tabela falhou a sério nesta chamada,\n            // a promise devolvida por guardarDados() falha também, e quem estiver à espera dela\n            // (com await + try/catch) fica mesmo a saber, em vez de pensar que ficou tudo guardado.\n            if (erros > 0) throw new Error(primeiroErro || 'Não foi possível confirmar a gravação no servidor.');"""
new_block = """            window.TotalGestSyncFinalize.run({\n                errors: erros,\n                firstError: primeiroErro,\n                showSyncStatus: mostrarStatusSync,\n                saveCache: _guardarCacheLocal,\n                showOfflineStatus: mostrarStatusOffline\n            });"""

if app.count(old_block) != 1:
    raise SystemExit(f'Bloco final esperado 1 vez, encontrado {app.count(old_block)}')
if app.count('syncFiles: true') != 1:
    raise SystemExit('syncFiles: true deveria existir exatamente uma vez')

app = app.replace(old_block, new_block, 1)
app = app.replace('syncFiles: true,', 'syncFiles: true, syncFinalize: true,', 1)

module_text = """/* Total Gest — finalização da sincronização\n * Atualiza estados/cache e propaga falhas confirmadas ao chamador.\n */\n(function () {\n  'use strict';\n\n  function run(options) {\n    const opts = options || {};\n    const errors = Number(opts.errors || 0);\n    const firstError = opts.firstError || '';\n    const showSyncStatus = opts.showSyncStatus;\n    const saveCache = opts.saveCache;\n    const showOfflineStatus = opts.showOfflineStatus;\n\n    if (typeof showSyncStatus !== 'function' || typeof saveCache !== 'function' || typeof showOfflineStatus !== 'function') {\n      throw new Error('TotalGestSyncFinalize: dependencias invalidas');\n    }\n\n    showSyncStatus(errors, firstError);\n    saveCache();\n    showOfflineStatus(errors > 0);\n\n    if (errors > 0) {\n      throw new Error(firstError || 'Não foi possível confirmar a gravação no servidor.');\n    }\n  }\n\n  window.TotalGestSyncFinalize = { run: run };\n})();\n"""

if MODULE.exists():
    raise SystemExit(f'{MODULE} já existe')
MODULE.write_text(module_text, encoding='utf-8')

if shell.count("syncFiles: './assets/js/app-sync-files.js',") != 1:
    raise SystemExit('Marcador syncFiles no shell inesperado')
if shell.count('if (options.syncFiles === true) pedidos.push(MODULOS.syncFiles);') != 1:
    raise SystemExit('Loader syncFiles inesperado')
shell = shell.replace("    syncFiles: './assets/js/app-sync-files.js',", "    syncFiles: './assets/js/app-sync-files.js',\n    syncFinalize: './assets/js/app-sync-finalize.js',", 1)
shell = shell.replace('    if (options.syncFiles === true) pedidos.push(MODULOS.syncFiles);', '    if (options.syncFiles === true) pedidos.push(MODULOS.syncFiles);\n    if (options.syncFinalize === true) pedidos.push(MODULOS.syncFinalize);', 1)

if "const CACHE = 'totalgest-v31';" not in sw:
    raise SystemExit('Versão PWA esperada v31 não encontrada')
if sw.count("  './assets/js/app-sync-files.js',") != 1:
    raise SystemExit('Marcador app-sync-files.js no SW inesperado')
sw = sw.replace("const CACHE = 'totalgest-v31';", "const CACHE = 'totalgest-v32';", 1)
sw = sw.replace("  './assets/js/app-sync-files.js',", "  './assets/js/app-sync-files.js',\n  './assets/js/app-sync-finalize.js',", 1)

if app.count('window.TotalGestSyncFinalize.run(') != 1:
    raise SystemExit('A nova finalização deve existir exatamente uma vez')
if app.count('async function _sincronizar()') != 1:
    raise SystemExit('_sincronizar() deveria continuar a existir exatamente uma vez')
if app.count('syncFinalize: true') != 1:
    raise SystemExit('syncFinalize: true deveria existir exatamente uma vez')
if 'mostrarStatusSync(erros, primeiroErro);' in app:
    raise SystemExit('A finalização inline ainda existe')

APP.write_text(app, encoding='utf-8')
SHELL.write_text(shell, encoding='utf-8')
SW.write_text(sw, encoding='utf-8')
print('Extração da finalização preparada com sucesso.')
