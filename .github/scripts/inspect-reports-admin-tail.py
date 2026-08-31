from pathlib import Path
text=Path('app.html').read_text(encoding='utf-8')
pos=text.index('function atualizarContagens()')
print(text[pos:pos+24000])
