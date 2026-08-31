from pathlib import Path
text=Path('app.html').read_text(encoding='utf-8')
start=text.index('function renderizarReports(')
end=text.index('function renderizarReportsDashboard(',start)
block=text[start:end]
for term in ['licen','expira','Sem licença','Ativas','Expiradas']:
    print('\n===',term,'===')
    low=block.lower(); needle=term.lower(); p=0; count=0
    while True:
        p=low.find(needle,p)
        if p<0: break
        count+=1
        print(block[max(0,p-700):p+1000])
        p+=len(needle)
    print('COUNT',count)
