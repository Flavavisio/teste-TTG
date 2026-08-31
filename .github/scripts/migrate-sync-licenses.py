from pathlib import Path
import re

app_path = Path('app.html')
shell_path = Path('assets/js/app-shell.js')
sw_path = Path('sw.js')
module_path = Path('assets/js/app-sync-licenses.js')

text = app_path.read_text(encoding='utf-8')
shell = shell_path.read_text(encoding='utf-8')
sw = sw_path.read_text(encoding='utf-8')

if module_path.exists() or 'app-sync-licenses.js' in shell or 'app-sync-licenses.js' in sw:
    raise SystemExit('app-sync-licenses ja presente; abortar para evitar duplicacao')

# 1) Registar o novo modulo no shell.
marker = "    syncUpsert: './assets/js/app-sync-upsert.js',"
if shell.count(marker) != 1:
    raise SystemExit('marcador syncUpsert no app-shell inesperado')
shell = shell.replace(marker, marker + "\n    syncLicenses: './assets/js/app-sync-licenses.js',", 1)

load_marker = '    if (options.syncUpsert === true) pedidos.push(MODULOS.syncUpsert);'
if shell.count(load_marker) != 1:
    raise SystemExit('carregamento syncUpsert no app-shell inesperado')
shell = shell.replace(load_marker, load_marker + "\n    if (options.syncLicenses === true) pedidos.push(MODULOS.syncLicenses);", 1)

# 2) Ativar o modulo no init de app.html.
init_re = re.compile(r"window\.TotalGestApp\.init\(\{([^}]*)\}\);")
matches = list(init_re.finditer(text))
if len(matches) != 1:
    raise SystemExit(f'init modular inesperado: {len(matches)}')
opts = matches[0].group(1)
if 'syncUpsert: true' not in opts or 'saveQueue: true' not in opts:
    raise SystemExit('opcoes esperadas do init em falta')
if 'syncLicenses:' in opts:
    raise SystemExit('syncLicenses ja aparece no init')
old_init = matches[0].group(0)
new_opts = opts.replace('saveQueue: true', 'syncLicenses: true, saveQueue: true', 1)
text = text.replace(old_init, f'window.TotalGestApp.init({{{new_opts}}});', 1)

# 3) Extrair apenas o bloco de licencas, mantendo o tratamento de erro em _sincronizar().
old_block = """                // licenças (a seguir aos administradores)\n                if (col === 'administradores') {\n                    const licUp = [];\n                    const licUpJson = [];\n                    for (const a of lista) {\n                        if (!a.licenca) continue;\n                        const row = licToRow(a.id, a.licenca);\n                        const json = JSON.stringify(row);\n                        if (_snapLic.get(a.id) !== json) { licUp.push(row); licUpJson.push({ id: a.id, json }); }\n                    }\n                    if (licUp.length) {\n                        const { error } = await supa.from('licencas').upsert(licUp, { onConflict: 'admin_id' });\n                        if (error) { console.error('upsert licencas:', error.message); if (!_tabelaInexistente(error)) { erros++; if (!primeiroErro) primeiroErro = 'licencas — ' + (error.message || error.code || 'erro'); } }\n                        else { licUpJson.forEach(u => _snapLic.set(u.id, u.json)); }\n                    }\n                }\n"""
new_block = """                // licenças (a seguir aos administradores)\n                if (col === 'administradores') {\n                    const licResult = await window.TotalGestSyncLicenses.run({\n                        supabase: supa,\n                        admins: lista,\n                        snapshot: _snapLic,\n                        toRow: licToRow\n                    });\n                    if (licResult.error && !_tabelaInexistente(licResult.error)) {\n                        erros++;\n                        if (!primeiroErro) primeiroErro = 'licencas — ' + (licResult.error.message || licResult.error.code || 'erro');\n                    }\n                }\n"""
if text.count(old_block) != 1:
    raise SystemExit(f'bloco de licencas inesperado: {text.count(old_block)}')
text = text.replace(old_block, new_block, 1)

# 4) Criar modulo dedicado. A API Supabase recebida e a tabela usada sao exatamente as mesmas.
module_path.write_text("""/* Total Gest — sincronizacao de licencas\n * Mantem a chamada legada a tabela licencas e atualiza o snapshot apenas apos sucesso.\n */\n(function () {\n  'use strict';\n\n  async function run(options) {\n    const opts = options || {};\n    const supabase = opts.supabase;\n    const admins = opts.admins || [];\n    const snapshot = opts.snapshot;\n    const toRow = opts.toRow;\n\n    if (!supabase || !snapshot || typeof toRow !== 'function') {\n      throw new Error('TotalGestSyncLicenses: dependencias invalidas');\n    }\n\n    const rows = [];\n    const states = [];\n    for (const admin of admins) {\n      if (!admin.licenca) continue;\n      const row = toRow(admin.id, admin.licenca);\n      const json = JSON.stringify(row);\n      if (snapshot.get(admin.id) !== json) {\n        rows.push(row);\n        states.push({ id: admin.id, json: json });\n      }\n    }\n\n    if (!rows.length) return { error: null };\n\n    const result = await supabase.from('licencas').upsert(rows, { onConflict: 'admin_id' });\n    if (result.error) {\n      console.error('upsert licencas:', result.error.message);\n      return { error: result.error };\n    }\n\n    states.forEach(function (state) { snapshot.set(state.id, state.json); });\n    return { error: null };\n  }\n\n  window.TotalGestSyncLicenses = { run: run };\n})();\n""", encoding='utf-8')

# 5) Cache PWA.
cache_marker = "  './assets/js/app-sync-upsert.js',"
if sw.count(cache_marker) != 1:
    raise SystemExit('marcador syncUpsert no service worker inesperado')
sw = sw.replace(cache_marker, cache_marker + "\n  './assets/js/app-sync-licenses.js',", 1)
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
    'syncLicenses no shell': shell.count("syncLicenses: './assets/js/app-sync-licenses.js'") == 1,
    'loader syncLicenses': shell.count('options.syncLicenses === true') == 1,
    'syncLicenses no init': text.count('syncLicenses: true') == 1,
    'modulo usado': text.count('TotalGestSyncLicenses.run(') == 1,
    '_sincronizar preservada': text.count('async function _sincronizar()') == 1,
    'tabela licencas apenas no modulo novo': "supa.from('licencas').upsert" not in text,
    'junção preservada inline': "supa.from('encarregado_funcionarios').delete()" in text,
    'modulo em cache': sw.count("'./assets/js/app-sync-licenses.js'") == 1,
}
for name, ok in checks.items():
    print(name, 'OK' if ok else 'FALHOU')
    if not ok:
        raise SystemExit(1)
print(f'cache PWA: totalgest-v{old_v} -> totalgest-v{old_v + 1}')
