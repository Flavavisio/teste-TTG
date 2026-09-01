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

rows = []
for pos, (start, indent, name) in enumerate(decls):
    end = len(lines)
    for i, ind, n in decls[pos + 1:]:
        if ind <= indent:
            end = i
            break
    body = '\n'.join(lines[start:end])
    rows.append((len(body), body.count('\n') + 1, name, start + 1, end, body.count('innerHTML'), body.count('<div'), body.count('addEventListener')))

for chars, nlines, name, start, end, inner, divs, listeners in sorted(rows, reverse=True)[:18]:
    print(f'{name}: chars={chars} lines={nlines} span={start}-{end} innerHTML={inner} divs={divs} listeners={listeners}')

for target in ['renderizarReports', '_abrirModalRelatorioEspecialidade', 'renderizarAlertas', 'renderizarMinhaLicenca', 'renderizarServicos']:
    hits = [row for row in rows if row[2] == target]
    if hits:
        row = hits[0]
        print(f'TARGET {target}: chars={row[0]} lines={row[1]}')

print('AUDIT_NEXT_APP_HOTSPOT=OK')
