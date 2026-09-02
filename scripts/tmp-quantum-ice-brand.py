from pathlib import Path

OLD_BLUE='#243B8F'
OLD_LIGHT='#FFF0C9'
NEW_BLUE='#2457FF'
NEW_LIGHT='#DFF7FF'

files=[
    'assets/css/brand-theme.css',
    'assets/css/login.css',
    'assets/css/registar.css',
    'assets/css/redefinir-password.css',
    'confirmar-trial.html',
    'index.html',
    'app.html',
    'login.html',
    'registar.html',
    'redefinir-password.html',
]

for name in files:
    p=Path(name)
    text=p.read_text(encoding='utf-8')
    text=text.replace(OLD_BLUE,NEW_BLUE).replace(OLD_LIGHT,NEW_LIGHT)
    p.write_text(text,encoding='utf-8')

# Atualiza também nomes/comentário da identidade visual no tema.
p=Path('assets/css/brand-theme.css')
text=p.read_text(encoding='utf-8')
text=text.replace('tema de marca Blueberry + Cream Soda','tema de marca Quantum Blue + Ice Glass')
text=text.replace('Blueberry: #2457FF | Cream Soda: #DFF7FF','Quantum Blue: #2457FF | Ice Glass: #DFF7FF')
p.write_text(text,encoding='utf-8')

sw=Path('sw.js')
text=sw.read_text(encoding='utf-8')
assert "const CACHE = 'totalgest-v180';" in text
sw.write_text(text.replace("const CACHE = 'totalgest-v180';","const CACHE = 'totalgest-v181';",1),encoding='utf-8')

# Validações visuais e estruturais.
brand=Path('assets/css/brand-theme.css').read_text(encoding='utf-8')
assert NEW_BLUE in brand and NEW_LIGHT in brand
assert OLD_BLUE not in brand and OLD_LIGHT not in brand
for name in ['index.html','app.html']:
    t=Path(name).read_text(encoding='utf-8')
    assert 'assets/css/brand-theme.css' in t
    assert NEW_BLUE in t
for name in ['assets/css/login.css','assets/css/registar.css','assets/css/redefinir-password.css','confirmar-trial.html']:
    assert NEW_BLUE in Path(name).read_text(encoding='utf-8'), name
app=Path('app.html').read_text(encoding='utf-8')
assert 'bootstrapSupabase()' in app
for marker,delegate in [
    ('function renderizarServicos() {','createServicesAreaRendererFromDocument({'),
    ('function renderizarPonto() {','prepareAttendanceViewState({'),
    ('function renderizarAlertas() {','applyAlertsState('),
    ('function renderizarClientes() {','renderClientsArea({'),
    ('function renderizarFuncionarios() {','renderEmployeesArea({'),
    ('function renderizarEncarregados() {','renderManagersArea({'),
    ('function renderizarRequisicoes() {','renderRequisitionsArea({'),
    ('function renderizarArtigos() {','renderArticlesArea({'),
    ('function renderizarFornecedores() {','renderSuppliersArea({'),
    ('function renderizarObras() {','renderWorksArea({'),
    ('function renderizarFerramentas() {','renderToolsArea({')]:
    s=app.index(marker)
    assert delegate in app[s:s+9000], (marker,delegate)
assert "const CACHE = 'totalgest-v181';" in Path('sw.js').read_text(encoding='utf-8')
print('QUANTUM_ICE_BRAND=OK')
print('REFRACTOR_BOUNDARY=OK')
print('CACHE_V181=OK')
