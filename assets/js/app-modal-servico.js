/* Total Gest — formulário do modal de ordem de serviço. */
(function () {
  'use strict';
  function render(options) {
    const opts = options || {};
    const item = opts.item || null;
    const dados = opts.data || {};
    const usuarioLogado = opts.user || null;
    const _tenantId = function () { return opts.tenantId; };
    const getFuncionariosByAdmin = opts.getFuncionariosByAdmin;
    const _pessoasParaAtribuir = opts.pessoasParaAtribuir;
    const escapeHtmlSimples = opts.escapeHtmlSimples;
    const getDataHoje = opts.getDataHoje;
    const _clienteLabel = opts.clienteLabel;
    const moduloContratosAtivo = opts.moduloContratosAtivo;
    const obrasAvancadoAtivo = opts.obrasAvancadoAtivo;
    const moduloArmazemAtivo = opts.moduloArmazemAtivo;
    const adminAtual = function () { return opts.admin || null; };
    let html = '';
                let funcOpts = '';
                let clientes = [];
                let adminIdParaClientes = null;

                if (usuarioLogado?.role === 'admin' || usuarioLogado?.role === 'subadmin') {
                    adminIdParaClientes = _tenantId();
                    const funcionarios = getFuncionariosByAdmin(adminIdParaClientes);
                    const encarregados = (dados.encarregados || []).filter(e => e.adminId === _tenantId());
                    const fOpts = funcionarios.map(f => `<option value="${f.id}" ${item && item.funcionarioId === f.id ? 'selected' : ''}>${f.nome}</option>`).join('');
                    const eOpts = encarregados.map(e => `<option value="${e.id}" ${item && item.funcionarioId === e.id ? 'selected' : ''}>${e.nome}</option>`).join('');
                    funcOpts = `<option value="">Todos</option>`
                        + (fOpts ? `<optgroup label="Funcionários">${fOpts}</optgroup>` : '')
                        + (eOpts ? `<optgroup label="Encarregados">${eOpts}</optgroup>` : '');
                } else if (usuarioLogado?.role === 'encarregado') {
                    const encarregado = dados.encarregados?.find(e => e.id === usuarioLogado.id);
                    if (encarregado) {
                        adminIdParaClientes = encarregado.adminId;
                        const funcionarios = dados.funcionarios?.filter(f =>
                            encarregado.funcionariosIds?.includes(f.id) &&
                            f.role !== 'admin' &&
                            f.role !== 'superadmin'
                        ) || [];
                        const fOpts = funcionarios.map(f => `<option value="${f.id}" ${item && item.funcionarioId === f.id ? 'selected' : ''}>${f.nome}</option>`).join('');
                        funcOpts = `<option value="">Todos</option>`
                            + `<optgroup label="Eu (encarregado)"><option value="${encarregado.id}" ${item && item.funcionarioId === encarregado.id ? 'selected' : ''}>${encarregado.nome}</option></optgroup>`
                            + (fOpts ? `<optgroup label="Funcionários">${fOpts}</optgroup>` : '');
                    }
                } else if (usuarioLogado?.role === 'funcionario') {
                    const funcObj = dados.funcionarios?.find(f => f.id === usuarioLogado.id);
                    if (funcObj) {
                        adminIdParaClientes = funcObj.adminId;
                        funcOpts = `<option value="${usuarioLogado.id}" selected>${usuarioLogado.nome}</option>`;
                    }
                }

                // Clientes do admin
                if (adminIdParaClientes) {
                    clientes = dados.clientes?.filter(c => c.adminId === adminIdParaClientes) || [];
                }
                const cliOpts = clientes.map(c =>
                    `<option value="${c.id}" ${item && item.clienteId === c.id ? 'selected' : ''}>${c.nome}</option>`
                ).join('');
                const statusOpts = ['pendente', 'em andamento', 'stand by', 'concluído'].map(st =>
                    `<option value="${st}" ${item && item.status === st ? 'selected' : ''}>${st}</option>`
                ).join('');
                const _idsSelecionados = (item?.funcionariosIds?.length ? item.funcionariosIds : (item?.funcionarioId ? [item.funcionarioId] : []));
                let funcCheckOpts = '';
                if (usuarioLogado?.role === 'admin' || usuarioLogado?.role === 'subadmin') {
                    const _pessoas = _pessoasParaAtribuir(_tenantId());
                    funcCheckOpts = _pessoas.map(p => `
                        <label style="display:flex;align-items:center;gap:8px;padding:4px 0;cursor:pointer;">
                            <input type="checkbox" class="s-func-check" value="${p.id}" onchange="_sAtualizarFuncPrincipal()" ${_idsSelecionados.includes(p.id) ? 'checked' : ''} style="width:auto;" />
                            ${escapeHtmlSimples(p.nome)}
                        </label>`).join('');
                } else if (usuarioLogado?.role === 'encarregado') {
                    const encarregado = dados.encarregados?.find(e => e.id === usuarioLogado.id);
                    const _fs = encarregado ? (dados.funcionarios?.filter(f => encarregado.funcionariosIds?.includes(f.id) && f.role !== 'admin' && f.role !== 'superadmin') || []) : [];
                    const _todos = encarregado ? [{ id: encarregado.id, nome: encarregado.nome + ' (eu)' }, ..._fs] : _fs;
                    funcCheckOpts = _todos.map(p => `
                        <label style="display:flex;align-items:center;gap:8px;padding:4px 0;cursor:pointer;">
                            <input type="checkbox" class="s-func-check" value="${p.id}" onchange="_sAtualizarFuncPrincipal()" ${_idsSelecionados.includes(p.id) ? 'checked' : ''} style="width:auto;" />
                            ${escapeHtmlSimples(p.nome)}
                        </label>`).join('');
                }

                if (!funcOpts && usuarioLogado?.role !== 'funcionario' && usuarioLogado?.role !== 'encarregado' && usuarioLogado?.role !== 'vendedor') {
                    html = '<p class="text-muted">Não tem funcionários atribuídos para criar OS.</p>';
                } else {
                    const today = getDataHoje();
                    const now = new Date().toTimeString().slice(0, 5);
                    html = `
                        <div class="ff-wrap">
                        <div class="ff-hero">
                            <div class="ff-avatar-drop" style="cursor:default;">
                                <div class="ff-avatar-ph" style="display:flex;"><i class="fas fa-clipboard-list"></i></div>
                            </div>
                            <div class="ff-hero-fields">
                                <input type="text" id="s_cliente_busca" class="ff-nome-input" style="width:100%;flex:1 1 100%;box-sizing:border-box;display:block;" placeholder="Digite o nome ou nº do cliente…" value="${item && item.clienteId ? (() => { const cc = clientes.find(x => x.id === item.clienteId); return cc ? _clienteLabel(cc) : ''; })() : ''}" ${item && item.origem === 'portal' ? 'disabled' : ''} oninput="clienteBuscaInput('s_cliente_busca','s_cliente', _osPreencherMorada)" onfocus="clienteBuscaFoco('s_cliente_busca')" onblur="clienteBuscaEsconder('s_cliente_busca')" autocomplete="off" required />
                                <input type="hidden" id="s_cliente" value="${item && item.clienteId ? item.clienteId : ''}" />
                                <select id="s_status" class="ff-cargo-input" style="max-width:200px;" ${usuarioLogado?.role === 'funcionario' ? 'disabled' : ''}>${statusOpts}</select>
                                ${usuarioLogado?.role === 'funcionario' ? '<div class="help-text" style="margin-top:2px;">O estado muda automaticamente ao picar entrada/saída na Agenda de Obras.</div>' : ''}
                            </div>
                        </div>
                        <div id="s_cliente_ajuda"></div>
                        ${(!item && usuarioLogado?.role !== 'funcionario') ? '<div class="help-text" style="margin:-14px 0 14px;">Cliente não existe? <a href="#" onclick="fecharModal(); abrirModal(\'cliente\', null); return false;">Criar cliente</a> e volte a abrir a nova OS.</div>' : ''}
                        ${item && item.origem === 'portal' ? `<div class="help-text" style="margin:-14px 0 14px;"><i class="fas fa-lock"></i> Pedido enviado pelo cliente via Portal — o cliente não pode ser alterado.</div>` : ''}

                        <div class="ff-secao ff-tint-id">
                            <div class="ff-secao-head"><i class="fas fa-user-check"></i> Atribuição</div>
                            <div class="ff-secao-body">
                                <div class="form-group ff-span2"><label>Funcionário(s) *</label>
                                    ${usuarioLogado?.role === 'funcionario' ? `
                                        <input type="text" value="${usuarioLogado.nome}" disabled style="background:#e9edf2;" />
                                        <input type="hidden" id="s_funcionario" value="${usuarioLogado.id}" />
                                    ` : `
                                        <div id="s_func_checkboxes" style="max-height:150px;overflow-y:auto;border:1px solid #e2e8f0;border-radius:8px;padding:8px;">
                                            <label style="display:flex;align-items:center;gap:8px;padding:4px 0 8px;border-bottom:1px solid #f1f5f9;margin-bottom:4px;cursor:pointer;font-weight:700;">
                                                <input type="checkbox" id="s_func_todos" onchange="_sToggleTodosFuncionarios(this.checked)" style="width:auto;" /> Selecionar todos
                                            </label>
                                            ${funcCheckOpts}
                                        </div>
                                        <input type="hidden" id="s_funcionario" value="${(item?.funcionariosIds?.[0] || item?.funcionarioId || '')}" />
                                        <div class="help-text">Podes selecionar mais que um — cada um pica entrada/saída pela Agenda de Obras.</div>
                                        <div id="s_relatorio_responsavel_cont" style="display:none;margin-top:10px;">
                                            <label>Quem é o responsável por preencher o relatório e a folha de obra?</label>
                                            <select id="s_relatorio_responsavel"></select>
                                            <div class="help-text">Só esta pessoa vai ser convidada a preencher, ao dar saída. Os restantes atribuídos só picam entrada/saída, sem precisar de preencher nada.</div>
                                        </div>
                                    `}
                                </div>
                                <div class="form-group"><label>Data</label><input type="date" id="s_data" value="${item ? item.data : today}" /></div>
                                <div class="form-group"><label>Hora</label><input type="time" id="s_hora" value="${item ? item.hora : now}" /></div>
                            </div>
                        </div>

                        <div class="ff-secao ff-tint-id">
                            <div class="ff-secao-head"><i class="fas fa-note-sticky"></i> Descrição</div>
                            <div class="ff-secao-body">
                                <div class="form-group ff-span2">
                                    <div id="s_descricao_tags" style="display:flex;gap:6px;flex-wrap:wrap;margin-bottom:8px;"></div>
                                    <label style="display:block;font-size:.85rem;font-weight:700;margin-bottom:4px;">Descrição do trabalho * <span class="help-text" style="font-weight:400;">(mínimo 3 caracteres)</span></label>
                                    <textarea id="s_descricao" required minlength="3" placeholder="Ex.: Instalação de câmara CCTV no piso 1...">${item ? (item.descricao || '') : ''}</textarea>
                                </div>
                                <div class="form-group ff-span2">
                                    <label style="display:block;font-size:.85rem;font-weight:700;margin-bottom:4px;">Observações <span class="help-text" style="font-weight:400;">(opcional — visível ao técnico em "O Meu Dia")</span></label>
                                    <textarea id="s_observacoes" placeholder="Ex.: Cliente só pode receber depois das 14h, cão solto no quintal...">${item ? (item.observacoes || '') : ''}</textarea>
                                </div>
                            </div>
                        </div>

                        ${moduloContratosAtivo(dados.administradores?.find(a => a.id === (usuarioLogado.role === 'admin' ? usuarioLogado.id : usuarioLogado.adminId))) ? `
                        <div class="ff-secao ff-tint-id">
                            <div class="ff-secao-head"><i class="fas fa-tags"></i> Tipo de trabalho</div>
                            <div class="ff-secao-body">
                                <div class="form-group ff-span2">
                                    <div id="s_tipos_trabalho_cont" style="display:flex;flex-wrap:wrap;gap:8px;"></div>
                                    <div style="margin-top:8px;display:flex;gap:8px;align-items:center;flex-wrap:wrap;">
                                        <input type="text" id="s_novo_tipo_input" placeholder="Novo tipo de trabalho..." style="max-width:220px;" />
                                        <button type="button" class="btn btn-sm btn-outline" onclick="_sAdicionarTipoTrabalho()"><i class="fas fa-plus"></i> Adicionar</button>
                                        <button type="button" class="btn btn-sm" style="background:#eef2ff;color:#3730a3;" onclick="abrirGestaoRelatoriosPersonalizados()"><i class="fas fa-clipboard-list"></i> Relatórios personalizados por tipo</button>
                                    </div>
                                    <div class="help-text">Os tipos REX, RBI, RSI, RCM, RIE, RCP, CCTV e Intrusão geram automaticamente um relatório de especialidade a preencher quando a OS for concluída.</div>
                                </div>
                            </div>
                        </div>
                        ` : ''}
                        ${obrasAvancadoAtivo(adminAtual()) ? `
                        <div class="ff-secao ff-tint-id">
                            <div class="ff-secao-head"><i class="fas fa-clipboard-check"></i> Checklist de Saída em OS / Obra</div>
                            <div class="ff-secao-body">
                                <div class="form-group ff-span2">
                                    <div class="help-text" style="margin-bottom:8px;">Todos os pontos devem estar marcados no final da Obra ou da OS.</div>
                                    <button type="button" class="btn btn-sm" style="background:#ecfeff;color:#0e7490;" onclick="abrirGestaoChecklistObras()"><i class="fas fa-pen"></i> Gerir pontos do checklist</button>
                                </div>
                            </div>
                        </div>
                        ` : ''}
                        ${moduloArmazemAtivo(adminAtual()) ? `
                        <div class="ff-secao ff-tint-id">
                            <div class="ff-secao-head"><i class="fas fa-clipboard-check"></i> Checklist de Entrada em OS/Obra</div>
                            <div class="ff-secao-body">
                                <div class="form-group ff-span2">
                                    <div class="help-text" style="margin-bottom:8px;">Perguntado ao técnico (Sim/Não) sempre que dá entrada numa OS ou Obra, antes de começar a trabalhar — no telemóvel ("O Meu Dia") e no Modo Quiosque. Se responder "Não" a algum ponto, a entrada fica bloqueada até resolver.</div>
                                    <button type="button" class="btn btn-sm" style="background:#eef2ff;color:#3730a3;" onclick="abrirGestaoChecklistEntrada()"><i class="fas fa-pen"></i> Gerir pontos do checklist de entrada</button>
                                </div>
                            </div>
                        </div>
                        ` : ''}

                        <div class="ff-secao ff-tint-prof">
                            <div class="ff-secao-head"><i class="fas fa-note-sticky"></i> Detalhes</div>
                            <div class="ff-secao-body">
                                ${(usuarioLogado?.role === 'admin' || usuarioLogado?.role === 'subadmin') ? `<div class="form-group"><label>Valor a faturar (€)</label><input type="number" id="s_valor" step="0.01" min="0" value="${item && item.valor != null ? item.valor : ''}" placeholder="opcional" /><div id="s_valor_ajuda" class="help-text"></div>
                                    <label style="display:flex;align-items:center;gap:8px;font-weight:400;margin-top:8px;">
                                        <input type="checkbox" id="s_pagamento_local" ${item && item.pagamentoLocal ? 'checked' : ''} style="width:auto;" />
                                        Pagamento no local ao terminar o serviço
                                    </label>
                                </div>` : ''}
                                <div class="form-group"><label>Duração (min)</label><input type="number" id="s_duracao" step="15" min="0" value="${item && item.duracao != null ? item.duracao : ''}" placeholder="ex.: 60 (para detetar sobreposições)" /></div>
                                <div class="form-group"><label>Duração estimada (dias)</label><input type="number" id="s_duracao_dias" step="1" min="0" value="${item && item.duracaoDias != null ? item.duracaoDias : ''}" placeholder="para obras grandes" /></div>
                                <div class="form-group ff-span2"><label>Local / Instalação</label>
                                    <select id="s_local" onchange="_osPreencherMoradaDoLocal(this.value)">
                                        <option value="">— Morada principal do cliente —</option>
                                        ${(dados.locais || []).filter(l => l.clienteId === (item ? item.clienteId : '')).map(l => `<option value="${l.id}" ${item && item.localId === l.id ? 'selected' : ''}>${l.nome}</option>`).join('')}
                                        <option value="__novo__">➕ Criar novo local</option>
                                    </select>
                                    <div class="help-text">Se o cliente tiver mais que uma instalação registada, escolhe aqui qual desta OS. Deixa em branco para usar a morada principal.</div>
                                </div>
                                <div id="s_novo_local" class="ff-span2" style="display:none; padding:10px; background:#f8fafc; border-radius:8px;">
                                    <div class="form-group" style="margin-bottom:8px;"><label>Nome do novo local *</label><input type="text" id="s_local_nome" placeholder="Ex: Loja Centro" /></div>
                                    <div class="form-group" style="margin-bottom:0;"><label><i class="fas fa-map-pin" style="color:#dc2626;"></i> Pin do Google Maps (opcional) <a href="https://www.google.com/maps" target="_blank" rel="noopener" style="font-weight:400;font-size:.78rem;color:#2563eb;text-decoration:none;margin-left:8px;"><i class="fas fa-up-right-from-square"></i> Abrir Google Maps</a></label><input type="text" id="s_local_pin_mapa" placeholder="Cola aqui o link ou as coordenadas copiadas do Google Maps" autocomplete="off" oninput="_clienteAtualizarLinkPin('s_local_pin_mapa','s_local_pin_mapa_link')" /><div id="s_local_pin_mapa_link" style="margin-top:6px;font-size:.82rem;"></div></div>
                                </div>
                                <div class="form-group ff-span2"><label>Morada da instalação</label><input type="text" id="s_morada" value="${item && item.morada != null ? item.morada : ''}" placeholder="Preenche automaticamente ao escolher o cliente, mas pode editar" autocomplete="off" /><div id="s_morada_ajuda" class="help-text"></div></div>
                                <div class="form-group"><label>Número de porta</label><input type="text" id="s_numero_porta" value="${item && item.numeroPorta != null ? item.numeroPorta : ''}" /></div>
                                <div class="form-group"><label>Código Postal</label><input type="text" id="s_codigo_postal" value="${item && item.codigoPostal != null ? item.codigoPostal : ''}" placeholder="0000-000" autocomplete="off" oninput="aplicarMascaraCP(this); _cttPreencherPorCP(this.value,{cidade:'s_cidade',freguesia:'s_freguesia',morada:'s_morada'})" /></div>
                                <div class="form-group"><label>Cidade</label><input type="text" id="s_cidade" value="${item && item.cidade != null ? item.cidade : ''}" autocomplete="off" /></div>
                                <div class="form-group"><label>Freguesia</label><input type="text" id="s_freguesia" value="${item && item.freguesia != null ? item.freguesia : ''}" autocomplete="off" /></div>
                            </div>
                        </div>
                        </div>
                    `;
                }
    return html;
  }
  window.TotalGestModalServico = { render: render };
})();
