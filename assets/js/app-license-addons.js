/* Total Gest — renderização dos add-ons da licença */
(function () {
  'use strict';

  function planLabel(plan) {
    if (plan === 'demo') return 'Demo';
    if (plan === 'anual') return 'Anual';
    return 'Mensal';
  }

  function renderAddon(options) {
    options = options || {};
    const active = options.active === true;
    const title = options.title || '';
    const expiry = options.expiry || null;
    const plan = planLabel(options.plan);
    const pending = options.pending === true;
    const pendingInstructions = options.pendingInstructions || '';
    const remainingDays = Number(options.remainingDays);
    const renewFunction = options.renewFunction || '';
    const monthlyPrice = Number(options.monthlyPrice || 0);
    const annualPrice = Number(options.annualPrice || 0);
    const inactiveBadgeStyle = options.inactiveBadgeStyle || 'background:#94a3b8;color:#fff;';
    const inactiveDescription = options.inactiveDescription || '';

    if (active) {
      const renewal = remainingDays <= 10
        ? (pending
          ? '<div style="margin-top:8px; padding:8px; background:#fef3c7; border-radius:6px; color:#92400e; font-size:13px;"><i class="fas fa-clock"></i> Renovação pedida — a aguardar confirmação.</div>'
          : `<div style="margin-top:8px; display:flex; gap:8px; flex-wrap:wrap;">
                                <button class="btn btn-sm btn-renovar" onclick="${renewFunction}('mensal')"><i class="fas fa-sync-alt"></i> Renovar Mensal — ${monthlyPrice.toFixed(2)} €</button>
                                <button class="btn btn-sm btn-renovar" onclick="${renewFunction}('anual')"><i class="fas fa-sync-alt"></i> Renovar Anual — ${annualPrice.toFixed(2)} €</button>
                            </div>`)
        : '';

      return `<div style="margin-top:10px;">
                            <div class="report-item"><span>${title}</span><span class="licenca-ativa">Ativo — ${plan} (até ${expiry})</span></div>
                            ${renewal}
                        </div>`;
    }

    return `<div style="margin-top:14px; padding:12px; background:#f1f5f9; border-radius:8px; text-align:left;">
                            <strong>${title}</strong> <span class="badge" style="${inactiveBadgeStyle}">Inativo</span>
                            <div style="margin-top:8px; font-size:13px; color:#475569;">${inactiveDescription}</div>
                            ${pending ? pendingInstructions : ''}
                        </div>`;
  }

  function renderRounds(options) {
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

  window.TotalGestLicenseAddons = {
    renderAddon: renderAddon,
    renderRounds: renderRounds,
    renderLicensePage: renderLicensePage
  };
})();
