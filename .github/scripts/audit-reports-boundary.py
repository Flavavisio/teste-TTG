from pathlib import Path
import re

lines = Path('app.html').read_text(encoding='utf-8').splitlines()
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
    return start, end, indent

start, end, indent = region('renderizarReports')
body_lines = lines[start:end]
body = '\n'.join(body_lines)
print(f'RENDERIZAR_REPORTS lines={end-start} chars={len(body)} span={start+1}-{end} indent={indent}')
print('modules=' + ','.join(sorted(set(re.findall(r'window\.(TotalGest[A-Za-z0-9_]+)', body)))))
for needle in ['usuarioLogado.role', '.innerHTML', 'TotalGestReportsSuperadminMetrics', 'TotalGestReportsDistributorMetrics', 'TotalGestReportsModuleMetrics', 'return;', 'PLANOS[', 'dados.']:
    print(f'{needle}={body.count(needle)}')
print('--- BEGIN renderizarReports ---')
for line in body_lines:
    print(line)
print('--- END renderizarReports ---')
assert body.count('window.TotalGestReportsSuperadminMetrics') >= 1
assert body.count('window.TotalGestReportsDistributorMetrics') >= 1
assert body.count('window.TotalGestReportsModuleMetrics') >= 1
print('REPORTS_BOUNDARY_ASSERTIONS=OK')
