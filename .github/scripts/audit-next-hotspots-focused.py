from pathlib import Path
import re

text = Path('app.html').read_text(encoding='utf-8')

def extract_function(name):
    marker = f'function {name}('
    start = text.find(marker)
    if start < 0:
        return None
    brace = text.find('{', start)
    if brace < 0:
        return None
    i = brace + 1
    depth = 1
    mode = 'code'
    quote = None
    template_expr_depth = 0
    while i < len(text):
        c = text[i]
        n = text[i+1] if i + 1 < len(text) else ''
        if mode == 'code':
            if c in ('\"', "'"):
                mode = 'string'; quote = c
            elif c == '`':
                mode = 'template'
            elif c == '/' and n == '/':
                mode = 'line_comment'; i += 1
            elif c == '/' and n == '*':
                mode = 'block_comment'; i += 1
            elif c == '{':
                depth += 1
            elif c == '}':
                depth -= 1
                if depth == 0:
                    return start, i + 1, text[start:i+1]
        elif mode == 'string':
            if c == '\\':
                i += 1
            elif c == quote:
                mode = 'code'
        elif mode == 'template':
            if c == '\\':
                i += 1
            elif c == '`' and template_expr_depth == 0:
                mode = 'code'
            elif c == '$' and n == '{':
                template_expr_depth += 1; i += 1
            elif c == '}' and template_expr_depth:
                template_expr_depth -= 1
        elif mode == 'line_comment':
            if c == '\n': mode = 'code'
        elif mode == 'block_comment':
            if c == '*' and n == '/': mode = 'code'; i += 1
        i += 1
    raise RuntimeError(f'unclosed function: {name}')

names = ['renderizarAuditoria', 'renderizarMinhaLicenca', 'renderizarDashboardAnalitico']
for name in names:
    item = extract_function(name)
    if not item:
        print(f'FUNCTION {name}: missing')
        continue
    start, end, body = item
    start_line = text.count('\n', 0, start) + 1
    end_line = text.count('\n', 0, end) + 1
    calls = sorted(set(re.findall(r'window\.(TotalGest[A-Za-z0-9_]+)', body)))
    templates = len(re.findall(r'`', body)) // 2
    inner = body.count('.innerHTML')
    awaits = body.count('await ')
    print(f'FUNCTION {name}: lines={end_line-start_line+1} span={start_line}-{end_line} chars={len(body)} innerHTML={inner} templates~={templates} awaits={awaits}')
    print('  modules=' + (','.join(calls) if calls else '-'))
    for needle in ['dados.', '_tenantId(', 'obterNomeCliente(', 'calcularHoras(', 'localStorage', 'supabase', 'bootstrapSupabase(', 'usuarioLogado']:
        print(f'  {needle}={body.count(needle)}')
    print('  head=' + re.sub(r'\s+', ' ', body[:240]))

assert text.count('function renderizarAuditoria()') == 1
assert text.count('function renderizarMinhaLicenca()') == 1
assert text.count('function renderizarDashboardAnalitico()') == 1
assert text.count('window.TotalGestDashboardAnalyticsMetrics.calculate({') == 1
print('STRUCTURAL_ASSERTIONS=OK')

item = extract_function('renderizarMinhaLicenca')
assert item is not None
print('--- BEGIN renderizarMinhaLicenca ---')
print(item[2])
print('--- END renderizarMinhaLicenca ---')
