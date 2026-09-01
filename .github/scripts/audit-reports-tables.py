from pathlib import Path

text = Path('app.html').read_text(encoding='utf-8')
start = text.index('        function renderizarReports() {')
end = text.index('\n        function ', start + 1)
body = text[start:end]

markers = [
    ('super_summary', '                html += `<div class="report-card"><h4><i class="fas fa-chart-line"></i> Resumo por Empresa</h4>`;', '                // Licenças de Manutenção (módulo Contratos)'),
    ('distributor_summary', '                html += `<div class="report-card"><h4><i class="fas fa-chart-line"></i> Resumo por Cliente</h4>`;', '                container.innerHTML = html;\n                return;\n            }\n\n            if (!usuarioLogado'),
]

print(f'RENDERIZAR_REPORTS chars={len(body)} lines={body.count(chr(10))+1}')
for name, a, b in markers:
    print(f'{name}_start_count={body.count(a)} end_count={body.count(b)}')
    if body.count(a) == 1 and body.count(b) == 1:
        s = body.index(a)
        e = body.index(b, s)
        chunk = body[s:e]
        print(f'{name}_chars={len(chunk)} lines={chunk.count(chr(10))+1}')
        print(f'--- {name.upper()} ---')
        print(chunk)
        print(f'--- END {name.upper()} ---')

view = Path('assets/js/app-reports-view.js').read_text(encoding='utf-8')
print(f'REPORTS_VIEW chars={len(view)} lines={view.count(chr(10))+1}')
print(view)

assert body.count('window.TotalGestReportsView.moduleLicenseCard({') == 5
assert body.count('window.TotalGestReportsView.revenueBars({') == 1
assert body.count('const _kpi = window.TotalGestReportsView.kpi;') == 2
print('REPORT_TABLE_AUDIT_ASSERTIONS=OK')
