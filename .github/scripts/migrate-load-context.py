from pathlib import Path

APP=Path('app.html'); SHELL=Path('assets/js/app-shell.js'); SW=Path('sw.js'); MOD=Path('assets/js/app-load-context.js')
app=APP.read_text(encoding='utf-8'); shell=SHELL.read_text(encoding='utf-8'); sw=SW.read_text(encoding='utf-8')
old="""            let tenantId = tenantIdParam;
            let ehSuperAdmin = superAdminParam;
            let clienteId = clienteIdParam;
            if (tenantId === undefined) {
                if (usuarioLogado) {
                    ehSuperAdmin = usuarioLogado.role === 'superadmin';
                    tenantId = ehSuperAdmin ? null : (usuarioLogado.role === 'admin' ? usuarioLogado.id : usuarioLogado.adminId);
                    clienteId = usuarioLogado.role === 'cliente' ? usuarioLogado.id : null;
                } else {
                    tenantId = null; ehSuperAdmin = true;
                }
            }
"""
new="""            const loadContext = window.TotalGestLoadContext.resolve({
                tenantIdParam: tenantIdParam,
                superAdminParam: superAdminParam,
                clienteIdParam: clienteIdParam,
                user: usuarioLogado
            });
            let tenantId = loadContext.tenantId;
            let ehSuperAdmin = loadContext.superAdmin;
            let clienteId = loadContext.clienteId;
"""
assert app.count(old)==1, app.count(old)
app=app.replace(old,new,1)
assert app.count('periodLoading: true')==1
app=app.replace('periodLoading: true','periodLoading: true, loadContext: true',1)
MOD.write_text("""/* Total Gest — resolução do contexto de carregamento\n * Determina tenant, superadmin e cliente sem efetuar chamadas de rede.\n */\n(function () {\n  'use strict';\n\n  function resolve(options) {\n    const opts = options || {};\n    let tenantId = opts.tenantIdParam;\n    let superAdmin = opts.superAdminParam;\n    let clienteId = opts.clienteIdParam;\n    const user = opts.user;\n\n    if (tenantId === undefined) {\n      if (user) {\n        superAdmin = user.role === 'superadmin';\n        tenantId = superAdmin ? null : (user.role === 'admin' ? user.id : user.adminId);\n        clienteId = user.role === 'cliente' ? user.id : null;\n      } else {\n        tenantId = null;\n        superAdmin = true;\n      }\n    }\n\n    return { tenantId: tenantId, superAdmin: superAdmin, clienteId: clienteId };\n  }\n\n  window.TotalGestLoadContext = { resolve: resolve };\n})();\n""",encoding='utf-8')
needle="    periodLoading: './assets/js/app-period-loading.js',\n"; assert shell.count(needle)==1
shell=shell.replace(needle,needle+"    loadContext: './assets/js/app-load-context.js',\n",1)
needle="    if (options.periodLoading === true) pedidos.push(MODULOS.periodLoading);\n"; assert shell.count(needle)==1
shell=shell.replace(needle,needle+"    if (options.loadContext === true) pedidos.push(MODULOS.loadContext);\n",1)
assert "const CACHE = 'totalgest-v37';" in sw
sw=sw.replace("const CACHE = 'totalgest-v37';","const CACHE = 'totalgest-v38';",1)
needle="  './assets/js/app-period-loading.js',\n"; assert sw.count(needle)==1
sw=sw.replace(needle,needle+"  './assets/js/app-load-context.js',\n",1)
for token in ['window.TotalGestLoadContext.resolve({','loadContext: true']:
    assert app.count(token)==1,(token,app.count(token))
APP.write_text(app,encoding='utf-8'); SHELL.write_text(shell,encoding='utf-8'); SW.write_text(sw,encoding='utf-8')
