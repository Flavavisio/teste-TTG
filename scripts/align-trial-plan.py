from pathlib import Path

path = Path('app.html')
text = path.read_text(encoding='utf-8')

old = "            'demo_30': { dias: 30, funcionarios: 5, preco: 0, label: 'Licença Trial 30 dias' },"
new = "            'demo_30': { dias: 14, funcionarios: 5, preco: 0, label: 'Licença Trial 14 dias' },"

# Guardas: alterar apenas o trial principal. As demos manuais de módulos
# (demo_1/demo_10/demo_30) e os planos mensais de 30 dias têm de ficar intactos.
if text.count(old) != 1:
    raise SystemExit('definicao exata do trial principal inesperada')
if text.count(new) != 0:
    raise SystemExit('trial principal de 14 dias ja existe ou esta duplicado')

manual_demo_30_before = text.count('Demo 30 dias (Grátis)')
monthly_30_5_before = text.count("'30_5': { dias: 30, funcionarios: 5, preco: 29.99")

text = text.replace(old, new, 1)

if text.count(old) != 0 or text.count(new) != 1:
    raise SystemExit('substituicao do trial principal inesperada')
if text.count('Demo 30 dias (Grátis)') != manual_demo_30_before:
    raise SystemExit('uma demo manual de 30 dias foi alterada indevidamente')
if text.count("'30_5': { dias: 30, funcionarios: 5, preco: 29.99") != monthly_30_5_before:
    raise SystemExit('plano pago de 30 dias foi alterado indevidamente')

path.write_text(text, encoding='utf-8')
print('OK: trial principal = 14 dias; demo_30 mantido como identificador; demos manuais e planos pagos preservados.')
