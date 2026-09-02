/* Total Gest — formulário do modal de folha de obra. */
(function () {
  'use strict';
  function render(options) {
    const opts = options || {};
    const item = opts.item || null;
    const dados = opts.data || {};
    const usuarioLogado = opts.user || null;
    const _clienteLabel = opts.clienteLabel;
    const _gerarOpcoesHoras = opts.gerarOpcoesHoras;
    const _pessoasParaAtribuir = opts.pessoasParaAtribuir;
    return `
                        <div class="ff-wrap">
                        <div class="ff-hero">
                            <div class="ff-avatar-drop" style="cursor:default;">
                                <div class="ff-avatar-ph" style="display:flex;"><i class="fas fa-file-lines"></i></div>
                            </div>
                            <div class="ff-hero-fields">
                                <input type="text" id="fo_cliente_busca" class="ff-nome-input" style="width:100%;flex:1 1 100%;box-sizing:border-box;display:block;" placeholder="Digite o nome ou nº do cliente…" value="${item && item.clienteId ? (() => { const cc = (dados.clientes || []).find(x => x.id === item.clienteId); return cc ? _clienteLabel(cc) : ''; })() : ''}" oninput="clienteBuscaInput('fo_cliente_busca','fo_cliente', _foPreencherLocaisCliente)" onfocus="clienteBuscaFoco('fo_cliente_busca')" onblur="clienteBuscaEsconder('fo_cliente_busca')" autocomplete="off" required />
                                <input type="hidden" id="fo_cliente" value="${item && item.clienteId ? item.clienteId : ''}" />
                                <input type="date" id="fo_data" class="ff-cargo-input" value="${item ? item.data : ''}" />
                            </div>
                        </div>
                        ${!item ? `<div class="help-text" style="margin:-14px 0 14px;">Cliente não existe? <a href="#" onclick="fecharModal(); abrirModal('cliente', null); return false;">Criar cliente</a> e volte a abrir a nova folha.</div>` : ''}

                        <div class="ff-secao ff-tint-id">
                            <div class="ff-secao-head"><i class="fas fa-map-marker-alt"></i> Local da Instalação</div>
                            <div class="ff-secao-body">
                                <div class="form-group ff-span2"><label>Local / Instalação</label>
                                    <select id="fo_local" onchange="_foNovoLocalToggle()">
                                        <option value="">— Morada principal do cliente (Sede) —</option>
                                        ${(dados.locais || []).filter(l => l.clienteId === (item ? item.clienteId : '')).map(l => `<option value="${l.id}" ${item && item.localId === l.id ? 'selected' : ''}>${l.nome}</option>`).join('')}
                                        <option value="__novo__">➕ Criar novo local</option>
                                    </select>
                                    <div class="help-text">Por defeito usa a Sede (morada principal do cliente). Escolhe outra instalação se o cliente tiver mais que uma.</div>
                                </div>
                                <div id="fo_novo_local" class="ff-span2" style="display:none; padding:10px; background:#f8fafc; border-radius:8px;">
                                    <div class="form-group" style="margin-bottom:0;"><label>Nome do novo local *</label><input type="text" id="fo_local_nome" placeholder="Ex: Loja Centro" /></div>
                                </div>
                            </div>
                        </div>

                        <div class="ff-secao ff-tint-id">
                            <div class="ff-secao-head"><i class="fas fa-hard-hat"></i> Obra e Materiais</div>
                            <div class="ff-secao-body">
                                <div class="form-group ff-span2"><label>Obra (materiais / stock)</label>
                                    <select id="fo_obra" onchange="renderPlanoConsumoFolha()">
                                        <option value="">— Sem obra associada —</option>
                                        ${(dados.obras || []).filter(o => o.adminId === (usuarioLogado?.adminId || usuarioLogado?.id)).map(o => `<option value="${o.id}" ${item && item.obraId === o.id ? 'selected' : ''}>${o.nome}</option>`).join('')}
                                    </select>
                                    <div class="help-text">Associa a uma obra para registar o consumo de materiais do plano.</div>
                                </div>
                                <div class="form-group ff-span2" id="fo_plano_materiais"></div>
                            </div>
                        </div>

                        <div class="ff-secao ff-tint-prof">
                            <div class="ff-secao-head"><i class="fas fa-note-sticky"></i> Trabalho Realizado</div>
                            <div class="ff-secao-body">
                                <div class="form-group ff-span2"><label>Descrição do trabalho * <span class="help-text">(mínimo 3 caracteres)</span></label><textarea id="fo_descricao" required minlength="3">${item ? item.descricao : ''}</textarea></div>
                                <div class="form-group ff-span2"><label>Materiais utilizados</label><textarea id="fo_materiais">${item ? item.materiais : ''}</textarea></div>
                                <div class="form-group"><label>Horas trabalhadas</label>
                                    <select id="fo_horas">${_gerarOpcoesHoras(item ? item.horasTrabalhadas : 0)}</select>
                                    <div class="help-text">Seleciona em blocos de 10 minutos (ex: 1h10).</div>
                                </div>
                                ${usuarioLogado?.role === 'admin' ? `
                                    <div class="form-group"><label>Funcionário (opcional)</label>
                                        <select id="fo_funcionario">
                                            <option value="">Selecione</option>
                                            ${_pessoasParaAtribuir(usuarioLogado.id).map(f => `<option value="${f.id}" ${item && item.funcionarioId === f.id ? 'selected' : ''}>${f.nome}</option>`).join('')}
                                        </select>
                                    </div>
                                ` : ''}
                            </div>
                        </div>

                        <div class="ff-secao ff-tint-acesso">
                            <div class="ff-secao-head"><i class="fas fa-signature"></i> Assinatura do Cliente</div>
                            <div class="ff-secao-body">
                                <div class="form-group ff-span2">
                                    <input type="text" id="fo_assinatura_nome" placeholder="Nome de quem assina" value="${item ? (item.assinaturaNome || '') : ''}" style="margin-bottom:6px;" />
                                    <div style="border:1px solid #cbd5e1;border-radius:8px;background:#fff;">
                                        <canvas id="fo_assinatura_canvas" style="width:100%;height:160px;touch-action:none;display:block;border-radius:8px;"></canvas>
                                    </div>
                                    <div style="display:flex;gap:8px;margin-top:6px;align-items:center;flex-wrap:wrap;">
                                        <button type="button" id="fo_btn_assinar" class="btn btn-outline" onclick="ativarAssinatura()"><i class="fas fa-signature"></i> Assinar</button>
                                        <button type="button" class="btn btn-outline" onclick="limparAssinatura()"><i class="fas fa-eraser"></i> Limpar</button>
                                        <span id="fo_assinar_aviso" class="help-text" style="margin:0;">Carregue em <strong>Assinar</strong> e assine com o dedo ou o rato.</span>
                                    </div>
                                    <input type="hidden" id="fo_assinatura_data" value="${item && item.assinatura ? item.assinatura : ''}" />
                                </div>
                            </div>
                        </div>
                        </div>
                        <input type="hidden" id="fo_funcionario_id" value="${usuarioLogado ? usuarioLogado.id : ''}" />
                        <input type="hidden" id="fo_servico_id" value="${item && item.servicoId ? item.servicoId : ''}" />
                    `;
  }
  window.TotalGestModalFolha = { render: render };
})();
