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

  function prepareMaintenanceContractAlerts(options) {
    const o = options || {};
    const items = (Array.isArray(o.contracts) ? o.contracts : []).filter(function (contract) {
      return contract.adminId === o.adminId && o.getMaintenanceState(o.getNextMaintenance(contract)).chave === 'a_vencer';
    }).map(function (contract) {
      return { contract: contract, days: o.getMaintenanceState(o.getNextMaintenance(contract)).dias };
    });
    return {
      items: items,
      alert: items.length ? { tipo: 'warning', titulo: items.length + ' ' + (items.length === 1 ? 'contrato de manutenção a vencer' : 'contratos de manutenção a vencer') + ' nos próximos 30 dias', sub: 'Verifique se é preciso gerar a OS de manutenção.', acao: "abrirSecao('contratos')" } : null
    };
  }

  function licenseExpiryState(admin, calculateDaysRemaining) {
    if (!admin || !admin.licenca || !admin.licenca.dataExpiracao) return null;
    return { days: calculateDaysRemaining(admin.licenca.dataExpiracao) };
  }

  function regulatoryRenewal(validity, options) {
    if (!validity) return null;
    const o = options || {};
    const days = o.calculateDaysRemaining(new Date(validity + 'T00:00:00').getTime());
    if (days > o.thresholdDays) return null;
    return {
      days: days,
      alert: { tipo: 'danger', titulo: '⚠️ ' + o.title, sub: 'Vence em ' + days + ' dia(s) (' + validity + '). ' + o.subtitle, acao: "abrirEditarPerfil()" }
    };
  }

  function prepareRegulatoryRenewals(options) {
    const o = options || {}, admin = o.admin || {};
    return {
      registoPrevio: regulatoryRenewal(admin.registoPrevioValidade, { calculateDaysRemaining: o.calculateDaysRemaining, thresholdDays: o.thresholdDays, title: 'Registo prévio a renovar', subtitle: 'Renove junto do Departamento de Segurança Privada da PSP.' }),
      anepc: regulatoryRenewal(admin.anepcValidade, { calculateDaysRemaining: o.calculateDaysRemaining, thresholdDays: o.thresholdDays, title: 'Registo ANEPC a renovar', subtitle: 'Renove junto da ANEPC.' })
    };
  }

  function personAgeOnDate(birthDate, now) {
    if (!birthDate) return null;
    const birth = new Date(birthDate + 'T00:00:00');
    let age = now.getFullYear() - birth.getFullYear();
    const beforeBirthday = now.getMonth() < birth.getMonth() || (now.getMonth() === birth.getMonth() && now.getDate() < birth.getDate());
    if (beforeBirthday) age--;
    return age;
  }

  function prepareShstRenewals(options) {
    const o = options || {}, now = o.now instanceof Date ? o.now : new Date(o.now || Date.now());
    const people = (Array.isArray(o.employees) ? o.employees : []).concat(Array.isArray(o.managers) ? o.managers : []).filter(function (person) {
      return person.adminId === o.adminId && person.suspenso !== true && person.shstUltimaConsulta;
    });
    return people.map(function (person) {
      const age = personAgeOnDate(person.dataNascimento, now);
      const periodicityYears = age == null ? 1 : (age >= 50 ? 1 : 2);
      const expiry = new Date(person.shstUltimaConsulta + 'T00:00:00');
      expiry.setFullYear(expiry.getFullYear() + periodicityYears);
      const days = o.calculateDaysRemaining(expiry.getTime());
      return { person: person, expiry: expiry, days: days };
    }).filter(function (item) { return item.days <= 30; }).map(function (item) {
      item.alert = { tipo: 'danger', titulo: '⚠️ SHST a renovar — ' + item.person.nome, sub: 'Consulta de medicina do trabalho vence em ' + item.days + ' dia(s) (' + item.expiry.toLocaleDateString('pt-PT') + ').', acao: "abrirModal('funcionario','" + item.person.id + "')" };
      return item;
    });
  }

  function prepareWarehouseAlerts(options) {
    const o = options || {}, alerts = [];
    const lowStock = (Array.isArray(o.articles) ? o.articles : []).filter(function (article) {
      return article.adminId === o.adminId && article.alertaStock === true && article.stockMinimo != null && o.getCurrentStock(article.id) <= article.stockMinimo;
    }).length;
    if (lowStock) alerts.push({ tipo: 'warning', titulo: lowStock + ' ' + (lowStock === 1 ? 'artigo em falta' : 'artigos em falta'), sub: 'Stock no mínimo ou abaixo — reponha o armazém.', acao: "abrirSecao('artigos')" });
    const works = new Set();
    (Array.isArray(o.workMaterials) ? o.workMaterials : []).forEach(function (material) {
      if (material.adminId === o.adminId && (material.qtdConsumida || 0) > (material.qtdPrevista || 0)) works.add(material.obraId);
    });
    if (works.size) alerts.push({ tipo: 'warning', titulo: works.size + ' ' + (works.size === 1 ? 'obra com excedente de materiais' : 'obras com excedente de materiais'), sub: 'Consumo acima do previsto. Verifique o plano da obra.', acao: "abrirSecao('obras')" });
    return alerts;
  }

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

  window.TotalGestAlertsView = {
    alertsCard: alertsCard,
    isEmployeeAlertsRole: isEmployeeAlertsRole,
    employeeAlertState: employeeAlertState,
    employeeAlertCardHtml: employeeAlertCardHtml,
    employeeGlobalAlertHtml: employeeGlobalAlertHtml,
    applyEmployeeAlertState: applyEmployeeAlertState,
    birthdayAlert: birthdayAlert,
    pendingServiceOrdersAlert: pendingServiceOrdersAlert,
    pendingAssistancesAlert: pendingAssistancesAlert,
    pendingRequisitionsAlert: pendingRequisitionsAlert,
    pendingLeaveRequestsAlert: pendingLeaveRequestsAlert,
    latestFleetMaintenance: latestFleetMaintenance,
    fleetVehicleAttention: fleetVehicleAttention,
    prepareFleetAttention: prepareFleetAttention,
    prepareMaintenanceContractAlerts: prepareMaintenanceContractAlerts,
    licenseExpiryState: licenseExpiryState,
    prepareRegulatoryRenewals: prepareRegulatoryRenewals,
    prepareShstRenewals: prepareShstRenewals,
    prepareWarehouseAlerts: prepareWarehouseAlerts,
    alertsViewElements: alertsViewElements,
    needsEmployeePushNotification: needsEmployeePushNotification,
    clearGlobalAlert: clearGlobalAlert,
    isAdminAlertsRole: isAdminAlertsRole,
    resolveAlertsAdminId: resolveAlertsAdminId,
    prepareInitialAdminAlerts: prepareInitialAdminAlerts,
    preparePendingAdminRequestsAlerts: preparePendingAdminRequestsAlerts,
    applyAlertsState: applyAlertsState,
    runMaintenanceContractAlertFlow: runMaintenanceContractAlertFlow,
    runFleetAlertFlow: runFleetAlertFlow,
    runLicenseAlertFlow: runLicenseAlertFlow,
    runRegulatoryAlertFlow: runRegulatoryAlertFlow,
    runShstAlertFlow: runShstAlertFlow,
    runWarehouseAlertFlow: runWarehouseAlertFlow
  };
})();
