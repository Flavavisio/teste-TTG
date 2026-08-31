from pathlib import Path
text=Path('app.html').read_text(encoding='utf-8')
start=text.index('function renderizarReports(')
for needle in ["const meusClientes = (dados.administradores || []).filter(a => a.distribuidorId === admin.id);", 'TotalGestApp.init({']:
    pos=text.index(needle, start if needle.startswith('const meusClientes') else 0)
    print('\n---', needle, '---')
    print(text[max(0,pos-1200):pos+6500])
