from pathlib import Path
text=Path('app.html').read_text(encoding='utf-8')
start=text.index('function renderizarReports(')
block=text[start:start+70000]
for term in ['licen','expira','Sem licença','Ativas','Expiradas']:
    print('\n===',term,'===')
    low=block.lower(); needle=term.lower(); p=0; count=0
    while True:
        p=low.find(needle,p)
        if p<0: break
        count+=1
        print(block[max(0,p-500):p+800])
        p+=len(needle)
    print('COUNT',count)
