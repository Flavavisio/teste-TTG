from pathlib import Path

text = Path('app.html').read_text(encoding='utf-8')
start = text.index('        function renderizarAlertas() {')
end = text.index('\n        function ', start + 1)
body = text[start:end]
print(f'RENDERIZAR_ALERTAS chars={len(body)} lines={body.count(chr(10))+1}')
print('innerHTML=', body.count('innerHTML'))
print('report-card=', body.count('report-card'))
print('alert-card=', body.count('alert'))
print('--- BODY BEGIN ---')
print(body)
print('--- BODY END ---')
print('AUDIT_RENDERIZAR_ALERTAS=OK')
