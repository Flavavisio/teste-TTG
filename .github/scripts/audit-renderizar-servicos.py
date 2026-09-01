from pathlib import Path

text = Path('app.html').read_text(encoding='utf-8')
start = text.index('        function renderizarServicos() {')
end = text.index('\n        function ', start + 1)
block = text[start:end]
lines = block.splitlines()
print(f'RENDERIZAR_SERVICOS chars={len(block)} lines={len(lines)}')
print('--- FIRST 90 LINES ---')
for i, line in enumerate(lines[:90], 1):
    print(f'{i:03d}: {line}')
print('--- COUNTS ---')
for needle in [
    "usuarioLogado.role === 'admin'",
    "usuarioLogado.role === 'subadmin'",
    "usuarioLogado.role === 'encarregado'",
    "usuarioLogado.role === 'funcionario'",
    "usuarioLogado?.role === 'superadmin'",
    '_aplicarFiltroOrdenacao(',
    '_toolbarHtml(',
    'tbody.innerHTML = servicos.map(',
    'faturarOSViaTOConline(',
    'faturarOSViaMoloni(',
    '_verificarPagamentoMoloni(',
    'emitirGuiaTransporteMoloni(',
    'emitirNotaCreditoMoloni('
]:
    print(needle, block.count(needle))
