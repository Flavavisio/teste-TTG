from pathlib import Path

INDEX_JS = Path('assets/js/index.js')
APP_UI = Path('assets/js/app-ui.js')
SW = Path('sw.js')
THEME = Path('assets/css/brand-theme.css')

index_js = INDEX_JS.read_text(encoding='utf-8')
app_ui = APP_UI.read_text(encoding='utf-8')
sw = SW.read_text(encoding='utf-8')
theme = THEME.read_text(encoding='utf-8')

assert '#243B8F' in theme and '#FFF0C9' in theme
assert 'data-tg-brand-theme' not in index_js
assert 'data-tg-brand-theme' not in app_ui

loader = """  function carregarTemaMarca() {\n    if (document.querySelector('link[data-tg-brand-theme]')) return;\n    const link = document.createElement('link');\n    link.rel = 'stylesheet';\n    link.href = './assets/css/brand-theme.css';\n    link.dataset.tgBrandTheme = '1';\n    document.head.appendChild(link);\n    const meta = document.querySelector('meta[name=\"theme-color\"]');\n    if (meta) meta.setAttribute('content', '#243B8F');\n  }\n\n"""

# Landing: inserir imediatamente após o strict e ativar antes do resto do comportamento.
index_anchor = "  'use strict';\n\n"
assert index_js.count(index_anchor) == 1
index_js = index_js.replace(index_anchor, index_anchor + loader + '  carregarTemaMarca();\n\n', 1)

# App: mesma responsabilidade visual dentro do módulo de UI.
ui_anchor = "  'use strict';\n\n"
assert app_ui.count(ui_anchor) == 1
app_ui = app_ui.replace(ui_anchor, ui_anchor + loader, 1)
ui_call_anchor = '  // O módulo é carregado no fim do body, quando os clones do logótipo já existem.\n  aplicarBranding();'
assert app_ui.count(ui_call_anchor) == 1
app_ui = app_ui.replace(ui_call_anchor, '  // O módulo é carregado no fim do body, quando os clones do logótipo já existem.\n  carregarTemaMarca();\n  aplicarBranding();', 1)

# PWA: cachear a folha e invalidar a cache anterior.
assert sw.count("const CACHE = 'totalgest-v121';") == 1
assert "'./assets/css/brand-theme.css'," not in sw
asset_anchor = "  './assets/css/app.css',\n"
assert sw.count(asset_anchor) == 1
sw = sw.replace(asset_anchor, asset_anchor + "  './assets/css/brand-theme.css',\n", 1)
sw = sw.replace("const CACHE = 'totalgest-v121';", "const CACHE = 'totalgest-v122';", 1)

# Assertions estruturais.
assert index_js.count("link.href = './assets/css/brand-theme.css';") == 1
assert app_ui.count("link.href = './assets/css/brand-theme.css';") == 1
assert index_js.count("meta.setAttribute('content', '#243B8F')") == 1
assert app_ui.count("meta.setAttribute('content', '#243B8F')") == 1
assert sw.count("'./assets/css/brand-theme.css',") == 1
assert sw.count("const CACHE = 'totalgest-v122';") == 1

INDEX_JS.write_text(index_js, encoding='utf-8')
APP_UI.write_text(app_ui, encoding='utf-8')
SW.write_text(sw, encoding='utf-8')
print('BRAND_THEME_MIGRATION=OK')
