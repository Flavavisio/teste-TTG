from pathlib import Path
p=Path('app.html'); text=p.read_text(encoding='utf-8')
s=text.index('        function renderizarServicos() {'); e=text.index('\n        function ',s+1); b=text[s:e]
old_start=b.index('                            <td>\n                                <div class="acoes">')
old_end=b.index('                            </td>',old_start)+len('                            </td>')
old=b[old_start:old_end]
for x in ['primaryRowActions({','erpRowActions({',"excluirEntidade('servico'"]:
    assert old.count(x)==1,(x,old.count(x))
new='''                            ${window.TotalGestServicesView.rowActions({
                                serviceId: s.id,
                                status: s.status,
                                role: usuarioLogado?.role || '',
                                localPayment: s.pagamentoLocal === true,
                                paid: s.pago === true,
                                receiptMoloniId: s.reciboMoloniId || '',
                                canManage: usuarioLogado?.role === 'admin' || usuarioLogado?.role === 'subadmin',
                                hasValue: s.valor != null,
                                erpActive: moduloErpAtivo(dados.administradores?.find(a => a.id === s.adminId)),
                                provider: dados.administradores?.find(a => a.id === s.adminId)?.integracaoFaturacao?.provider || '',
                                invoiceTOId: s.faturaTOConlineId || '',
                                invoiceMoloniId: s.faturaMoloniId || '',
                                invoiceMoloniUrl: s.faturaMoloniUrl || '',
                                receiptMoloniUrl: s.reciboMoloniUrl || '',
                                guideMoloniId: s.guiaMoloniId || '',
                                guideMoloniUrl: s.guiaMoloniUrl || '',
                                creditNoteMoloniId: s.notaCreditoMoloniId || '',
                                creditNoteMoloniUrl: s.notaCreditoMoloniUrl || ''
                            })}'''
b2=b[:old_start]+new+b[old_end:]
assert b2.count('rowActions({')==1
assert b2.count('primaryRowActions({')==0 and b2.count('erpRowActions({')==0 and b2.count("excluirEntidade('servico'")==0
for x in ['bootstrapSupabase()','supabase.auth','rowLeadingCells({','statusControl({','workSheetActions({')]:
    assert text.count(x)==(text[:s]+b2+text[e:]).count(x),x
p.write_text(text[:s]+b2+text[e:],encoding='utf-8')
sw=Path('sw.js'); st=sw.read_text(encoding='utf-8'); assert "const CACHE = 'totalgest-v132';" in st
sw.write_text(st.replace("const CACHE = 'totalgest-v132';","const CACHE = 'totalgest-v133';",1),encoding='utf-8')
print(f'RENDERIZAR_SERVICOS_AFTER chars={len(b2)} lines={len(b2.splitlines())}')
print('SERVICES_ROW_ACTIONS_MIGRATION=OK')
