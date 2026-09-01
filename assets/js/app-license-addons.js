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

  window.TotalGestLicenseAddons = {
    renderAddon: renderAddon
  };
})();
