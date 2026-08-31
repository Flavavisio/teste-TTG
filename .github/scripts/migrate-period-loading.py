from pathlib import Path

APP = Path('app.html')
SHELL = Path('assets/js/app-shell.js')
SW = Path('sw.js')
MODULE = Path('assets/js/app-period-loading.js')

app = APP.read_text(encoding='utf-8')
shell = SHELL.read_text(encoding='utf-8')
sw = SW.read_text(encoding='utf-8')

replacements = [
("""        function _dataCorteMeses(meses) {
            const d = new Date();
            d.setMonth(d.getMonth() - meses);
            return d.toISOString().slice(0, 10);
        }
""", """        function _dataCorteMeses(meses) {
            return window.TotalGestPeriodLoading.cutoffMonths(meses);
        }
"""),
("""        async function garantirPontoCarregado(desdeStr) {
            if (!desdeStr || !_pontoCarregadoDesde || desdeStr >= _pontoCarregadoDesde) return; // já temos tudo
            const { data, error } = await supa.from('ponto').select('*').gte('data', desdeStr).lt('data', _pontoCarregadoDesde);
            if (error) { console.error('carregar ponto mais antigo:', error.message); return; }
            const novos = (data || []).map(M.ponto.from);
            const idsJaTinha = new Set((dados.ponto || []).map(p => p.id));
            dados.ponto = [...(dados.ponto || []), ...novos.filter(p => !idsJaTinha.has(p.id))];
            _pontoCarregadoDesde = desdeStr;
        }
""", """        async function garantirPontoCarregado(desdeStr) {
            return window.TotalGestPeriodLoading.ensurePoint({
                desde: desdeStr,
                currentSince: _pontoCarregadoDesde,
                supabase: supa,
                data: dados,
                fromRow: M.ponto.from,
                setSince: value => { _pontoCarregadoDesde = value; }
            });
        }
"""),
("""        function _mesesDesdeCorteAtual(corteStr) {
            if (!corteStr) return 0;
            const hoje = new Date(), corte = new Date(corteStr + 'T00:00:00');
            return Math.max(0, Math.round((hoje - corte) / (30.44 * 24 * 60 * 60 * 1000)));
        }
""", """        function _mesesDesdeCorteAtual(corteStr) {
            return window.TotalGestPeriodLoading.monthsSinceCutoff(corteStr);
        }
"""),
("""        async function garantirFolhasCarregadas(desdeStr) {
            if (!desdeStr || !_folhasCarregadoDesde || desdeStr >= _folhasCarregadoDesde) return 0; // já temos tudo
            const { data, error } = await supa.from('folhas_obra').select('*')
                .not('assinatura', 'is', null)
                .gte('data', desdeStr)
                .lt('data', _folhasCarregadoDesde);
            if (error) { console.error('carregar folhas mais antigas:', error.message); _folhasCarregadoDesde = desdeStr; return 0; }
            const novos = (data || []).map(M.folhasObra.from);
            const idsJaTinha = new Set((dados.folhasObra || []).map(f => f.id));
            const aAdicionar = novos.filter(f => !idsJaTinha.has(f.id));
            dados.folhasObra = [...(dados.folhasObra || []), ...aAdicionar];
            _folhasCarregadoDesde = desdeStr;
            return aAdicionar.length;
        }
""", """        async function garantirFolhasCarregadas(desdeStr) {
            return window.TotalGestPeriodLoading.ensureSheets({
                desde: desdeStr,
                currentSince: _folhasCarregadoDesde,
                supabase: supa,
                data: dados,
                fromRow: M.folhasObra.from,
                setSince: value => { _folhasCarregadoDesde = value; }
            });
        }
"""),
("""        async function garantirServicosCarregados(desdeStr) {
            if (!desdeStr || !_servicosCarregadoDesde || desdeStr >= _servicosCarregadoDesde) return 0; // já temos tudo
            const { data, error } = await supa.from('servicos').select('*')
                .eq('status', 'concluído')
                .gte('data', desdeStr)
                .lt('data', _servicosCarregadoDesde);
            if (error) { console.error('carregar OS mais antigas:', error.message); _servicosCarregadoDesde = desdeStr; return 0; }
            const novos = (data || []).map(M.servicos.from);
            const idsJaTinha = new Set((dados.servicos || []).map(s => s.id));
            const aAdicionar = novos.filter(s => !idsJaTinha.has(s.id));
            dados.servicos = [...(dados.servicos || []), ...aAdicionar];
            _servicosCarregadoDesde = desdeStr;
            return aAdicionar.length;
        }
""", """        async function garantirServicosCarregados(desdeStr) {
            return window.TotalGestPeriodLoading.ensureServices({
                desde: desdeStr,
                currentSince: _servicosCarregadoDesde,
                supabase: supa,
                data: dados,
                fromRow: M.servicos.from,
                setSince: value => { _servicosCarregadoDesde = value; }
            });
        }
""")
]

for old, new in replacements:
    if app.count(old) != 1:
        raise SystemExit(f'Bloco esperado não encontrado exatamente uma vez: {old.splitlines()[0]} | count={app.count(old)}')
    app = app.replace(old, new, 1)

# Inserir o flag de carregamento junto do módulo pending, sem depender da indentação da linha inteira.
needle = 'syncPending: true'
if app.count(needle) != 1:
    raise SystemExit('syncPending: true deve existir exatamente uma vez')
app = app.replace(needle, 'syncPending: true, periodLoading: true', 1)

module_src = """/* Total Gest — carregamento incremental por períodos
 * Centraliza cálculos de corte e carregamentos históricos sem alterar filtros ou queries existentes.
 */
(function () {
  'use strict';

  function cutoffMonths(months) {
    const date = new Date();
    date.setMonth(date.getMonth() - months);
    return date.toISOString().slice(0, 10);
  }

  function monthsSinceCutoff(cutoff) {
    if (!cutoff) return 0;
    const today = new Date();
    const date = new Date(cutoff + 'T00:00:00');
    return Math.max(0, Math.round((today - date) / (30.44 * 24 * 60 * 60 * 1000)));
  }

  async function ensurePoint(options) {
    const opts = options || {};
    if (!opts.desde || !opts.currentSince || opts.desde >= opts.currentSince) return;
    const result = await opts.supabase.from('ponto').select('*').gte('data', opts.desde).lt('data', opts.currentSince);
    if (result.error) {
      console.error('carregar ponto mais antigo:', result.error.message);
      return;
    }
    const incoming = (result.data || []).map(opts.fromRow);
    const existingIds = new Set((opts.data.ponto || []).map(item => item.id));
    opts.data.ponto = [...(opts.data.ponto || []), ...incoming.filter(item => !existingIds.has(item.id))];
    opts.setSince(opts.desde);
  }

  async function ensureSheets(options) {
    const opts = options || {};
    if (!opts.desde || !opts.currentSince || opts.desde >= opts.currentSince) return 0;
    const result = await opts.supabase.from('folhas_obra').select('*')
      .not('assinatura', 'is', null)
      .gte('data', opts.desde)
      .lt('data', opts.currentSince);
    if (result.error) {
      console.error('carregar folhas mais antigas:', result.error.message);
      opts.setSince(opts.desde);
      return 0;
    }
    const incoming = (result.data || []).map(opts.fromRow);
    const existingIds = new Set((opts.data.folhasObra || []).map(item => item.id));
    const additions = incoming.filter(item => !existingIds.has(item.id));
    opts.data.folhasObra = [...(opts.data.folhasObra || []), ...additions];
    opts.setSince(opts.desde);
    return additions.length;
  }

  async function ensureServices(options) {
    const opts = options || {};
    if (!opts.desde || !opts.currentSince || opts.desde >= opts.currentSince) return 0;
    const result = await opts.supabase.from('servicos').select('*')
      .eq('status', 'concluído')
      .gte('data', opts.desde)
      .lt('data', opts.currentSince);
    if (result.error) {
      console.error('carregar OS mais antigas:', result.error.message);
      opts.setSince(opts.desde);
      return 0;
    }
    const incoming = (result.data || []).map(opts.fromRow);
    const existingIds = new Set((opts.data.servicos || []).map(item => item.id));
    const additions = incoming.filter(item => !existingIds.has(item.id));
    opts.data.servicos = [...(opts.data.servicos || []), ...additions];
    opts.setSince(opts.desde);
    return additions.length;
  }

  window.TotalGestPeriodLoading = {
    cutoffMonths: cutoffMonths,
    monthsSinceCutoff: monthsSinceCutoff,
    ensurePoint: ensurePoint,
    ensureSheets: ensureSheets,
    ensureServices: ensureServices
  };
})();
"""
MODULE.write_text(module_src, encoding='utf-8')

needle = "    syncPending: './assets/js/app-sync-pending.js',\n"
if shell.count(needle) != 1:
    raise SystemExit('Registo syncPending inesperado no shell')
shell = shell.replace(needle, needle + "    periodLoading: './assets/js/app-period-loading.js',\n", 1)

needle = "    if (options.syncPending === true) pedidos.push(MODULOS.syncPending);\n"
if shell.count(needle) != 1:
    raise SystemExit('Loader syncPending inesperado no shell')
shell = shell.replace(needle, needle + "    if (options.periodLoading === true) pedidos.push(MODULOS.periodLoading);\n", 1)

if "const CACHE = 'totalgest-v36';" not in sw:
    raise SystemExit('Versão PWA esperada totalgest-v36 não encontrada')
sw = sw.replace("const CACHE = 'totalgest-v36';", "const CACHE = 'totalgest-v37';", 1)
needle = "  './assets/js/app-sync-pending.js',\n"
if sw.count(needle) != 1:
    raise SystemExit('Entrada app-sync-pending.js inesperada no SW')
sw = sw.replace(needle, needle + "  './assets/js/app-period-loading.js',\n", 1)

for token in [
    'window.TotalGestPeriodLoading.cutoffMonths(meses)',
    'window.TotalGestPeriodLoading.monthsSinceCutoff(corteStr)',
    'window.TotalGestPeriodLoading.ensurePoint({',
    'window.TotalGestPeriodLoading.ensureSheets({',
    'window.TotalGestPeriodLoading.ensureServices({',
    'periodLoading: true'
]:
    if app.count(token) != 1:
        raise SystemExit(f'Invariante falhou para {token}: {app.count(token)}')

APP.write_text(app, encoding='utf-8')
SHELL.write_text(shell, encoding='utf-8')
SW.write_text(sw, encoding='utf-8')
