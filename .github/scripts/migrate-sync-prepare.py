from pathlib import Path
import re

app_path = Path('app.html')
shell_path = Path('assets/js/app-shell.js')
sw_path = Path('sw.js')
module_path = Path('assets/js/app-sync-prepare.js')

text = app_path.read_text(encoding='utf-8')
shell = shell_path.read_text(encoding='utf-8')
sw = sw_path.read_text(encoding='utf-8')

if module_path.exists() or 'app-sync-prepare.js' in shell or 'app-sync-prepare.js' in sw:
    raise SystemExit('app-sync-prepare ja presente; abortar para evitar duplicacao')

old_block = """            // repara equipamentos com localId inválido (ex: placeholder '__novo__' de um local nunca gravado)\n            {\n                const idsLocaisValidos = new Set((dados.locais || []).map(l => l.id));\n                (dados.equipamentos || []).forEach(eq => {\n                    if (eq.localId && !idsLocaisValidos.has(eq.localId)) eq.localId = null;\n                });\n            }\n"""
new_block = """            // repara equipamentos com localId inválido (ex: placeholder '__novo__' de um local nunca gravado)\n            window.TotalGestSyncPrepare.repairInvalidEquipmentLocations(dados);\n"""
if text.count(old_block) != 1:
    raise SystemExit(f'bloco de preparacao inesperado: {text.count(old_block)}')
text = text.replace(old_block, new_block, 1)

marker = "    syncDiff: './assets/js/app-sync-diff.js',"
if shell.count(marker) != 1:
    raise SystemExit('marcador syncDiff inesperado')
shell = shell.replace(marker, marker + "\n    syncPrepare: './assets/js/app-sync-prepare.js',", 1)

load_marker = '    if (options.syncDiff === true) pedidos.push(MODULOS.syncDiff);'
if shell.count(load_marker) != 1:
    raise SystemExit('loader syncDiff inesperado')
shell = shell.replace(load_marker, load_marker + "\n    if (options.syncPrepare === true) pedidos.push(MODULOS.syncPrepare);", 1)

init_re = re.compile(r"window\.TotalGestApp\.init\(\{([^}]*)\}\);")
matches = list(init_re.finditer(text))
if len(matches) != 1:
    raise SystemExit(f'init modular inesperado: {len(matches)}')
old_init = matches[0].group(0)
opts = matches[0].group(1)
if 'syncDiff: true' not in opts or 'syncUpsert: true' not in opts:
    raise SystemExit('opcoes sync esperadas em falta no init')
if 'syncPrepare:' in opts:
    raise SystemExit('syncPrepare ja aparece no init')
new_opts = opts.replace('syncDiff: true', 'syncDiff: true, syncPrepare: true', 1)
text = text.replace(old_init, f'window.TotalGestApp.init({{{new_opts}}});', 1)

module_path.write_text("""/* Total Gest — preparação local antes da sincronização\n * Corrige apenas referências locais inválidas; não faz pedidos de rede.\n */\n(function () {\n  'use strict';\n\n  function repairInvalidEquipmentLocations(data) {\n    const source = data || {};\n    const validLocationIds = new Set((source.locais || []).map(function (location) { return location.id; }));\n    (source.equipamentos || []).forEach(function (equipment) {\n      if (equipment.localId && !validLocationIds.has(equipment.localId)) equipment.localId = null;\n    });\n  }\n\n  window.TotalGestSyncPrepare = {\n    repairInvalidEquipmentLocations: repairInvalidEquipmentLocations\n  };\n})();\n""", encoding='utf-8')

cache_marker = "  './assets/js/app-sync-diff.js',"
if sw.count(cache_marker) != 1:
    raise SystemExit('marcador syncDiff no service worker inesperado')
sw = sw.replace(cache_marker, cache_marker + "\n  './assets/js/app-sync-prepare.js',", 1)
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
    'prepare no shell': shell.count("syncPrepare: './assets/js/app-sync-prepare.js'") == 1,
    'loader prepare': shell.count('options.syncPrepare === true') == 1,
    'prepare no init': text.count('syncPrepare: true') == 1,
    'helper usado': text.count('TotalGestSyncPrepare.repairInvalidEquipmentLocations(dados)') == 1,
    'sincronizar preservada': text.count('async function _sincronizar()') == 1,
    'migracao ficheiros preservada': text.count('await migrarFicheirosPendentes();') == 1,
    'modulo no cache': sw.count("'./assets/js/app-sync-prepare.js'") == 1,
}
for name, ok in checks.items():
    print(name, 'OK' if ok else 'FALHOU')
    if not ok:
        raise SystemExit(1)
print(f'cache PWA: totalgest-v{old_v} -> totalgest-v{old_v + 1}')
