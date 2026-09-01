from pathlib import Path

text = Path('app.html').read_text(encoding='utf-8')
start = text.index('        function renderizarMinhaLicenca() {')
end = text.index('\n        function ', start + 1)
block = text[start:end]
lines = block.splitlines()

print(f'RENDERIZAR_MINHA_LICENCA chars={len(block)} lines={len(lines)}')
print('DELEGATIONS')
for needle in [
    'window.TotalGestLicenseAddons.renderAddon({',
    'container.innerHTML',
    'innerHTML =',
    'onclick=',
    'addEventListener',
    'PLANOS',
    'moduloContratosAtivo',
    'moduloFrotaAtivo',
    'moduloArmazemAtivo',
    'moduloCrmAtivo',
    'bootstrapSupabase()',
    'supabase.auth'
]:
    print(needle, block.count(needle))

print('--- FUNCTION START ---')
for i, line in enumerate(lines, 1):
    print(f'{i:03d}: {line}')
print('--- FUNCTION END ---')
