from pathlib import Path
import re

text = Path('app.html').read_text(encoding='utf-8')
lines = text.splitlines()
pat = re.compile(r'^(\s*)(?:async\s+)?function\s+([A-Za-z_$][\w$]*)\s*\(')
decls = []
for i, line in enumerate(lines):
    m = pat.match(line)
    if m:
        decls.append((i, len(m.group(1).replace('\t', '    ')), m.group(2)))

def region(name):
    hits = [(i, indent) for i, indent, n in decls if n == name]
    assert len(hits) == 1, (name, hits)
    start, indent = hits[0]
    end = len(lines)
    for i, ind, n in decls:
        if i > start and ind <= indent:
            end = i
            break
    body_lines = lines[start:end]
    return '\n'.join(body_lines), start + 1, end

def describe(name):
    body, start, end = region(name)
    print(f'{name}: chars={len(body)} lines={body.count(chr(10))+1} span={start}-{end}')
    for needle in ['innerHTML', 'html +=', 'window.TotalGestReportsView.', 'window.TotalGestReportsSuperadminMetrics.', 'window.TotalGestReportsDistributorMetrics.', '<table', '<div class="report-card"', 'onclick=', 'addEventListener']:
        print(f'  {needle}={body.count(needle)}')
    templates = []
    i = 0
    while i < len(body):
        if body[i] != '`':
            i += 1
            continue
        start_i = i
        i += 1
        depth = 0
        escaped = False
        while i < len(body):
            ch = body[i]
            if escaped:
                escaped = False
            elif ch == '\\':
                escaped = True
            elif ch == '`' and depth == 0:
                i += 1
                templates.append(body[start_i:i])
                break
            elif ch == '$' and i + 1 < len(body) and body[i+1] == '{':
                depth += 1
                i += 1
            elif ch == '}' and depth:
                depth -= 1
            i += 1
        else:
            break
    ranked = sorted(templates, key=len, reverse=True)[:8]
    for idx, tpl in enumerate(ranked, 1):
        preview = ' '.join(tpl[:180].split())
        print(f'  template#{idx}: chars={len(tpl)} preview={preview}')
    print('--- BODY BEGIN ---')
    print(body)
    print('--- BODY END ---')

for target in ['renderizarReports', '_abrirModalRelatorioEspecialidade']:
    describe(target)

print('AUDIT_NEXT_REPORTS_HOTSPOT=OK')
