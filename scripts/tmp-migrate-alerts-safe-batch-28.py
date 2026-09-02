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

old_contracts='''            if (moduloContratosAtivo(adminRecAlerta)) {
                const contratosAVencerLista = (dados.contratos || []).filter(c => c.adminId === adminId && estadoManutencao(calcularProximaManutencao(c)).chave === 'a_vencer');
                if (contratosAVencerLista.length) alertas.push({ tipo: 'warning', titulo: `${contratosAVencerLista.length} ${contratosAVencerLista.length === 1 ? 'contrato de manutenção a vencer' : 'contratos de manutenção a vencer'} nos próximos 30 dias`, sub: 'Verifique se é preciso gerar a OS de manutenção.', acao: "abrirSecao('contratos')" });
                contratosAVencerLista.forEach(c => {
                    const dias = estadoManutencao(calcularProximaManutencao(c)).dias;
                    _notificarPorFaseVencimento('contrato_vencer_' + adminId, c.id, dias, () => {
                        _notificarAdminESubadmin(adminId, '📄 Contrato de manutenção a vencer', 'Contrato ' + (c.numero || '#' + c.id) + ' — ' + _clienteLabel(dados.clientes?.find(cl => cl.id === c.clienteId) || {}) + ' vence em ' + dias + ' dia(s).', "abrirSecao('contratos')");
                    });
                });
            }'''
new_contracts='''            if (moduloContratosAtivo(adminRecAlerta)) {
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
            }'''
assert app.count(old_contracts)==1, app.count(old_contracts)
app=app.replace(old_contracts,new_contracts,1)

old_license='''            if (adminRecAlerta?.licenca?.dataExpiracao) {
                const diasLic = calcularDiasRestantes(adminRecAlerta.licenca.dataExpiracao);
                _notificarPorFaseVencimento('licenca_' + adminId, 'atual', diasLic, () => {
                    _notificarAdminESubadmin(adminId, '⏰ Licença a expirar', 'A licença da tua empresa expira em ' + diasLic + ' dia(s). Renova em "Minha Licença" para não perderes acesso.', "abrirSecao('minha-licenca')");
                });
            }'''
new_license='''            const licenseExpiry = window.TotalGestAlertsView.licenseExpiryState(adminRecAlerta, calcularDiasRestantes);
            if (licenseExpiry) {
                const diasLic = licenseExpiry.days;
                _notificarPorFaseVencimento('licenca_' + adminId, 'atual', diasLic, () => {
                    _notificarAdminESubadmin(adminId, '⏰ Licença a expirar', 'A licença da tua empresa expira em ' + diasLic + ' dia(s). Renova em "Minha Licença" para não perderes acesso.', "abrirSecao('minha-licenca')");
                });
            }'''
assert app.count(old_license)==1, app.count(old_license)
app=app.replace(old_license,new_license,1)

old_reg='''            // Registo prévio e ANEPC — alerta vermelho quando faltarem 6 meses (180 dias) para a renovação.
            const _seisMesesDias = 180;
            if (adminRecAlerta?.registoPrevioValidade) {
                const diasRP = calcularDiasRestantes(new Date(adminRecAlerta.registoPrevioValidade + 'T00:00:00').getTime());
                if (diasRP <= _seisMesesDias) {
                    alertas.push({ tipo: 'danger', titulo: `⚠️ Registo prévio a renovar`, sub: `Vence em ${diasRP} dia(s) (${adminRecAlerta.registoPrevioValidade}). Renove junto do Departamento de Segurança Privada da PSP.`, acao: "abrirEditarPerfil()" });
                    _notificarPorFaseVencimento('registo_previo_' + adminId, 'atual', diasRP, () => {
                        _notificarAdminESubadmin(adminId, '⚠️ Registo prévio a renovar', 'O registo prévio da tua empresa vence em ' + diasRP + ' dia(s). Trata da renovação junto da PSP.', "abrirEditarPerfil()");
                    });
                }
            }
            if (adminRecAlerta?.anepcValidade) {
                const diasAN = calcularDiasRestantes(new Date(adminRecAlerta.anepcValidade + 'T00:00:00').getTime());
                if (diasAN <= _seisMesesDias) {
                    alertas.push({ tipo: 'danger', titulo: `⚠️ Registo ANEPC a renovar`, sub: `Vence em ${diasAN} dia(s) (${adminRecAlerta.anepcValidade}). Renove junto da ANEPC.`, acao: "abrirEditarPerfil()" });
                    _notificarPorFaseVencimento('anepc_' + adminId, 'atual', diasAN, () => {
                        _notificarAdminESubadmin(adminId, '⚠️ Registo ANEPC a renovar', 'O registo ANEPC da tua empresa vence em ' + diasAN + ' dia(s). Trata da renovação junto da ANEPC.', "abrirEditarPerfil()");
                    });
                }
            }'''
new_reg='''            const regulatoryAlerts = window.TotalGestAlertsView.prepareRegulatoryRenewals({
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
            }'''
assert app.count(old_reg)==1, app.count(old_reg)
app=app.replace(old_reg,new_reg,1)

old_shst='''            // SHST — consulta de medicina do trabalho: avisa 30 dias antes de vencer, por
            // funcionário/encarregado. Só corre se o admin tiver o SHST ativo no Perfil.
            if (adminRecAlerta?.shstAtivo) {
                const _shstPessoas = [
                    ...(dados.funcionarios || []).filter(f => f.adminId === adminId && f.suspenso !== true),
                    ...(dados.encarregados || []).filter(e => e.adminId === adminId && e.suspenso !== true)
                ];
                _shstPessoas.forEach(p => {
                    if (!p.shstUltimaConsulta) return;
                    let periodicidadeAnos = 1;
                    if (p.dataNascimento) {
                        const nasc = new Date(p.dataNascimento + 'T00:00:00');
                        const hojeP = new Date();
                        let idade = hojeP.getFullYear() - nasc.getFullYear();
                        const aindaNaoFezAnos = (hojeP.getMonth() < nasc.getMonth()) || (hojeP.getMonth() === nasc.getMonth() && hojeP.getDate() < nasc.getDate());
                        if (aindaNaoFezAnos) idade--;
                        periodicidadeAnos = idade >= 50 ? 1 : 2;
                    }
                    const vencSHST = new Date(p.shstUltimaConsulta + 'T00:00:00');
                    vencSHST.setFullYear(vencSHST.getFullYear() + periodicidadeAnos);
                    const diasSHST = calcularDiasRestantes(vencSHST.getTime());
                    if (diasSHST <= 30) {
                        alertas.push({ tipo: 'danger', titulo: `⚠️ SHST a renovar — ${p.nome}`, sub: `Consulta de medicina do trabalho vence em ${diasSHST} dia(s) (${vencSHST.toLocaleDateString('pt-PT')}).`, acao: `abrirModal('funcionario','${p.id}')` });
                        _notificarPorFaseVencimento('shst_' + p.id, 'atual', diasSHST, () => {
                            _notificarAdminESubadmin(adminId, '⚠️ SHST a renovar', 'A consulta de medicina do trabalho de ' + p.nome + ' vence em ' + diasSHST + ' dia(s).', `abrirModal('funcionario','${p.id}')`);
                        });
                    }
                });
            }'''
new_shst='''            if (adminRecAlerta?.shstAtivo) {
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
            }'''
assert app.count(old_shst)==1, app.count(old_shst)
app=app.replace(old_shst,new_shst,1)

old_stock='''            if (moduloArmazemAtivo(adminAtual())) {
                const stockBaixo = (dados.artigos || []).filter(a => a.adminId === adminId && a.alertaStock === true && a.stockMinimo != null && stockAtualArtigo(a.id) <= a.stockMinimo).length;
                if (stockBaixo) alertas.push({ tipo: 'warning', titulo: `${stockBaixo} ${stockBaixo === 1 ? 'artigo em falta' : 'artigos em falta'}`, sub: 'Stock no mínimo ou abaixo — reponha o armazém.', acao: "abrirSecao('artigos')" });

                const obrasExced = new Set();
                (dados.obraMateriais || []).forEach(m => {
                    if (m.adminId === adminId && (m.qtdConsumida || 0) > (m.qtdPrevista || 0)) obrasExced.add(m.obraId);
                });
                if (obrasExced.size) alertas.push({ tipo: 'warning', titulo: `${obrasExced.size} ${obrasExced.size === 1 ? 'obra com excedente de materiais' : 'obras com excedente de materiais'}`, sub: 'Consumo acima do previsto. Verifique o plano da obra.', acao: "abrirSecao('obras')" });
            }'''
new_stock='''            if (moduloArmazemAtivo(adminAtual())) {
                const warehouseAlerts = window.TotalGestAlertsView.prepareWarehouseAlerts({
                    articles: dados.artigos || [],
                    workMaterials: dados.obraMateriais || [],
                    adminId: adminId,
                    getCurrentStock: stockAtualArtigo
                });
                warehouseAlerts.forEach(alert => alertas.push(alert));
            }'''
assert app.count(old_stock)==1, app.count(old_stock)
app=app.replace(old_stock,new_stock,1)

marker='\n  window.TotalGestAlertsView = {'
helpers='''
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
'''
assert view.count(marker)==1
view=view.replace(marker,helpers+marker,1)
oldexp='''    latestFleetMaintenance: latestFleetMaintenance,
    fleetVehicleAttention: fleetVehicleAttention,
    prepareFleetAttention: prepareFleetAttention
  };'''
newexp='''    latestFleetMaintenance: latestFleetMaintenance,
    fleetVehicleAttention: fleetVehicleAttention,
    prepareFleetAttention: prepareFleetAttention,
    prepareMaintenanceContractAlerts: prepareMaintenanceContractAlerts,
    licenseExpiryState: licenseExpiryState,
    prepareRegulatoryRenewals: prepareRegulatoryRenewals,
    prepareShstRenewals: prepareShstRenewals,
    prepareWarehouseAlerts: prepareWarehouseAlerts
  };'''
assert view.count(oldexp)==1
view=view.replace(oldexp,newexp,1)
assert "const CACHE = 'totalgest-v170';" in sw
sw=sw.replace("const CACHE = 'totalgest-v170';","const CACHE = 'totalgest-v171';",1)

app_path.write_text(app,encoding='utf-8'); view_path.write_text(view,encoding='utf-8'); sw_path.write_text(sw,encoding='utf-8')
assert block(app,'        function renderizarServicos() {')==services_before
assert block(app,'        function renderizarPonto() {')==point_before
assert block(app,'        function _guardarEdicaoPontoRegisto(regId) {')==persist_before
assert block(app,'        function _repararEntradasPresas() {')==repair_before
alerts=block(app,'        function renderizarAlertas() {')
for item in ['prepareMaintenanceContractAlerts({','licenseExpiryState(','prepareRegulatoryRenewals({','prepareShstRenewals({','prepareWarehouseAlerts({']:
    assert alerts.count(item)==1,(item,alerts.count(item))
for item in ["_notificarPorFaseVencimento('contrato_vencer_", "_notificarPorFaseVencimento('frota_vencer_", "_notificarPorFaseVencimento('licenca_", "_notificarPorFaseVencimento('registo_previo_", "_notificarPorFaseVencimento('anepc_", "_notificarPorFaseVencimento('shst_"]:
    assert alerts.count(item)==1,(item,alerts.count(item))
print('SAFE_CUTS=6'); print('SERVICES_BLOCK_UNCHANGED=OK'); print('POINT_BLOCK_UNCHANGED=OK'); print('POINT_PERSISTENCE_UNCHANGED=OK'); print('POINT_REPAIR_UNCHANGED=OK'); print('ALERT_NOTIFICATION_SIDE_EFFECTS_PRESERVED=OK'); print('ALERTS_BEFORE_CHARS=',len(alerts_before)); print('ALERTS_AFTER_CHARS=',len(alerts)); print('ALERTS_AFTER_LINES=',alerts.count('\n')+1); print('STRUCTURE=OK')
