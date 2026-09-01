from pathlib import Path

# 1) Extend the existing services selection/data-preparation module.
module_path = Path('assets/js/app-services-selection.js')
module = module_path.read_text(encoding='utf-8')
assert 'function prepareServiceRow(' not in module
marker = "  window.TotalGestServicesSelection = {\n"
assert module.count(marker) == 1
helper = """  function prepareServiceRow(options) {
    options = options || {};
    const service = options.service || {};
    const getEmployeeName = typeof options.getEmployeeName === 'function' ? options.getEmployeeName : function (id) { return id || ''; };
    const getClientName = typeof options.getClientName === 'function' ? options.getClientName : function (id) { return id || ''; };
    const generateNumber = typeof options.generateNumber === 'function' ? options.generateNumber : function () { return ''; };
    const hasMaterials = typeof options.hasMaterials === 'function' ? options.hasMaterials : function () { return false; };
    const isErpActive = typeof options.isErpActive === 'function' ? options.isErpActive : function () { return false; };
    const administrators = Array.isArray(options.administrators) ? options.administrators : [];
    const employeeIds = assignedIds(service);
    const administrator = administrators.find(item => item.id === service.adminId);

    return {
      employeeName: employeeIds.length ? employeeIds.map(getEmployeeName).join('<br>') : 'Todos',
      clientName: getClientName(service.clienteId),
      number: service.numeroRegisto || generateNumber(),
      hasMaterials: hasMaterials(service.id),
      erpActive: isErpActive(administrator),
      provider: administrator?.integracaoFaturacao?.provider || ''
    };
  }

"""
module = module.replace(marker, helper + marker, 1)
old_export = "    selectVisibleServices: selectVisibleServices,\n    selectPendingSpecialtyServices: selectPendingSpecialtyServices\n"
new_export = "    selectVisibleServices: selectVisibleServices,\n    selectPendingSpecialtyServices: selectPendingSpecialtyServices,\n    prepareServiceRow: prepareServiceRow\n"
assert module.count(old_export) == 1
module = module.replace(old_export, new_export, 1)
module_path.write_text(module, encoding='utf-8')

# 2) Migrate only the row data derivation inside renderizarServicos().
app_path = Path('app.html')
text = app_path.read_text(encoding='utf-8')
start = text.index('        function renderizarServicos() {')
end = text.index('\n        function ', start + 1)
body = text[start:end]
old_counts = {token: text.count(token) for token in ['bootstrapSupabase()', 'supabase.auth']}
old_derivation = """                const _idsAtribOS = (s.funcionariosIds && s.funcionariosIds.length) ? s.funcionariosIds : (s.funcionarioId ? [s.funcionarioId] : []);
                const nomeFunc = _idsAtribOS.length ? _idsAtribOS.map(id => obterNomeFuncionario(id)).join('<br>') : 'Todos';
                const numero = s.numeroRegisto || gerarNumeroRegisto();
                const _temMateriaisOS = _osTemMateriais(s.id);
"""
assert body.count(old_derivation) == 1
new_derivation = """                const rowData = window.TotalGestServicesSelection.prepareServiceRow({
                    service: s,
                    administrators: dados.administradores || [],
                    getEmployeeName: obterNomeFuncionario,
                    getClientName: obterNomeCliente,
                    generateNumber: gerarNumeroRegisto,
                    hasMaterials: _osTemMateriais,
                    isErpActive: moduloErpAtivo
                });
"""
body2 = body.replace(old_derivation, new_derivation, 1)
replacements = {
    'number: numero,': 'number: rowData.number,',
    'hasMaterials: _temMateriaisOS,': 'hasMaterials: rowData.hasMaterials,',
    'clientName: obterNomeCliente(s.clienteId),': 'clientName: rowData.clientName,',
    'employeeName: nomeFunc,': 'employeeName: rowData.employeeName,',
    "erpActive: moduloErpAtivo(dados.administradores?.find(a => a.id === s.adminId)),": 'erpActive: rowData.erpActive,',
    "provider: dados.administradores?.find(a => a.id === s.adminId)?.integracaoFaturacao?.provider || '',": 'provider: rowData.provider,'
}
for old, new in replacements.items():
    assert body2.count(old) == 1, (old, body2.count(old))
    body2 = body2.replace(old, new, 1)

assert body2.count('prepareServiceRow({') == 1
for token in ['_idsAtribOS', 'nomeFunc', 'const numero =', '_temMateriaisOS']:
    assert token not in body2, token
assert body2.count('obterNomeFuncionario(') == 0
assert body2.count('gerarNumeroRegisto()') == 0
assert body2.count('_osTemMateriais(') == 0
assert body2.count('moduloErpAtivo(') == 0
for token in ['selectVisibleServices({', 'selectPendingSpecialtyServices({', 'rowLeadingCells({', 'rowActions({', 'statusControl({', 'workSheetActions({']:
    assert body2.count(token) == 1, (token, body2.count(token))
new_text = text[:start] + body2 + text[end:]
for token, count in old_counts.items():
    assert new_text.count(token) == count, (token, count, new_text.count(token))
app_path.write_text(new_text, encoding='utf-8')

# 3) Cache bump for changed persistent JS/app shell.
sw_path = Path('sw.js')
sw = sw_path.read_text(encoding='utf-8')
assert "const CACHE = 'totalgest-v134';" in sw
sw_path.write_text(sw.replace("const CACHE = 'totalgest-v134';", "const CACHE = 'totalgest-v135';", 1), encoding='utf-8')

print(f'RENDERIZAR_SERVICOS_AFTER chars={len(body2)} lines={len(body2.splitlines())}')
print('SERVICES_ROW_MODEL_MIGRATION=OK')
