from pathlib import Path

APP=Path('app.html'); SHELL=Path('assets/js/app-shell.js'); SW=Path('sw.js'); MODULE=Path('assets/js/app-reports-superadmin-metrics.js')
app=APP.read_text(encoding='utf-8'); shell=SHELL.read_text(encoding='utf-8'); sw=SW.read_text(encoding='utf-8')
fn='function renderizarReports()'; assert app.count(fn)==1
fs=app.index(fn); fb=app.index('{',fs)

def scan_end(text, brace):
    depth=0; mode='normal'; escape=False; stack=[]; tdepth=[]; i=brace
    while i<len(text):
        c=text[i]; n=text[i+1] if i+1<len(text) else ''
        if mode=='line_comment':
            if c=='\n': mode=stack.pop() if stack else 'normal'
        elif mode=='block_comment':
            if c=='*' and n=='/': mode=stack.pop() if stack else 'normal'; i+=1
        elif mode in ('single','double'):
            if escape: escape=False
            elif c=='\\': escape=True
            elif (mode=='single' and c=="'") or (mode=='double' and c=='"'): mode=stack.pop() if stack else 'normal'
        elif mode=='template':
            if escape: escape=False
            elif c=='\\': escape=True
            elif c=='`': mode=stack.pop() if stack else 'normal'
            elif c=='$' and n=='{': stack.append('template'); mode='template_expr'; tdepth.append(1); depth+=1; i+=1
        else:
            current=mode
            if c=='/' and n=='/': stack.append(current); mode='line_comment'; i+=1
            elif c=='/' and n=='*': stack.append(current); mode='block_comment'; i+=1
            elif c=="'": stack.append(current); mode='single'
            elif c=='"': stack.append(current); mode='double'
            elif c=='`': stack.append(current); mode='template'
            elif c=='{':
                depth+=1
                if current=='template_expr': tdepth[-1]+=1
            elif c=='}':
                depth-=1
                if current=='template_expr':
                    tdepth[-1]-=1
                    if tdepth[-1]==0: tdepth.pop(); mode=stack.pop()
                elif depth==0: return i+1
        i+=1
    raise AssertionError('unclosed')
fe=scan_end(app,fb); block=app[fs:fe]
start_marker="                const admins = dados.administradores || [];\n"
end_marker="                const _kpi = (lbl, val, cor, ic) =>"
assert block.count(start_marker)==1
assert block.count(end_marker)==1
bs=block.index(start_marker); be=block.index(end_marker,bs)
old_metrics=block[bs:be]
for token in ['const _emp =', 'const _now = Date.now();', 'const _ativo =', 'const _empAtivas =', 'const _expira =', 'const _totFunc =', 'const _totEnc =', 'const _addons =', 'let _recT = 0;', '_emp.forEach(a =>']:
    assert token in old_metrics, token

module="""/* Total Gest — métricas de superadmin para Relatórios. */
(function () {
  'use strict';

  function calculate(options) {
    const opts = options || {};
    const admins = opts.admins || [];
    const data = opts.data || {};
    const empresas = admins.filter(a => a.id !== 'superadmin');
    const now = Date.now();
    const ativo = a => !!(a.licenca && a.ativo !== false && a.licenca.dataExpiracao && a.licenca.dataExpiracao > now);
    const empresasAtivas = empresas.filter(ativo).length;
    const expiramEm10Dias = empresas.filter(a => a.licenca && a.licenca.dataExpiracao > now && (a.licenca.dataExpiracao - now) <= 10 * 86400000).length;
    const totalFuncionarios = (data.funcionarios || []).filter(f => f.role !== 'admin' && f.role !== 'superadmin').length;
    const totalEncarregados = (data.encarregados || []).length;
    const addonsAtivos = empresas.filter(a => opts.contractsActive(a)).length
      + empresas.filter(a => opts.fleetActive(a)).length
      + empresas.filter(a => opts.warehouseActive(a)).length
      + empresas.filter(a => opts.crmActive(a)).length
      + empresas.filter(a => opts.erpActive(a)).length;
    let receitaRecorrente = 0;
    empresas.forEach(a => {
      if (ativo(a)) receitaRecorrente += opts.baseValueCharged(a);
      if (opts.contractsActive(a)) receitaRecorrente += (a.contratosPlano === 'anual' ? opts.contractsAnnualPrice : opts.contractsMonthlyPrice);
      if (opts.fleetActive(a)) receitaRecorrente += (a.frotaPlano === 'anual' ? opts.fleetAnnualPrice : opts.fleetMonthlyPrice);
      if (opts.warehouseActive(a)) receitaRecorrente += (a.armazemPlano === 'anual' ? opts.warehouseAnnualPrice : opts.warehouseMonthlyPrice);
      if (opts.crmActive(a)) receitaRecorrente += (a.crmPlano === 'anual' ? opts.crmAnnualPrice : opts.crmMonthlyPrice);
      /* Assist incluído no CRM — não soma à parte. */
      if (opts.erpActive(a)) receitaRecorrente += (a.erpPlano === 'anual' ? opts.erpAnnualPrice : opts.erpMonthlyPrice);
    });

    return {
      empresas: empresas,
      empresasAtivas: empresasAtivas,
      expiramEm10Dias: expiramEm10Dias,
      totalFuncionarios: totalFuncionarios,
      totalEncarregados: totalEncarregados,
      addonsAtivos: addonsAtivos,
      receitaRecorrente: receitaRecorrente
    };
  }

  window.TotalGestReportsSuperadminMetrics = { calculate: calculate };
})();
"""
MODULE.write_text(module,encoding='utf-8')
new_metrics="""                const admins = dados.administradores || [];
                const _metrics = window.TotalGestReportsSuperadminMetrics.calculate({
                    admins: admins,
                    data: dados,
                    contractsActive: moduloContratosAtivo,
                    fleetActive: moduloFrotaAtivo,
                    warehouseActive: moduloArmazemAtivo,
                    crmActive: moduloCrmAtivo,
                    erpActive: moduloErpAtivo,
                    baseValueCharged: valorBaseCobradoDe,
                    contractsAnnualPrice: PRECO_CONTRATOS_ANUAL,
                    contractsMonthlyPrice: PRECO_CONTRATOS_MENSAL,
                    fleetAnnualPrice: PRECO_FROTA_ANUAL,
                    fleetMonthlyPrice: PRECO_FROTA_MENSAL,
                    warehouseAnnualPrice: PRECO_ARMAZEM_ANUAL,
                    warehouseMonthlyPrice: PRECO_ARMAZEM_MENSAL,
                    crmAnnualPrice: PRECO_CRM_ANUAL,
                    crmMonthlyPrice: PRECO_CRM_MENSAL,
                    erpAnnualPrice: PRECO_ERP_ANUAL,
                    erpMonthlyPrice: PRECO_ERP_MENSAL
                });
                const _emp = _metrics.empresas;
                const _empAtivas = _metrics.empresasAtivas;
                const _expira = _metrics.expiramEm10Dias;
                const _totFunc = _metrics.totalFuncionarios;
                const _totEnc = _metrics.totalEncarregados;
                const _addons = _metrics.addonsAtivos;
                const _recT = _metrics.receitaRecorrente;
"""
new_block=block[:bs]+new_metrics+block[be:]
app=app[:fs]+new_block+app[fe:]

init_anchor='myDay: true'; assert app.count(init_anchor)==1; app=app.replace(init_anchor,init_anchor+', reportsSuperadminMetrics: true',1)
shell_anchor="    myDay: './assets/js/app-my-day.js',\n"; assert shell.count(shell_anchor)==1; shell=shell.replace(shell_anchor,shell_anchor+"    reportsSuperadminMetrics: './assets/js/app-reports-superadmin-metrics.js',\n",1)
load_anchor="    if (options.myDay === true) pedidos.push(MODULOS.myDay);\n"; assert shell.count(load_anchor)==1; shell=shell.replace(load_anchor,load_anchor+"    if (options.reportsSuperadminMetrics === true) pedidos.push(MODULOS.reportsSuperadminMetrics);\n",1)
assert "const CACHE = 'totalgest-v95';" in sw; sw=sw.replace("const CACHE = 'totalgest-v95';","const CACHE = 'totalgest-v96';",1)
sw_anchor="  './assets/js/app-my-day.js',\n"; assert sw.count(sw_anchor)==1; sw=sw.replace(sw_anchor,sw_anchor+"  './assets/js/app-reports-superadmin-metrics.js',\n",1)

nfs=app.index(fn); nfe=scan_end(app,app.index('{',nfs)); nblock=app[nfs:nfe]
assert nblock.count('window.TotalGestReportsSuperadminMetrics.calculate({')==1
for token in ['const _now = Date.now();','const _ativo = a =>','let _recT = 0;','_emp.forEach(a => { if (_ativo(a))']:
    assert token not in nblock, token
assert shell.count('./assets/js/app-reports-superadmin-metrics.js')==1
assert sw.count('./assets/js/app-reports-superadmin-metrics.js')==1
APP.write_text(app,encoding='utf-8'); SHELL.write_text(shell,encoding='utf-8'); SW.write_text(sw,encoding='utf-8')
