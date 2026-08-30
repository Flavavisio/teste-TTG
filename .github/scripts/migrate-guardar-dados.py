# Trigger da migração protegida de guardarDados
from pathlib import Path
import re

app = Path('app.html')
text = app.read_text(encoding='utf-8')

if 'assets/js/app-save-queue.js' in text:
    raise SystemExit('app-save-queue.js ja referenciado; abortar')

helper_pat = re.compile(r'(^[ \t]*<script[^>]+src=["\'][^"\']*app-sync-helpers\.js["\'][^>]*></script>)', re.M)
text, n = helper_pat.subn(r'\1\n    <script src="assets/js/app-save-queue.js"></script>', text, count=1)
if n != 1:
    raise SystemExit(f'Esperava 1 referencia a app-sync-helpers.js, encontrei {n}')

if text.count('let _syncChain = Promise.resolve();') != 1:
    raise SystemExit('Fronteira _syncChain inesperada')
text = text.replace('        let _syncChain = Promise.resolve();\n', '', 1)

if text.count('await _syncChain;') != 1:
    raise SystemExit('Uso de _syncChain em carregarDados inesperado')
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

app.write_text(text, encoding='utf-8')

module = Path('assets/js/app-save-queue.js')
module.write_text("""/* Total Gest — fila de gravacao/sincronizacao
 * Mantem as gravacoes serializadas sem conhecer o modelo de dados nem o Supabase.
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
      opts.saveCache();
      if (!opts.isOnline()) opts.showOffline();

      const attempt = chain.then(opts.sync);
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

checks = {
    'script modulo': text.count('assets/js/app-save-queue.js') == 1,
    'queue criada': text.count('window.TotalGestSaveQueue.create({') == 1,
    'wrapper guardarDados': text.count('return _guardarDadosQueue.save();') == 1,
    'carregar espera queue': text.count('await _guardarDadosQueue.waitForIdle();') == 1,
    '_syncChain removida': '_syncChain' not in text,
    '_sincronizar preservada': text.count('async function _sincronizar()') == 1,
}
for name, ok in checks.items():
    print(name, 'OK' if ok else 'FALHOU')
    if not ok:
        raise SystemExit(1)
