from pathlib import Path
import re

lines = Path('app.html').read_text(encoding='utf-8').splitlines()
pat = re.compile(r'^(\s*)(?:async\s+)?function\s+([A-Za-z_$][\w$]*)\s*\(')
decls = []
for i, line in enumerate(lines):
    m = pat.match(line)
    if m:
        decls.append((i, len(m.group(1).replace('\t', '    ')), m.group(2), m.group(1)))

rows = []
for pos, (start, indent, name, prefix) in enumerate(decls):
    end = len(lines)
    for nxt_start, nxt_indent, nxt_name, _ in decls[pos + 1:]:
        if nxt_indent <= indent:
            end = nxt_start
            break
    body_lines = lines[start:end]
    body = '\n'.join(body_lines)
    rows.append({
        'name': name,
        'start': start + 1,
        'end': end,
        'lines': end - start,
        'chars': len(body),
        'indent': indent,
        'inner': body.count('.innerHTML'),
        'templates': body.count('`') // 2,
        'awaits': body.count('await '),
        'dados': body.count('dados.'),
        'user': body.count('usuarioLogado'),
        'modules': sorted(set(re.findall(r'window\.(TotalGest[A-Za-z0-9_]+)', body))),
    })

# Os globais do app usam a indentação predominante das funções conhecidas.
known = {r['name']: r for r in rows}
for required in ['renderizarMinhaLicenca', 'renderizarDashboardAnalitico', 'renderizarAuditoria', 'renderizarServicos']:
    assert required in known, required
base_indent = known['renderizarMinhaLicenca']['indent']
main = [r for r in rows if r['indent'] == base_indent]
main.sort(key=lambda r: (r['chars'], r['lines']), reverse=True)
print(f'DECLARATIONS={len(rows)} MAIN_INDENT={base_indent} MAIN_FUNCTIONS={len(main)}')
print('TOP_30_MAIN_BY_CHARS')
for rank, r in enumerate(main[:30], 1):
    mods = ','.join(r['modules']) if r['modules'] else '-'
    print(f"{rank:02d} {r['name']} chars={r['chars']} lines={r['lines']} span={r['start']}-{r['end']} innerHTML={r['inner']} templates~={r['templates']} awaits={r['awaits']} dados.={r['dados']} usuarioLogado={r['user']} modules={mods}")

r = known['renderizarServicos']
print('RENDERIZAR_SERVICOS_SUMMARY', r)
start = r['start'] - 1
end = r['end']
body_lines = lines[start:end]
print('RENDERIZAR_SERVICOS_HEAD')
for line in body_lines[:120]:
    print(line)
print('RENDERIZAR_SERVICOS_NESTED_DECLARATIONS')
for idx in range(start + 1, end):
    m = pat.match(lines[idx])
    if m and len(m.group(1).replace('\t', '    ')) > r['indent']:
        print(f"line={idx+1} indent={len(m.group(1).replace(chr(9), '    '))} name={m.group(2)}")
print('LEXICAL_AUDIT_ASSERTIONS=OK')
