from pathlib import Path
app_path=Path('app.html'); sw_path=Path('sw.js')
app=app_path.read_text(encoding='utf-8'); sw=sw_path.read_text(encoding='utf-8')
protected={n:app.count(n) for n in ['bootstrapSupabase()','supabase.auth','faturarOSViaTOConline(','faturarOSViaMoloni(','_verificarPagamentoMoloni(','emitirGuiaTransporteMoloni(','emitirNotaCreditoMoloni(']}
fs=app.index('        function renderizarServicos() {'); fe=app.index('\n        function ',fs+1); block=app[fs:fe]
start='                            <td><strong>${numero}</strong> ${_temMateriaisOS ? \'<i class="fas fa-boxes-stacked" style="color:#0891b2;" title="Esta OS tem materiais associados"></i>\' : \'\'}</td>'
end='                            <td>\n                                <div class="acoes">'
assert block.count(start)==1 and block.count(end)==1
s=block.index(start); e=block.index(end,s)
old=block[s:e]
for x in ['obterNomeCliente(s.clienteId)','escapeHtmlSimples(s.descricao || \'-\')','_tiposTrabalhoBadgesHTML(s)','${statusHtml}']: assert x in old
new="""                            ${window.TotalGestServicesView.rowLeadingCells({
                                number: numero,
                                hasMaterials: _temMateriaisOS,
                                clientName: obterNomeCliente(s.clienteId),
                                employeeName: nomeFunc,
                                date: s.data || '-',
                                time: s.hora || '-',
                                description: escapeHtmlSimples(s.descricao || '-'),
                                workTypesHtml: _tiposTrabalhoBadgesHTML(s),
                                statusHtml
                            })}
"""
block=block[:s]+new+block[e:]
assert block.count('window.TotalGestServicesView.rowLeadingCells({')==1
app=app[:fs]+block+app[fe:]
for n,c in protected.items(): assert app.count(n)==c,(n,c,app.count(n))
assert "const CACHE = 'totalgest-v129';" in sw
sw=sw.replace("const CACHE = 'totalgest-v129';","const CACHE = 'totalgest-v130';",1)
app_path.write_text(app,encoding='utf-8'); sw_path.write_text(sw,encoding='utf-8')
print(f'RENDERIZAR_SERVICOS_AFTER chars={len(block)} lines={len(block.splitlines())}')
print('SERVICES_ROW_CELLS_MIGRATION=OK')
