from pathlib import Path
import re

text = Path('app.html').read_text(encoding='utf-8')

# Extrator conservador de funções nomeadas: ignora chavetas em strings, comentários e templates.
def extract_at(start):
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
        n = text[i + 1] if i + 1 < len(text) else ''
        if mode == 'code':
            if c in ('"', "'"):
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
                    return i + 1
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
            if c == '\n':
                mode = 'code'
        elif mode == 'block_comment':
            if c == '*' and n == '/':
                mode = 'code'; i += 1
        i += 1
    return None

rows = []
seen = set()
for match in re.finditer(r'(?m)^\s*(?:async\s+)?function\s+([A-Za-z_$][\w$]*)\s*\(', text):
    name = match.group(1)
    start = match.start()
    end = extract_at(start)
    if end is None or (name, start) in seen:
        continue
    seen.add((name, start))
    body = text[start:end]
    start_line = text.count('\n', 0, start) + 1
    end_line = text.count('\n', 0, end) + 1
    modules = sorted(set(re.findall(r'window\.(TotalGest[A-Za-z0-9_]+)', body)))
    rows.append({
        'name': name,
        'chars': len(body),
        'lines': end_line - start_line + 1,
        'start': start_line,
        'end': end_line,
        'inner': body.count('.innerHTML'),
        'templates': body.count('`') // 2,
        'awaits': body.count('await '),
        'dados': body.count('dados.'),
        'supabase': body.count('supabase'),
        'storage': body.count('localStorage'),
        'user': body.count('usuarioLogado'),
        'modules': modules,
    })

rows.sort(key=lambda x: (x['chars'], x['lines']), reverse=True)
print(f'NAMED_FUNCTIONS={len(rows)}')
print('TOP_30_BY_CHARS')
for rank, r in enumerate(rows[:30], 1):
    mods = ','.join(r['modules']) if r['modules'] else '-'
    print(
        f"{rank:02d} {r['name']} chars={r['chars']} lines={r['lines']} span={r['start']}-{r['end']} "
        f"innerHTML={r['inner']} templates~={r['templates']} awaits={r['awaits']} dados.={r['dados']} "
        f"supabase={r['supabase']} localStorage={r['storage']} usuarioLogado={r['user']} modules={mods}"
    )

# Guardas para sabermos que o parser encontrou pontos já conhecidos corretamente.
by_name = {r['name']: r for r in rows}
for required in ['renderizarMinhaLicenca', 'renderizarDashboardAnalitico', 'renderizarAuditoria']:
    assert required in by_name, required
assert text.count('window.TotalGestLicenseAddons.renderAddon({') == 4
assert text.count('window.TotalGestDashboardAnalyticsMetrics.calculate({') == 1
print('GLOBAL_AUDIT_ASSERTIONS=OK')
