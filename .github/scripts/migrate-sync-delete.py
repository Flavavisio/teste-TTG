from pathlib import Path
import re

app_path = Path('app.html')
shell_path = Path('assets/js/app-shell.js')
sw_path = Path('sw.js')
module_path = Path('assets/js/app-sync-delete.js')

text = app_path.read_text(encoding='utf-8')
shell = shell_path.read_text(encoding='utf-8')
sw = sw_path.read_text(encoding='utf-8')

if module_path.exists() or 'app-sync-delete.js' in shell or 'app-sync-delete.js' in sw:
    raise SystemExit('app-sync-delete ja presente; abortar para evitar duplicacao')

# 1) Registar módulo no shell.
marker = "    syncEncarregados: './assets/js/app-sync-encarregados.js',"
if shell.count(marker) != 1:
    raise SystemExit('marcador syncEncarregados inesperado')
shell = shell.replace(marker, marker + "\n    syncDelete: './assets/js/app-sync-delete.js',", 1)

load_marker = '    if (options.syncEncarregados === true) pedidos.push(MODULOS.syncEncarregados);'
if shell.count(load_marker) != 1:
    raise SystemExit('loader syncEncarregados inesperado')
shell = shell.replace(load_marker, load_marker + "\n    if (options.syncDelete === true) pedidos.push(MODULOS.syncDelete);", 1)

# 2) Ativar no init modular.
init_re = re.compile(r"window\.TotalGestApp\.init\(\{([^}]*)\}\);")
matches = list(init_re.finditer(text))
if len(matches) != 1:
    raise SystemExit(f'init modular inesperado: {len(matches)}')
opts = matches[0].group(1)
if 'syncEncarregados: true' not in opts or 'saveQueue: true' not in opts:
    raise SystemExit('opcoes esperadas do init em falta')
if 'syncDelete:' in opts:
    raise SystemExit('syncDelete ja aparece no init')
old_init = matches[0].group(0)
new_opts = opts.replace('saveQueue: true', 'syncDelete: true, saveQueue: true', 1)
text = text.replace(old_init, f'window.TotalGestApp.init({{{new_opts}}});', 1)

# 3) Substituir apenas o bloco genérico de DELETEs.
old_block = """            // 2) DELETES na ordem inversa
            for (let i = ORDEM.length - 1; i >= 0; i--) {
                const col = ORDEM[i];
                const meta = M[col];
                const remover = window.TotalGestSyncDiff.deletedIds(dados[col] || [], _snap[col]);
                if (remover.length) {
                    const { error } = await supa.from(meta.tabela).delete().in('id', remover);
                    if (error) {
                        console.error('delete ' + meta.tabela + ':', error.message);
                        if (!_tabelaInexistente(error)) { erros++; if (!primeiroErro) primeiroErro = 'apagar ' + meta.tabela + ' — ' + (error.message || error.code || 'erro'); }
                        // NÃO remove do snapshot — tenta apagar de novo na próxima sincronização
                    } else {
                        for (const id of remover) { _snap[col].delete(id); _snapLic.delete(id); _snapJunc.delete(id); }
                    }
                }
            }
"""
new_block = """            // 2) DELETES na ordem inversa
            const deleteResult = await window.TotalGestSyncDelete.run({
                supabase: supa,
                order: ORDEM,
                metadata: M,
                data: dados,
                snapshots: _snap,
                licenseSnapshot: _snapLic,
                junctionSnapshot: _snapJunc,
                deletedIds: window.TotalGestSyncDiff.deletedIds,
                missingTable: _tabelaInexistente
            });
            erros += deleteResult.errors;
            if (!primeiroErro && deleteResult.firstError) primeiroErro = deleteResult.firstError;
"""
if text.count(old_block) != 1:
    raise SystemExit(f'bloco DELETE inesperado: {text.count(old_block)}')
text = text.replace(old_block, new_block, 1)

# 4) Criar módulo.
module_path.write_text("""/* Total Gest — DELETE genérico da sincronização
 * Executa remoções na ordem inversa das FKs e só limpa snapshots após confirmação do servidor.
 */
(function () {
  'use strict';

  async function run(options) {
    const opts = options || {};
    const supabase = opts.supabase;
    const order = opts.order || [];
    const metadata = opts.metadata || {};
    const data = opts.data || {};
    const snapshots = opts.snapshots || {};
    const licenseSnapshot = opts.licenseSnapshot;
    const junctionSnapshot = opts.junctionSnapshot;
    const deletedIds = opts.deletedIds;
    const missingTable = opts.missingTable;
    let errors = 0;
    let firstError = '';

    if (!supabase || typeof deletedIds !== 'function' || typeof missingTable !== 'function') {
      throw new Error('TotalGestSyncDelete: dependencias invalidas');
    }

    for (let i = order.length - 1; i >= 0; i--) {
      const collection = order[i];
      const meta = metadata[collection];
      const snapshot = snapshots[collection];
      if (!meta || !snapshot) continue;

      const removed = deletedIds(data[collection] || [], snapshot);
      if (!removed.length) continue;

      const result = await supabase.from(meta.tabela).delete().in('id', removed);
      const error = result.error;
      if (error) {
        console.error('delete ' + meta.tabela + ':', error.message);
        if (!missingTable(error)) {
          errors++;
          if (!firstError) firstError = 'apagar ' + meta.tabela + ' — ' + (error.message || error.code || 'erro');
        }
        // Mantém snapshots para voltar a tentar na próxima sincronização.
        continue;
      }

      for (const id of removed) {
        snapshot.delete(id);
        if (licenseSnapshot) licenseSnapshot.delete(id);
        if (junctionSnapshot) junctionSnapshot.delete(id);
      }
    }

    return { errors: errors, firstError: firstError };
  }

  window.TotalGestSyncDelete = { run: run };
})();
""", encoding='utf-8')

# 5) Cache PWA.
cache_marker = "  './assets/js/app-sync-encarregados.js',"
if sw.count(cache_marker) != 1:
    raise SystemExit('marcador syncEncarregados no SW inesperado')
sw = sw.replace(cache_marker, cache_marker + "\n  './assets/js/app-sync-delete.js',", 1)
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
    'syncDelete no shell': shell.count("syncDelete: './assets/js/app-sync-delete.js'") == 1,
    'loader syncDelete': shell.count('options.syncDelete === true') == 1,
    'syncDelete no init': text.count('syncDelete: true') == 1,
    'run syncDelete': text.count('TotalGestSyncDelete.run({') == 1,
    'delete inline removido': ".delete().in('id', remover)" not in text,
    '_sincronizar preservada': text.count('async function _sincronizar()') == 1,
    'modulo em cache': sw.count("'./assets/js/app-sync-delete.js'") == 1,
}
for name, ok in checks.items():
    print(name, 'OK' if ok else 'FALHOU')
    if not ok:
        raise SystemExit(1)
print(f'cache PWA: totalgest-v{old_v} -> totalgest-v{old_v + 1}')
