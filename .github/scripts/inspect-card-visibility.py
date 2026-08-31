from pathlib import Path

text = Path('app.html').read_text(encoding='utf-8')
marker = 'function ajustarVisibilidadeCards()'
assert text.count(marker) == 1, text.count(marker)
start = text.index(marker)
brace = text.index('{', start)

def scan_end(text, brace):
    depth = 0
    mode = 'normal'
    escape = False
    template_expr_depth = 0
    return_modes = []
    i = brace
    while i < len(text):
        c = text[i]
        n = text[i+1] if i + 1 < len(text) else ''
        if mode == 'line_comment':
            if c == '\n': mode = 'normal'
        elif mode == 'block_comment':
            if c == '*' and n == '/': mode = 'normal'; i += 1
        elif mode in ('single', 'double'):
            if escape: escape = False
            elif c == '\\': escape = True
            elif (mode == 'single' and c == "'") or (mode == 'double' and c == '"'): mode = return_modes.pop() if return_modes else 'normal'
        elif mode == 'template':
            if escape: escape = False
            elif c == '\\': escape = True
            elif c == '`': mode = return_modes.pop() if return_modes else 'normal'
            elif c == '$' and n == '{':
                return_modes.append('template')
                mode = 'template_expr'
                template_expr_depth = 1
                depth += 1
                i += 1
        else:  # normal or template_expr
            current = mode
            if c == '/' and n == '/': mode = 'line_comment'; return_modes.append(current); i += 1
            elif c == '/' and n == '*': mode = 'block_comment'; return_modes.append(current); i += 1
            elif c == "'": return_modes.append(current); mode = 'single'
            elif c == '"': return_modes.append(current); mode = 'double'
            elif c == '`': return_modes.append(current); mode = 'template'
            elif c == '{':
                depth += 1
                if current == 'template_expr': template_expr_depth += 1
            elif c == '}':
                depth -= 1
                if current == 'template_expr':
                    template_expr_depth -= 1
                    if template_expr_depth == 0:
                        mode = return_modes.pop()
                elif depth == 0:
                    return i + 1
        if mode in ('line_comment','block_comment') and return_modes and return_modes[-1] in ('normal','template_expr'):
            # comments resume the previous JS mode
            pass
        # special resume handling for comments
        if mode == 'line_comment' and c == '\n':
            mode = return_modes.pop() if return_modes else 'normal'
        i += 1
    raise RuntimeError('unclosed')

end = scan_end(text, brace)
block = text[start:end]
out = Path('.github/diagnostics/card-visibility.txt')
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(block, encoding='utf-8')
print('LINES', len(block.splitlines()), 'CHARS', len(block))
for token in ['querySelectorAll', 'getElementById', 'style.display', 'classList', 'usuarioLogado', 'adminAtual()', 'dados.', 'localStorage', 'TotalGest']:
    print(token, block.count(token))
