from pathlib import Path

text = Path('app.html').read_text(encoding='utf-8')
start = text.index('        function renderizarServicos() {')
end = text.index('\n        function ', start + 1)
block = text[start:end]
lines = block.splitlines()
print(f'RENDERIZAR_SERVICOS chars={len(block)} lines={len(lines)}')
row_start = next(i for i, line in enumerate(lines) if 'tbody.innerHTML = servicos.map(s =>' in line)
print('--- ROW BLOCK FROM MAP ---')
for i, line in enumerate(lines[row_start:], row_start + 1):
    print(f'{i:03d}: {line}')
print('--- COUNTS ---')
for needle in [
    'statusBadge(',
    'alterarStatusOS(',
    'faturarOSViaTOConline(',
    'faturarOSViaMoloni(',
    '_verificarPagamentoMoloni(',
    'emitirGuiaTransporteMoloni(',
    'emitirNotaCreditoMoloni(',
    'abrirModalServico(',
    'eliminarServico(',
    'abrirModalFolha(',
    '_tiposEspecialidadePendentes(',
    'obterNomeCliente(',
    'podeEditar'
]:
    print(needle, block.count(needle))
