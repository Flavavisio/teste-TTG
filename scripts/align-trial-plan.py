from pathlib import Path
import re

path = Path('app.html')
text = path.read_text(encoding='utf-8')

plan_pattern = re.compile(r"'demo_30'\s*:\s*\{\s*dias:\s*30,\s*label:\s*'Licença Demo 30 dias'\s*\},")
name_pattern = re.compile(r"demo_30\s*:\s*'Demo 30 dias',")
monthly_pattern = re.compile(r"'mensal'\s*:\s*\{\s*dias:\s*30,\s*label:\s*'Licença Mensal'\s*\},")

if len(plan_pattern.findall(text)) != 1:
    raise SystemExit('definicao demo_30 inesperada')
if len(name_pattern.findall(text)) != 1:
    raise SystemExit('nome demo_30 inesperado')
if len(monthly_pattern.findall(text)) != 1:
    raise SystemExit('plano mensal de 30 dias inesperado')

text, n1 = plan_pattern.subn("'demo_30': { dias: 14, label: 'Licença Demo 14 dias' },", text, count=1)
text, n2 = name_pattern.subn("demo_30: 'Demo 14 dias',", text, count=1)

if n1 != 1 or n2 != 1:
    raise SystemExit('substituicoes trial inesperadas')
if len(monthly_pattern.findall(text)) != 1:
    raise SystemExit('plano mensal foi alterado indevidamente')
if text.count("'demo_30': { dias: 14, label: 'Licença Demo 14 dias' },") != 1:
    raise SystemExit('novo demo de 14 dias nao ficou unico')
if text.count("demo_30: 'Demo 14 dias',") != 1:
    raise SystemExit('novo nome demo de 14 dias nao ficou unico')

path.write_text(text, encoding='utf-8')
print('OK: demo_30 = 14 dias; mensal = 30 dias.')
