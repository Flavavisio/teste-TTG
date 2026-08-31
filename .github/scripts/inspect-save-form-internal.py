from pathlib import Path

text = Path('app.html').read_text(encoding='utf-8')
marker = 'function _salvarFormularioInterno('
assert text.count(marker) == 1, text.count(marker)
start = text.index(marker)
# Scan balanced braces from the function body.
brace = text.index('{', start)
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
        if c == '*' and n == '/':
            block_comment = False; i += 1
    elif quote:
        if escape:
            escape = False
        elif c == '\\':
            escape = True
        elif c == quote:
            quote = None
    else:
        if c == '/' and n == '/':
            line_comment = True; i += 1
        elif c == '/' and n == '*':
            block_comment = True; i += 1
        elif c in ('\"', "'", '`'):
            quote = c
        elif c == '{':
            depth += 1
        elif c == '}':
            depth -= 1
            if depth == 0:
                i += 1
                break
    i += 1
block = text[start:i]
out = Path('.github/diagnostics/save-form-internal.txt')
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(block, encoding='utf-8')
print('LINES', len(block.splitlines()), 'CHARS', len(block))
for token in [
    'TotalGestSaveFormDispatch',
    'TotalGestSaveFormPersist',
    'TotalGestSaveFormPostPersist',
    'TotalGestSaveFormFinalize',
    'TotalGestSaveFormAuth',
    'TotalGestSaveFormContactValidation',
    'TotalGestSaveFormServico.run({',
    'TotalGestSaveFormFolha.run({',
    'guardarDados(',
    'await '
]:
    print(token, block.count(token))
