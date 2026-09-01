/* Total Gest — primitivas visuais dos relatórios.
 * Mantém a apresentação reutilizável fora de app.html sem regras de negócio.
 */
(function () {
  'use strict';

  function kpi(label, value, color, icon) {
    return `<div style="border:1px solid #e6eaf2;border-left:4px solid ${color};border-radius:10px;padding:12px 14px;background:#fff;"><div style="font-size:.78rem;color:#64748b;"><i class="fas ${icon}" style="color:${color};"></i> ${label}</div><div style="font-size:1.2rem;font-weight:800;color:#0f172a;margin-top:4px;">${value}</div></div>`;
  }

  function superadminHeader(options) {
    options = options || {};
    const empresas = Number(options.empresas) || 0;
    const empresasAtivas = Number(options.empresasAtivas) || 0;
    const expiram = Number(options.expiramEm10Dias) || 0;
    const receita = Number(options.receitaRecorrente) || 0;
    let html = `<div style="display:flex;justify-content:flex-end;margin-bottom:10px;"><button class="btn btn-outline" onclick="relSuperAdminPDF()"><i class="fas fa-file-pdf"></i> Exportar PDF</button></div>`;
    html += `<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(155px,1fr));gap:12px;margin-bottom:16px;">
      ${kpi('Empresas', empresas + ` <span style="font-size:.7rem;color:#16a34a;">(${empresasAtivas} ativas)</span>`, '#2563eb', 'fa-building')}
      ${kpi('Utilizadores', String(Number(options.totalUtilizadores) || 0), '#0e7490', 'fa-users')}
      ${kpi('Add-ons ativos', String(Number(options.addonsAtivos) || 0), '#b45309', 'fa-puzzle-piece')}
      ${kpi('A expirar (≤10d)', String(expiram), expiram ? '#dc2626' : '#16a34a', 'fa-hourglass-half')}
      ${kpi('Receita recorrente', receita.toLocaleString('pt-PT', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) + ' €', '#16a34a', 'fa-euro-sign')}
    </div>`;
    return html;
  }

  function distributorHeader(options) {
    options = options || {};
    const clientes = Number(options.clientes) || 0;
    const ativos = Number(options.clientesAtivos) || 0;
    return `<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(155px,1fr));gap:12px;margin-bottom:16px;">
      ${kpi('Clientes', clientes + ` <span style="font-size:.7rem;color:#16a34a;">(${ativos} ativos)</span>`, '#7c3aed', 'fa-user-tie')}
    </div>`;
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

  function adminOverviewCards(options) {
    options = options || {};
    return `
                    <div class="report-card">
                        <h4><i class="fas fa-users"></i> Recursos Humanos</h4>
                        <div class="report-item"><span>Total de Funcionários</span><span>${options.totalFunc}</span></div>
                        <div class="report-item"><span>Total de Encarregados</span><span>${options.totalEncarregados}</span></div>
                        <div class="report-item"><span>Total de Clientes</span><span>${options.totalCli}</span></div>
                        <div class="report-item"><span>Gasto com Funcionários (bruto)</span><span>${options.gastoFunc}</span></div>
                        <div class="report-item"><span>Gasto com Encarregados (bruto)</span><span>${options.gastoEnc}</span></div>
                        <div class="report-item" style="font-weight:bold; border-top:1px solid #e2e8f0; padding-top:8px;"><span>Gasto Total com Pessoal</span><span>${options.gastoTotal}</span></div>
                    </div>
                    <div class="report-card">
                        <h4><i class="fas fa-tools"></i> Ordens de Serviço</h4>
                        <div class="report-item"><span>Total</span><span>${options.totalOS}</span></div>
                        <div class="report-item"><span>Pendentes</span><span>${options.osPendentes}</span></div>
                        <div class="report-item"><span>Em andamento</span><span>${options.osAndamento}</span></div>
                        <div class="report-item"><span>Concluídas</span><span>${options.osConcluidas}</span></div>
                    </div>
                    <div class="report-card">
                        <h4><i class="fas fa-clock"></i> Assiduidade</h4>
                        <div class="report-item"><span>Total de registos de ponto</span><span>${options.totalPonto}</span></div>
                    </div>
                    <div class="report-card">
                        <h4><i class="fas fa-calendar-check"></i> Férias / Faltas</h4>
                        <div class="report-item"><span>Total de pedidos</span><span>${options.totalPedidos}</span></div>
                        <div class="report-item"><span>Pendentes</span><span>${options.pedPend}</span></div>
                    </div>
                    <div class="report-card">
                        <h4><i class="fas fa-clipboard-list"></i> Folhas de Obra</h4>
                        <div class="report-item"><span>Total</span><span>${options.totalFolhas}</span></div>
                        <div class="report-item"><span>Ordens de trabalho de manutenção</span><span>${options.folhasOT}</span></div>
                    </div>
                    <div class="report-card">
                        <h4><i class="fas fa-boxes"></i> Requisições</h4>
                        <div class="report-item"><span>Total</span><span>${options.totalReqs}</span></div>
                        <div class="report-item"><span>Pendentes</span><span>${options.reqPend}</span></div>
                    </div>
                    <div class="report-card">
                        <h4><i class="fas fa-file-signature"></i> Contratos de Manutenção</h4>
                        <div class="report-item"><span>Módulo</span><span>${options.moduloAtivoTxt}</span></div>
                        <div class="report-item"><span>Total de contratos</span><span>${options.contratosCount}</span></div>
                        <div class="report-item"><span>Em dia</span><span style="color:#16a34a;">${options.ctEmDia}</span></div>
                        <div class="report-item"><span>A vencer (≤30d)</span><span style="color:#f59e0b;">${options.ctAVencer}</span></div>
                        <div class="report-item"><span>Vencidos</span><span style="color:#dc2626;">${options.ctVencidos}</span></div>
                        <div class="report-item"><span>Locais / Equipamentos</span><span>${options.totalLocais} / ${options.totalEquip}</span></div>
                        <div class="report-item"><span>Manutenções realizadas</span><span>${options.totalRegistos}</span></div>
                        <div class="report-item" style="font-weight:bold; border-top:1px solid #e2e8f0; padding-top:8px;"><span>Valor anual contratado</span><span>${options.ctValor}</span></div>
                    </div>
                    <div class="report-card">
                        <h4><i class="fas fa-car"></i> Frota</h4>
                        <div class="report-item"><span>Total de veículos</span><span>${options.frotaTotal}</span></div>
                        <div class="report-item"><span>Em dia</span><span style="color:#16a34a;">${options.frotaEmDia}</span></div>
                        <div class="report-item"><span>A vencer</span><span style="color:#f59e0b;">${options.frotaAVencer}</span></div>
                        <div class="report-item"><span>Vencidos</span><span style="color:#dc2626;">${options.frotaVencido}</span></div>
                        <div class="report-item"><span>Intervenções registadas</span><span>${options.totalIntervencoes}</span></div>
                        <div class="report-item"><span>Sinistros</span><span>${options.totalSinistros}</span></div>
                        <div class="report-item" style="font-weight:bold; border-top:1px solid #e2e8f0; padding-top:8px;"><span>Valor gasto (manutenção/inspeção)</span><span>${options.gastoVeiculos}</span></div>
                    </div>
                    <div class="report-card">
                        <h4><i class="fas fa-headset"></i> Suporte Técnico</h4>
                        <div class="report-item"><span>Total</span><span>${options.suporteTotal}</span></div>
                        <div class="report-item"><span>Pendentes</span><span>${options.ajPend}</span></div>
                        <div class="report-item"><span>Concluídas</span><span>${options.ajConcl}</span></div>
                    </div>
                `;
  }

  window.TotalGestReportsView = {
    kpi: kpi,
    superadminHeader: superadminHeader,
    distributorHeader: distributorHeader,
    moduleLicenseCard: moduleLicenseCard,
    revenueBars: revenueBars,
    superadminCompanySummary: superadminCompanySummary,
    distributorClientSummary: distributorClientSummary,
    adminOverviewCards: adminOverviewCards
  };
})();
