from pathlib import Path

APP = Path('app.html')
SW = Path('sw.js')

app = APP.read_text(encoding='utf-8')
sw = SW.read_text(encoding='utf-8')

bad = "            if (!usuarioLogado                container.innerHTML = html;\n                return;\n            }\n\n"
proper = "            if (!usuarioLogado || usuarioLogado.role !== 'admin' && usuarioLogado.role !== 'subadmin') {"

def reports_region(text):
    start = text.index('        function renderizarReports() {')
    end = text.index('\n        function ', start + 1)
    return text[start:end]

before = reports_region(app)
assert before.count(bad) == 1, before.count(bad)
assert before.count(proper) == 1, before.count(proper)
assert app.count('function renderizarReports()') == 1
assert app.count('bootstrapSupabase()') >= 1

auth_count = app.count('supabase.auth')
bootstrap_count = app.count('bootstrapSupabase()')

app = app.replace(bad, '', 1)
after = reports_region(app)

assert bad not in after
assert after.count(proper) == 1
assert app.count('function renderizarReports()') == 1
assert app.count('supabase.auth') == auth_count
assert app.count('bootstrapSupabase()') == bootstrap_count

assert sw.count("const CACHE = 'totalgest-v115';") == 1
sw = sw.replace("const CACHE = 'totalgest-v115';", "const CACHE = 'totalgest-v116';", 1)
assert sw.count("const CACHE = 'totalgest-v116';") == 1

APP.write_text(app, encoding='utf-8')
SW.write_text(sw, encoding='utf-8')
print('REPORTS_ACCESS_GUARD_HOTFIX=OK')
