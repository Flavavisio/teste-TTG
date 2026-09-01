from pathlib import Path
p=Path('app.html'); text=p.read_text(encoding='utf-8')
s=text.index('        function renderizarServicos() {'); e=text.index('\n        function ',s+1); b=text[s:e]
start=b.index("            const avisoDiv = document.getElementById('servicosAvisoEspecialidade');")
end=b.index("\n\n            servicos = _aplicarFiltroOrdenacao", start)
old=b[start:end]
for token in ["_podeVerPendentes", "_servicosPendentesEspecialidade", "_tiposEspecialidadePendentes(s.id)", "specialtyAndHistoryNotice({"]:
    assert token in old, token
new="""            const avisoDiv = document.getElementById('servicosAvisoEspecialidade');
            if (avisoDiv) {
                const _pendingSpecialty = window.TotalGestServicesSelection.selectPendingSpecialtyServices({
                    services: servicos,
                    role: usuarioLogado?.role || '',
                    getPendingTypes: serviceId => _tiposEspecialidadePendentes(serviceId)
                });
                avisoDiv.innerHTML = window.TotalGestServicesView.specialtyAndHistoryNotice({
                    canSeePending: _pendingSpecialty.canSeePending,
                    pendingServices: _pendingSpecialty.pendingServices,
                    loadedSinceLabel: _servicosCarregadoDesde
                        ? new Date(_servicosCarregadoDesde + 'T00:00:00').toLocaleDateString('pt-PT')
                        : '—'
                });
            }"""
b2=b[:start]+new+b[end:]
assert b2.count('selectPendingSpecialtyServices({')==1
assert '_podeVerPendentes' not in b2 and '_servicosPendentesEspecialidade' not in b2
assert b2.count('_tiposEspecialidadePendentes(')==1
for token in ['selectVisibleServices({','specialtyAndHistoryNotice({','statusControl({','workSheetActions({','rowLeadingCells({','rowActions({']:
    assert b2.count(token)==1,(token,b2.count(token))
new_text=text[:s]+b2+text[e:]
assert new_text.count('bootstrapSupabase()')==text.count('bootstrapSupabase()')
assert new_text.count('supabase.auth')==text.count('supabase.auth')
p.write_text(new_text,encoding='utf-8')
sw=Path('sw.js'); st=sw.read_text(encoding='utf-8'); assert "const CACHE = 'totalgest-v133';" in st
sw.write_text(st.replace("const CACHE = 'totalgest-v133';","const CACHE = 'totalgest-v134';",1),encoding='utf-8')
print(f'RENDERIZAR_SERVICOS_AFTER chars={len(b2)} lines={len(b2.splitlines())}')
print('SERVICES_PENDING_SPECIALTY_MIGRATION=OK')
