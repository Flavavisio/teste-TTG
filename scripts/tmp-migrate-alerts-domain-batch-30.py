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

repls=[]
repls.append(('''            if (moduloContratosAtivo(adminRecAlerta)) {
                const contractAttention = window.TotalGestAlertsView.prepareMaintenanceContractAlerts({
                    contracts: dados.contratos || [],
                    adminId: adminId,
                    getNextMaintenance: calcularProximaManutencao,
                    getMaintenanceState: estadoManutencao
                });
                if (contractAttention.alert) alertas.push(contractAttention.alert);
                contractAttention.items.forEach(item => {
                    const c = item.contract;
                    const dias = item.days;
                    _notificarPorFaseVencimento('contrato_vencer_' + adminId, c.id, dias, () => {
                        _notificarAdminESubadmin(adminId, '📄 Contrato de manutenção a vencer', 'Contrato ' + (c.numero || '#' + c.id) + ' — ' + _clienteLabel(dados.clientes?.find(cl => cl.id === c.clienteId) || {}) + ' vence em ' + dias + ' dia(s).', "abrirSecao('contratos')");
                    });
                });
            }''','''            window.TotalGestAlertsView.runMaintenanceContractAlertFlow({
                enabled: moduloContratosAtivo(adminRecAlerta), contracts: dados.contratos || [], clients: dados.clientes || [], adminId,
                alerts: alertas, getNextMaintenance: calcularProximaManutencao, getMaintenanceState: estadoManutencao,
                getClientLabel: _clienteLabel, notifyByPhase: _notificarPorFaseVencimento, notifyAdmin: _notificarAdminESubadmin
            });'''))
repls.append(('''            const fleetAttention = window.TotalGestAlertsView.prepareFleetAttention({
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
            });''','''            window.TotalGestAlertsView.runFleetAlertFlow({
                vehicles: dados.veiculos || [], interventions: dados.veiculoIntervencoes || [], adminId, alerts: alertas,
                getDateState: estadoDataFrota, notifyByPhase: _notificarPorFaseVencimento, notifyAdmin: _notificarAdminESubadmin
            });'''))
repls.append(('''            const licenseExpiry = window.TotalGestAlertsView.licenseExpiryState(adminRecAlerta, calcularDiasRestantes);
            if (licenseExpiry) {
                const diasLic = licenseExpiry.days;
                _notificarPorFaseVencimento('licenca_' + adminId, 'atual', diasLic, () => {
                    _notificarAdminESubadmin(adminId, '⏰ Licença a expirar', 'A licença da tua empresa expira em ' + diasLic + ' dia(s). Renova em "Minha Licença" para não perderes acesso.', "abrirSecao('minha-licenca')");
                });
            }''','''            window.TotalGestAlertsView.runLicenseAlertFlow({
                admin: adminRecAlerta, adminId, calculateDaysRemaining: calcularDiasRestantes,
                notifyByPhase: _notificarPorFaseVencimento, notifyAdmin: _notificarAdminESubadmin
            });'''))
repls.append(('''            const regulatoryAlerts = window.TotalGestAlertsView.prepareRegulatoryRenewals({
                admin: adminRecAlerta,
                calculateDaysRemaining: calcularDiasRestantes,
                thresholdDays: 180
            });
            if (regulatoryAlerts.registoPrevio) {
                const diasRP = regulatoryAlerts.registoPrevio.days;
                alertas.push(regulatoryAlerts.registoPrevio.alert);
                _notificarPorFaseVencimento('registo_previo_' + adminId, 'atual', diasRP, () => {
                    _notificarAdminESubadmin(adminId, '⚠️ Registo prévio a renovar', 'O registo prévio da tua empresa vence em ' + diasRP + ' dia(s). Trata da renovação junto da PSP.', "abrirEditarPerfil()");
                });
            }
            if (regulatoryAlerts.anepc) {
                const diasAN = regulatoryAlerts.anepc.days;
                alertas.push(regulatoryAlerts.anepc.alert);
                _notificarPorFaseVencimento('anepc_' + adminId, 'atual', diasAN, () => {
                    _notificarAdminESubadmin(adminId, '⚠️ Registo ANEPC a renovar', 'O registo ANEPC da tua empresa vence em ' + diasAN + ' dia(s). Trata da renovação junto da ANEPC.', "abrirEditarPerfil()");
                });
            }''','''            window.TotalGestAlertsView.runRegulatoryAlertFlow({
                admin: adminRecAlerta, adminId, alerts: alertas, thresholdDays: 180, calculateDaysRemaining: calcularDiasRestantes,
                notifyByPhase: _notificarPorFaseVencimento, notifyAdmin: _notificarAdminESubadmin
            });'''))
repls.append(('''            if (adminRecAlerta?.shstAtivo) {
                const shstRenewals = window.TotalGestAlertsView.prepareShstRenewals({
                    employees: dados.funcionarios || [],
                    managers: dados.encarregados || [],
                    adminId: adminId,
                    calculateDaysRemaining: calcularDiasRestantes,
                    now: new Date()
                });
                shstRenewals.forEach(item => {
                    const p = item.person;
                    const diasSHST = item.days;
                    alertas.push(item.alert);
                    _notificarPorFaseVencimento('shst_' + p.id, 'atual', diasSHST, () => {
                        _notificarAdminESubadmin(adminId, '⚠️ SHST a renovar', 'A consulta de medicina do trabalho de ' + p.nome + ' vence em ' + diasSHST + ' dia(s).', `abrirModal('funcionario','${p.id}')`);
                    });
                });
            }''','''            window.TotalGestAlertsView.runShstAlertFlow({
                enabled: adminRecAlerta?.shstAtivo === true, employees: dados.funcionarios || [], managers: dados.encarregados || [],
                adminId, alerts: alertas, calculateDaysRemaining: calcularDiasRestantes, now: new Date(),
                notifyByPhase: _notificarPorFaseVencimento, notifyAdmin: _notificarAdminESubadmin
            });'''))
repls.append(('''            if (moduloArmazemAtivo(adminAtual())) {
                const warehouseAlerts = window.TotalGestAlertsView.prepareWarehouseAlerts({
                    articles: dados.artigos || [],
                    workMaterials: dados.obraMateriais || [],
                    adminId: adminId,
                    getCurrentStock: stockAtualArtigo
                });
                warehouseAlerts.forEach(alert => alertas.push(alert));
            }''','''            window.TotalGestAlertsView.runWarehouseAlertFlow({
                enabled: moduloArmazemAtivo(adminAtual()), articles: dados.artigos || [], workMaterials: dados.obraMateriais || [],
                adminId, alerts: alertas, getCurrentStock: stockAtualArtigo
            });'''))

for old,new in repls:
    assert app.count(old)==1, ('missing block', old[:80], app.count(old))
    app=app.replace(old,new,1)

helpers=r'''
  function appendAlert(alerts, alert) {
    if (Array.isArray(alerts) && alert) alerts.push(alert);
  }

  function runMaintenanceContractAlertFlow(options) {
    const o = options || {};
    if (!o.enabled) return { items: [], alert: null };
    const state = prepareMaintenanceContractAlerts(o);
    appendAlert(o.alerts, state.alert);
    state.items.forEach(function (item) {
      const contract = item.contract, days = item.days;
      o.notifyByPhase('contrato_vencer_' + o.adminId, contract.id, days, function () {
        const client = (Array.isArray(o.clients) ? o.clients : []).find(function (item) { return item.id === contract.clienteId; }) || {};
        o.notifyAdmin(o.adminId, '📄 Contrato de manutenção a vencer', 'Contrato ' + (contract.numero || '#' + contract.id) + ' — ' + o.getClientLabel(client) + ' vence em ' + days + ' dia(s).', "abrirSecao('contratos')");
      });
    });
    return state;
  }

  function runFleetAlertFlow(options) {
    const o = options || {}, state = prepareFleetAttention(o);
    appendAlert(o.alerts, state.alert);
    state.items.forEach(function (item) {
      const vehicle = item.vehicle, reasons = item.reasons, days = item.days;
      const safeDays = isFinite(days) ? days : 30;
      o.notifyByPhase('frota_vencer_' + o.adminId, vehicle.id, safeDays, function () {
        o.notifyAdmin(o.adminId, '🚗 Veículo a vencer', 'Matrícula ' + (vehicle.matricula || '—') + ' — ' + reasons.join(' e ') + ' a vencer em ' + (isFinite(days) ? days : '30') + ' dia(s).', "abrirSecao('frota')");
      });
    });
    return state;
  }

  function runLicenseAlertFlow(options) {
    const o = options || {}, state = licenseExpiryState(o.admin, o.calculateDaysRemaining);
    if (!state) return null;
    const days = state.days;
    o.notifyByPhase('licenca_' + o.adminId, 'atual', days, function () {
      o.notifyAdmin(o.adminId, '⏰ Licença a expirar', 'A licença da tua empresa expira em ' + days + ' dia(s). Renova em "Minha Licença" para não perderes acesso.', "abrirSecao('minha-licenca')");
    });
    return state;
  }

  function runRegulatoryAlertFlow(options) {
    const o = options || {}, state = prepareRegulatoryRenewals(o);
    if (state.registoPrevio) {
      const days = state.registoPrevio.days;
      appendAlert(o.alerts, state.registoPrevio.alert);
      o.notifyByPhase('registo_previo_' + o.adminId, 'atual', days, function () {
        o.notifyAdmin(o.adminId, '⚠️ Registo prévio a renovar', 'O registo prévio da tua empresa vence em ' + days + ' dia(s). Trata da renovação junto da PSP.', "abrirEditarPerfil()");
      });
    }
    if (state.anepc) {
      const days = state.anepc.days;
      appendAlert(o.alerts, state.anepc.alert);
      o.notifyByPhase('anepc_' + o.adminId, 'atual', days, function () {
        o.notifyAdmin(o.adminId, '⚠️ Registo ANEPC a renovar', 'O registo ANEPC da tua empresa vence em ' + days + ' dia(s). Trata da renovação junto da ANEPC.', "abrirEditarPerfil()");
      });
    }
    return state;
  }

  function runShstAlertFlow(options) {
    const o = options || {};
    if (!o.enabled) return [];
    const items = prepareShstRenewals(o);
    items.forEach(function (item) {
      const person = item.person, days = item.days;
      appendAlert(o.alerts, item.alert);
      o.notifyByPhase('shst_' + person.id, 'atual', days, function () {
        o.notifyAdmin(o.adminId, '⚠️ SHST a renovar', 'A consulta de medicina do trabalho de ' + person.nome + ' vence em ' + days + ' dia(s).', "abrirModal('funcionario','" + person.id + "')");
      });
    });
    return items;
  }

  function runWarehouseAlertFlow(options) {
    const o = options || {};
    if (!o.enabled) return [];
    const alerts = prepareWarehouseAlerts(o);
    alerts.forEach(function (alert) { appendAlert(o.alerts, alert); });
    return alerts;
  }
'''
marker='\n  window.TotalGestAlertsView = {'
assert view.count(marker)==1
view=view.replace(marker,helpers+marker,1)
old_export='''    preparePendingAdminRequestsAlerts: preparePendingAdminRequestsAlerts,
    applyAlertsState: applyAlertsState
  };'''
new_export='''    preparePendingAdminRequestsAlerts: preparePendingAdminRequestsAlerts,
    applyAlertsState: applyAlertsState,
    runMaintenanceContractAlertFlow: runMaintenanceContractAlertFlow,
    runFleetAlertFlow: runFleetAlertFlow,
    runLicenseAlertFlow: runLicenseAlertFlow,
    runRegulatoryAlertFlow: runRegulatoryAlertFlow,
    runShstAlertFlow: runShstAlertFlow,
    runWarehouseAlertFlow: runWarehouseAlertFlow
  };'''
assert view.count(old_export)==1
view=view.replace(old_export,new_export,1)
assert "const CACHE = 'totalgest-v172';" in sw
sw=sw.replace("const CACHE = 'totalgest-v172';","const CACHE = 'totalgest-v173';",1)

app_path.write_text(app,encoding='utf-8'); view_path.write_text(view,encoding='utf-8'); sw_path.write_text(sw,encoding='utf-8')
assert block(app,'        function renderizarServicos() {')==services_before
assert block(app,'        function renderizarPonto() {')==point_before
assert block(app,'        function _guardarEdicaoPontoRegisto(regId) {')==persist_before
assert block(app,'        function _repararEntradasPresas() {')==repair_before
alerts=block(app,'        function renderizarAlertas() {')
for name in ['runMaintenanceContractAlertFlow({','runFleetAlertFlow({','runLicenseAlertFlow({','runRegulatoryAlertFlow({','runShstAlertFlow({','runWarehouseAlertFlow({']:
    assert alerts.count(name)==1,(name,alerts.count(name))
for literal in ["_notificarPorFaseVencimento('contrato_vencer_", "_notificarPorFaseVencimento('frota_vencer_", "_notificarPorFaseVencimento('licenca_", "_notificarPorFaseVencimento('registo_previo_", "_notificarPorFaseVencimento('anepc_", "_notificarPorFaseVencimento('shst_"]:
    assert literal not in alerts,literal
assert alerts.count('notifyByPhase: _notificarPorFaseVencimento')==5
assert alerts.count('notifyAdmin: _notificarAdminESubadmin')==5
print('DOMAIN_CUTS=6')
print('SERVICES_BLOCK_UNCHANGED=OK')
print('POINT_BLOCK_UNCHANGED=OK')
print('POINT_PERSISTENCE_UNCHANGED=OK')
print('POINT_REPAIR_UNCHANGED=OK')
print('ALERT_EFFECT_CALLBACKS_PRESERVED=OK')
print('ALERTS_BEFORE_CHARS=',len(alerts_before))
print('ALERTS_AFTER_CHARS=',len(alerts))
print('ALERTS_AFTER_LINES=',alerts.count('\n')+1)
print('DOMAIN_SEPARATION=OK')
