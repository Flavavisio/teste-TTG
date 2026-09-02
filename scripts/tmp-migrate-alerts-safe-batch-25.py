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

old_employee='''            if (['funcionario', 'encarregado', 'vendedor', 'vigilante', 'supervisor_vigilantes'].includes(usuarioLogado?.role)) {
                const hojeF = getDataHoje();
                const jaPicou = (dados.ponto || []).some(p => p.funcionarioId === usuarioLogado.id && p.data === hojeF && p.entrada);
                const precisaAtivarPush = (typeof Notification !== 'undefined' && Notification.permission === 'default') && moduloNotificacoesAtivo(adminDoUtilizador());
                const botaoNotif = precisaAtivarPush
                    ? `<button class="btn btn-sm" style="margin-left:auto;background:#0ea5e9;color:#fff;" onclick="_ativarNotificacoesPush()"><i class="fas fa-bell"></i> Ativar lembretes no telemóvel</button>`
                    : '';
                if (!jaPicou || precisaAtivarPush) {
                    cont.style.display = 'block';
                    cont.innerHTML = (!jaPicou ? `<div class="home-card" style="border-left:4px solid #f59e0b;margin-bottom:10px;">
                        <div style="display:flex;align-items:center;gap:10px;flex-wrap:wrap;">
                            <i class="fas fa-clock" style="color:#f59e0b;font-size:1.3rem;"></i>
                            <div><strong>Ainda não picaste o ponto hoje.</strong><br><span style="font-size:.85rem;color:#64748b;">Não te esqueças de registar a tua entrada.</span></div>
                            ${botaoNotif}
                        </div>
                    </div>` : (precisaAtivarPush ? `<div class="home-card" style="border-left:4px solid #0ea5e9;">
                        <div style="display:flex;align-items:center;gap:10px;flex-wrap:wrap;">
                            <i class="fas fa-bell" style="color:#0ea5e9;font-size:1.3rem;"></i>
                            <div><strong>Ativa as notificações no telemóvel</strong><br><span style="font-size:.85rem;color:#64748b;">Recebe logo os avisos de novas OS e lembretes de ponto.</span></div>
                            ${botaoNotif}
                        </div>
                    </div>` : ''));
                    if (contGlobal) {
                        contGlobal.classList.add('mostrar');
                        // No topo do telemóvel, o pedido para ativar as notificações tem sempre prioridade
                        // sobre o aviso de ponto — é a primeira coisa que a pessoa deve ver ao abrir a app.
                        if (precisaAtivarPush) {
                            contGlobal.innerHTML = `<div class="conteudo-alerta" style="justify-content:space-between;">
                                <div style="display:flex;align-items:center;gap:10px;min-width:0;">
                                    <i class="fas fa-bell" style="color:#0ea5e9;"></i>
                                    <div style="min-width:0;"><strong>Ativa as notificações</strong><div class="sub">${!jaPicou ? 'E não te esqueças: ainda não picaste o ponto hoje.' : 'Recebe avisos de novas OS e lembretes de ponto.'}</div></div>
                                </div>
                                <button class="btn btn-sm" style="background:#0ea5e9;color:#fff;flex-shrink:0;" onclick="event.stopPropagation();_ativarNotificacoesPush()"><i class="fas fa-bell"></i> Ativar</button>
                            </div>`;
                        } else {
                            contGlobal.innerHTML = `<div class="conteudo-alerta" onclick="abrirSecao('ponto')" style="cursor:pointer;">
                                <i class="fas fa-clock" style="color:#f59e0b;"></i>
                                <div><strong>Ainda não picaste o ponto hoje.</strong><div class="sub">Toca aqui para ires a "Registo de Ponto".</div></div>
                            </div>`;
                        }
                    }
                } else {
                    cont.style.display = 'none'; cont.innerHTML = '';
                    if (contGlobal) { contGlobal.classList.remove('mostrar'); contGlobal.innerHTML = ''; }
                }
                return;
            }'''
new_employee='''            if (window.TotalGestAlertsView.isEmployeeAlertsRole(usuarioLogado?.role)) {
                const precisaAtivarPush = (typeof Notification !== 'undefined' && Notification.permission === 'default') && moduloNotificacoesAtivo(adminDoUtilizador());
                const employeeAlertState = window.TotalGestAlertsView.employeeAlertState({
                    points: dados.ponto || [],
                    userId: usuarioLogado.id,
                    today: getDataHoje(),
                    needsPush: precisaAtivarPush
                });
                window.TotalGestAlertsView.applyEmployeeAlertState({ container: cont, globalContainer: contGlobal }, employeeAlertState);
                return;
            }'''
assert app.count(old_employee)==1,app.count(old_employee); app=app.replace(old_employee,new_employee,1)

old_birthday='''            const _hojeAniv = new Date();
            const _md = (m, d) => String(m).padStart(2, '0') + '-' + String(d).padStart(2, '0');
            const _hojeMD = _md(_hojeAniv.getMonth() + 1, _hojeAniv.getDate());
            const _aniversariantes = [
                ...(dados.funcionarios || []).filter(f => f.adminId === adminId && f.dataNascimento),
                ...(dados.encarregados || []).filter(e => e.adminId === adminId && e.dataNascimento)
            ].filter(p => { const _dn = (p.dataNascimento || '').split('-'); return _dn.length === 3 && _md(+_dn[1], +_dn[2]) === _hojeMD; });
            if (_aniversariantes.length) {
                const _nomes = _aniversariantes.map(p => p.nome).join(', ');
                alertas.push({ tipo: 'info', titulo: `🎂 ${_aniversariantes.length === 1 ? _aniversariantes[0].nome + ' faz anos hoje' : _nomes + ' fazem anos hoje'}`, sub: 'Aproveite para o(a) cumprimentar!', acao: '' });
            }'''
new_birthday='''            const birthdayAlert = window.TotalGestAlertsView.birthdayAlert({
                employees: dados.funcionarios || [],
                managers: dados.encarregados || [],
                adminId: adminId,
                now: new Date()
            });
            if (birthdayAlert) alertas.push(birthdayAlert);'''
assert app.count(old_birthday)==1,app.count(old_birthday); app=app.replace(old_birthday,new_birthday,1)

insert='''
  function isEmployeeAlertsRole(role) {
    return ['funcionario', 'encarregado', 'vendedor', 'vigilante', 'supervisor_vigilantes'].includes(role);
  }

  function employeeAlertState(options) {
    const o = options || {};
    const punched = (Array.isArray(o.points) ? o.points : []).some(function (point) {
      return point.funcionarioId === o.userId && point.data === o.today && point.entrada;
    });
    return { punched: punched, needsPush: o.needsPush === true, show: !punched || o.needsPush === true };
  }

  function employeePushButtonHtml(needsPush) {
    return needsPush ? '<button class="btn btn-sm" style="margin-left:auto;background:#0ea5e9;color:#fff;" onclick="_ativarNotificacoesPush()"><i class="fas fa-bell"></i> Ativar lembretes no telemóvel</button>' : '';
  }

  function employeeAlertCardHtml(state) {
    const s = state || {}, button = employeePushButtonHtml(s.needsPush === true);
    if (!s.punched) return `<div class="home-card" style="border-left:4px solid #f59e0b;margin-bottom:10px;">
                        <div style="display:flex;align-items:center;gap:10px;flex-wrap:wrap;">
                            <i class="fas fa-clock" style="color:#f59e0b;font-size:1.3rem;"></i>
                            <div><strong>Ainda não picaste o ponto hoje.</strong><br><span style="font-size:.85rem;color:#64748b;">Não te esqueças de registar a tua entrada.</span></div>
                            ${button}
                        </div>
                    </div>`;
    if (s.needsPush) return `<div class="home-card" style="border-left:4px solid #0ea5e9;">
                        <div style="display:flex;align-items:center;gap:10px;flex-wrap:wrap;">
                            <i class="fas fa-bell" style="color:#0ea5e9;font-size:1.3rem;"></i>
                            <div><strong>Ativa as notificações no telemóvel</strong><br><span style="font-size:.85rem;color:#64748b;">Recebe logo os avisos de novas OS e lembretes de ponto.</span></div>
                            ${button}
                        </div>
                    </div>`;
    return '';
  }

  function employeeGlobalAlertHtml(state) {
    const s = state || {};
    if (s.needsPush) return `<div class="conteudo-alerta" style="justify-content:space-between;">
                                <div style="display:flex;align-items:center;gap:10px;min-width:0;">
                                    <i class="fas fa-bell" style="color:#0ea5e9;"></i>
                                    <div style="min-width:0;"><strong>Ativa as notificações</strong><div class="sub">${!s.punched ? 'E não te esqueças: ainda não picaste o ponto hoje.' : 'Recebe avisos de novas OS e lembretes de ponto.'}</div></div>
                                </div>
                                <button class="btn btn-sm" style="background:#0ea5e9;color:#fff;flex-shrink:0;" onclick="event.stopPropagation();_ativarNotificacoesPush()"><i class="fas fa-bell"></i> Ativar</button>
                            </div>`;
    if (!s.punched) return `<div class="conteudo-alerta" onclick="abrirSecao('ponto')" style="cursor:pointer;">
                                <i class="fas fa-clock" style="color:#f59e0b;"></i>
                                <div><strong>Ainda não picaste o ponto hoje.</strong><div class="sub">Toca aqui para ires a "Registo de Ponto".</div></div>
                            </div>`;
    return '';
  }

  function applyEmployeeAlertState(elements, state) {
    const e = elements || {}, s = state || {};
    if (!e.container) return false;
    if (s.show) {
      e.container.style.display = 'block';
      e.container.innerHTML = employeeAlertCardHtml(s);
      if (e.globalContainer) {
        e.globalContainer.classList.add('mostrar');
        e.globalContainer.innerHTML = employeeGlobalAlertHtml(s);
      }
    } else {
      e.container.style.display = 'none';
      e.container.innerHTML = '';
      if (e.globalContainer) {
        e.globalContainer.classList.remove('mostrar');
        e.globalContainer.innerHTML = '';
      }
    }
    return true;
  }

  function birthdayAlert(options) {
    const o = options || {}, now = o.now instanceof Date ? o.now : new Date(o.now || Date.now());
    const md = function (m, d) { return String(m).padStart(2, '0') + '-' + String(d).padStart(2, '0'); };
    const todayMd = md(now.getMonth() + 1, now.getDate());
    const people = (Array.isArray(o.employees) ? o.employees : []).concat(Array.isArray(o.managers) ? o.managers : []).filter(function (person) {
      if (person.adminId !== o.adminId || !person.dataNascimento) return false;
      const parts = String(person.dataNascimento).split('-');
      return parts.length === 3 && md(+parts[1], +parts[2]) === todayMd;
    });
    if (!people.length) return null;
    const names = people.map(function (person) { return person.nome; }).join(', ');
    return { tipo: 'info', titulo: '🎂 ' + (people.length === 1 ? people[0].nome + ' faz anos hoje' : names + ' fazem anos hoje'), sub: 'Aproveite para o(a) cumprimentar!', acao: '' };
  }
'''
marker='\n  window.TotalGestAlertsView = {'
assert view.count(marker)==1
view=view.replace(marker,insert+marker,1)
old_export='''  window.TotalGestAlertsView = {
    alertsCard: alertsCard
  };'''
new_export='''  window.TotalGestAlertsView = {
    alertsCard: alertsCard,
    isEmployeeAlertsRole: isEmployeeAlertsRole,
    employeeAlertState: employeeAlertState,
    employeeAlertCardHtml: employeeAlertCardHtml,
    employeeGlobalAlertHtml: employeeGlobalAlertHtml,
    applyEmployeeAlertState: applyEmployeeAlertState,
    birthdayAlert: birthdayAlert
  };'''
assert view.count(old_export)==1
view=view.replace(old_export,new_export,1)
assert "const CACHE = 'totalgest-v167';" in sw
sw=sw.replace("const CACHE = 'totalgest-v167';","const CACHE = 'totalgest-v168';",1)

app_path.write_text(app,encoding='utf-8'); view_path.write_text(view,encoding='utf-8'); sw_path.write_text(sw,encoding='utf-8')
assert block(app,'        function renderizarServicos() {')==services_before
assert block(app,'        function renderizarPonto() {')==point_before
assert block(app,'        function _guardarEdicaoPontoRegisto(regId) {')==persist_before
assert block(app,'        function _repararEntradasPresas() {')==repair_before
alerts=block(app,'        function renderizarAlertas() {')
for item in ['isEmployeeAlertsRole(','employeeAlertState({','applyEmployeeAlertState({ container: cont, globalContainer: contGlobal }, employeeAlertState)','birthdayAlert({']:
    assert alerts.count(item)==1,(item,alerts.count(item))
for item in ['const botaoNotif =','const _aniversariantes = [','const _hojeMD =']:
    assert item not in alerts,item
for item in ["_notificarPorFaseVencimento('contrato_vencer_", "_notificarPorFaseVencimento('frota_vencer_", "_notificarPorFaseVencimento('licenca_", "_notificarPorFaseVencimento('registo_previo_", "_notificarPorFaseVencimento('anepc_", "_notificarPorFaseVencimento('shst_"]:
    assert alerts.count(item)==1,(item,alerts.count(item))
print('SAFE_CUTS=6'); print('SERVICES_BLOCK_UNCHANGED=OK'); print('POINT_BLOCK_UNCHANGED=OK'); print('POINT_PERSISTENCE_UNCHANGED=OK'); print('POINT_REPAIR_UNCHANGED=OK'); print('ALERT_NOTIFICATION_SIDE_EFFECTS_PRESERVED=OK'); print('ALERTS_BEFORE_CHARS=',len(alerts_before)); print('ALERTS_AFTER_CHARS=',len(alerts)); print('ALERTS_AFTER_LINES=',alerts.count('\n')+1); print('STRUCTURE=OK')
