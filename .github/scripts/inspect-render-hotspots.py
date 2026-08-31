from pathlib import Path

text = Path('app.html').read_text(encoding='utf-8')

def extract(name):
    markers = [f'function {name}(', f'async function {name}(']
    positions = [(text.find(m), m) for m in markers if text.find(m) >= 0]
    assert len(positions) == 1, (name, positions)
    start, marker = positions[0]
    brace = text.index('{', start)
    depth = 0
    mode = 'normal'
    escape = False
    return_modes = []
    template_depths = []
    i = brace
    while i < len(text):
        c = text[i]
        n = text[i+1] if i + 1 < len(text) else ''
        if mode == 'line_comment':
            if c == '\n': mode = return_modes.pop() if return_modes else 'normal'
        elif mode == 'block_comment':
            if c == '*' and n == '/': mode = return_modes.pop() if return_modes else 'normal'; i += 1
        elif mode in ('single','double'):
            if escape: escape = False
            elif c == '\\': escape = True
            elif (mode == 'single' and c == "'") or (mode == 'double' and c == '"'):
                mode = return_modes.pop() if return_modes else 'normal'
        elif mode == 'template':
            if escape: escape = False
            elif c == '\\': escape = True
            elif c == '`': mode = return_modes.pop() if return_modes else 'normal'
            elif c == '$' and n == '{':
                return_modes.append('template')
                mode = 'template_expr'
                template_depths.append(1)
                depth += 1
                i += 1
        else:
            current = mode
            if c == '/' and n == '/': return_modes.append(current); mode = 'line_comment'; i += 1
            elif c == '/' and n == '*': return_modes.append(current); mode = 'block_comment'; i += 1
            elif c == "'": return_modes.append(current); mode = 'single'
            elif c == '"': return_modes.append(current); mode = 'double'
            elif c == '`': return_modes.append(current); mode = 'template'
            elif c == '{':
                depth += 1
                if current == 'template_expr': template_depths[-1] += 1
            elif c == '}':
                depth -= 1
                if current == 'template_expr':
                    template_depths[-1] -= 1
                    if template_depths[-1] == 0:
                        template_depths.pop()
                        mode = return_modes.pop()
                elif depth == 0:
                    return text[start:i+1]
        i += 1
    raise RuntimeError(name)

outdir = Path('.github/diagnostics/render-hotspots')
outdir.mkdir(parents=True, exist_ok=True)
for name in ['renderizarHomeDashboard','renderizarOMeuDia','renderizarReports']:
    block = extract(name)
    (outdir / f'{name}.txt').write_text(block, encoding='utf-8')
    print(name, 'LINES', len(block.splitlines()), 'CHARS', len(block))
    for token in ['innerHTML', 'querySelector', 'getElementById', 'dados.', 'usuarioLogado', 'adminAtual()', 'localStorage', 'window.TotalGest', 'await ', 'supabase', 'fetch(']:
        print(' ', token, block.count(token))
