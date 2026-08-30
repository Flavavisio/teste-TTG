from pathlib import Path
import re

app_path = Path('app.html')
shell_path = Path('assets/js/app-shell.js')
sw_path = Path('sw.js')
module_path = Path('assets/js/app-save-queue.js')

text = app_path.read_text(encoding='utf-8')
shell = shell_path.read_text(encoding='utf-8')
sw = sw_path.read_text(encoding='utf-8')

if module_path.exists() or 'app-save-queue.js' in text or 'app-save-queue.js' in shell:
    raise SystemExit('app-save-queue ja presente; abortar para evitar duplicacao')

# 1) Registar o novo modulo no shell modular.
marker = "    syncHelpers: './assets/js/app-sync-helpers.js',"
if shell.count(marker) != 1:
    raise SystemExit('marcador syncHelpers no app-shell inesperado')
shell = shell.replace(marker, marker + "\n    saveQueue: './assets/js/app-save-queue.js',", 1)

load_marker = '    if (options.syncHelpers === true) pedidos.push(MODULOS.syncHelpers);'
if shell.count(load_marker) != 1:
    raise SystemExit('carregamento syncHelpers no app-shell inesperado')
shell = shell.replace(load_marker, load_marker + "\n    if (options.saveQueue === true) pedidos.push(MODULOS.saveQueue);", 1)

# 2) Ativar saveQueue no init modular de app.html.
init_re = re.compile(r"window\.TotalGestApp\.init\(\{([^}]*)\}\);")
matches = list(init_re.finditer(text))
if len(matches) != 1:
    raise SystemExit(f'init modular inesperado: {len(matches)}')
opts = matches[0].group(1)
if 'syncHelpers: true' not in opts or 'bootstrap: true' not in opts:
    raise SystemExit('opcoes esperadas do init em falta')
if 'saveQueue:' in opts:
    raise SystemExit('saveQueue ja aparece no init')
old_init = matches[0].group(0)
new_opts = opts.replace('bootstrap: true', 'saveQueue: true, bootstrap: true', 1)
text = text.replace(old_init, f'window.TotalGestApp.init({{{new_opts}}});', 1)

# 3) Extrair a serializacao de guardarDados mantendo _sincronizar inline.
if text.count('let _syncChain = Promise.resolve();') != 1:
    raise SystemExit('fronteira _syncChain inesperada')
text = text.replace('        let _syncChain = Promise.resolve();\n', '', 1)

if text.count('await _syncChain;') != 1:
    raise SystemExit('uso de _syncChain em carregarDados inesperado')
text = text.replace('await _syncChain;', 'await _guardarDadosQueue.waitForIdle();', 1)

pat = re.compile(
    r'        function guardarDados\(\) \{.*?\n        \}\n\n        async function _sincronizar\(\) \{',
    re.S,
)
replacement = '''        const _guardarDadosQueue = window.TotalGestSaveQueue.create({
            saveCache: () => _guardarCacheLocal(),
            isOnline: () => navigator.onLine,
            showOffline: () => mostrarStatusOffline(),
            sync: () => _sincronizar(),
            reportError: (err) => {
                console.error('sync:', err);
                mostrarStatusSync(1, 'Ligação: ' + (err && err.message ? err.message : err));
            }
        });

        function guardarDados() {
            return _guardarDadosQueue.save();
        }

        async function _sincronizar() {'''
text, n = pat.subn(replacement, text, count=1)
if n != 1:
    raise SystemExit(f'Esperava substituir 1 guardarDados(), substitui {n}')

# 4) Criar o modulo sem qualquer conhecimento do Supabase/modelo de dados.
module_path.write_text("""/* Total Gest — fila de gravacao/sincronizacao
 * Serializa tentativas de gravacao sem conhecer o modelo de dados nem o Supabase.
 */
(function () {
  'use strict';

  function create(options) {
    const opts = options || {};
    if (typeof opts.saveCache !== 'function' ||
        typeof opts.isOnline !== 'function' ||
        typeof opts.showOffline !== 'function' ||
        typeof opts.sync !== 'function' ||
        typeof opts.reportError !== 'function') {
      throw new Error('TotalGestSaveQueue: dependencias invalidas');
    }

    let chain = Promise.resolve();

    function save() {
      // Mantem a ordem legada: cache primeiro, feedback offline, depois sincronizacao.
      opts.saveCache();
      if (!opts.isOnline()) opts.showOffline();

      const attempt = chain.then(opts.sync);
      // A fila interna recupera para permitir a proxima gravacao; a Promise devolvida
      // por save() continua a refletir o sucesso/erro real desta tentativa.
      chain = attempt.catch(opts.reportError);
      return attempt;
    }

    function waitForIdle() {
      return chain;
    }

    return { save, waitForIdle };
  }

  window.TotalGestSaveQueue = { create };
})();
""", encoding='utf-8')

# 5) Cache PWA: incluir o novo modulo e avançar uma versao para invalidar caches antigos.
cache_marker = "  './assets/js/app-sync-helpers.js',"
if sw.count(cache_marker) != 1:
    raise SystemExit('marcador syncHelpers no service worker inesperado')
sw = sw.replace(cache_marker, cache_marker + "\n  './assets/js/app-save-queue.js',", 1)
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
    'saveQueue no shell': shell.count("saveQueue: './assets/js/app-save-queue.js'") == 1,
    'loader saveQueue': shell.count('options.saveQueue === true') == 1,
    'saveQueue no init': text.count('saveQueue: true') == 1,
    'queue criada': text.count('window.TotalGestSaveQueue.create({') == 1,
    'wrapper guardarDados': text.count('return _guardarDadosQueue.save();') == 1,
    'carregar espera queue': text.count('await _guardarDadosQueue.waitForIdle();') == 1,
    '_syncChain removida': '_syncChain' not in text,
    '_sincronizar preservada': text.count('async function _sincronizar()') == 1,
    'modulo em cache': sw.count("'./assets/js/app-save-queue.js'") == 1,
}
for name, ok in checks.items():
    print(name, 'OK' if ok else 'FALHOU')
    if not ok:
        raise SystemExit(1)
print(f'cache PWA: totalgest-v{old_v} -> totalgest-v{old_v + 1}')
