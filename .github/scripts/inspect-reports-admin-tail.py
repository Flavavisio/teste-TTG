from pathlib import Path
text=Path('app.html').read_text(encoding='utf-8')
needle='reportsDistributorMetrics'
pos=0
while True:
    pos=text.find(needle,pos)
    if pos<0: break
    print('\n---',pos,'---')
    print(text[max(0,pos-800):pos+1200])
    pos+=len(needle)
