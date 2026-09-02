/* Total Gest — apresentação reutilizável de alertas */
(function () {
  'use strict';

  function icon(tipo) {
    if (tipo === 'danger') {
      return '<span class="alerta-ic danger"><i class="fas fa-triangle-exclamation"></i></span>';
    }
    if (tipo === 'warning') {
      return '<span class="alerta-ic warn"><i class="fas fa-exclamation-triangle"></i></span>';
    }
    return '<span class="alerta-ic info"><i class="fas fa-info"></i></span>';
  }

  function alertLines(alertas) {
    return (alertas || []).map(function (alerta) {
      return `<div class="alerta-linha ${alerta.tipo === 'danger' ? 'danger' : ''}" onclick="${alerta.acao}">
                    ${icon(alerta.tipo)}
                    <div class="alerta-txt"><div class="alerta-t">${alerta.titulo}</div><div class="alerta-s">${alerta.sub}</div></div>
                    <i class="fas fa-chevron-right alerta-chev"></i>
                </div>`;
    }).join('');
  }

  function alertsCard(options) {
    options = options || {};
    const linhasHtml = alertLines(options.alertas);

    if (options.mobile === true) {
      return `<div class="alertas-card">
                    <div class="alertas-h alertas-h--acordeao" onclick="this.closest('.alertas-card').classList.toggle('aberto')">
                        <span style="display:flex;align-items:center;gap:8px;"><i class="fas fa-bell"></i> Alertas e Pendências <span class="tgm-live-dot tgm-live-dot--vermelho"></span></span>
                        <i class="fas fa-chevron-down alertas-acordeao-seta"></i>
                    </div>
                    <div class="alertas-corpo">${linhasHtml}</div>
                </div>`;
    }

    return `<div class="alertas-card">
                    <div class="alertas-h"><i class="fas fa-bell"></i> Alertas e Pendências</div>
                    ${linhasHtml}
                </div>`;
  }

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

  window.TotalGestAlertsView = {
    alertsCard: alertsCard,
    isEmployeeAlertsRole: isEmployeeAlertsRole,
    employeeAlertState: employeeAlertState,
    employeeAlertCardHtml: employeeAlertCardHtml,
    employeeGlobalAlertHtml: employeeGlobalAlertHtml,
    applyEmployeeAlertState: applyEmployeeAlertState,
    birthdayAlert: birthdayAlert
  };
})();
