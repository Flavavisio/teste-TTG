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

pairs=[
("""            const osPend = (dados.servicos || []).filter(s => s.adminId === adminId && (s.status || 'pendente') === 'pendente').length;
            if (osPend) alertas.push({ tipo: 'info', titulo: `${osPend} ${osPend === 1 ? 'ordem de serviço pendente' : 'ordens de serviço pendentes'}`, sub: 'Atribua ou inicie as ordens para manter o fluxo.', acao: "abrirSecao('agenda-obras')" });""",
"""            const pendingServiceOrdersAlert = window.TotalGestAlertsView.pendingServiceOrdersAlert(dados.servicos || [], adminId);
            if (pendingServiceOrdersAlert) alertas.push(pendingServiceOrdersAlert);"""),
("""            const assistPend = (dados.servicos || []).filter(s => s.adminId === adminId && s.status === 'por aprovar').length;
            if (assistPend) alertas.push({ tipo: 'warning', titulo: `${assistPend} ${assistPend === 1 ? 'pedido de assistência por aprovar' : 'pedidos de assistência por aprovar'}`, sub: 'Pedidos enviados pelos clientes no Portal. Aprove ou rejeite.', acao: "abrirSecao('servicos')" });""",
"""            const pendingAssistancesAlert = window.TotalGestAlertsView.pendingAssistancesAlert(dados.servicos || [], adminId);
            if (pendingAssistancesAlert) alertas.push(pendingAssistancesAlert);"""),
("""            const reqPend = (dados.requisicoes || []).filter(r => r.adminId === adminId && (r.status === 'pendente' || r.status === 'pendente_aprov')).length;
            if (reqPend) alertas.push({ tipo: 'info', titulo: `${reqPend} ${reqPend === 1 ? 'requisição pendente' : 'requisições pendentes'}`, sub: 'Há requisições a aguardar resposta.', acao: "abrirSecao('requisicoes')" });""",
"""            const pendingRequisitionsAlert = window.TotalGestAlertsView.pendingRequisitionsAlert(dados.requisicoes || [], adminId);
            if (pendingRequisitionsAlert) alertas.push(pendingRequisitionsAlert);"""),
("""            const pedPend = (dados.pedidos || []).filter(p => p.adminId === adminId && (p.status === 'pendente' || p.status === 'pendente_aprov')).length;
            if (pedPend) alertas.push({ tipo: 'info', titulo: `${pedPend} ${pedPend === 1 ? 'pedido de férias/faltas pendente' : 'pedidos de férias/faltas pendentes'}`, sub: 'Há pedidos a aguardar aprovação.', acao: "abrirSecao('pedidos')" });""",
"""            const pendingLeaveRequestsAlert = window.TotalGestAlertsView.pendingLeaveRequestsAlert(dados.pedidos || [], adminId);
            if (pendingLeaveRequestsAlert) alertas.push(pendingLeaveRequestsAlert);""")]
for old,new in pairs:
    assert app.count(old)==1,(old[:40],app.count(old)); app=app.replace(old,new,1)

marker='\n  window.TotalGestAlertsView = {'
helpers='''
  function pendingServiceOrdersAlert(services, adminId) {
    const count = (Array.isArray(services) ? services : []).filter(function (service) {
      return service.adminId === adminId && (service.status || 'pendente') === 'pendente';
    }).length;
    if (!count) return null;
    return { tipo: 'info', titulo: count + ' ' + (count === 1 ? 'ordem de serviço pendente' : 'ordens de serviço pendentes'), sub: 'Atribua ou inicie as ordens para manter o fluxo.', acao: "abrirSecao('agenda-obras')" };
  }

  function pendingAssistancesAlert(services, adminId) {
    const count = (Array.isArray(services) ? services : []).filter(function (service) {
      return service.adminId === adminId && service.status === 'por aprovar';
    }).length;
    if (!count) return null;
    return { tipo: 'warning', titulo: count + ' ' + (count === 1 ? 'pedido de assistência por aprovar' : 'pedidos de assistência por aprovar'), sub: 'Pedidos enviados pelos clientes no Portal. Aprove ou rejeite.', acao: "abrirSecao('servicos')" };
  }

  function pendingRequisitionsAlert(requisitions, adminId) {
    const count = (Array.isArray(requisitions) ? requisitions : []).filter(function (request) {
      return request.adminId === adminId && (request.status === 'pendente' || request.status === 'pendente_aprov');
    }).length;
    if (!count) return null;
    return { tipo: 'info', titulo: count + ' ' + (count === 1 ? 'requisição pendente' : 'requisições pendentes'), sub: 'Há requisições a aguardar resposta.', acao: "abrirSecao('requisicoes')" };
  }

  function pendingLeaveRequestsAlert(requests, adminId) {
    const count = (Array.isArray(requests) ? requests : []).filter(function (request) {
      return request.adminId === adminId && (request.status === 'pendente' || request.status === 'pendente_aprov');
    }).length;
    if (!count) return null;
    return { tipo: 'info', titulo: count + ' ' + (count === 1 ? 'pedido de férias/faltas pendente' : 'pedidos de férias/faltas pendentes'), sub: 'Há pedidos a aguardar aprovação.', acao: "abrirSecao('pedidos')" };
  }
'''
assert view.count(marker)==1; view=view.replace(marker,helpers+marker,1)
oldexp='''    applyEmployeeAlertState: applyEmployeeAlertState,
    birthdayAlert: birthdayAlert
  };'''
newexp='''    applyEmployeeAlertState: applyEmployeeAlertState,
    birthdayAlert: birthdayAlert,
    pendingServiceOrdersAlert: pendingServiceOrdersAlert,
    pendingAssistancesAlert: pendingAssistancesAlert,
    pendingRequisitionsAlert: pendingRequisitionsAlert,
    pendingLeaveRequestsAlert: pendingLeaveRequestsAlert
  };'''
assert view.count(oldexp)==1; view=view.replace(oldexp,newexp,1)
assert "const CACHE = 'totalgest-v168';" in sw; sw=sw.replace("const CACHE = 'totalgest-v168';","const CACHE = 'totalgest-v169';",1)

app_path.write_text(app,encoding='utf-8'); view_path.write_text(view,encoding='utf-8'); sw_path.write_text(sw,encoding='utf-8')
assert block(app,'        function renderizarServicos() {')==services_before
assert block(app,'        function renderizarPonto() {')==point_before
assert block(app,'        function _guardarEdicaoPontoRegisto(regId) {')==persist_before
assert block(app,'        function _repararEntradasPresas() {')==repair_before
alerts=block(app,'        function renderizarAlertas() {')
for item in ['pendingServiceOrdersAlert(','pendingAssistancesAlert(','pendingRequisitionsAlert(','pendingLeaveRequestsAlert(']: assert alerts.count(item)==1,(item,alerts.count(item))
for item in ['const osPend =','const assistPend =','const reqPend =','const pedPend =']: assert item not in alerts,item
for item in ["_notificarPorFaseVencimento('contrato_vencer_", "_notificarPorFaseVencimento('frota_vencer_", "_notificarPorFaseVencimento('licenca_", "_notificarPorFaseVencimento('registo_previo_", "_notificarPorFaseVencimento('anepc_", "_notificarPorFaseVencimento('shst_"]:
    assert alerts.count(item)==1,(item,alerts.count(item))
print('SAFE_CUTS=4'); print('SERVICES_BLOCK_UNCHANGED=OK'); print('POINT_BLOCK_UNCHANGED=OK'); print('POINT_PERSISTENCE_UNCHANGED=OK'); print('POINT_REPAIR_UNCHANGED=OK'); print('ALERT_NOTIFICATION_SIDE_EFFECTS_PRESERVED=OK'); print('ALERTS_BEFORE_CHARS=',len(alerts_before)); print('ALERTS_AFTER_CHARS=',len(alerts)); print('ALERTS_AFTER_LINES=',alerts.count('\n')+1); print('STRUCTURE=OK')
