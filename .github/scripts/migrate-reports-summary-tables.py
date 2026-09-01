from pathlib import Path

APP = Path('app.html')
VIEW = Path('assets/js/app-reports-view.js')
SW = Path('sw.js')

app = APP.read_text(encoding='utf-8')
view = VIEW.read_text(encoding='utf-8')
sw = SW.read_text(encoding='utf-8')

protected = {
    'bootstrapSupabase()': app.count('bootstrapSupabase()'),
    'supabase.auth': app.count('supabase.auth'),
    'window.TotalGestReportsSuperadminMetrics.calculateCompany({': app.count('window.TotalGestReportsSuperadminMetrics.calculateCompany({'),
    'window.TotalGestReportsDistributorMetrics.calculateClient({': app.count('window.TotalGestReportsDistributorMetrics.calculateClient({'),
}


def replace_region(text, start_marker, end_marker, replacement):
    assert text.count(start_marker) == 1, (start_marker, text.count(start_marker))
    assert text.count(end_marker) == 1, (end_marker, text.count(end_marker))
    start = text.index(start_marker)
    end = text.index(end_marker, start)
    assert end > start
    return text[:start] + replacement + text[end:]


super_start = '                html += `<div class="report-card"><h4><i class="fas fa-chart-line"></i> Resumo por Empresa</h4>`;'
super_end = '                // Licenças de Manutenção (módulo Contratos)'
super_replacement = '''                const _companyRows = [];
                let totalReceitaGlobal = 0;
                let totalFuncGlobal = 0;
                let totalEncarregadosGlobal = 0;
                let totalContratosGlobal = 0;
                let totalFrotaGlobal = 0;
                let totalArmazemGlobal = 0;
                let totalCrmGlobal = 0;
                let totalErpGlobal = 0;
                let totalRondasGlobal = 0;
                admins.forEach(admin => {
                    const _row = window.TotalGestReportsSuperadminMetrics.calculateCompany({
                        admin: admin,
                        data: dados,
                        baseValueCharged: valorBaseCobradoDe,
                        contractsActive: moduloContratosAtivo,
                        fleetActive: moduloFrotaAtivo,
                        warehouseActive: moduloArmazemAtivo,
                        crmActive: moduloCrmAtivo,
                        erpActive: moduloErpAtivo,
                        roundsActive: moduloRondasAtivo,
                        contractsAnnualPrice: PRECO_CONTRATOS_ANUAL,
                        contractsMonthlyPrice: PRECO_CONTRATOS_MENSAL,
                        fleetAnnualPrice: PRECO_FROTA_ANUAL,
                        fleetMonthlyPrice: PRECO_FROTA_MENSAL,
                        warehouseAnnualPrice: PRECO_ARMAZEM_ANUAL,
                        warehouseMonthlyPrice: PRECO_ARMAZEM_MENSAL,
                        crmAnnualPrice: PRECO_CRM_ANUAL,
                        crmMonthlyPrice: PRECO_CRM_MENSAL,
                        erpAnnualPrice: PRECO_ERP_ANUAL,
                        erpMonthlyPrice: PRECO_ERP_MENSAL,
                        roundsAnnualPrice: PRECO_RONDAS_ANUAL,
                        roundsMonthlyPrice: PRECO_RONDAS_MENSAL
                    });
                    const funcs = _row.funcionarios;
                    const encarregados = _row.encarregados;
                    const temContratos = _row.temContratos;
                    const temFrota = _row.temFrota;
                    const temArmazem = _row.temArmazem;
                    const temCrm = _row.temCrm;
                    const temErp = _row.temErp;
                    const temRondas = _row.temRondas;
                    const valorEmpresa = _row.valorEmpresa;
                    const dataExp = admin.licenca ? new Date(admin.licenca.dataExpiracao).toLocaleDateString(
                        'pt-PT') : '-';
                    const planoLabel = admin.licenca ? PLANOS[admin.licenca.plano]?.label || admin.licenca.plano :
                        'Sem licença';
                    const maxFunc = admin.licenca ? admin.licenca.maxFuncionarios : 0;
                    const atingiuLimite = funcs >= maxFunc && maxFunc > 0;
                    const rowClass = atingiuLimite ? 'tr-limite-atingido' : '';
                    totalReceitaGlobal += valorEmpresa;
                    totalFuncGlobal += funcs;
                    totalEncarregadosGlobal += encarregados;
                    if (temContratos) totalContratosGlobal++;
                    if (temFrota) totalFrotaGlobal++;
                    if (temArmazem) totalArmazemGlobal++;
                    if (temCrm) totalCrmGlobal++;
                    if (temErp) totalErpGlobal++;
                    if (temRondas) totalRondasGlobal++;
                    _companyRows.push({
                        rowClass: rowClass,
                        empresa: admin.empresa || 'Sem empresa',
                        nome: admin.nome,
                        planoLabel: planoLabel,
                        dataExp: dataExp,
                        funcionarios: funcs,
                        atingiuLimite: atingiuLimite,
                        encarregados: encarregados,
                        temContratos: temContratos,
                        temFrota: temFrota,
                        temArmazem: temArmazem,
                        temCrm: temCrm,
                        temErp: temErp,
                        temRondas: temRondas,
                        valorEmpresa: valorEmpresa
                    });
                });
                html += window.TotalGestReportsView.superadminCompanySummary({
                    rows: _companyRows,
                    totals: {
                        funcionarios: totalFuncGlobal,
                        encarregados: totalEncarregadosGlobal,
                        contratos: totalContratosGlobal,
                        frota: totalFrotaGlobal,
                        armazem: totalArmazemGlobal,
                        crm: totalCrmGlobal,
                        erp: totalErpGlobal,
                        rondas: totalRondasGlobal,
                        receita: totalReceitaGlobal
                    }
                });

'''
app = replace_region(app, super_start, super_end, super_replacement)

dist_start = '                html += `<div class="report-card"><h4><i class="fas fa-chart-line"></i> Resumo por Cliente</h4>`;'
dist_end = '                container.innerHTML = html;\n                return;\n            }\n\n            if (!usuarioLogado'
dist_replacement = '''                const _clientRows = [];
                let totalCobradoGlobal = 0;
                meusClientes.forEach(c => {
                    const _clientMetrics = window.TotalGestReportsDistributorMetrics.calculateClient({
                        client: c,
                        data: dados,
                        contractsActive: moduloContratosAtivo,
                        fleetActive: moduloFrotaAtivo,
                        warehouseActive: moduloArmazemAtivo,
                        crmActive: moduloCrmAtivo,
                        getPlanValue: getValorPlano,
                        contractsAnnualPrice: PRECO_CONTRATOS_ANUAL,
                        contractsMonthlyPrice: PRECO_CONTRATOS_MENSAL,
                        fleetAnnualPrice: PRECO_FROTA_ANUAL,
                        fleetMonthlyPrice: PRECO_FROTA_MENSAL,
                        warehouseAnnualPrice: PRECO_ARMAZEM_ANUAL,
                        warehouseMonthlyPrice: PRECO_ARMAZEM_MENSAL,
                        crmAnnualPrice: PRECO_CRM_ANUAL,
                        crmMonthlyPrice: PRECO_CRM_MENSAL
                    });
                    const funcs = _clientMetrics.funcionarios;
                    const temContratos = _clientMetrics.temContratos;
                    const temFrota = _clientMetrics.temFrota;
                    const temArmazem = _clientMetrics.temArmazem;
                    const temCrm = _clientMetrics.temCrm;
                    const valorCliente = _clientMetrics.valorCliente;
                    totalCobradoGlobal += valorCliente;
                    const dataExp = c.licenca ? new Date(c.licenca.dataExpiracao).toLocaleDateString('pt-PT') : '-';
                    const planoLabel = c.licenca ? PLANOS[c.licenca.plano]?.label || c.licenca.plano : 'Sem licença';
                    _clientRows.push({
                        empresa: c.empresa || '-',
                        nome: c.nome,
                        planoLabel: planoLabel,
                        dataExp: dataExp,
                        funcionarios: funcs,
                        temContratos: temContratos,
                        temFrota: temFrota,
                        temArmazem: temArmazem,
                        temCrm: temCrm,
                        valorCliente: valorCliente
                    });
                });
                html += window.TotalGestReportsView.distributorClientSummary({
                    rows: _clientRows,
                    totalCobrado: totalCobradoGlobal
                });
'''
app = replace_region(app, dist_start, dist_end, dist_replacement + dist_end)

view_anchor = '  window.TotalGestReportsView = {\n'
assert view.count(view_anchor) == 1
new_view_functions = '''  function superadminCompanySummary(options) {
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

'''
view = view.replace(view_anchor, new_view_functions + view_anchor, 1)
export_anchor = '    revenueBars: revenueBars\n'
assert view.count(export_anchor) == 1
view = view.replace(export_anchor, '    revenueBars: revenueBars,\n    superadminCompanySummary: superadminCompanySummary,\n    distributorClientSummary: distributorClientSummary\n', 1)

assert sw.count("const CACHE = 'totalgest-v114';") == 1
sw = sw.replace("const CACHE = 'totalgest-v114';", "const CACHE = 'totalgest-v115';", 1)

for needle, count in protected.items():
    assert app.count(needle) == count, (needle, count, app.count(needle))
assert app.count('window.TotalGestReportsView.superadminCompanySummary({') == 1
assert app.count('window.TotalGestReportsView.distributorClientSummary({') == 1
assert app.count('Resumo por Empresa</h4>') == 0
assert app.count('Resumo por Cliente</h4>') == 0
assert view.count('function superadminCompanySummary(options)') == 1
assert view.count('function distributorClientSummary(options)') == 1
assert view.count('Resumo por Empresa</h4>') == 1
assert view.count('Resumo por Cliente</h4>') == 1
assert sw.count("const CACHE = 'totalgest-v115';") == 1

start = app.index('        function renderizarReports() {')
end = app.index('\n        function ', start + 1)
reports = app[start:end]
print(f'RENDERIZAR_REPORTS_AFTER chars={len(reports)} lines={reports.count(chr(10))+1}')
print('REPORT_SUMMARY_TABLE_MIGRATION_ASSERTIONS=OK')

APP.write_text(app, encoding='utf-8')
VIEW.write_text(view, encoding='utf-8')
SW.write_text(sw, encoding='utf-8')
