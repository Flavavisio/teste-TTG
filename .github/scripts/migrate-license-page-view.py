from pathlib import Path

APP = Path('app.html')
MODULE = Path('assets/js/app-license-addons.js')
SW = Path('sw.js')

app = APP.read_text(encoding='utf-8')
module = MODULE.read_text(encoding='utf-8')
sw = SW.read_text(encoding='utf-8')


def license_region(text):
    start = text.index('        function renderizarMinhaLicenca() {')
    end = text.index('\n        function ', start + 1)
    return start, end, text[start:end]

protected = {
    'bootstrapSupabase()': app.count('bootstrapSupabase()'),
    'supabase.auth': app.count('supabase.auth'),
    'adminAtual()': app.count('adminAtual()'),
    'calcularDiasRestantes(': app.count('calcularDiasRestantes('),
    'isLicencaValida(': app.count('isLicencaValida('),
    'window.TotalGestLicenseAddons.renderAddon({': app.count('window.TotalGestLicenseAddons.renderAddon({'),
    'moduloContratosAtivo(admin)': app.count('moduloContratosAtivo(admin)'),
    'moduloFrotaAtivo(admin)': app.count('moduloFrotaAtivo(admin)'),
    'moduloArmazemAtivo(admin)': app.count('moduloArmazemAtivo(admin)'),
    'moduloCrmAtivo(admin)': app.count('moduloCrmAtivo(admin)'),
    'moduloRondasAtivo(admin)': app.count('moduloRondasAtivo(admin)'),
}

start, end, block = license_region(app)

feedback_old = '''            const fb = admin.licencaFeedback;\n            const fbClasse = fb === 'verde' ? 'pisca-verde' : fb === 'vermelho' ? 'pisca-vermelho' : '';\n            const fbBanner = fb === 'verde'\n                ? `<div style="margin-bottom:14px; padding:12px; background:#d1fae5; border-radius:8px; color:#065f46;"><i class="fas fa-check-circle"></i> O seu último pedido de licença foi <strong>aprovado</strong>.</div>`\n                : fb === 'vermelho'\n                ? `<div style="margin-bottom:14px; padding:12px; background:#fee2e2; border-radius:8px; color:#991b1b;"><i class="fas fa-times-circle"></i> O seu último pedido de licença foi <strong>recusado</strong>.</div>`\n                : '';'''
assert block.count(feedback_old) == 1
block = block.replace(feedback_old, '            const fb = admin.licencaFeedback;', 1)

portal_old = '''            const portalBloco = `<div style="margin-top:10px;"><div class="report-item"><span>Portal do Cliente</span><span class="licenca-ativa">Incluído na licença base</span></div></div>`;\n            const notificacoesBloco = `<div style="margin-top:10px;"><div class="report-item"><span>Notificações</span><span class="licenca-ativa">Incluído na licença base</span></div></div>`;\n'''
assert block.count(portal_old) == 1
block = block.replace(portal_old, '', 1)

rounds_start = block.index('            const rondasBloco = rondasAtivo\n')
final_start = block.rindex('            container.innerHTML = `')
rounds_old = block[rounds_start:final_start]
assert "Rondas / Vigilância" in rounds_old
assert "solicitarRondas('mensal')" in rounds_old
rounds_new = '''            const rondasBloco = window.TotalGestLicenseAddons.renderRounds({\n                active: rondasAtivo,\n                plan: admin.rondasPlano,\n                expiry: rondasExp,\n                pending: !!rondasPedidoPend,\n                pendingInstructions: rondasPedidoPend ? blocoInstrucoesPagamento(rondasPedidoPend) : ''\n            });\n'''
block = block[:rounds_start] + rounds_new + block[final_start:]

# Recalcular o início do template final depois da substituição anterior.
final_start = block.rindex('            container.innerHTML = `')
final_end_marker = '                `;'
final_end = block.rindex(final_end_marker) + len(final_end_marker)
final_old = block[final_start:final_end]
for needle in [
    '${fbBanner}',
    '${pedidoBasePend',
    'Resumo do pedido conjunto',
    '_ativAddonsAbrir()',
    '${modBloco}',
    '${frotaBloco}',
    '${armazemBloco}',
    '${portalBloco}',
    '${notificacoesBloco}',
    '${crmBloco}',
    '${rondasBloco}',
    '${_referenciaBlocoHTML(admin)}',
    'exportarTudoZipComFicheiros()',
    '_abrirModalCancelamento()'
]:
    assert needle in final_old, needle

final_new = '''            const baseAcaoBloco = pedidoBasePend\n                ? `<div style="margin-top:16px; padding:12px; background:#fef3c7; border-radius:8px; color:#92400e;">\n                    <i class="fas fa-clock"></i> <strong>Pedido de licença enviado</strong> — a aguardar aprovação do Super Admin.\n                    <div style="margin-top:4px; font-size:13px;">Plano pedido: ${PLANOS[pedidoBasePend.planoPedido]?.label || pedidoBasePend.planoPedido}</div>\n                </div>`\n                : (!isDemo ? `\n                    <div style="margin-top:16px; display:flex; gap:10px; flex-wrap:wrap;">\n                        ${diasRest <= 10 ? `<button class="btn btn-sm btn-renovar" onclick="abrirModalRenovacao('renovacao')"><i class="fas fa-sync-alt"></i> Pedir Renovação</button>` : ''}\n                        <button class="btn btn-sm btn-warning" onclick="abrirModalRenovacao('alteracao')"><i class="fas fa-exchange-alt"></i> Alterar Plano</button>\n                    </div>\n                ` : `\n                    <div style="margin-top:16px; padding:12px; background:#fef3c7; border-radius:8px; color:#92400e;">\n                        <i class="fas fa-info-circle"></i> Plano Demo.\n                    </div>\n                    <div style="margin-top:12px;">\n                        <button class="btn btn-sm btn-primary" onclick="abrirModalRenovacao('alteracao')"><i class="fas fa-exchange-alt"></i> Adquirir Licença</button>\n                    </div>\n                `);\n\n            const _pendentesTodos = [contratoPedidoPend, frotaPedidoPend, armazemPedidoPend, crmPedidoPend].filter(Boolean);\n            let pedidoConjuntoBloco = '';\n            if (_pendentesTodos.length >= 2) {\n                const _totalPend = _pendentesTodos.reduce((s, p) => s + valorDoPedido(p), 0);\n                const _nomesTipo = { contrato: 'Contratos de Manutenção', frota: 'Frota', armazem: 'Armazém / Stock / Gestão de Obras', crm: 'CRM Comercial + Assist' };\n                pedidoConjuntoBloco = `\n                    <div style="margin-top:16px;padding:14px 16px;background:#f0fdfa;border:1px solid #99f6e4;border-radius:10px;">\n                        <div style="font-weight:700;color:#0f766e;margin-bottom:8px;"><i class="fas fa-receipt"></i> Resumo do pedido conjunto</div>\n                        ${_pendentesTodos.map(p => `<div style="display:flex;justify-content:space-between;font-size:.88rem;color:#134e4a;padding:3px 0;"><span>${_nomesTipo[(p.tipo || '').split('_')[0]] || p.tipo}</span><span>${valorDoPedido(p).toFixed(2)} €</span></div>`).join('')}\n                        <div style="display:flex;justify-content:space-between;font-weight:700;color:#0f766e;border-top:1px solid #99f6e4;margin-top:6px;padding-top:6px;"><span>Total</span><span>${_totalPend.toFixed(2)} €</span></div>\n                    </div>`;\n            }\n\n            const ativarAddonsBloco = (!isDemo && (!modAtivo || !frotaAtivo || !armazemAtivo || !crmAtivo))\n                ? `<div style="margin-top:16px;text-align:left;">\n                    <button class="btn btn-sm" style="background:#0f766e;color:#fff;" onclick="_ativAddonsAbrir()"><i class="fas fa-puzzle-piece"></i> Ativar Add-ons</button>\n                </div>`\n                : '';\n\n            const _cancPend = (dados.pedidosRenovacao || []).find(p => p.adminId === admin.id && p.tipo === 'cancelamento' && p.status === 'pendente');\n            const cancelamentoBloco = _cancPend\n                ? `<div style="margin-top:20px; padding:14px 16px; background:#fef2f2; border-radius:10px; border:1px solid #fecaca; color:#991b1b;">\n                    <i class="fas fa-clock"></i> Pedido de encerramento assinado por <strong>${_cancPend.assinaturaNome}</strong> em ${_cancPend.dataAssinatura ? new Date(_cancPend.dataAssinatura).toLocaleDateString('pt-PT') : '-'} — a aguardar confirmação da Total Gest.\n                </div>`\n                : `<div style="margin-top:20px;">\n                    <button class="btn" style="background:#dc2626;color:#fff;" onclick="_abrirModalCancelamento()"><i class="fas fa-file-signature"></i> Encerrar Acordo com a Total Gest</button>\n                </div>`;\n\n            container.innerHTML = window.TotalGestLicenseAddons.renderLicensePage({\n                feedback: fb,\n                valid: valida,\n                name: admin.nome,\n                company: admin.empresa || '-',\n                planLabel: planoLabel,\n                demo: isDemo,\n                value: valor,\n                maxEmployees: maxFunc,\n                currentEmployees: totalFunc,\n                licenseCode: admin.licenca.codigo,\n                expiry: dataExpiracao,\n                statusClass: statusColor,\n                statusText: statusText,\n                remainingDays: diasRest,\n                baseActionHtml: baseAcaoBloco,\n                jointRequestHtml: pedidoConjuntoBloco,\n                activateAddonsHtml: ativarAddonsBloco,\n                contractsHtml: modBloco,\n                fleetHtml: frotaBloco,\n                warehouseHtml: armazemBloco,\n                crmHtml: crmBloco,\n                roundsHtml: rondasBloco,\n                referenceHtml: _referenciaBlocoHTML(admin),\n                cancellationHtml: cancelamentoBloco\n            });'''
block = block[:final_start] + final_new + block[final_end:]
app = app[:start] + block + app[end:]

# Adicionar apenas renderizadores de apresentação ao módulo já carregado.
export_anchor = '''  window.TotalGestLicenseAddons = {\n    renderAddon: renderAddon\n  };'''
assert module.count(export_anchor) == 1
assert 'function renderRounds(options)' not in module
assert 'function renderLicensePage(options)' not in module

view_functions = r'''  function renderRounds(options) {
    options = options || {};
    if (options.active === true) {
      return `<div style="margin-top:10px;">
                            <div class="report-item"><span>Rondas / Vigilância</span><span class="licenca-ativa">Ativo — ${planLabel(options.plan)} (até ${options.expiry || '-'}) — grátis</span></div>
                        </div>`;
    }

    return `<div style="margin-top:14px; padding:12px; background:#f1f5f9; border-radius:8px; text-align:left;">
                            <strong>Rondas / Vigilância</strong> <span class="badge" style="background:#0f766e;color:#fff;">Novo — Grátis temporário</span>
                            <div style="margin-top:8px; font-size:13px; color:#475569;">Gestão de rondas de segurança: postos com QR/NFC, rotas com horário e SLA, execução com scanner no telemóvel e alertas automáticos de postos saltados ou fora de horário. Grátis por agora, fase de lançamento.</div>
                            ${options.pending === true
                              ? (options.pendingInstructions || '')
                              : `<div style="margin-top:10px; display:flex; gap:10px; flex-wrap:wrap;">
                                <button class="btn btn-sm btn-success" onclick="solicitarRondas('mensal')"><i class="fas fa-shield-halved"></i> Ativar (Grátis)</button>
                            </div>`}
                        </div>`;
  }

  function renderLicensePage(options) {
    options = options || {};
    const feedbackClass = options.feedback === 'verde' ? 'pisca-verde' : options.feedback === 'vermelho' ? 'pisca-vermelho' : '';
    const feedbackBanner = options.feedback === 'verde'
      ? `<div style="margin-bottom:14px; padding:12px; background:#d1fae5; border-radius:8px; color:#065f46;"><i class="fas fa-check-circle"></i> O seu último pedido de licença foi <strong>aprovado</strong>.</div>`
      : options.feedback === 'vermelho'
        ? `<div style="margin-bottom:14px; padding:12px; background:#fee2e2; border-radius:8px; color:#991b1b;"><i class="fas fa-times-circle"></i> O seu último pedido de licença foi <strong>recusado</strong>.</div>`
        : '';

    return `
                    ${feedbackBanner}
                    <div class="report-card ${feedbackClass}" style="border-left-color: ${options.valid ? '#16a34a' : '#dc2626'};">
                        <h4><i class="fas fa-id-card"></i> ${options.name || ''}</h4>
                        <div class="report-item"><span>Empresa</span><span>${options.company || '-'}</span></div>
                        <div class="report-item"><span>Plano</span><span>${options.planLabel || ''} ${options.demo ? '<span class="badge badge-demo">Demo</span>' : ''}</span></div>
                        <div class="report-item"><span>Valor</span><span>${options.value}€</span></div>
                        <div class="report-item"><span>Funcionários permitidos</span><span>${options.maxEmployees}</span></div>
                        <div class="report-item"><span>Funcionários atuais (incl. encarregados)</span><span>${options.currentEmployees} / ${options.maxEmployees}</span></div>
                        <div class="report-item"><span>Código da Licença</span><span><strong>${options.licenseCode || ''}</strong></span></div>
                        <div class="report-item"><span>Data de Expiração</span><span>${options.expiry || '-'}</span></div>
                        <div class="report-item"><span>Status</span><span class="${options.statusClass || ''}">${options.statusText || ''} (${options.remainingDays} dias)</span></div>
                        ${options.baseActionHtml || ''}
                        ${options.jointRequestHtml || ''}
                        ${options.activateAddonsHtml || ''}
                        ${options.contractsHtml || ''}
                        ${options.fleetHtml || ''}
                        ${options.warehouseHtml || ''}
                        <div style="margin-top:10px;"><div class="report-item"><span>Portal do Cliente</span><span class="licenca-ativa">Incluído na licença base</span></div></div>
                        <div style="margin-top:10px;"><div class="report-item"><span>Notificações</span><span class="licenca-ativa">Incluído na licença base</span></div></div>
                        ${options.crmHtml || ''}
                        ${options.roundsHtml || ''}
                        ${options.referenceHtml || ''}
                        <div style="margin-top:20px; padding:14px 16px; background:#eff6ff; border-radius:10px; border:1px solid #bfdbfe;">
                            <div style="font-weight:700; color:var(--tg-brand-blue,#243B8F); margin-bottom:4px;"><i class="fas fa-box-archive"></i> Os teus dados são teus</div>
                            <div style="font-size:.85rem; color:#475569; margin-bottom:10px;">Podes descarregar, a qualquer momento, uma cópia completa de todos os teus dados e ficheiros (clientes, contratos, OS, folhas de obra, relatórios, assiduidade, assinaturas, fotos, etc.), num único ficheiro ZIP.</div>
                            <button class="btn btn-sm" style="background:var(--tg-brand-blue,#243B8F);color:#fff;" onclick="exportarTudoZipComFicheiros()" id="btnExportarTudoZip"><i class="fas fa-file-zipper"></i> Descarregar cópia completa (dados + ficheiros)</button>
                        </div>
                        ${options.cancellationHtml || ''}
                    </div>
                `;
  }

'''
module = module.replace(export_anchor, view_functions + '''  window.TotalGestLicenseAddons = {\n    renderAddon: renderAddon,\n    renderRounds: renderRounds,\n    renderLicensePage: renderLicensePage\n  };''', 1)

assert sw.count("const CACHE = 'totalgest-v122';") == 1
sw = sw.replace("const CACHE = 'totalgest-v122';", "const CACHE = 'totalgest-v123';", 1)

for needle, before in protected.items():
    assert app.count(needle) == before, (needle, before, app.count(needle))

_, _, after = license_region(app)
assert after.count('window.TotalGestLicenseAddons.renderAddon({') == 4
assert after.count('window.TotalGestLicenseAddons.renderRounds({') == 1
assert after.count('window.TotalGestLicenseAddons.renderLicensePage({') == 1
assert 'const fbBanner =' not in after
assert 'const portalBloco =' not in after
assert 'const notificacoesBloco =' not in after
assert 'const rondasBloco = rondasAtivo' not in after
assert after.count('container.innerHTML = `') == 1  # apenas o caso sem licença
assert module.count('function renderRounds(options)') == 1
assert module.count('function renderLicensePage(options)') == 1
assert module.count('renderRounds: renderRounds') == 1
assert module.count('renderLicensePage: renderLicensePage') == 1
assert sw.count("const CACHE = 'totalgest-v123';") == 1

APP.write_text(app, encoding='utf-8')
MODULE.write_text(module, encoding='utf-8')
SW.write_text(sw, encoding='utf-8')
print(f'RENDERIZAR_MINHA_LICENCA_AFTER chars={len(after)} lines={after.count(chr(10)) + 1}')
print('LICENSE_PAGE_VIEW_MIGRATION=OK')
