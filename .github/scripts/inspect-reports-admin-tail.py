from pathlib import Path
text=Path('app.html').read_text(encoding='utf-8')
start=text.index('function renderizarReports(')
pos=text.index('const _adminOperations = window.TotalGestReportsDistributorMetrics.calculateAdminOperations({', start)
print(text[pos:pos+18000])
