/* Total Gest — renderização do painel O Meu Dia. */
(function () {
  'use strict';

  function run(options) {
    const opts = options || {};
    const forcarDesktop = opts.forceDesktop;
    const document = opts.document;
    const window = opts.window;
    const alert = opts.alert;
    const confirm = opts.confirm;
    const usuarioLogado = opts.user;
    const dados = opts.data;
    const _ehPerfilMobile = opts.isMobileProfile;
    const getDataHoje = opts.getToday;
    const escapeHtmlSimples = opts.escapeHtml;
    const _osMapaInfo = opts.mapInfo;
    const obterNomeCliente = opts.clientName;
    const _obraLongaPontoAberto = opts.longWorkOpenClock;
    const _botaoPontoObraHTML = opts.longWorkClockButtonHtml;
    const _moradaCompletaObra = opts.fullWorkAddress;
    const _htmlPainelAdminHoje = opts.adminTodayHtml;
    const _htmlResumoEquipaHoje = opts.teamTodayHtml;
    const _tgmMostrarTempo = opts.showWeather;
    const _tgmAplicarGrelhaDesktop = opts.applyDesktopGrid;

            const cont = document.getElementById('omeudia');
            if (!cont) return;
            // Se este painel já vive dentro da Home do admin/subadmin no desktop (movido para lá
            // por renderizarHomeDashboard), trata sempre como "forçado" — sem isto, a atualização
            // periódica em segundo plano (que chama esta função sem argumento nenhum) voltava a
            // escondê-lo, desfazendo o layout lado a lado sempre que atualizava sozinha.
            const dentroDaHomeDesktop = cont.parentElement && cont.parentElement.id === 'homeAgendaWrap';
            if (!_ehPerfilMobile() && !forcarDesktop && !dentroDaHomeDesktop) { cont.style.display = 'none'; return; }
            // Se já navegaste para outra secção (ex.: Ordens Serviço), não deixar uma
            // atualização periódica em segundo plano repor "O Meu Dia" visível por baixo dela —
            // era isso que causava o painel a "ressurgir" sozinho ao trocar de menu.
            if (!forcarDesktop && !dentroDaHomeDesktop && document.querySelector('.section-container.active')) { cont.style.display = 'none'; return; }
            // "Alertas e Pendências" pode ter sido movido para dentro deste painel (na Home do
            // desktop) — e esta função reconstrói tudo com cont.innerHTML mais abaixo. Sem isto,
            // qualquer chamada a esta função (incluindo a atualização periódica em segundo plano,
            // que não sabe nada disto) destruía esse elemento de vez, fazendo-o desaparecer
            // sozinho ao fim de alguns segundos. Por isso protege-se aqui mesmo, na origem —
            // não só no sítio que o move para lá — para cobrir TODAS as chamadas a esta função.
            if (dentroDaHomeDesktop) {
                const alertasElProteger = document.getElementById('homeAlertas');
                if (alertasElProteger && alertasElProteger.parentElement === cont) {
                    cont.parentElement.insertBefore(alertasElProteger, cont);
                }
            }
            const hoje = getDataHoje();
            // Vigilante tem um "O Meu Dia" próprio e mais simples — não faz OS/obras. A execução
            // da ronda em si vive inteiramente no TOTALGEST_RONDAS.html (ficheiro à parte, como o
            // CRM/Assist) — aqui é só um atalho para lá, sem duplicar a lógica de rondas.
            if (usuarioLogado?.role === 'vigilante') {
                cont.style.display = 'block';
                const abertoGeralVig = (dados.ponto || []).find(p => !p.servicoId && !p.obraId && p.funcionarioId === usuarioLogado.id && p.data === hoje && p.entrada && !p.saida);
                const pontoHtmlVig = abertoGeralVig
                    ? `<button type="button" class="btn tgm-btn-saida tgm-btn-ponto" style="width:100%;" onclick="picarPonto()"><i class="fas fa-stop-circle"></i> Saída <span class="tgm-mono">${abertoGeralVig.entrada}</span></button>`
                    : `<button type="button" class="btn tgm-btn-entrada tgm-btn-ponto" style="width:100%;" onclick="picarPonto()"><i class="fas fa-fingerprint"></i> Entrada</button>`;
                // Seguro de Acidentes de Trabalho — só mostra se estiver mesmo preenchido no
                // perfil dele; senão não vale a pena ocupar espaço no "O Meu Dia".
                const funcVig = dados.funcionarios?.find(f => f.id === usuarioLogado.id);
                const _fmtDataVig = d => d ? new Date(d + 'T00:00:00').toLocaleDateString('pt-PT') : null;
                const seguroHtml = (funcVig && (funcVig.apoliceNumero || funcVig.apoliceSeguradora || funcVig.apoliceValidade)) ? `
                    <div class="tgm-panel tgm-panel--dia" style="margin-top:14px;">
                        <div class="tgm-eyebrow">O meu perfil</div>
                        <div class="tgm-title"><i class="fas fa-shield-halved"></i> Seguro de Acidentes de Trabalho</div>
                        <div style="font-size:.85rem;color:#334155;margin-top:6px;line-height:1.6;">
                            ${funcVig.apoliceSeguradora ? `<div><strong>Seguradora:</strong> ${escapeHtmlSimples(funcVig.apoliceSeguradora)}</div>` : ''}
                            ${funcVig.apoliceNumero ? `<div><strong>Apólice nº:</strong> ${escapeHtmlSimples(funcVig.apoliceNumero)}</div>` : ''}
                            ${funcVig.apoliceValidade ? `<div><strong>Validade:</strong> ${_fmtDataVig(funcVig.apoliceValidade)}</div>` : ''}
                        </div>
                    </div>` : '';
                cont.innerHTML = `
                    <div class="tgm-panel tgm-panel--dia">
                        <div class="tgm-eyebrow">Agenda de hoje</div>
                        <div class="tgm-title"><i class="fas fa-clock"></i> Ponto</div>
                        ${pontoHtmlVig}
                        <a href="javascript:void(0)" onclick="abrirSecao('ponto')" style="display:block;text-align:center;margin-top:8px;font-size:.82rem;color:#0f766e;font-weight:600;text-decoration:none;"><i class="fas fa-list-check"></i> Ver o meu registo de ponto</a>
                    </div>
                    <div class="tgm-panel tgm-panel--dia" style="margin-top:14px;">
                        <div class="tgm-eyebrow">Agenda de hoje</div>
                        <div class="tgm-title"><i class="fas fa-shield-halved"></i> Rondas</div>
                        <p style="color:#64748b;margin:8px 0 10px;">Abre as tuas rondas de hoje.</p>
                        <a href="TOTALGEST_RONDAS.html" target="_blank" rel="noopener" class="btn btn-primary" style="width:100%;padding:14px;text-decoration:none;justify-content:center;"><i class="fas fa-arrow-right"></i> Abrir Rondas</a>
                    </div>
                    ${seguroHtml}
                `;
                return;
            }
            // Para admin/sub-admin, "a minha empresa" é a própria conta; para os restantes, é o adminId a que pertencem.
            const adminId = (usuarioLogado.role === 'admin') ? usuarioLogado.id : (usuarioLogado.adminId || usuarioLogado.id);
            const meuId = usuarioLogado.id;

            // Ponto geral
            const abertoGeral = (dados.ponto || []).find(p => !p.servicoId && !p.obraId && p.funcionarioId === meuId && p.data === hoje && p.entrada && !p.saida);
            const pontoHtml = abertoGeral
                ? `<button type="button" class="btn tgm-btn-saida tgm-btn-ponto" onclick="picarPonto()"><i class="fas fa-stop-circle"></i> Saída <span class="tgm-mono">${abertoGeral.entrada}</span></button>`
                : `<button type="button" class="btn tgm-btn-entrada tgm-btn-ponto" onclick="picarPonto()"><i class="fas fa-fingerprint"></i> Entrada</button>`;

            const _vejoTudo = ['admin', 'subadmin'].includes(usuarioLogado.role);

            // OS de hoje — só as que o próprio está associado (dar entrada é uma ação pessoal, não
            // faz sentido admin/sub-admin verem entrada disponível numa OS que não é deles; a
            // visão geral da empresa já existe à parte, no resumo da equipa mais abaixo).
            const minhasOS = (dados.servicos || []).filter(s => s.adminId === adminId && s.data === hoje && s.status !== 'concluído' && s.status !== 'cancelado'
                && (((s.funcionariosIds && s.funcionariosIds.length) ? s.funcionariosIds : [s.funcionarioId].filter(Boolean)).includes(meuId)))
                .sort((a, b) => (a.hora || '99:99').localeCompare(b.hora || '99:99')); // sem hora fica sempre no fim

            // Obras ativas — mesma regra: admin/sub-admin têm acesso a todas, mesmo sem estarem alocados
            const minhasObras = (dados.obras || []).filter(o => o.adminId === adminId && o.estado !== 'concluida'
                && (_vejoTudo || (((o.responsaveisIds && o.responsaveisIds.length) ? o.responsaveisIds : [o.responsavelId].filter(Boolean)).includes(meuId))));
            const _botaoMapa = (urlInfo, servicoId) => urlInfo ? `<a href="${urlInfo.url}" target="_blank" rel="noopener" onclick="event.stopPropagation();${servicoId ? `_registarKmViagemOS('${servicoId}');` : ''}" class="tgm-btn-mapa" title="${urlInfo.exato ? 'Navegar (Google Maps)' : 'Navegar por morada (Google Maps)'}"><i class="fas fa-diamond-turn-right"></i></a>${urlInfo?.wazeUrl ? `<a href="${urlInfo.wazeUrl}" target="_blank" rel="noopener" onclick="event.stopPropagation();${servicoId ? `_registarKmViagemOS('${servicoId}');` : ''}" class="tgm-btn-mapa" title="Navegar no Waze"><i class="fas fa-w" style="font-family:sans-serif;font-style:normal;font-weight:800;">W</i></a>` : ''}` : '';

            const linhaOS = s => {
                const aberto = (dados.ponto || []).find(p => p.servicoId === s.id && p.funcionarioId === meuId && p.entrada && !p.saida);
                const btn = aberto
                    ? `<button type="button" class="btn btn-sm tgm-btn-saida" onclick="picarPontoOS('${s.id}','saida')"><i class="fas fa-stop-circle"></i> Saída</button>`
                    : `<button type="button" class="btn btn-sm tgm-btn-entrada" onclick="picarPontoOS('${s.id}','entrada')"><i class="fas fa-fingerprint"></i> Entrada</button>`;
                const btnVer = `<button type="button" class="btn btn-sm btn-outline tgm-btn-ver" onclick="abrirVerOS('${s.id}')"><i class="fas fa-eye"></i> Ver OS</button>`;
                const cliente = dados.clientes?.find(c => c.id === s.clienteId);
                const morada = cliente ? [cliente.morada, cliente.codigoPostal, cliente.localidade].filter(Boolean).join(', ') : '';
                const urlInfo = _osMapaInfo(s.clienteId, s.morada || morada, s.localId);
                const _atrasada = s.hora && !aberto && s.hora < new Date().toTimeString().slice(0, 5);
                const btnLigar = cliente?.telefone ? `<button type="button" class="tgm-btn-mapa" title="Ligar a ${escapeHtmlSimples(obterNomeCliente(s.clienteId) || 'cliente')}" onclick="event.stopPropagation();_ligarClienteOS('${s.id}')"><i class="fas fa-phone"></i></button>` : '';
                const btnWhatsapp = cliente?.telefone ? `<a href="${_whatsappUrlOS(cliente.telefone)}" target="_blank" rel="noopener" class="tgm-btn-mapa" title="Abrir WhatsApp" onclick="event.stopPropagation();" style="color:#25D366;"><i class="fab fa-whatsapp"></i></a>` : '';
                const btnObs = (s.observacoes && s.observacoes.trim()) ? `<button type="button" class="tgm-btn-mapa" title="Ver observações" onclick="event.stopPropagation();_verObservacoesOS('${s.id}')"><i class="fas fa-comment-dots"></i></button>` : '';
                const _materiaisDestaOS = s.obraId ? (dados.obraMateriais || []).filter(m => m.obraId === s.obraId) : [];
                const btnMateriais = _materiaisDestaOS.length ? `<button type="button" class="tgm-btn-mapa" title="Ver materiais desta OS" onclick="event.stopPropagation();_verMateriaisOS('${s.id}')"><i class="fas fa-boxes-stacked"></i></button>` : '';
                return `<div class="tgm-row tgm-row--os">
                    ${aberto ? '<span class="tgm-live-dot" title="Em curso"></span>' : ''}
                    <div class="tgm-row-icon tgm-row-icon--os"><i class="fas fa-wrench"></i></div>
                    <div class="tgm-row-txt">
                        <div class="tgm-row-title">${escapeHtmlSimples(obterNomeCliente(s.clienteId) || 'OS')}</div>
                        <div class="tgm-row-sub">${s.hora ? `<span class="tgm-mono tgm-hora">${s.hora}</span> · ` : ''}${escapeHtmlSimples((s.descricao || '').slice(0, 50))}${_atrasada ? ' <span style="color:#dc2626;font-weight:700;">· Atrasada</span>' : ''}</div>
                    </div>
                    <div class="tgm-row-acoes">
                        <div class="tgm-row-acoes-top">${btn}</div>
                        ${btnVer}
                    </div>
                </div>
                ${(btnObs || btnMateriais || btnLigar || btnWhatsapp || _botaoMapa(urlInfo, s.id)) ? `<div class="tgm-row-extra" style="display:flex;gap:8px;justify-content:flex-end;margin:-6px 0 8px;padding-right:2px;">${btnObs}${btnMateriais}${btnLigar}${btnWhatsapp}${_botaoMapa(urlInfo, s.id)}</div>` : ''}`;
            };
            // Ligar ao cliente: pergunta explicitamente pelo nome antes de abrir o marcador
            // (tel:), para evitar toques acidentais no botão a ligarem sem querer.
            window._ligarClienteOS = function(servicoId) {
                const s = (dados.servicos || []).find(x => x.id === servicoId); if (!s) return;
                const cliente = dados.clientes?.find(c => c.id === s.clienteId);
                if (!cliente?.telefone) { alert('Este cliente não tem telefone registado.'); return; }
                if (!confirm('Ligar ao cliente ' + (cliente.nome || obterNomeCliente(s.clienteId) || '') + '?\n' + cliente.telefone)) return;
                window.location.href = 'tel:' + cliente.telefone.replace(/\s+/g, '');
            };
            // Ver observações da OS num popup simples, sem ter de abrir o "Ver OS" completo.
            window._verObservacoesOS = function(servicoId) {
                const s = (dados.servicos || []).find(x => x.id === servicoId); if (!s) return;
                alert('Observações da OS — ' + (obterNomeCliente(s.clienteId) || '') + ':\n\n' + (s.observacoes || '(sem observações)'));
            };
            // Lista rápida (popup) dos materiais estipulados na Obra de origem desta OS —
            // previsto vs. já consumido, sem precisar de abrir o "Ver OS" completo.
            window._verMateriaisOS = function(servicoId) {
                const s = (dados.servicos || []).find(x => x.id === servicoId); if (!s || !s.obraId) return;
                const mats = (dados.obraMateriais || []).filter(m => m.obraId === s.obraId);
                if (!mats.length) { alert('Sem materiais estipulados para esta OS.'); return; }
                const linhas = mats.map(m => {
                    const art = dados.artigos?.find(a => a.id === m.artigoId);
                    const prev = Number(m.qtdPrevista) || 0, cons = Number(m.qtdConsumida) || 0;
                    const unid = art ? (art.unidade || 'un') : '';
                    const estado = cons >= prev && prev > 0 ? '✅' : (cons > 0 ? '🟡' : '⚪');
                    return estado + ' ' + (art ? art.nome : '(artigo removido)') + ' — Previsto: ' + prev + ' ' + unid + ' · Consumido: ' + cons + ' ' + unid;
                }).join('\n');
                alert('Materiais desta OS — ' + (obterNomeCliente(s.clienteId) || '') + ':\n\n' + linhas);
            };
            // Equivalentes das funções acima, mas para o card de Obra em "O Meu Dia" — mesmo
            // padrão, só muda a entidade (obra em vez de OS).
            window._ligarClienteObra = function(obraId) {
                const o = (dados.obras || []).find(x => x.id === obraId); if (!o) return;
                const cliente = dados.clientes?.find(c => c.id === o.clienteId);
                if (!cliente?.telefone) { alert('Este cliente não tem telefone registado.'); return; }
                if (!confirm('Ligar ao cliente ' + (cliente.nome || obterNomeCliente(o.clienteId) || '') + '?\n' + cliente.telefone)) return;
                window.location.href = 'tel:' + cliente.telefone.replace(/\s+/g, '');
            };
            window._verObservacoesObra = function(obraId) {
                const o = (dados.obras || []).find(x => x.id === obraId); if (!o) return;
                alert('Observações da Obra — ' + (obterNomeCliente(o.clienteId) || '') + ':\n\n' + (o.observacoes || '(sem observações)'));
            };
            window._verMateriaisObra = function(obraId) {
                const o = (dados.obras || []).find(x => x.id === obraId); if (!o) return;
                const mats = (dados.obraMateriais || []).filter(m => m.obraId === obraId);
                if (!mats.length) { alert('Sem materiais estipulados para esta Obra.'); return; }
                const linhas = mats.map(m => {
                    const art = dados.artigos?.find(a => a.id === m.artigoId);
                    const prev = Number(m.qtdPrevista) || 0, cons = Number(m.qtdConsumida) || 0;
                    const unid = art ? (art.unidade || 'un') : '';
                    const estado = cons >= prev && prev > 0 ? '✅' : (cons > 0 ? '🟡' : '⚪');
                    return estado + ' ' + (art ? art.nome : '(artigo removido)') + ' — Previsto: ' + prev + ' ' + unid + ' · Consumido: ' + cons + ' ' + unid;
                }).join('\n');
                alert('Materiais desta Obra — ' + (obterNomeCliente(o.clienteId) || '') + ':\n\n' + linhas);
            };
            // Formata o telefone para o link do WhatsApp (wa.me exige indicativo de país,
            // sem espaços nem símbolos). Assume Portugal (351) quando o número já não tem
            // um indicativo (números portugueses normais têm 9 dígitos).
            function _whatsappFormatarTelefone(telefone) {
                let limpo = (telefone || '').replace(/\D/g, '');
                if (limpo.length === 9) limpo = '351' + limpo;
                return limpo;
            }
            function _whatsappUrlOS(telefone, mensagem) {
                const numero = _whatsappFormatarTelefone(telefone);
                return `https://wa.me/${numero}` + (mensagem ? `?text=${encodeURIComponent(mensagem)}` : '');
            }
            const linhaObra = o => {
                const aberto = _obraLongaPontoAberto ? _obraLongaPontoAberto(o.id) : null;
                const btn = _botaoPontoObraHTML(o) || `<button type="button" class="btn btn-sm btn-outline" onclick="abrirObraLongaDetalhe('${o.id}')">Ver</button>`;
                const btnVer = `<button type="button" class="btn btn-sm btn-outline tgm-btn-ver" onclick="abrirObraLongaDetalhe('${o.id}')"><i class="fas fa-eye"></i> Ver Obra</button>`;
                const morada = _moradaCompletaObra(o);
                const urlInfo = _osMapaInfo(o.clienteId, morada !== '—' ? morada : '', o.localId);
                const cliente = dados.clientes?.find(c => c.id === o.clienteId);
                // "Iniciada" — já houve pelo menos uma entrada registada nesta obra, alguma vez
                // (não só hoje) — diferente de "Em curso" (tgm-live-dot), que é só agora mesmo.
                const jaIniciou = (dados.obraPontoLonga || []).some(p => p.obraId === o.id && p.entrada);
                const btnLigar = cliente?.telefone ? `<button type="button" class="tgm-btn-mapa" title="Ligar a ${escapeHtmlSimples(obterNomeCliente(o.clienteId) || 'cliente')}" onclick="event.stopPropagation();_ligarClienteObra('${o.id}')"><i class="fas fa-phone"></i></button>` : '';
                const btnWhatsapp = cliente?.telefone ? `<a href="${_whatsappUrlOS(cliente.telefone)}" target="_blank" rel="noopener" class="tgm-btn-mapa" title="Abrir WhatsApp" onclick="event.stopPropagation();" style="color:#25D366;"><i class="fab fa-whatsapp"></i></a>` : '';
                const btnObs = (o.observacoes && o.observacoes.trim()) ? `<button type="button" class="tgm-btn-mapa" title="Ver observações" onclick="event.stopPropagation();_verObservacoesObra('${o.id}')"><i class="fas fa-comment-dots"></i></button>` : '';
                const _materiaisDestaObra = (dados.obraMateriais || []).filter(m => m.obraId === o.id);
                const btnMateriais = _materiaisDestaObra.length ? `<button type="button" class="tgm-btn-mapa" title="Ver materiais desta Obra" onclick="event.stopPropagation();_verMateriaisObra('${o.id}')"><i class="fas fa-boxes-stacked"></i></button>` : '';
                return `<div class="tgm-row tgm-row--obra">
                    ${aberto ? '<span class="tgm-live-dot" title="Em curso"></span>' : ''}
                    <div class="tgm-row-icon tgm-row-icon--obra"><i class="fas fa-hard-hat"></i></div>
                    <div class="tgm-row-txt">
                        <div class="tgm-row-title">${escapeHtmlSimples(o.nome)}</div>
                        <div class="tgm-row-sub">${o.dataInicioPrevista ? `<span class="tgm-mono tgm-hora">${o.dataInicioPrevista.split('-').reverse().join('/')}</span> · ` : ''}${escapeHtmlSimples(obterNomeCliente(o.clienteId) || '')}${jaIniciou ? ' <span style="color:#16a34a;font-weight:700;">· Iniciada</span>' : ' <span style="color:#94a3b8;">· Ainda não iniciada</span>'}</div>
                    </div>
                    <div class="tgm-row-acoes">
                        <div class="tgm-row-acoes-top">${btn}</div>
                        ${btnVer}
                    </div>
                </div>
                ${(btnObs || btnMateriais || btnLigar || btnWhatsapp || _botaoMapa(urlInfo, null)) ? `<div class="tgm-row-extra" style="display:flex;gap:8px;justify-content:flex-end;margin:-6px 0 8px;padding-right:2px;">${btnObs}${btnMateriais}${btnLigar}${btnWhatsapp}${_botaoMapa(urlInfo, null)}</div>` : ''}`;
            };

            cont.style.display = 'block';
            cont.innerHTML = `
                <div class="tgm-panel tgm-panel--dia">
                    <div class="tgm-panel-head">
                        <div>
                            <div class="tgm-eyebrow">Agenda de hoje</div>
                            <div class="tgm-title"><i class="fas fa-sun"></i> O Meu Dia</div>
                            <div class="tgm-date">${new Date(hoje + 'T12:00:00').toLocaleDateString('pt-PT', { weekday: 'long', day: '2-digit', month: '2-digit' })}</div>
                        </div>
                        ${pontoHtml}
                    </div>
                    <div id="tgmTempoWidget"></div>
                    ${minhasOS.length ? `<div class="tgm-lista">${minhasOS.map(linhaOS).join('')}</div>` : `<p class="tgm-vazio">${_vejoTudo ? 'Sem OS marcadas para hoje.' : 'Sem OS atribuídas a ti hoje.'}</p>`}
                </div>
                ${['admin', 'subadmin'].includes(usuarioLogado.role) ? _htmlPainelAdminHoje(adminId, hoje) : ''}
                ${['admin', 'subadmin'].includes(usuarioLogado.role) ? _htmlResumoEquipaHoje(adminId, hoje) : ''}
                <div class="tgm-panel tgm-panel--obras">
                    <div class="tgm-eyebrow">Em curso</div>
                    <div class="tgm-title tgm-title--sm"><i class="fas fa-hard-hat"></i> Obras Ativas</div>
                    ${minhasObras.length ? `<div class="tgm-lista">${minhasObras.map(linhaObra).join('')}</div>` : `<p class="tgm-vazio">${_vejoTudo ? 'Sem obras ativas de momento.' : 'Sem obras ativas atribuídas a ti.'}</p>`}
                </div>
            `;
            _tgmMostrarTempo();
            // Reaplica sempre a moldagem da grelha do desktop (Alertas ao lado de "O Meu Dia",
            // etc.) mesmo quando quem chamou esta função foi a atualização periódica em segundo
            // plano (que não sabe nada disto) — assim fica protegido em qualquer chamada, não só
            // na que vem de renderizarHomeDashboard.
            if (dentroDaHomeDesktop) _tgmAplicarGrelhaDesktop(cont);
        
  }

  window.TotalGestMyDay = { run: run };
})();
