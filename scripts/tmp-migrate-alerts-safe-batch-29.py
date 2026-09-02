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

old_start='''            const cont = document.getElementById('alertasPendencias');
            const contGlobal = document.getElementById('alertaPontoGlobal');
            if (!cont) return;
            if (window.TotalGestAlertsView.isEmployeeAlertsRole(usuarioLogado?.role)) {
                const precisaAtivarPush = (typeof Notification !== 'undefined' && Notification.permission === 'default') && moduloNotificacoesAtivo(adminDoUtilizador());
                const employeeAlertState = window.TotalGestAlertsView.employeeAlertState({
                    points: dados.ponto || [],
                    userId: usuarioLogado.id,
                    today: getDataHoje(),
                    needsPush: precisaAtivarPush
                });
                window.TotalGestAlertsView.applyEmployeeAlertState({ container: cont, globalContainer: contGlobal }, employeeAlertState);
                return;
            }
            if (contGlobal) { contGlobal.classList.remove('mostrar'); contGlobal.innerHTML = ''; }
            if (usuarioLogado?.role !== 'admin' && usuarioLogado?.role !== 'subadmin') { cont.style.display = 'none'; cont.innerHTML = ''; return; }
            const adminId = usuarioLogado.role === 'admin' ? usuarioLogado.id : usuarioLogado.adminId;
            const alertas = [];

            const birthdayAlert = window.TotalGestAlertsView.birthdayAlert({
                employees: dados.funcionarios || [],
                managers: dados.encarregados || [],
                adminId: adminId,
                now: new Date()
            });
            if (birthdayAlert) alertas.push(birthdayAlert);

            const pendingServiceOrdersAlert = window.TotalGestAlertsView.pendingServiceOrdersAlert(dados.servicos || [], adminId);
            if (pendingServiceOrdersAlert) alertas.push(pendingServiceOrdersAlert);

            const pendingAssistancesAlert = window.TotalGestAlertsView.pendingAssistancesAlert(dados.servicos || [], adminId);
            if (pendingAssistancesAlert) alertas.push(pendingAssistancesAlert);'''
new_start='''            const alertElements = window.TotalGestAlertsView.alertsViewElements(document);
            const cont = alertElements.container;
            const contGlobal = alertElements.globalContainer;
            if (!cont) return;
            if (window.TotalGestAlertsView.isEmployeeAlertsRole(usuarioLogado?.role)) {
                const precisaAtivarPush = window.TotalGestAlertsView.needsEmployeePushNotification(
                    typeof Notification !== 'undefined' ? Notification.permission : '',
                    moduloNotificacoesAtivo(adminDoUtilizador())
                );
                const employeeAlertState = window.TotalGestAlertsView.employeeAlertState({
                    points: dados.ponto || [],
                    userId: usuarioLogado.id,
                    today: getDataHoje(),
                    needsPush: precisaAtivarPush
                });
                window.TotalGestAlertsView.applyEmployeeAlertState(alertElements, employeeAlertState);
                return;
            }
            window.TotalGestAlertsView.clearGlobalAlert(contGlobal);
            if (!window.TotalGestAlertsView.isAdminAlertsRole(usuarioLogado?.role)) {
                window.TotalGestAlertsView.applyAlertsState(cont, [], false);
                return;
            }
            const adminId = window.TotalGestAlertsView.resolveAlertsAdminId(usuarioLogado);
            const alertas = window.TotalGestAlertsView.prepareInitialAdminAlerts({
                employees: dados.funcionarios || [],
                managers: dados.encarregados || [],
                services: dados.servicos || [],
                adminId: adminId,
                now: new Date()
            });'''
assert app.count(old_start)==1, app.count(old_start)
app=app.replace(old_start,new_start,1)

old_requests='''            const pendingRequisitionsAlert = window.TotalGestAlertsView.pendingRequisitionsAlert(dados.requisicoes || [], adminId);
            if (pendingRequisitionsAlert) alertas.push(pendingRequisitionsAlert);

            const pendingLeaveRequestsAlert = window.TotalGestAlertsView.pendingLeaveRequestsAlert(dados.pedidos || [], adminId);
            if (pendingLeaveRequestsAlert) alertas.push(pendingLeaveRequestsAlert);'''
new_requests='''            window.TotalGestAlertsView.preparePendingAdminRequestsAlerts({
                requisitions: dados.requisicoes || [],
                requests: dados.pedidos || [],
                adminId: adminId
            }).forEach(alert => alertas.push(alert));'''
assert app.count(old_requests)==1, app.count(old_requests)
app=app.replace(old_requests,new_requests,1)

old_end='''            if (!alertas.length) { cont.style.display = 'none'; cont.innerHTML = ''; return; }
            cont.style.display = 'block';
            cont.innerHTML = window.TotalGestAlertsView.alertsCard({
                alertas: alertas,
                mobile: _ehPerfilMobile()
            });'''
new_end='''            window.TotalGestAlertsView.applyAlertsState(cont, alertas, _ehPerfilMobile());'''
assert app.count(old_end)==1, app.count(old_end)
app=app.replace(old_end,new_end,1)

marker='\n  window.TotalGestAlertsView = {'
helpers='''
  function alertsViewElements(doc) {
    return {
      container: doc && doc.getElementById ? doc.getElementById('alertasPendencias') : null,
      globalContainer: doc && doc.getElementById ? doc.getElementById('alertaPontoGlobal') : null
    };
  }

  function needsEmployeePushNotification(permission, notificationsActive) {
    return permission === 'default' && notificationsActive === true;
  }

  function clearGlobalAlert(globalContainer) {
    if (!globalContainer) return false;
    globalContainer.classList.remove('mostrar');
    globalContainer.innerHTML = '';
    return true;
  }

  function isAdminAlertsRole(role) {
    return role === 'admin' || role === 'subadmin';
  }

  function resolveAlertsAdminId(user) {
    if (!user) return null;
    return user.role === 'admin' ? user.id : user.adminId;
  }

  function prepareInitialAdminAlerts(options) {
    const o = options || {}, alerts = [];
    const birthday = birthdayAlert({ employees: o.employees, managers: o.managers, adminId: o.adminId, now: o.now });
    if (birthday) alerts.push(birthday);
    const serviceOrders = pendingServiceOrdersAlert(o.services, o.adminId);
    if (serviceOrders) alerts.push(serviceOrders);
    const assistances = pendingAssistancesAlert(o.services, o.adminId);
    if (assistances) alerts.push(assistances);
    return alerts;
  }

  function preparePendingAdminRequestsAlerts(options) {
    const o = options || {}, alerts = [];
    const requisitions = pendingRequisitionsAlert(o.requisitions, o.adminId);
    if (requisitions) alerts.push(requisitions);
    const requests = pendingLeaveRequestsAlert(o.requests, o.adminId);
    if (requests) alerts.push(requests);
    return alerts;
  }

  function applyAlertsState(container, alerts, mobile) {
    if (!container) return false;
    if (!Array.isArray(alerts) || !alerts.length) {
      container.style.display = 'none';
      container.innerHTML = '';
      return false;
    }
    container.style.display = 'block';
    container.innerHTML = alertsCard({ alertas: alerts, mobile: mobile === true });
    return true;
  }
'''
assert view.count(marker)==1
view=view.replace(marker,helpers+marker,1)
oldexp='''    prepareRegulatoryRenewals: prepareRegulatoryRenewals,
    prepareShstRenewals: prepareShstRenewals,
    prepareWarehouseAlerts: prepareWarehouseAlerts
  };'''
newexp='''    prepareRegulatoryRenewals: prepareRegulatoryRenewals,
    prepareShstRenewals: prepareShstRenewals,
    prepareWarehouseAlerts: prepareWarehouseAlerts,
    alertsViewElements: alertsViewElements,
    needsEmployeePushNotification: needsEmployeePushNotification,
    clearGlobalAlert: clearGlobalAlert,
    isAdminAlertsRole: isAdminAlertsRole,
    resolveAlertsAdminId: resolveAlertsAdminId,
    prepareInitialAdminAlerts: prepareInitialAdminAlerts,
    preparePendingAdminRequestsAlerts: preparePendingAdminRequestsAlerts,
    applyAlertsState: applyAlertsState
  };'''
assert view.count(oldexp)==1
view=view.replace(oldexp,newexp,1)
assert "const CACHE = 'totalgest-v171';" in sw
sw=sw.replace("const CACHE = 'totalgest-v171';","const CACHE = 'totalgest-v172';",1)

app_path.write_text(app,encoding='utf-8'); view_path.write_text(view,encoding='utf-8'); sw_path.write_text(sw,encoding='utf-8')
assert block(app,'        function renderizarServicos() {')==services_before
assert block(app,'        function renderizarPonto() {')==point_before
assert block(app,'        function _guardarEdicaoPontoRegisto(regId) {')==persist_before
assert block(app,'        function _repararEntradasPresas() {')==repair_before
alerts=block(app,'        function renderizarAlertas() {')
for item in ['alertsViewElements(document)','needsEmployeePushNotification(','clearGlobalAlert(contGlobal)','isAdminAlertsRole(','resolveAlertsAdminId(','prepareInitialAdminAlerts({','preparePendingAdminRequestsAlerts({','applyAlertsState(cont, alertas, _ehPerfilMobile())']:
    assert alerts.count(item)==1,(item,alerts.count(item))
for item in ["_notificarPorFaseVencimento('contrato_vencer_", "_notificarPorFaseVencimento('frota_vencer_", "_notificarPorFaseVencimento('licenca_", "_notificarPorFaseVencimento('registo_previo_", "_notificarPorFaseVencimento('anepc_", "_notificarPorFaseVencimento('shst_"]:
    assert alerts.count(item)==1,(item,alerts.count(item))
print('SAFE_CUTS=8'); print('SERVICES_BLOCK_UNCHANGED=OK'); print('POINT_BLOCK_UNCHANGED=OK'); print('POINT_PERSISTENCE_UNCHANGED=OK'); print('POINT_REPAIR_UNCHANGED=OK'); print('ALERT_NOTIFICATION_SIDE_EFFECTS_PRESERVED=OK'); print('ALERTS_BEFORE_CHARS=',len(alerts_before)); print('ALERTS_AFTER_CHARS=',len(alerts)); print('ALERTS_AFTER_LINES=',alerts.count('\n')+1); print('STRUCTURE=OK')
