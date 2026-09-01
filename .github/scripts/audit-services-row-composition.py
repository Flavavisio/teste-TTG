from pathlib import Path
text=Path('app.html').read_text(encoding='utf-8')
s=text.index('        function renderizarServicos() {'); e=text.index('\n        function ',s+1); b=text[s:e]
print(f'RENDERIZAR_SERVICOS chars={len(b)} lines={len(b.splitlines())}')
for token in ['rowLeadingCells({','primaryRowActions({','erpRowActions({',"excluirEntidade('servico'",'tbody.innerHTML = servicos.map(']: print(token,b.count(token))
print('--- TAIL ---')
print('\n'.join(b.splitlines()[-85:]))
