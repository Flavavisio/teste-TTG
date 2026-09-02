from pathlib import Path
import subprocess

app_path = Path('app.html')
selection_path = Path('assets/js/app-services-selection.js')
view_path = Path('assets/js/app-services-view.js')
sw_path = Path('sw.js')

# Corte 1: seletor de especialidades configurável
selection = selection_path.read_text(encoding='utf-8')
anchor_prepare = """  function prepareServiceRow(options) {
"""
assert selection.count(anchor_prepare) == 1
assert 'function createPendingSpecialtySelector(options)' not in selection
helper_pending = """  function createPendingSpecialtySelector(options) {
    options = options || {};
    return function (services) {
      return selectPendingSpecialtyServicesForUser({
        services: services || [],
        user: options.user || null,
        getPendingTypes: options.getPendingTypes
      });
    };
  }

"""
selection = selection.replace(anchor_prepare, helper_pending + anchor_prepare, 1)
export_old = """    selectPendingSpecialtyServicesForUser: selectPendingSpecialtyServicesForUser,
    prepareServiceRow: prepareServiceRow,
"""
export_new = """    selectPendingSpecialtyServicesForUser: selectPendingSpecialtyServicesForUser,
    createPendingSpecialtySelector: createPendingSpecialtySelector,
    prepareServiceRow: prepareServiceRow,
"""
assert selection.count(export_old) == 1
selection = selection.replace(export_old, export_new, 1)
selection_path.write_text(selection, encoding='utf-8')

# Corte 2: centralizar referências DOM da área de serviços
view = view_path.read_text(encoding='utf-8')
anchor_history = """  function serviceHistoryLoadedSinceLabel(value) {
"""
assert view.count(anchor_history) == 1
assert 'function servicesViewElements(doc)' not in view
helper_elements = """  function servicesViewElements(doc) {
    const source = doc || document;
    return {
      tbody: source.getElementById('tabelaServicos'),
      emptyElement: source.getElementById('emptyServ'),
      noticeElement: source.getElementById('servicosAvisoEspecialidade'),
      toolbarElement: source.getElementById('servicosToolbar')
    };
  }

"""
view = view.replace(anchor_history, helper_elements + anchor_history, 1)

# Corte 3: extrair renderização da coleção de linhas + atribuição DOM
anchor_service_row = """  function serviceRow(options) {
"""
assert view.count(anchor_service_row) == 1
assert 'function renderServiceRowsToTable(options)' not in view
helper_rows = """  function renderServiceRowsToTable(options) {
    const opts = options || {};
    const services = Array.isArray(opts.services) ? opts.services : [];
    const renderItem = typeof opts.renderItem === 'function' ? opts.renderItem : function () { return ''; };
    if (!opts.tbody) return false;
    opts.tbody.innerHTML = services.map(renderItem).join('');
    return true;
  }

"""
view = view.replace(anchor_service_row, helper_rows + anchor_service_row, 1)
export_old_view = "window.TotalGestServicesView = { serviceHistoryLoadedSinceLabel, specialtyAndHistoryNotice, specialtyAndHistoryNoticeFromState, applySpecialtyAndHistoryNotice, servicesTableState, applyServicesTableState, renderServicesTableState, statusControl, serviceStatusControl, workSheetActions, rowLeadingCells, primaryRowActions, erpRowActions, rowActions, serviceRowFromData, createServiceRowRenderer, serviceRow };"
export_new_view = "window.TotalGestServicesView = { servicesViewElements, serviceHistoryLoadedSinceLabel, specialtyAndHistoryNotice, specialtyAndHistoryNoticeFromState, applySpecialtyAndHistoryNotice, servicesTableState, applyServicesTableState, renderServicesTableState, statusControl, serviceStatusControl, workSheetActions, rowLeadingCells, primaryRowActions, erpRowActions, rowActions, serviceRowFromData, createServiceRowRenderer, renderServiceRowsToTable, serviceRow };"
assert view.count(export_old_view) == 1
view = view.replace(export_old_view, export_new_view, 1)
view_path.write_text(view, encoding='utf-8')

# Alterações semânticas em renderizarServicos
app = app_path.read_text(encoding='utf-8')
marker = '        function renderizarServicos() {'
assert app.count(marker) == 1
start = app.index(marker)
end = app.index('\n        function ', start + len(marker))
before = app[start:end]

# Capturar objeto actions literalmente antes das mudanças
old_actions_marker = '                return renderRow(s, rowData, {'
actions_start_before = before.index(old_actions_marker) + len(old_actions_marker)
actions_end_before = before.index('\n                });', actions_start_before)
actions_body_before = before[actions_start_before:actions_end_before]

old_dom = """        function renderizarServicos() {
            const tbody = document.getElementById('tabelaServicos');
            const empty = document.getElementById('emptyServ');
"""
new_dom = """        function renderizarServicos() {
            const viewElements = window.TotalGestServicesView.servicesViewElements(document);
            const tbody = viewElements.tbody;
            const empty = viewElements.emptyElement;
"""
assert app.count(old_dom) == 1
app = app.replace(old_dom, new_dom, 1)

old_notice = """            const avisoDiv = document.getElementById('servicosAvisoEspecialidade');
            if (avisoDiv) {
                const _pendingSpecialty = window.TotalGestServicesSelection.selectPendingSpecialtyServicesForUser({
                    services: servicos,
                    user: usuarioLogado,
                    getPendingTypes: serviceId => _tiposEspecialidadePendentes(serviceId)
                });
                window.TotalGestServicesView.applySpecialtyAndHistoryNotice({
                    element: avisoDiv,
                    pendingState: _pendingSpecialty,
                    loadedSince: _servicosCarregadoDesde
                });
            }
"""
new_notice = """            const avisoDiv = viewElements.noticeElement;
            if (avisoDiv) {
                const selectPendingSpecialty = window.TotalGestServicesSelection.createPendingSpecialtySelector({
                    user: usuarioLogado,
                    getPendingTypes: serviceId => _tiposEspecialidadePendentes(serviceId)
                });
                window.TotalGestServicesView.applySpecialtyAndHistoryNotice({
                    element: avisoDiv,
                    pendingState: selectPendingSpecialty(servicos),
                    loadedSince: _servicosCarregadoDesde
                });
            }
"""
assert before.count(old_notice) == 1
app = app.replace(old_notice, new_notice, 1)

old_toolbar = "toolbarElement: document.getElementById('servicosToolbar'),"
new_toolbar = "toolbarElement: viewElements.toolbarElement,"
assert before.count(old_toolbar) == 1
app = app.replace(old_toolbar, new_toolbar, 1)

# Alterar apenas o invólucro map/join; callback e objeto actions permanecem textualmente iguais
start = app.index(marker)
end = app.index('\n        function ', start + len(marker))
current = app[start:end]
old_rows_open = """            tbody.innerHTML = servicos.map(s => {
                const rowData = prepareRow(s);
                return renderRow(s, rowData, {
"""
new_rows_open = """            window.TotalGestServicesView.renderServiceRowsToTable({
                tbody,
                services: servicos,
                renderItem: s => {
                    const rowData = prepareRow(s);
                    return renderRow(s, rowData, {
"""
assert current.count(old_rows_open) == 1
current = current.replace(old_rows_open, new_rows_open, 1)
old_rows_close = """                });
            }).join('');
"""
new_rows_close = """                    });
                }
            });
"""
assert current.count(old_rows_close) == 1, current.count(old_rows_close)
current = current.replace(old_rows_close, new_rows_close, 1)
app = app[:start] + current + app[end:]
app_path.write_text(app, encoding='utf-8')

# cache
sw = sw_path.read_text(encoding='utf-8')
assert sw.count("const CACHE = 'totalgest-v145';") == 1
sw = sw.replace("const CACHE = 'totalgest-v145';", "const CACHE = 'totalgest-v146';", 1)
sw_path.write_text(sw, encoding='utf-8')

# Estrutura final
final_app = app_path.read_text(encoding='utf-8')
start = final_app.index(marker)
end = final_app.index('\n        function ', start + len(marker))
block = final_app[start:end]
for item in ['servicesViewElements(document)','createPendingSpecialtySelector({','selectPendingSpecialty(servicos)','renderServiceRowsToTable({','createServiceFilterSorter({','renderServicesTableState({','createServiceRowPreparer({','createServiceRowRenderer({','return renderRow(s, rowData, {']:
    assert block.count(item) == 1, (item, block.count(item))
for item in ["document.getElementById('tabelaServicos')","document.getElementById('emptyServ')","document.getElementById('servicosAvisoEspecialidade')","document.getElementById('servicosToolbar')",'selectPendingSpecialtyServicesForUser({','tbody.innerHTML = servicos.map(']:
    assert block.count(item) == 0, (item, block.count(item))
for item in ['invoiceTOId:','invoiceMoloniId:','invoiceMoloniUrl:','receiptMoloniUrl:','guideMoloniId:','guideMoloniUrl:','creditNoteMoloniId:','creditNoteMoloniUrl:']:
    assert block.count(item) == 1, (item, block.count(item))
new_actions_marker = '                    return renderRow(s, rowData, {'
actions_start_after = block.index(new_actions_marker) + len(new_actions_marker)
actions_end_after = block.index('\n                    });', actions_start_after)
actions_body_after = block[actions_start_after:actions_end_after]
assert actions_body_after == actions_body_before, (actions_body_before, actions_body_after)

# Testes unitários dos três cortes
node_test = r"""
const fs = require('fs');
const vm = require('vm');
const assert = require('assert');
const context = { window: {}, document: { getElementById: () => null } };
vm.createContext(context);
vm.runInContext(fs.readFileSync('assets/js/app-services-selection.js', 'utf8'), context);
vm.runInContext(fs.readFileSync('assets/js/app-services-view.js', 'utf8'), context);
const sel = context.window.TotalGestServicesSelection;
const view = context.window.TotalGestServicesView;

const services = [{ id: 's1', status: 'concluído', numeroRegisto: 'OS-1' }, { id: 's2', status: 'pendente' }];
const user = { role: 'admin' };
const getPendingTypes = id => id === 's1' ? ['AVAC'] : [];
const expectedPending = sel.selectPendingSpecialtyServicesForUser({ services, user, getPendingTypes });
const actualPending = sel.createPendingSpecialtySelector({ user, getPendingTypes })(services);
assert.deepStrictEqual(JSON.parse(JSON.stringify(actualPending)), JSON.parse(JSON.stringify(expectedPending)));

const nodes = {
  tabelaServicos: { id: 'tbody', innerHTML: '' },
  emptyServ: { id: 'empty', style: {} },
  servicosAvisoEspecialidade: { id: 'notice', innerHTML: '' },
  servicosToolbar: { id: 'toolbar', innerHTML: '' }
};
const doc = { getElementById: id => nodes[id] || null };
const elements = view.servicesViewElements(doc);
assert.strictEqual(elements.tbody, nodes.tabelaServicos);
assert.strictEqual(elements.emptyElement, nodes.emptyServ);
assert.strictEqual(elements.noticeElement, nodes.servicosAvisoEspecialidade);
assert.strictEqual(elements.toolbarElement, nodes.servicosToolbar);

const tbody = { innerHTML: 'OLD' };
const rendered = view.renderServiceRowsToTable({ tbody, services: [1,2,3], renderItem: n => `<tr>${n}</tr>` });
assert.strictEqual(rendered, true);
assert.strictEqual(tbody.innerHTML, '<tr>1</tr><tr>2</tr><tr>3</tr>');
assert.strictEqual(view.renderServiceRowsToTable({ tbody: null, services: [1] }), false);
console.log('SAFE_BATCH_3_UNIT=OK');
"""
subprocess.run(['node', '-e', node_test], check=True)
subprocess.run(['node', '--check', 'assets/js/app-services-selection.js'], check=True)
subprocess.run(['node', '--check', 'assets/js/app-services-view.js'], check=True)
subprocess.run(['node', '--check', 'sw.js'], check=True)
subprocess.run(['git', 'diff', '--check'], check=True)
print('SAFE_CUTS=3')
print('ACTIONS_SEGMENT_UNCHANGED=OK')
print('RENDERIZAR_SERVICOS_BEFORE_CHARS=', len(before))
print('RENDERIZAR_SERVICOS_AFTER_CHARS=', len(block))
print('RENDERIZAR_SERVICOS_AFTER_LINES=', len(block.splitlines()))
print('STRUCTURE=OK')
