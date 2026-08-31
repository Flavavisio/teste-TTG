from pathlib import Path
import re

text = Path('app.html').read_text(encoding='utf-8')
pattern = re.compile(r'(?m)^[ \t]*(?:async\s+)?function\s+([A-Za-z_$][\w$]*)\s*\([^\n]*?\)\s*\{')


def scan_end(brace):
    depth = 0
    quote = None
    escape = False
    line_comment = False
    block_comment = False
    i = brace
    while i < len(text):
        c = text[i]
        n = text[i+1] if i + 1 < len(text) else ''
        if line_comment:
            if c == '\n': line_comment = False
        elif block_comment:
            if c == '*' and n == '/': block_comment = False; i += 1
        elif quote:
            if escape: escape = False
            elif c == '\\': escape = True
            elif c == quote: quote = None
        else:
            if c == '/' and n == '/': line_comment = True; i += 1
            elif c == '/' and n == '*': block_comment = True; i += 1
            elif c in ('\"', "'", '`'): quote = c
            elif c == '{': depth += 1
            elif c == '}':
                depth -= 1
                if depth == 0: return i + 1
        i += 1
    raise RuntimeError('unclosed function')

rows = []
for m in pattern.finditer(text):
    brace = text.index('{', m.start(), m.end())
    try:
        end = scan_end(brace)
    except Exception:
        continue
    block = text[m.start():end]
    rows.append((len(block.splitlines()), len(block), m.group(1)))
rows.sort(reverse=True)
out = Path('.github/diagnostics/app-hotspots.txt')
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text('\n'.join(f'{lines:5d} {chars:7d} {name}' for lines, chars, name in rows[:40]) + '\n', encoding='utf-8')
print('functions:', len(rows))
for row in rows[:20]: print(*row)
