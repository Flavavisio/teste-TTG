from pathlib import Path
text = Path('app.html').read_text(encoding='utf-8')
for name in ['renderizarReports','renderizarServicos']:
    marker = f'        function {name}() {{'
    start = text.index(marker)
    end = text.index('\n        function ', start + 1)
    block = text[start:end]
    print(f'===== {name} chars={len(block)} lines={len(block.splitlines())} =====')
    for i, line in enumerate(block.splitlines(), 1):
        print(f'{i:03d}: {line}')
