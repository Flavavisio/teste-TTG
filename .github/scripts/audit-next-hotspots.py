from pathlib import Path
text=Path('app.html').read_text(encoding='utf-8')
for needle in ['function renderizarDashboardAnalitico(', 'function renderizarAuditoria(', 'function renderizarMinhaLicenca(']:
    p=text.find(needle)
    print('\n===',needle,'pos',p,'===')
    if p>=0:
        print(text[p:p+14000])
