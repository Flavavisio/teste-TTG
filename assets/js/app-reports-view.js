/* Total Gest — primitivas visuais dos relatórios.
 * Mantém a apresentação reutilizável fora de app.html sem regras de negócio.
 */
(function () {
  'use strict';

  function kpi(label, value, color, icon) {
    return `<div style="border:1px solid #e6eaf2;border-left:4px solid ${color};border-radius:10px;padding:12px 14px;background:#fff;"><div style="font-size:.78rem;color:#64748b;"><i class="fas ${icon}" style="color:${color};"></i> ${label}</div><div style="font-size:1.2rem;font-weight:800;color:#0f172a;margin-top:4px;">${value}</div></div>`;
  }

  function moduleLicenseCard(options) {
    options = options || {};
    const activeCount = Number(options.activeCount) || 0;
    const monthly = Number(options.monthly) || 0;
    const annual = Number(options.annual) || 0;
    const demos = Number(options.demos) || 0;
    const revenue = Number(options.revenue) || 0;
    const demoRow = demos
      ? `<div class="report-item"><span>Demo</span><span>${demos}</span></div>`
      : '';

    return `<div class="report-card">
                            <h4><i class="fas ${options.icon || 'fa-puzzle-piece'}"></i> ${options.title || ''}</h4>
                            <div class="report-item"><span>Empresas com módulo ativo</span><span>${activeCount}</span></div>
                            <div class="report-item"><span>Plano Mensal</span><span>${monthly}</span></div>
                            <div class="report-item"><span>Plano Anual</span><span>${annual}</span></div>
                            ${demoRow}
                            <div class="report-item" style="font-weight:bold; border-top:1px solid #e2e8f0; padding-top:8px;"><span>Receita do módulo</span><span>${revenue.toLocaleString('pt-PT', { minimumFractionDigits: 2, maximumFractionDigits: 2 })} €</span></div>
                        </div>`;
  }

  function revenueBars(options) {
    options = options || {};
    const modules = Array.isArray(options.modules) ? options.modules : [];
    const maxRevenue = Number(options.maxModuleRevenue) || 1;
    return modules.map(function (module) {
      const value = Number(module.v) || 0;
      return `<div style="margin:8px 0;"><div style="display:flex;justify-content:space-between;font-size:.85rem;"><span>${module.l}</span><strong>${value.toLocaleString('pt-PT', { minimumFractionDigits: 2, maximumFractionDigits: 2 })} €</strong></div><div style="background:#eef2f7;border-radius:6px;height:10px;overflow:hidden;margin-top:3px;"><div style="height:100%;width:${Math.round(value / maxRevenue * 100)}%;background:${module.c};"></div></div></div>`;
    }).join('');
  }

  window.TotalGestReportsView = {
    kpi: kpi,
    moduleLicenseCard: moduleLicenseCard,
    revenueBars: revenueBars
  };
})();
