/* Total Gest — política de visibilidade dos cartões principais. */
(function () {
  'use strict';

  function run(options) {
    const opts = options || {};
    const document = opts.document;
    const usuarioLogado = opts.user;
    const dados = opts.data;
    const localStorage = opts.localStorage;
    const _licencaValidaTenant = opts.licenseValid;
    const moduloFrotaAtivo = opts.moduleFleetActive;
    const adminDoUtilizador = opts.userAdmin;
    const _utilizadorTemVeiculo = opts.userHasVehicle;
    const moduloCrmAtivo = opts.moduleCrmActive;
    const moduloRondasAtivo = opts.moduleRoundsActive;
    const adminAtual = opts.currentAdmin;
    const moduloAssistAtivo = opts.moduleAssistActive;
    const moduloErpAtivo = opts.moduleErpActive;
    const moduloArmazemAtivo = opts.moduleWarehouseActive;
    const moduloContratosAtivo = opts.moduleContractsActive;

            if (!_licencaValidaTenant()) {
                const permitidos = (usuarioLogado.role === 'admin' || usuarioLogado.role === 'subadmin')
                    ? ['assiduidade', 'minha-licenca']
                    : ['ponto'];
                document.querySelectorAll('.card-principal').forEach(card => {
                    card.classList.toggle('hidden-card', !permitidos.includes(card.dataset.card));
                });
                return;
            }
            const cards = document.querySelectorAll('.card-principal');
            const isSuperAdmin = usuarioLogado?.role === 'superadmin';
            const isAdmin = usuarioLogado?.role === 'admin' || usuarioLogado?.role === 'subadmin';
            const isEncarregado = usuarioLogado?.role === 'encarregado';
            const isFuncionario = usuarioLogado?.role === 'funcionario';
            const isAutenticado = !!usuarioLogado;

            // Vendedor: papel muito restrito — só Ponto, Férias/Faltas, Frota (só se tiver
            // veículo atribuído, e só vê o seu), Manual/Guia, e CRM Comercial quando existir.
            if (usuarioLogado?.role === 'vendedor') {
                const podeFrotaVend = moduloFrotaAtivo(adminDoUtilizador()) && _utilizadorTemVeiculo();
                const podeCrmVend = moduloCrmAtivo(adminDoUtilizador());
                const permitidosVendedor = ['ponto', 'pedidos', 'calendario-equipa', 'guia', 'contactos', 'ajuda-peticoes'];
                cards.forEach(card => {
                    const cardName = card.dataset.card;
                    if (cardName === 'frota') { card.classList.toggle('hidden-card', !podeFrotaVend); return; }
                    if (cardName === 'crm') { card.classList.toggle('hidden-card', !podeCrmVend); return; }
                    card.classList.toggle('hidden-card', !permitidosVendedor.includes(cardName));
                });
                return;
            }

            // Vigilante e Supervisor de Vigilantes: mesmo layout dos funcionários (menu inferior,
            // "O Meu Dia"...), mas só com acesso a picar o ponto, férias/faltas, e às Rondas do
            // dia (se o addon estiver ativo) — nada de OS, Obras, Frota, Agenda, etc. Isto vale
            // também no PC (não só no telemóvel) — antes o Supervisor não tinha nenhum bloco
            // próprio e caía na lógica genérica lá em baixo, que deixava passar coisas como a
            // Agenda de Planeamento de Obras.
            if (usuarioLogado?.role === 'vigilante' || usuarioLogado?.role === 'supervisor_vigilantes') {
                const podeRondasVig = moduloRondasAtivo(adminDoUtilizador());
                const permitidosVigilante = ['ponto', 'pedidos'];
                cards.forEach(card => {
                    const cardName = card.dataset.card;
                    if (cardName === 'rondas') { card.classList.toggle('hidden-card', !podeRondasVig); return; }
                    card.classList.toggle('hidden-card', !permitidosVigilante.includes(cardName));
                });
                return;
            }

            // Distribuidor: não é uma empresa operacional normal — só faz sentido ter acesso à
            // sua própria área de revenda, ao suporte da Total Gest, e à auditoria da conta dele.
            // Tudo o resto (Funcionários, Obras, OS, Armazém, etc.) fica escondido.
            if (usuarioLogado?.role === 'admin' && adminAtual()?.ehDistribuidor) {
                const permitidosDistribuidor = ['distribuicao', 'ajuda-peticoes', 'auditoria', 'licencas', 'licencas-vencer', 'reports'];
                cards.forEach(card => {
                    card.classList.toggle('hidden-card', !permitidosDistribuidor.includes(card.dataset.card));
                });
                return;
            }

            cards.forEach(card => {
                const cardName = card.dataset.card;

                if (cardName === 'crm') {
                    card.classList.toggle('hidden-card', !(isAdmin && moduloCrmAtivo(adminAtual())));
                    return;
                }
                if (cardName === 'assistencias') {
                    card.classList.toggle('hidden-card', !(isAdmin && moduloAssistAtivo(adminAtual())));
                    return;
                }
                if (cardName === 'rondas') {
                    // Como o CRM: card só existe para quem tem a licença ativa. Sem addon, nem
                    // aparece — nunca fica "greyed out" a convidar a comprar (diferente da Frota).
                    card.classList.toggle('hidden-card', !(
                        (isAdmin && moduloRondasAtivo(adminAtual())) ||
                        ((usuarioLogado?.role === 'supervisor_vigilantes' || usuarioLogado?.role === 'vigilante') && moduloRondasAtivo(adminDoUtilizador()))
                    ));
                    return;
                }
                if (cardName === 'erp') {
                    card.classList.toggle('hidden-card', !(isAdmin && moduloErpAtivo(adminAtual())));
                    return;
                }
                if (cardName === 'distribuicao') {
                    card.classList.toggle('hidden-card', !(isAdmin && adminAtual()?.ehDistribuidor));
                    return;
                }

                if (['superadmin', 'licencas', 'licencas-vencer', 'pedidos-renovacao', 'historico-licencas', 'online-admins', 'licencas-distribuidor', 'uso-cards', 'analytics'].includes(cardName)) {
                    if (isSuperAdmin) {
                        card.classList.remove('hidden-card');
                    } else {
                        card.classList.add('hidden-card');
                    }
                    return;
                }

                if (cardName === 'guia') {
                    if (isAdmin || isEncarregado || isFuncionario) { card.classList.remove('hidden-card'); } else { card.classList.add('hidden-card'); }
                    return;
                }

                if (cardName === 'auditoria') {
                    if (isAdmin || usuarioLogado?.role === 'superadmin') { card.classList.remove('hidden-card'); } else { card.classList.add('hidden-card'); }
                    return;
                }

                if (cardName === 'ajuda-peticoes') {
                    if (isSuperAdmin || isAdmin || isEncarregado) {
                        card.classList.remove('hidden-card');
                    } else {
                        card.classList.add('hidden-card');
                    }
                    return;
                }

                if (cardName === 'contactos') {
                    if (isAutenticado) {
                        card.classList.add('hidden-card');
                    } else {
                        card.classList.remove('hidden-card');
                    }
                    return;
                }

                if (cardName === 'agenda-obras') {
                    if (isAdmin || isEncarregado) { card.classList.remove('hidden-card'); }
                    else if (isFuncionario) {
                        const adminId = usuarioLogado.adminId || usuarioLogado.id;
                        const temOS = (dados.servicos || []).some(s => {
                            const atribuidos = (s.funcionariosIds && s.funcionariosIds.length) ? s.funcionariosIds : [s.funcionarioId].filter(Boolean);
                            return s.adminId === adminId && atribuidos.includes(usuarioLogado.id) && s.status !== 'por aprovar';
                        });
                        card.classList.toggle('hidden-card', !temOS);
                    } else { card.classList.add('hidden-card'); }
                    return;
                }

                if (['artigos', 'encomendas', 'fornecedores', 'financeiro'].includes(cardName)) {
                    if (isAdmin) {
                        card.classList.remove('hidden-card');
                        const ativo = moduloArmazemAtivo(adminAtual());
                        card.classList.toggle('card-modulo-inativo', !ativo);
                        card.title = ativo ? '' : 'Add-on Armazém / Stock / Gestão de Obras — 9,99€/mês. Clica para ativar em "Minha Licença".';
                    } else { card.classList.add('hidden-card'); }
                    return;
                }

                if (cardName === 'obras') {
                    if (isAdmin) {
                        card.classList.remove('hidden-card');
                        const ativo = moduloArmazemAtivo(adminAtual());
                        card.classList.toggle('card-modulo-inativo', !ativo);
                        card.title = ativo ? '' : 'Add-on Armazém / Stock / Gestão de Obras — 9,99€/mês. Clica para ativar em "Minha Licença".';
                    }
                    else if ((isEncarregado || isFuncionario) && moduloArmazemAtivo(adminDoUtilizador())) { card.classList.remove('hidden-card'); }
                    else { card.classList.add('hidden-card'); }
                    return;
                }

                if (cardName === 'obras-longa') {
                    if (isAdmin) {
                        card.classList.remove('hidden-card');
                        const ativo = moduloArmazemAtivo(adminAtual());
                        card.classList.toggle('card-modulo-inativo', !ativo);
                        card.title = ativo ? '' : 'Add-on Armazém / Stock / Gestão de Obras — 9,99€/mês. Clica para ativar em "Minha Licença".';
                    }
                    else if ((isEncarregado || isFuncionario) && moduloArmazemAtivo(adminDoUtilizador())) { card.classList.remove('hidden-card'); }
                    else { card.classList.add('hidden-card'); }
                    return;
                }

                if (cardName === 'relatorio-os') {
                    if (isAdmin || usuarioLogado?.role === 'encarregado') {
                        card.classList.remove('hidden-card');
                    } else {
                        card.classList.add('hidden-card');
                    }
                    return;
                }

                if (cardName === 'assiduidade' || cardName === 'alertas-geofence') {
                    if (isAdmin) {
                        card.classList.remove('hidden-card');
                    } else {
                        card.classList.add('hidden-card');
                    }
                    return;
                }

                if (cardName === 'calendario-equipa') {
                    if (isAdmin || isEncarregado) { card.classList.remove('hidden-card'); } else { card.classList.add('hidden-card'); }
                    return;
                }

                if (cardName === 'mapa-equipa') {
                    if (isAdmin || isEncarregado) { card.classList.remove('hidden-card'); } else { card.classList.add('hidden-card'); }
                    return;
                }

                if (cardName === 'despesas') {
                    if (isAdmin) { card.classList.remove('hidden-card'); } else { card.classList.add('hidden-card'); }
                    return;
                }

                if (cardName === 'dashboard-analitico') {
                    if (isAdmin) { card.classList.remove('hidden-card'); } else { card.classList.add('hidden-card'); }
                    return;
                }

                if (cardName === 'reports') {
                    if (isSuperAdmin || isAdmin) {
                        card.classList.remove('hidden-card');
                    } else {
                        card.classList.add('hidden-card');
                    }
                    return;
                }

                if (cardName === 'agenda') {
                    card.classList.toggle('hidden-card', !(isAdmin || isEncarregado || isFuncionario));
                    return;
                }
                if (cardName === 'frota') {
                    if (isAdmin) {
                        card.classList.remove('hidden-card');
                        const ativo = moduloFrotaAtivo(adminAtual());
                        card.classList.toggle('card-modulo-inativo', !ativo);
                        card.title = ativo ? '' : 'Add-on Frota — 9,99€/mês. Clica para ativar em "Minha Licença".';
                    } else if ((isEncarregado || isFuncionario) && moduloFrotaAtivo(adminDoUtilizador()) && _utilizadorTemVeiculo()) {
                        card.classList.remove('hidden-card');
                    } else {
                        card.classList.add('hidden-card');
                    }
                    return;
                }

                if (cardName === 'contratos') {
                    if (isAdmin) {
                        card.classList.remove('hidden-card');
                        const ativo = moduloContratosAtivo(adminAtual());
                        card.classList.toggle('card-modulo-inativo', !ativo);
                        card.title = ativo ? '' : 'Add-on Contratos de Manutenção / SCIE — 14,99€/mês. Clica para ativar em "Minha Licença".';
                    } else {
                        card.classList.add('hidden-card');
                    }
                    return;
                }

                if (cardName === 'ferramentas') {
                    card.classList.toggle('hidden-card', !isAdmin);
                    return;
                }

                if (cardName === 'alertas-manutencao') {
                    card.classList.add('hidden-card');
                    return;
                }

                if (cardName === 'exportar-dados') {
                    card.classList.toggle('hidden-card', !isAdmin);
                    return;
                }

                if (['minha-licenca', 'funcionarios', 'encarregados', 'clientes'].includes(cardName)) {
                    if (isAdmin) {
                        card.classList.remove('hidden-card');
                        if (cardName === 'minha-licenca') {
                            const _admId = usuarioLogado.role === 'admin' ? usuarioLogado.id : usuarioLogado.adminId;
                            let _ateVerde = 0;
                            try { _ateVerde = parseInt(localStorage.getItem('tg_aprovacao_ate_' + _admId) || '0', 10); } catch (e) {}
                            const _emJanelaVerde = _ateVerde && Date.now() < _ateVerde;
                            const _temPendenteMeu = (dados.pedidosRenovacao || []).some(p => p.adminId === _admId && p.status === 'pendente');
                            card.classList.remove('pisca-amarelo', 'fixo-verde');
                            if (_emJanelaVerde) card.classList.add('fixo-verde');
                            else if (_temPendenteMeu) card.classList.add('pisca-amarelo');
                        }
                    } else {
                        card.classList.add('hidden-card');
                    }
                    return;
                }

                if (['servicos', 'ponto', 'pedidos', 'folhas', 'requisicoes'].includes(cardName)) {
                    if (isAdmin || isEncarregado || isFuncionario) {
                        card.classList.remove('hidden-card');
                    } else {
                        card.classList.add('hidden-card');
                    }
                    return;
                }

                if (['artigos', 'encomendas', 'fornecedores', 'obras'].includes(cardName)) {
                    card.classList.toggle('hidden-card', !isAdmin);
                    return;
                }

                if (!isAutenticado) {
                    card.classList.add('hidden-card');
                    return;
                }

                card.classList.remove('hidden-card');
            });
        
  }

  window.TotalGestCardVisibility = { run: run };
})();
