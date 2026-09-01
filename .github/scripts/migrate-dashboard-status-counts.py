from pathlib import Path

APP = Path('app.html')
MODULE = Path('assets/js/app-dashboard-counts.js')
SW = Path('sw.js')

app = APP.read_text(encoding='utf-8')
module = MODULE.read_text(encoding='utf-8')
sw = SW.read_text(encoding='utf-8')

fn = app.index('function atualizarContagens()')
start = app.index('            const licencasAtivas =', fn)
end = app.index("            document.getElementById('countLicencas').textContent", start)
old = app[start:end]
assert old.count('const licencasAtivas =') == 1
assert old.count('const aVencer =') == 1
assert old.count('const pedidosPendentes =') == 1
assert old.count('let ajudasPendentes =') == 1
assert old.count('let ajudasRelevantes =') == 1
assert old.count("usuarioLogado.role === 'superadmin'") == 1

new = """            const _statusCounts = window.TotalGestDashboardCounts.calculateStatusCounts({
                admins: dados.administradores,
                renewalRequests: dados.pedidosRenovacao,
                helps: dados.ajudas,
                user: usuarioLogado,
                isLicenseValid: isLicencaValida,
                daysRemaining: calcularDiasRestantes
            });
            const licencasAtivas = _statusCounts.licencasAtivas;
            const aVencer = _statusCounts.aVencer;
            const pedidosPendentes = _statusCounts.pedidosPendentes;
            const ajudasPendentes = _statusCounts.ajudasPendentes;
            const ajudasAnalise = _statusCounts.ajudasAnalise;
            const ajudasConcluido = _statusCounts.ajudasConcluido;
"""
app = app[:start] + new + app[end:]
assert app.count('TotalGestDashboardCounts.calculateStatusCounts({') == 1

insert_before = "  window.TotalGestDashboardCounts = { calculateRoleCounts: calculateRoleCounts };\n"
assert module.count(insert_before) == 1
status_fn = """  function calculateStatusCounts(options) {
    const opts = options || {};
    const admins = opts.admins || [];
    const renewalRequests = opts.renewalRequests || [];
    const helps = opts.helps || [];
    const user = opts.user;
    const licencasAtivas = admins.filter(a => a.ativo && a.licenca && opts.isLicenseValid(a.licenca.dataExpiracao)).length;
    const aVencer = admins.filter(a => a.ativo && a.licenca && opts.isLicenseValid(a.licenca.dataExpiracao) && opts.daysRemaining(a.licenca.dataExpiracao) <= 5).length;
    const pedidosPendentes = renewalRequests.filter(p => p.status === 'pendente').length;
    let ajudasRelevantes = [];
    if (user) {
      if (user.role === 'admin' || user.role === 'encarregado') {
        ajudasRelevantes = helps.filter(a => a.remetenteId === user.id);
      } else if (user.role === 'superadmin') {
        ajudasRelevantes = helps;
      }
    }
    return {
      licencasAtivas: licencasAtivas,
      aVencer: aVencer,
      pedidosPendentes: pedidosPendentes,
      ajudasPendentes: ajudasRelevantes.filter(a => a.status === 'pendente').length,
      ajudasAnalise: ajudasRelevantes.filter(a => a.status === 'analise').length,
      ajudasConcluido: ajudasRelevantes.filter(a => a.status === 'concluido').length
    };
  }

"""
module = module.replace(insert_before, status_fn + "  window.TotalGestDashboardCounts = { calculateRoleCounts: calculateRoleCounts, calculateStatusCounts: calculateStatusCounts };\n", 1)
assert module.count('function calculateStatusCounts(') == 1
assert module.count('calculateStatusCounts: calculateStatusCounts') == 1

assert "const CACHE = 'totalgest-v108';" in sw
sw = sw.replace("const CACHE = 'totalgest-v108';", "const CACHE = 'totalgest-v109';", 1)

APP.write_text(app, encoding='utf-8')
MODULE.write_text(module, encoding='utf-8')
SW.write_text(sw, encoding='utf-8')
