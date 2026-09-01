from pathlib import Path

text = Path('app.html').read_text(encoding='utf-8')

def get_function(name):
    marker = f'        function {name}() {{'
    start = text.index(marker)
    end = text.index('\n        function ', start + 1)
    return text[start:end]

for name in ['renderizarMinhaLicenca', 'renderizarAlertas', 'renderizarServicos']:
    block = get_function(name)
    lines = block.splitlines()
    print(f'=== {name} chars={len(block)} lines={len(lines)} ===')
    for i, line in enumerate(lines, 1):
        print(f'{i:03d}: {line}')
    print()
