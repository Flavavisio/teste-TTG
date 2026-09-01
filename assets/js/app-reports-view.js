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

  function superadminCompanySummary(options) {
    options = options || {};
    const rows = Array.isArray(options.rows) ? options.rows : [];
    const totals = options.totals || {};
    let html = `<div class="report-card"><h4><i class="fas fa-chart-line"></i> Resumo por Empresa</h4>`;
    if (!rows.length) {
      return html + `<p class="text-muted">Nenhuma empresa registada.</p></div>`;
    }
    html += `<div class="table-wrapper"><table>
                                <thead><tr><th>Empresa</th><th>Administrador</th><th>Plano</th><th>Expiração</th><th>Funcionários</th><th>Encarregados</th><th>Contratos</th><th>Frota</th><th>Armazém</th><th>CRM + Assist</th><th>ERP</th><th>Rondas</th><th>Receita (€)</th></tr></thead><tbody>`;
    rows.forEach(function (row) {
      html += `<tr class="${row.rowClass}">
                                    <td>${row.empresa}</td>
                                    <td>${row.nome}</td>
                                    <td>${row.planoLabel}</td>
                                    <td>${row.dataExp}</td>
                                    <td>${row.funcionarios}${row.atingiuLimite ? ' ⚠️' : ''}</td>
                                    <td>${row.encarregados}</td>
                                    <td style="text-align:center; color:${row.temContratos ? '#16a34a' : '#cbd5e1'};">${row.temContratos ? '✓' : '—'}</td>
                                    <td style="text-align:center; color:${row.temFrota ? '#16a34a' : '#cbd5e1'};">${row.temFrota ? '✓' : '—'}</td>
                                    <td style="text-align:center; color:${row.temArmazem ? '#16a34a' : '#cbd5e1'};">${row.temArmazem ? '✓' : '—'}</td>
                                    <td style="text-align:center; color:${row.temCrm ? '#16a34a' : '#cbd5e1'};">${row.temCrm ? '✓' : '—'}</td>
                                    <td style="text-align:center; color:${row.temErp ? '#16a34a' : '#cbd5e1'};">${row.temErp ? '✓' : '—'}</td>
                                    <td style="text-align:center; color:${row.temRondas ? '#16a34a' : '#cbd5e1'};">${row.temRondas ? '✓' : '—'}</td>
                                    <td>${row.valorEmpresa.toFixed(2)}</td>
                                </tr>`;
    });
    html += `<tr style="font-weight:bold; background:#f1f5f9;">
                                <td colspan="4">Total Geral</td>
                                <td>${totals.funcionarios}</td>
                                <td>${totals.encarregados}</td>
                                <td style="text-align:center;">${totals.contratos}</td>
                                <td style="text-align:center;">${totals.frota}</td>
                                <td style="text-align:center;">${totals.armazem}</td>
                                <td style="text-align:center;">${totals.crm}</td>
                                <td style="text-align:center;">${totals.erp}</td>
                                <td style="text-align:center;">${totals.rondas}</td>
                                <td>${totals.receita.toFixed(2)}</td>
                            </tr>`;
    return html + `</tbody></table></div></div>`;
  }

  function distributorClientSummary(options) {
    options = options || {};
    const rows = Array.isArray(options.rows) ? options.rows : [];
    let html = `<div class="report-card"><h4><i class="fas fa-chart-line"></i> Resumo por Cliente</h4>`;
    if (!rows.length) {
      return html + `<p class="text-muted">Ainda não criaste nenhum cliente.</p></div>`;
    }
    html += `<div class="table-wrapper"><table>
                                <thead><tr><th>Empresa</th><th>Administrador</th><th>Plano</th><th>Expiração</th><th>Funcionários</th><th>Contratos</th><th>Frota</th><th>Armazém</th><th>CRM+Assist</th><th>Cobras (€)</th></tr></thead><tbody>`;
    rows.forEach(function (row) {
      html += `<tr>
                            <td>${row.empresa}</td><td>${row.nome}</td><td>${row.planoLabel}</td><td>${row.dataExp}</td><td>${row.funcionarios}</td>
                            <td style="text-align:center;color:${row.temContratos ? '#16a34a' : '#cbd5e1'};">${row.temContratos ? '✓' : '—'}</td>
                            <td style="text-align:center;color:${row.temFrota ? '#16a34a' : '#cbd5e1'};">${row.temFrota ? '✓' : '—'}</td>
                            <td style="text-align:center;color:${row.temArmazem ? '#16a34a' : '#cbd5e1'};">${row.temArmazem ? '✓' : '—'}</td>
                            <td style="text-align:center;color:${row.temCrm ? '#16a34a' : '#cbd5e1'};">${row.temCrm ? '✓' : '—'}</td>
                            <td>${row.valorCliente.toFixed(2)}</td>
                        </tr>`;
    });
    html += `<tr style="font-weight:bold;background:#f1f5f9;"><td colspan="10">Total Geral</td><td>${options.totalCobrado.toFixed(2)}</td></tr>`;
    return html + `</tbody></table></div></div>`;
  }

  window.TotalGestReportsView = {
    kpi: kpi,
    moduleLicenseCard: moduleLicenseCard,
    revenueBars: revenueBars,
    superadminCompanySummary: superadminCompanySummary,
    distributorClientSummary: distributorClientSummary
  };
})();
