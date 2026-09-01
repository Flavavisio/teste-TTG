from pathlib import Path
text=Path('app.html').read_text(encoding='utf-8')
# Funções candidatas conhecidas; scanner simples só para corpos sem templates.
names=['renderizarAuditoria','renderizarGestaoEquipamentos','renderizarReportsDashboard','_renderizarAssistenciasAprovacao','renderizarMinhaLicenca','renderizarRelatorioOS','_renderizarTabelaGenerica','renderizarPainelVigilancia','renderizarDashboardAnalitico','renderizarAnalyticsSuperAdmin']

def scan(name):
    token='function '+name+'('
    s=text.find(token)
    if s<0: return None
    brace=text.find('{',s)
    mode='n'; esc=False; depth=0; i=brace
    while i<len(text):
        c=text[i]; n=text[i+1] if i+1<len(text) else ''
        if mode=='n':
            if c=="'": mode='s'
            elif c=='"': mode='d'
            elif c=='`': return ('template',s,None,None)
            elif c=='/' and n=='/': mode='lc'; i+=1
            elif c=='/' and n=='*': mode='bc'; i+=1
            elif c=='{': depth+=1
            elif c=='}':
                depth-=1
                if depth==0:
                    body=text[s:i+1]
                    return ('ok',s,i+1,body)
        elif mode in ('s','d'):
            if esc: esc=False
            elif c=='\\': esc=True
            elif (mode=='s' and c=="'") or (mode=='d' and c=='"'): mode='n'
        elif mode=='lc':
            if c=='\n': mode='n'
        elif mode=='bc':
            if c=='*' and n=='/': mode='n'; i+=1
        i+=1
    return ('unclosed',s,None,None)

for name in names:
    r=scan(name)
    print('\n###',name,r[0] if r else 'missing')
    if r and r[0]=='ok':
        b=r[3]
        print('lines',b.count('\n')+1,'chars',len(b),'await',b.count('await '),'supabase',b.lower().count('supabase'),'fetch',b.count('fetch('),'innerHTML',b.count('innerHTML'),'filter',b.count('.filter('),'reduce',b.count('.reduce('),'map',b.count('.map('))
        print(b[:2200])
