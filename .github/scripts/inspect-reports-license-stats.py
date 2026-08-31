from pathlib import Path
text=Path('app.html').read_text(encoding='utf-8')
start=text.index('function renderizarReports(')
for needle in ['_licStats','Expiram em 10d','Sem licença']:
    pos=text.index(needle,start)
    print('\n---',needle,'---')
    print(text[max(start,pos-1800):pos+2200])
