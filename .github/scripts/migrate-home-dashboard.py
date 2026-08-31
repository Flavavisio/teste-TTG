from pathlib import Path

APP=Path('app.html'); SHELL=Path('assets/js/app-shell.js'); SW=Path('sw.js'); MODULE=Path('assets/js/app-home-dashboard.js')
app=APP.read_text(encoding='utf-8'); shell=SHELL.read_text(encoding='utf-8'); sw=SW.read_text(encoding='utf-8')
marker='function renderizarHomeDashboard()'
assert app.count(marker)==1
start=app.index(marker); brace=app.index('{',start)

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

end=scan_end(app,brace); old=app[start:end]; body=app[brace+1:end-1]
assert len(old.splitlines())==206, len(old.splitlines())
for token in ['_favoritosHTML()', 'renderizarOMeuDia(true)', 'isLicencaValida(', '_tgBarras(', "adminAtual()?.ehDistribuidor", '_distValorAddonsCliente(', 'renderizarAgendaObras()']:
    assert token in old, token

prefix="""/* Total Gest — renderização do dashboard principal da Home. */
(function () {
  'use strict';

  function run(options) {
    const opts = options || {};
    const document = opts.document;
    const usuarioLogado = opts.user;
    const dados = opts.data;
    const _favoritosHTML = opts.favoritesHtml;
    const _renderizarOnboarding = opts.renderOnboarding;
    const renderizarOMeuDia = opts.renderMyDay;
    const isLicencaValida = opts.isLicenseValid;
    const calcularDiasRestantes = opts.daysRemaining;
    const valorBaseCobradoDe = opts.baseValueCharged;
    const _addonsAtivosDe = opts.activeAddons;
    const _kpi = opts.kpi;
    const _tgBarras = opts.barChart;
    const PLANOS = opts.plans;
    const moduloContratosAtivo = opts.contractsActive;
    const PRECO_CONTRATOS_ANUAL = opts.contractsAnnualPrice;
    const PRECO_CONTRATOS_MENSAL = opts.contractsMonthlyPrice;
    const moduloFrotaAtivo = opts.fleetActive;
    const PRECO_FROTA_ANUAL = opts.fleetAnnualPrice;
    const PRECO_FROTA_MENSAL = opts.fleetMonthlyPrice;
    const moduloArmazemAtivo = opts.warehouseActive;
    const PRECO_ARMAZEM_ANUAL = opts.warehouseAnnualPrice;
    const PRECO_ARMAZEM_MENSAL = opts.warehouseMonthlyPrice;
    const moduloNotificacoesAtivo = opts.notificationsActive;
    const PRECO_NOTIFICACOES_ANUAL = opts.notificationsAnnualPrice;
    const PRECO_NOTIFICACOES_MENSAL = opts.notificationsMonthlyPrice;
    const moduloCrmAtivo = opts.crmActive;
    const PRECO_CRM_ANUAL = opts.crmAnnualPrice;
    const PRECO_CRM_MENSAL = opts.crmMonthlyPrice;
    const adminAtual = opts.currentAdmin;
    const getValorPlano = opts.getPlanValue;
    const _distValorAddonsCliente = opts.distributorAddonValue;
    const getDataHoje = opts.getToday;
    const renderizarAgendaObras = opts.renderWorkAgenda;
"""
suffix="""
  }

  window.TotalGestHomeDashboard = { run: run };
})();
"""
MODULE.write_text(prefix+body+suffix,encoding='utf-8')
new="""function renderizarHomeDashboard() {
            window.TotalGestHomeDashboard.run({
                document: document,
                user: usuarioLogado,
                data: dados,
                favoritesHtml: _favoritosHTML,
                renderOnboarding: _renderizarOnboarding,
                renderMyDay: renderizarOMeuDia,
                isLicenseValid: isLicencaValida,
                daysRemaining: calcularDiasRestantes,
                baseValueCharged: valorBaseCobradoDe,
                activeAddons: _addonsAtivosDe,
                kpi: _kpi,
                barChart: _tgBarras,
                plans: PLANOS,
                contractsActive: moduloContratosAtivo,
                contractsAnnualPrice: PRECO_CONTRATOS_ANUAL,
                contractsMonthlyPrice: PRECO_CONTRATOS_MENSAL,
                fleetActive: moduloFrotaAtivo,
                fleetAnnualPrice: PRECO_FROTA_ANUAL,
                fleetMonthlyPrice: PRECO_FROTA_MENSAL,
                warehouseActive: moduloArmazemAtivo,
                warehouseAnnualPrice: PRECO_ARMAZEM_ANUAL,
                warehouseMonthlyPrice: PRECO_ARMAZEM_MENSAL,
                notificationsActive: moduloNotificacoesAtivo,
                notificationsAnnualPrice: PRECO_NOTIFICACOES_ANUAL,
                notificationsMonthlyPrice: PRECO_NOTIFICACOES_MENSAL,
                crmActive: moduloCrmAtivo,
                crmAnnualPrice: PRECO_CRM_ANUAL,
                crmMonthlyPrice: PRECO_CRM_MENSAL,
                currentAdmin: adminAtual,
                getPlanValue: getValorPlano,
                distributorAddonValue: _distValorAddonsCliente,
                getToday: getDataHoje,
                renderWorkAgenda: renderizarAgendaObras
            });
        }"""
app=app[:start]+new+app[end:]
init_anchor='cardVisibility: true'; assert app.count(init_anchor)==1; app=app.replace(init_anchor,init_anchor+', homeDashboard: true',1)
shell_anchor="    cardVisibility: './assets/js/app-card-visibility.js',\n"; assert shell.count(shell_anchor)==1; shell=shell.replace(shell_anchor,shell_anchor+"    homeDashboard: './assets/js/app-home-dashboard.js',\n",1)
load_anchor="    if (options.cardVisibility === true) pedidos.push(MODULOS.cardVisibility);\n"; assert shell.count(load_anchor)==1; shell=shell.replace(load_anchor,load_anchor+"    if (options.homeDashboard === true) pedidos.push(MODULOS.homeDashboard);\n",1)
assert "const CACHE = 'totalgest-v93';" in sw; sw=sw.replace("const CACHE = 'totalgest-v93';","const CACHE = 'totalgest-v94';",1)
sw_anchor="  './assets/js/app-card-visibility.js',\n"; assert sw.count(sw_anchor)==1; sw=sw.replace(sw_anchor,sw_anchor+"  './assets/js/app-home-dashboard.js',\n",1)
ns=app.index(marker); ne=scan_end(app,app.index('{',ns)); block=app[ns:ne]
assert block.count('window.TotalGestHomeDashboard.run({')==1
for token in ['_tgBarras(', 'dados.servicos', 'renderizarOMeuDia(true)']: assert token not in block, token
assert shell.count('./assets/js/app-home-dashboard.js')==1 and sw.count('./assets/js/app-home-dashboard.js')==1
APP.write_text(app,encoding='utf-8'); SHELL.write_text(shell,encoding='utf-8'); SW.write_text(sw,encoding='utf-8')
