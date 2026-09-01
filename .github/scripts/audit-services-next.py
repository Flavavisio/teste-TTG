from pathlib import Path
text = Path('app.html').read_text(encoding='utf-8')
start = text.index('        function renderizarServicos() {')
end = text.index('\n        function ', start + 1)
block = text[start:end]
print(f'RENDERIZAR_SERVICOS chars={len(block)} lines={len(block.splitlines())}')
print(block)
