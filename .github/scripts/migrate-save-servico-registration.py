from pathlib import Path

text = Path('app.html').read_text(encoding='utf-8')
needle = 'gerarNumeroRegistoServidor'
positions = []
start = 0
while True:
    pos = text.find(needle, start)
    if pos == -1:
        break
    positions.append(pos)
    start = pos + len(needle)
print('ocorrencias', len(positions))
for pos in positions:
    print('\n--- contexto ---')
    print(text[max(0, pos - 500):pos + 500])
raise SystemExit(1)
