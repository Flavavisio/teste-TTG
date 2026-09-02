from pathlib import Path

BLUE='#243B8F'; CREAM='#FFF0C9'

# Protect extracted domain orchestrators byte-for-byte.
app_path=Path('app.html')
app=app_path.read_text(encoding='utf-8')
def block(text, marker):
    s=text.index(marker); starts=[]
    for pat in ['\n        function ','\n        async function ']:
        p=text.find(pat,s+len(marker))
        if p!=-1: starts.append(p)
    return text[s:min(starts)]
markers=[
'        function renderizarServicos() {','        function renderizarPonto() {','        function renderizarAlertas() {',
'        function renderizarClientes() {','        function renderizarFuncionarios() {','        function renderizarEncarregados() {',
'        function renderizarRequisicoes() {','        function renderizarArtigos() {','        function renderizarFornecedores() {',
'        function renderizarObras() {','        function renderizarFerramentas() {'
]
protected={m:block(app,m) for m in markers}

# Landing: activate brand theme last and update browser/PWA theme colour.
idx=Path('index.html').read_text(encoding='utf-8')
idx=idx.replace('<meta name="theme-color" content="#152a52" />',f'<meta name="theme-color" content="{BLUE}" />',1)
if 'assets/css/brand-theme.css' not in idx:
    idx=idx.replace('  <link rel="stylesheet" href="assets/css/social-proof.css" />','  <link rel="stylesheet" href="assets/css/social-proof.css" />\n  <link rel="stylesheet" href="assets/css/brand-theme.css" />',1)
Path('index.html').write_text(idx,encoding='utf-8')

# Application: brand-theme must load after legacy styles.css.
app=app.replace('<meta name="theme-color" content="#152a52" />',f'<meta name="theme-color" content="{BLUE}" />',1)
if 'assets/css/brand-theme.css' not in app:
    app=app.replace('    <link rel="stylesheet" href="styles.css" />','    <link rel="stylesheet" href="styles.css" />\n    <link rel="stylesheet" href="assets/css/brand-theme.css" />',1)
app_path.write_text(app,encoding='utf-8')

# Login page + CSS.
login=Path('login.html').read_text(encoding='utf-8')
if 'name="theme-color"' not in login:
    login=login.replace('  <meta name="robots" content="noindex" />',f'  <meta name="robots" content="noindex" />\n  <meta name="theme-color" content="{BLUE}" />',1)
Path('login.html').write_text(login,encoding='utf-8')
lcss=Path('assets/css/login.css').read_text(encoding='utf-8')
lcss=lcss.replace('#152a52',BLUE).replace('#0b3b5c',BLUE).replace('#0b1a2c',BLUE).replace('#f4520e',BLUE).replace('#ff7a18',BLUE).replace('#fed7aa','#eadcae').replace('#fff7ed','#fffaf0').replace('#9a3412',BLUE).replace('#7c2d12','#4f4a38').replace('#b93800',BLUE)
Path('assets/css/login.css').write_text(lcss,encoding='utf-8')

# Registration page + CSS.
reg=Path('registar.html').read_text(encoding='utf-8').replace('<meta name="theme-color" content="#152a52" />',f'<meta name="theme-color" content="{BLUE}" />',1)
Path('registar.html').write_text(reg,encoding='utf-8')
rcss=Path('assets/css/registar.css').read_text(encoding='utf-8')
for old in ['#0b1a2c','#152a52','#f4520e','#ff7a18','#0b3b5c','#b93800']:
    rcss=rcss.replace(old,BLUE)
rcss=rcss.replace('#ffd8c2','#eadcae').replace('#fff3eb',CREAM).replace('rgba(255,122,24,.16)','rgba(255,240,201,.75)').replace('rgba(244,82,14,.1)','rgba(36,59,143,.1)').replace('rgba(244,82,14,.18)','rgba(36,59,143,.18)')
Path('assets/css/registar.css').write_text(rcss,encoding='utf-8')

# Password reset.
rp=Path('redefinir-password.html').read_text(encoding='utf-8')
if 'name="theme-color"' not in rp:
    rp=rp.replace('<meta name="viewport" content="width=device-width, initial-scale=1.0" />',f'<meta name="viewport" content="width=device-width, initial-scale=1.0" />\n<meta name="theme-color" content="{BLUE}" />',1)
Path('redefinir-password.html').write_text(rp,encoding='utf-8')
rpcss=Path('assets/css/redefinir-password.css').read_text(encoding='utf-8')
rpcss=rpcss.replace('#0b3b5c',BLUE).replace('#152a52',BLUE).replace('#0b1a2c',BLUE).replace('#f4520e',BLUE).replace('#ff7a18',BLUE)
Path('assets/css/redefinir-password.css').write_text(rpcss,encoding='utf-8')

# Trial confirmation inline styling.
ct=Path('confirmar-trial.html').read_text(encoding='utf-8')
if 'name="theme-color"' not in ct:
    ct=ct.replace('<meta name="robots" content="noindex" />',f'<meta name="robots" content="noindex" />\n<meta name="theme-color" content="{BLUE}" />',1)
ct=ct.replace('#f4520e',BLUE)
Path('confirmar-trial.html').write_text(ct,encoding='utf-8')

# Cache bust for visible UI change.
sw=Path('sw.js').read_text(encoding='utf-8').replace("const CACHE = 'totalgest-v179';","const CACHE = 'totalgest-v180';",1)
Path('sw.js').write_text(sw,encoding='utf-8')

# Validation.
app2=app_path.read_text(encoding='utf-8')
for m,b in protected.items(): assert block(app2,m)==b,m
assert idx.count('assets/css/brand-theme.css')==1
assert app2.count('assets/css/brand-theme.css')==1
assert BLUE in idx and BLUE in app2
assert "const CACHE = 'totalgest-v180';" in Path('sw.js').read_text(encoding='utf-8')
for f in ['assets/css/login.css','assets/css/registar.css','assets/css/redefinir-password.css','confirmar-trial.html']:
    t=Path(f).read_text(encoding='utf-8'); assert BLUE in t,f
print('BRAND_GLOBAL_APPLY=OK')
print('PROTECTED_DOMAIN_BLOCKS=OK')
print('CACHE_V180=OK')
