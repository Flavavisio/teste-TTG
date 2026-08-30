from pathlib import Path

path = Path('app.html')
text = path.read_text(encoding='utf-8')
original = text

old_plan = "'demo_30':    { dias: 30, label: 'Licença Demo 30 dias' },"
new_plan = "'demo_30':    { dias: 14, label: 'Licença Demo 14 dias' },"
old_name = "demo_30: 'Demo 30 dias',"
new_name = "demo_30: 'Demo 14 dias',"
paid_monthly = "'mensal':     { dias: 30, label: 'Licença Mensal' },"

if text.count(old_plan) != 1:
    raise SystemExit('definicao demo_30 inesperada')
if text.count(old_name) != 1:
    raise SystemExit('nome demo_30 inesperado')
if text.count(paid_monthly) != 1:
    raise SystemExit('plano mensal de 30 dias inesperado')

text = text.replace(old_plan, new_plan, 1).replace(old_name, new_name, 1)

if text.count(new_plan) != 1 or text.count(new_name) != 1:
    raise SystemExit('novo demo de 14 dias nao ficou unico')
if text.count(paid_monthly) != 1:
    raise SystemExit('plano mensal foi alterado indevidamente')
if len(original) != len(text) + 2:
    raise SystemExit('variacao de tamanho inesperada')

path.write_text(text, encoding='utf-8')
print('OK: demo_30 = 14 dias; mensal = 30 dias.')
