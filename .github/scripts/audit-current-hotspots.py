from pathlib import Path

text = Path('app.html').read_text(encoding='utf-8')
start = text.index('        function renderizarReports() {')
end = text.index('\n        function ', start + 1)
body = text[start:end]
print(f'RENDERIZAR_REPORTS chars={len(body)} lines={body.count(chr(10))+1}')
print('--- BODY BEGIN ---')
print(body)
print('--- BODY END ---')
print('AUDIT_RENDERIZAR_REPORTS=OK')
