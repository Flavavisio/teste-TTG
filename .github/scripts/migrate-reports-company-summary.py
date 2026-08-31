from pathlib import Path
APP=Path('app.html'); MOD=Path('assets/js/app-reports-superadmin-metrics.js'); SW=Path('sw.js')
app=APP.read_text(encoding='utf-8'); mod=MOD.read_text(encoding='utf-8'); sw=SW.read_text(encoding='utf-8')
start=app.index('function renderizarReports(')
bs=app.index('admins.forEach(admin => {',start)
be=app.index('                    });',bs)+len('                    });')
old=app[bs:be]
assert old.count('const funcs =')==1 and old.count('const valorEmpresa =')==1 and old.count('html += `<tr class=')==1
# Preserve HTML rendering inline; replace only calculation prefix through total counters.
htmlpos=old.index('                        html += `<tr class=')
prefix=old[:htmlpos]
calc_end=prefix.index('                        totalReceitaGlobal += valorEmpresa;')
# include totals/count updates up to just before HTML
calc_prefix=prefix[:calc_end]
updates=prefix[calc_end:]
assert 'if (temRondas) totalRondasGlobal++;' in updates
newcalc="""admins.forEach(admin => {
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
"""+updates
new=newcalc+old[htmlpos:]
app=app[:bs]+new+app[be:]
needle='  window.TotalGestReportsSuperadminMetrics = { calculate: calculate };\n'
assert mod.count(needle)==1
addition="""
  function calculateCompany(options) {
    const opts = options || {};
    const admin = opts.admin || {};
    const data = opts.data || {};
    const funcionarios = data.funcionarios ? data.funcionarios.filter(f => f.adminId === admin.id && f.role !== 'admin' && f.role !== 'superadmin').length : 0;
    const encarregados = data.encarregados ? data.encarregados.filter(e => e.adminId === admin.id).length : 0;
    const valorBase = admin.licenca && admin.ativo ? opts.baseValueCharged(admin) : 0;
    const temContratos = opts.contractsActive(admin);
    const temFrota = opts.fleetActive(admin);
    const temArmazem = opts.warehouseActive(admin);
    const temCrm = opts.crmActive(admin);
    const temErp = opts.erpActive(admin);
    const temRondas = opts.roundsActive(admin);
    const valorContratos = temContratos ? (admin.contratosPlano === 'anual' ? opts.contractsAnnualPrice : opts.contractsMonthlyPrice) : 0;
    const valorFrota = temFrota ? (admin.frotaPlano === 'anual' ? opts.fleetAnnualPrice : opts.fleetMonthlyPrice) : 0;
    const valorArmazem = temArmazem ? (admin.armazemPlano === 'anual' ? opts.warehouseAnnualPrice : opts.warehouseMonthlyPrice) : 0;
    const valorCrm = temCrm ? (admin.crmPlano === 'anual' ? opts.crmAnnualPrice : opts.crmMonthlyPrice) : 0;
    const valorErp = temErp ? (admin.erpPlano === 'anual' ? opts.erpAnnualPrice : opts.erpMonthlyPrice) : 0;
    /* Rondas: grátis por agora; cálculo preservado para quando tiver preço. */
    const valorRondas = temRondas ? (admin.rondasPlano === 'anual' ? opts.roundsAnnualPrice : opts.roundsMonthlyPrice) : 0;
    return {
      funcionarios: funcionarios,
      encarregados: encarregados,
      temContratos: temContratos,
      temFrota: temFrota,
      temArmazem: temArmazem,
      temCrm: temCrm,
      temErp: temErp,
      temRondas: temRondas,
      valorEmpresa: valorBase + valorContratos + valorFrota + valorArmazem + valorCrm + valorErp + valorRondas
    };
  }

"""
mod=mod.replace(needle,addition+'  window.TotalGestReportsSuperadminMetrics = { calculate: calculate, calculateCompany: calculateCompany };\n',1)
assert app.count('TotalGestReportsSuperadminMetrics.calculateCompany({')==1
assert mod.count('function calculateCompany(options)')==1
assert "const CACHE = 'totalgest-v101';" in sw
sw=sw.replace("const CACHE = 'totalgest-v101';","const CACHE = 'totalgest-v102';",1)
APP.write_text(app,encoding='utf-8'); MOD.write_text(mod,encoding='utf-8'); SW.write_text(sw,encoding='utf-8')
