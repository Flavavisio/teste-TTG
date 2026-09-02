from pathlib import Path

app_path=Path('app.html'); view_path=Path('assets/js/app-alerts-view.js'); sw_path=Path('sw.js')
app=app_path.read_text(encoding='utf-8'); view=view_path.read_text(encoding='utf-8'); sw=sw_path.read_text(encoding='utf-8')

def block(text, marker):
    s=text.index(marker); e=text.index('\n        function ',s+len(marker)); return text[s:e]
services_before=block(app,'        function renderizarServicos() {')
point_before=block(app,'        function renderizarPonto() {')
persist_before=block(app,'        function _guardarEdicaoPontoRegisto(regId) {')
repair_before=block(app,'        function _repararEntradasPresas() {')
alerts_before=block(app,'        function renderizarAlertas() {')

old='''            const veics = (dados.veiculos || []).filter(v => v.adminId === adminId);
            const crit = ['vencido', 'urgente', 'a_vencer'];
            const _ultimaIntervManut = (veiculoId) => {
                const doVeiculo = (dados.veiculoIntervencoes || []).filter(i => i.veiculoId === veiculoId && i.proximaData);
                if (!doVeiculo.length) return null;
                return doVeiculo.sort((a, b) => (b.data || '').localeCompare(a.data || '') || (b.dataCriacao || 0) - (a.dataCriacao || 0))[0];
            };
            const veicsAtencaoLista = veics.filter(v => {
                const insp = estadoDataFrota(v.inspecaoValidade).chave;
                const seg = estadoDataFrota(v.seguroValidade).chave;
                const ultimaManut = _ultimaIntervManut(v.id);
                const manut = ultimaManut && crit.includes(estadoDataFrota(ultimaManut.proximaData).chave);
                return crit.includes(insp) || crit.includes(seg) || manut;
            });
            if (veicsAtencaoLista.length) alertas.push({ tipo: 'warning', titulo: `${veicsAtencaoLista.length} ${veicsAtencaoLista.length === 1 ? 'frota a vencer manutenção' : 'frota a vencer manutenção'}`, sub: 'Verifique a frota e agende a manutenção.', acao: "abrirSecao('frota')" });
            veicsAtencaoLista.forEach(v => {
                const insp = estadoDataFrota(v.inspecaoValidade);
                const seg = estadoDataFrota(v.seguroValidade);
                const ultimaManut = _ultimaIntervManut(v.id);
                const manutEstado = ultimaManut ? estadoDataFrota(ultimaManut.proximaData) : null;
                const motivos = [];
                if (crit.includes(insp.chave)) motivos.push('inspeção');
                if (crit.includes(seg.chave)) motivos.push('seguro');
                if (manutEstado && crit.includes(manutEstado.chave)) motivos.push('manutenção');
                const candidatos = [insp, seg].concat(manutEstado ? [manutEstado] : []).filter(x => crit.includes(x.chave));
                const dias = candidatos.length ? Math.min(...candidatos.map(x => x.dias)) : 30;
                _notificarPorFaseVencimento('frota_vencer_' + adminId, v.id, isFinite(dias) ? dias : 30, () => {
                    _notificarAdminESubadmin(adminId, '🚗 Veículo a vencer', 'Matrícula ' + (v.matricula || '—') + ' — ' + motivos.join(' e ') + ' a vencer em ' + (isFinite(dias) ? dias : '30') + ' dia(s).', "abrirSecao('frota')");
                });
            });'''
new='''            const fleetAttention = window.TotalGestAlertsView.prepareFleetAttention({
                vehicles: dados.veiculos || [],
                interventions: dados.veiculoIntervencoes || [],
                adminId: adminId,
                getDateState: estadoDataFrota
            });
            if (fleetAttention.alert) alertas.push(fleetAttention.alert);
            fleetAttention.items.forEach(item => {
                const v = item.vehicle;
                const motivos = item.reasons;
                const dias = item.days;
                _notificarPorFaseVencimento('frota_vencer_' + adminId, v.id, isFinite(dias) ? dias : 30, () => {
                    _notificarAdminESubadmin(adminId, '🚗 Veículo a vencer', 'Matrícula ' + (v.matricula || '—') + ' — ' + motivos.join(' e ') + ' a vencer em ' + (isFinite(dias) ? dias : '30') + ' dia(s).', "abrirSecao('frota')");
                });
            });'''
assert app.count(old)==1, app.count(old)
app=app.replace(old,new,1)

marker='\n  window.TotalGestAlertsView = {'
helpers='''
  function latestFleetMaintenance(interventions, vehicleId) {
    const list = (Array.isArray(interventions) ? interventions : []).filter(function (item) {
      return item.veiculoId === vehicleId && item.proximaData;
    });
    if (!list.length) return null;
    return list.sort(function (a, b) {
      return (b.data || '').localeCompare(a.data || '') || (b.dataCriacao || 0) - (a.dataCriacao || 0);
    })[0];
  }

  function fleetVehicleAttention(vehicle, interventions, getDateState) {
    const critical = ['vencido', 'urgente', 'a_vencer'];
    const inspection = getDateState(vehicle.inspecaoValidade);
    const insurance = getDateState(vehicle.seguroValidade);
    const latestMaintenance = latestFleetMaintenance(interventions, vehicle.id);
    const maintenance = latestMaintenance ? getDateState(latestMaintenance.proximaData) : null;
    const reasons = [];
    if (critical.includes(inspection.chave)) reasons.push('inspeção');
    if (critical.includes(insurance.chave)) reasons.push('seguro');
    if (maintenance && critical.includes(maintenance.chave)) reasons.push('manutenção');
    const candidates = [inspection, insurance].concat(maintenance ? [maintenance] : []).filter(function (state) {
      return critical.includes(state.chave);
    });
    const days = candidates.length ? Math.min.apply(null, candidates.map(function (state) { return state.dias; })) : 30;
    return { vehicle: vehicle, reasons: reasons, days: days, needsAttention: reasons.length > 0 };
  }

  function prepareFleetAttention(options) {
    const o = options || {};
    const vehicles = (Array.isArray(o.vehicles) ? o.vehicles : []).filter(function (vehicle) {
      return vehicle.adminId === o.adminId;
    });
    const items = vehicles.map(function (vehicle) {
      return fleetVehicleAttention(vehicle, o.interventions, o.getDateState);
    }).filter(function (item) { return item.needsAttention; });
    return {
      items: items,
      alert: items.length ? { tipo: 'warning', titulo: items.length + ' frota a vencer manutenção', sub: 'Verifique a frota e agende a manutenção.', acao: "abrirSecao('frota')" } : null
    };
  }
'''
assert view.count(marker)==1
view=view.replace(marker,helpers+marker,1)
oldexp='''    pendingRequisitionsAlert: pendingRequisitionsAlert,
    pendingLeaveRequestsAlert: pendingLeaveRequestsAlert
  };'''
newexp='''    pendingRequisitionsAlert: pendingRequisitionsAlert,
    pendingLeaveRequestsAlert: pendingLeaveRequestsAlert,
    latestFleetMaintenance: latestFleetMaintenance,
    fleetVehicleAttention: fleetVehicleAttention,
    prepareFleetAttention: prepareFleetAttention
  };'''
assert view.count(oldexp)==1
view=view.replace(oldexp,newexp,1)
assert "const CACHE = 'totalgest-v169';" in sw
sw=sw.replace("const CACHE = 'totalgest-v169';","const CACHE = 'totalgest-v170';",1)

app_path.write_text(app,encoding='utf-8'); view_path.write_text(view,encoding='utf-8'); sw_path.write_text(sw,encoding='utf-8')
assert block(app,'        function renderizarServicos() {')==services_before
assert block(app,'        function renderizarPonto() {')==point_before
assert block(app,'        function _guardarEdicaoPontoRegisto(regId) {')==persist_before
assert block(app,'        function _repararEntradasPresas() {')==repair_before
alerts=block(app,'        function renderizarAlertas() {')
assert alerts.count('prepareFleetAttention({')==1
assert alerts.count("_notificarPorFaseVencimento('frota_vencer_")==1
assert alerts.count("_notificarAdminESubadmin(adminId, '🚗 Veículo a vencer'")==1
for item in ['const _ultimaIntervManut =','const veicsAtencaoLista =','const crit = [']:
    assert item not in alerts,item
print('SAFE_CUTS=3'); print('SERVICES_BLOCK_UNCHANGED=OK'); print('POINT_BLOCK_UNCHANGED=OK'); print('POINT_PERSISTENCE_UNCHANGED=OK'); print('POINT_REPAIR_UNCHANGED=OK'); print('FLEET_NOTIFICATION_SIDE_EFFECTS_PRESERVED=OK'); print('ALERTS_BEFORE_CHARS=',len(alerts_before)); print('ALERTS_AFTER_CHARS=',len(alerts)); print('ALERTS_AFTER_LINES=',alerts.count('\n')+1); print('STRUCTURE=OK')
