from pathlib import Path
p=Path('app.html'); text=p.read_text(encoding='utf-8')
s=text.index('        function renderizarServicos() {'); e=text.index('\n        function ',s+1); b=text[s:e]
start=b.index("                                        ${(() => {")
end=b.index("                                    ` : ''}", start)+len("                                    ` : ''}")
old=b[start:end]
for x in ['faturarOSViaTOConline(', 'faturarOSViaMoloni(', '_verificarPagamentoMoloni(', 'emitirGuiaTransporteMoloni(', 'emitirNotaCreditoMoloni(', 'moduloErpAtivo(']: assert x in old,x
new="""                                        ${window.TotalGestServicesView.erpRowActions({
                                            serviceId: s.id,
                                            status: s.status,
                                            canManage: usuarioLogado?.role === 'admin' || usuarioLogado?.role === 'subadmin',
                                            hasValue: s.valor != null,
                                            erpActive: moduloErpAtivo(dados.administradores?.find(a => a.id === s.adminId)),
                                            provider: dados.administradores?.find(a => a.id === s.adminId)?.integracaoFaturacao?.provider || '',
                                            invoiceTOId: s.faturaTOConlineId || '',
                                            invoiceMoloniId: s.faturaMoloniId || '',
                                            invoiceMoloniUrl: s.faturaMoloniUrl || '',
                                            receiptMoloniId: s.reciboMoloniId || '',
                                            receiptMoloniUrl: s.reciboMoloniUrl || '',
                                            localPayment: s.pagamentoLocal === true,
                                            guideMoloniId: s.guiaMoloniId || '',
                                            guideMoloniUrl: s.guiaMoloniUrl || '',
                                            creditNoteMoloniId: s.notaCreditoMoloniId || '',
                                            creditNoteMoloniUrl: s.notaCreditoMoloniUrl || ''
                                        })}"""
b2=b[:start]+new+b[end:]
assert b2.count('erpRowActions({')==1
for x in ['faturarOSViaTOConline(', 'faturarOSViaMoloni(', '_verificarPagamentoMoloni(', 'emitirGuiaTransporteMoloni(', 'emitirNotaCreditoMoloni(']: assert b2.count(x)==0,x
text2=text[:s]+b2+text[e:]
assert text2.count('bootstrapSupabase()')==text.count('bootstrapSupabase()')
assert text2.count('supabase.auth')==text.count('supabase.auth')
p.write_text(text2,encoding='utf-8')
sw=Path('sw.js'); w=sw.read_text(encoding='utf-8'); assert "const CACHE = 'totalgest-v131';" in w; sw.write_text(w.replace("const CACHE = 'totalgest-v131';","const CACHE = 'totalgest-v132';",1),encoding='utf-8')
print(f'RENDERIZAR_SERVICOS_AFTER chars={len(b2)} lines={len(b2.splitlines())}')
print('SERVICES_ERP_ACTIONS_MIGRATION=OK')
