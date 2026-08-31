from pathlib import Path
text=Path('app.html').read_text(encoding='utf-8')
start=text.index('function renderizarReports(')
for needle in ['const totalLocais', 'totalLocais', 'ctValor']:
    pos=text.find(needle,start)
    print('\n===',needle,'pos',pos,'===')
    if pos>=0: print(text[max(start,pos-1200):pos+6000])
