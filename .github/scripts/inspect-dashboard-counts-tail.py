from pathlib import Path

text = Path('app.html').read_text(encoding='utf-8')
fn = text.index('function atualizarContagens()')
start = text.index('            const licencasAtivas =', fn)
print(text[start:start + 18000])
