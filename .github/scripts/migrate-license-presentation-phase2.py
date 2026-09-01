from pathlib import Path

app_path = Path('app.html')
sw_path = Path('sw.js')
app = app_path.read_text(encoding='utf-8')
sw = sw_path.read_text(encoding='utf-8')

protected = {
    'bootstrapSupabase()': app.count('bootstrapSupabase()'),
    'supabase.auth': app.count('supabase.auth'),
    'function renderizarMinhaLicenca()': app.count('function renderizarMinhaLicenca()'),
    'window.TotalGestLicenseAddons.renderAddon({': app.count('window.TotalGestLicenseAddons.renderAddon({'),
    'window.TotalGestLicenseAddons.renderRounds({': app.count('window.TotalGestLicenseAddons.renderRounds({'),
    'window.TotalGestLicenseAddons.renderLicensePage({': app.count('window.TotalGestLicenseAddons.renderLicensePage({'),
}

func_start = app.index('        function renderizarMinhaLicenca() {')
func_end = app.index('\n        function ', func_start + 1)
block = app[func_start:func_end]


def replace_region(source, start_marker, end_marker, replacement):
    assert source.count(start_marker) == 1, (start_marker, source.count(start_marker))
    assert source.count(end_marker) == 1, (end_marker, source.count(end_marker))
    start = source.index(start_marker)
    end = source.index(end_marker, start)
    return source[:start] + replacement + source[end:]

block = replace_region(
    block,
    '            if (!admin.licenca) {',
    '            const diasRest = calcularDiasRestantes(admin.licenca.dataExpiracao);',
    """            if (!admin.licenca) {
                container.innerHTML = window.TotalGestLicenseAddons.renderNoLicense();
                return;
            }
"""
)

block = replace_region(
    block,
    '            const erpBloco = `',
    '            const rondasAtivo = moduloRondasAtivo(admin);',
    """            const erpBloco = window.TotalGestLicenseAddons.renderErpComingSoon();
"""
)

block = replace_region(
    block,
    '            const baseAcaoBloco = pedidoBasePend',
    '            const _pendentesTodos = [contratoPedidoPend, frotaPedidoPend, armazemPedidoPend, crmPedidoPend].filter(Boolean);',
    """            const baseAcaoBloco = window.TotalGestLicenseAddons.renderBaseAction({
                pending: !!pedidoBasePend,
                pendingPlanLabel: pedidoBasePend ? (PLANOS[pedidoBasePend.planoPedido]?.label || pedidoBasePend.planoPedido) : '',
                demo: isDemo,
                remainingDays: diasRest
            });

"""
)

block = replace_region(
    block,
    '            const _pendentesTodos = [contratoPedidoPend, frotaPedidoPend, armazemPedidoPend, crmPedidoPend].filter(Boolean);',
    '            const ativarAddonsBloco = (!isDemo && (!modAtivo || !frotaAtivo || !armazemAtivo || !crmAtivo))',
    """            const _nomesTipo = { contrato: 'Contratos de Manutenção', frota: 'Frota', armazem: 'Armazém / Stock / Gestão de Obras', crm: 'CRM Comercial + Assist' };
            const pedidoConjuntoBloco = window.TotalGestLicenseAddons.renderJointRequest({
                items: [contratoPedidoPend, frotaPedidoPend, armazemPedidoPend, crmPedidoPend]
                    .filter(Boolean)
                    .map(p => ({
                        label: _nomesTipo[(p.tipo || '').split('_')[0]] || p.tipo,
                        value: valorDoPedido(p)
                    }))
            });

"""
)

block = replace_region(
    block,
    '            const ativarAddonsBloco = (!isDemo && (!modAtivo || !frotaAtivo || !armazemAtivo || !crmAtivo))',
    "            const _cancPend = (dados.pedidosRenovacao || []).find(p => p.adminId === admin.id && p.tipo === 'cancelamento' && p.status === 'pendente');",
    """            const ativarAddonsBloco = window.TotalGestLicenseAddons.renderActivateAddons({
                visible: !isDemo && (!modAtivo || !frotaAtivo || !armazemAtivo || !crmAtivo)
            });

"""
)

block = replace_region(
    block,
    "            const _cancPend = (dados.pedidosRenovacao || []).find(p => p.adminId === admin.id && p.tipo === 'cancelamento' && p.status === 'pendente');",
    '            container.innerHTML = window.TotalGestLicenseAddons.renderLicensePage({',
    """            const _cancPend = (dados.pedidosRenovacao || []).find(p => p.adminId === admin.id && p.tipo === 'cancelamento' && p.status === 'pendente');
            const cancelamentoBloco = window.TotalGestLicenseAddons.renderCancellation({
                pending: !!_cancPend,
                signatureName: _cancPend?.assinaturaNome || '',
                signatureDate: _cancPend?.dataAssinatura ? new Date(_cancPend.dataAssinatura).toLocaleDateString('pt-PT') : '-'
            });

"""
)

rounds_line = '                roundsHtml: rondasBloco,\n'
assert block.count(rounds_line) == 1
block = block.replace(rounds_line, rounds_line + '                erpHtml: erpBloco,\n', 1)

for old in [
    'Sem licença atribuída',
    "Integração com ERP's",
    'Resumo do pedido conjunto',
    'Ativar Add-ons</button>',
    'Encerrar Acordo com a Total Gest',
    'Plano Demo.'
]:
    assert old not in block, old

for new in [
    'window.TotalGestLicenseAddons.renderNoLicense()',
    'window.TotalGestLicenseAddons.renderErpComingSoon()',
    'window.TotalGestLicenseAddons.renderBaseAction({',
    'window.TotalGestLicenseAddons.renderJointRequest({',
    'window.TotalGestLicenseAddons.renderActivateAddons({',
    'window.TotalGestLicenseAddons.renderCancellation({',
    'window.TotalGestLicenseAddons.renderLicensePage({'
]:
    assert block.count(new) == 1, (new, block.count(new))

app = app[:func_start] + block + app[func_end:]

for needle, count in protected.items():
    assert app.count(needle) == count, (needle, count, app.count(needle))

assert "const CACHE = 'totalgest-v125';" in sw
assert "const CACHE = 'totalgest-v126';" not in sw
sw = sw.replace("const CACHE = 'totalgest-v125';", "const CACHE = 'totalgest-v126';", 1)

app_path.write_text(app, encoding='utf-8')
sw_path.write_text(sw, encoding='utf-8')

new_start = app.index('        function renderizarMinhaLicenca() {')
new_end = app.index('\n        function ', new_start + 1)
new_block = app[new_start:new_end]
print(f'RENDERIZAR_MINHA_LICENCA_AFTER chars={len(new_block)} lines={len(new_block.splitlines())}')
print('LICENSE_PRESENTATION_PHASE2_MIGRATION=OK')
