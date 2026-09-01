from pathlib import Path
import re

text = Path('app.html').read_text(encoding='utf-8')
lines = text.splitlines(True)
pattern = re.compile(r'^(\s*)function\s+([A-Za-z_$][\w$]*)\s*\(')
items = []
for i, line in enumerate(lines):
    m = pattern.match(line)
    if not m:
        continue
    indent = len(m.group(1))
    name = m.group(2)
    end = len(lines)
    for j in range(i + 1, len(lines)):
        n = pattern.match(lines[j])
        if n and len(n.group(1)) <= indent:
            end = j
            break
    body = ''.join(lines[i:end])
    items.append((len(body), end - i, name, i + 1))

for chars, count, name, line in sorted(items, reverse=True)[:20]:
    print(f'{name}\tchars={chars}\tlines={count}\tline={line}')
print('AUDIT_CURRENT_HOTSPOTS=OK')
