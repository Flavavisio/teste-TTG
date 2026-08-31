from pathlib import Path
APP=Path('app.html'); SHELL=Path('assets/js/app-shell.js'); SW=Path('sw.js'); MODULE=Path('assets/js/app-my-day.js')
app=APP.read_text(encoding='utf-8'); shell=SHELL.read_text(encoding='utf-8'); sw=SW.read_text(encoding='utf-8')
marker='function renderizarOMeuDia(forcarDesktop)'; assert app.count(marker)==1
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
assert len(old.splitlines())==245
for token in ['window._ligarClienteOS = function', 'window._ligarClienteObra = function', '_htmlPainelAdminHoje(adminId, hoje)', '_tgmAplicarGrelhaDesktop(cont)']:
    assert token in old, token
prefix="""/* Total Gest — renderização do painel O Meu Dia. */
(function () {
  'use strict';

  function run(options) {
    const opts = options || {};
    const forcarDesktop = opts.forceDesktop;
    const document = opts.document;
    const window = opts.window;
    const alert = opts.alert;
    const confirm = opts.confirm;
    const usuarioLogado = opts.user;
    const dados = opts.data;
    const _ehPerfilMobile = opts.isMobileProfile;
    const getDataHoje = opts.getToday;
    const escapeHtmlSimples = opts.escapeHtml;
    const _osMapaInfo = opts.mapInfo;
    const obterNomeCliente = opts.clientName;
    const _obraLongaPontoAberto = opts.longWorkOpenClock;
    const _botaoPontoObraHTML = opts.longWorkClockButtonHtml;
    const _moradaCompletaObra = opts.fullWorkAddress;
    const _htmlPainelAdminHoje = opts.adminTodayHtml;
    const _htmlResumoEquipaHoje = opts.teamTodayHtml;
    const _tgmMostrarTempo = opts.showWeather;
    const _tgmAplicarGrelhaDesktop = opts.applyDesktopGrid;
"""
suffix="""
  }

  window.TotalGestMyDay = { run: run };
})();
"""
MODULE.write_text(prefix+body+suffix,encoding='utf-8')
new="""function renderizarOMeuDia(forcarDesktop) {
            window.TotalGestMyDay.run({
                forceDesktop: forcarDesktop,
                document: document,
                window: window,
                alert: alert,
                confirm: confirm,
                user: usuarioLogado,
                data: dados,
                isMobileProfile: _ehPerfilMobile,
                getToday: getDataHoje,
                escapeHtml: escapeHtmlSimples,
                mapInfo: _osMapaInfo,
                clientName: obterNomeCliente,
                longWorkOpenClock: _obraLongaPontoAberto,
                longWorkClockButtonHtml: _botaoPontoObraHTML,
                fullWorkAddress: _moradaCompletaObra,
                adminTodayHtml: _htmlPainelAdminHoje,
                teamTodayHtml: _htmlResumoEquipaHoje,
                showWeather: _tgmMostrarTempo,
                applyDesktopGrid: _tgmAplicarGrelhaDesktop
            });
        }"""
app=app[:start]+new+app[end:]
init_anchor='homeDashboard: true'; assert app.count(init_anchor)==1; app=app.replace(init_anchor,init_anchor+', myDay: true',1)
shell_anchor="    homeDashboard: './assets/js/app-home-dashboard.js',\n"; assert shell.count(shell_anchor)==1; shell=shell.replace(shell_anchor,shell_anchor+"    myDay: './assets/js/app-my-day.js',\n",1)
load_anchor="    if (options.homeDashboard === true) pedidos.push(MODULOS.homeDashboard);\n"; assert shell.count(load_anchor)==1; shell=shell.replace(load_anchor,load_anchor+"    if (options.myDay === true) pedidos.push(MODULOS.myDay);\n",1)
assert "const CACHE = 'totalgest-v94';" in sw; sw=sw.replace("const CACHE = 'totalgest-v94';","const CACHE = 'totalgest-v95';",1)
sw_anchor="  './assets/js/app-home-dashboard.js',\n"; assert sw.count(sw_anchor)==1; sw=sw.replace(sw_anchor,sw_anchor+"  './assets/js/app-my-day.js',\n",1)
ns=app.index(marker); ne=scan_end(app,app.index('{',ns)); block=app[ns:ne]
assert block.count('window.TotalGestMyDay.run({')==1
for token in ['window._ligarClienteOS = function','dados.servicos','_htmlPainelAdminHoje(adminId, hoje)']: assert token not in block
assert shell.count('./assets/js/app-my-day.js')==1 and sw.count('./assets/js/app-my-day.js')==1
APP.write_text(app,encoding='utf-8'); SHELL.write_text(shell,encoding='utf-8'); SW.write_text(sw,encoding='utf-8')
