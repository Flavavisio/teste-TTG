/* Total Gest — formulário do modal de obra. */
(function () {
  'use strict';
  function render(options) {
    const opts = options || {};
    const item = opts.item || null;
    const dados = opts.data || {};
    const usuarioLogado = opts.user || null;
    const _tenantId = function () { return opts.tenantId; };
    const _clienteLabel = opts.clienteLabel;
    const obrasAvancadoAtivo = opts.obrasAvancadoAtivo;
    const moduloCrmAtivo = opts.moduloCrmAtivo;
    const adminAtual = function () { return opts.admin || null; };
    let html = '';
                const cliOpts = (dados.clientes||[]).filter(c => c.adminId === _tenantId()).map(c => `<option value="${c.id}" ${item && item.clienteId===c.id?'selected':''}>${c.nome}</option>`).join('');
                html = `
                    <div class="ff-wrap">
                    <div class="ff-hero">
                        <div class="ff-avatar-drop" style="cursor:default;">
                            <div class="ff-avatar-ph" style="display:flex;"><i class="fas fa-hard-hat"></i></div>
                        </div>
                        <div class="ff-hero-fields">
                            <input type="text" id="ob_nome" class="ff-nome-input" placeholder="Nome da obra *" value="${item ? (item.nome||'') : ''}" required />
                            <select id="ob_estado" class="ff-cargo-input" style="max-width:200px;">
                                <option value="preparacao" ${!item || item.estado === 'preparacao' ? 'selected' : ''}>Preparação</option>
                                <option value="ativa" ${item && item.estado === 'ativa' ? 'selected' : ''}>Ativa</option>
                                <option value="suspensa" ${item && item.estado === 'suspensa' ? 'selected' : ''}>Suspensa</option>
                                <option value="concluida" ${item && item.estado === 'concluida' ? 'selected' : ''}>Concluída</option>
                            </select>
                        </div>
                    </div>

                    <div class="ff-secao ff-tint-id">
                        <div class="ff-secao-head"><i class="fas fa-location-dot"></i> Local e Cliente</div>
                        <div class="ff-secao-body">
                            <div class="form-group ff-span2"><label>Cliente</label><div style="display:flex;gap:8px;"><input type="text" id="ob_cliente_busca" style="flex:1;" placeholder="Digite o nome ou nº do cliente (opcional)…" value="${item && item.clienteId ? (() => { const cc = (dados.clientes || []).find(x => x.id === item.clienteId); return cc ? _clienteLabel(cc) : ''; })() : ''}" oninput="clienteBuscaInput('ob_cliente_busca','ob_cliente', onClienteObraChange)" onfocus="clienteBuscaFoco('ob_cliente_busca')" onblur="clienteBuscaEsconder('ob_cliente_busca')" autocomplete="off" /><input type="hidden" id="ob_cliente" value="${item && item.clienteId ? item.clienteId : ''}" /><button type="button" class="btn btn-outline" onclick="obraAddCliente()" title="Adicionar cliente"><i class="fas fa-plus"></i></button></div></div>
                            <div class="form-group ff-span2"><label>Local / Instalação</label>
                                <select id="ob_local" onchange="onLocalObraChange()">
                                    <option value="">— Morada principal do cliente (Sede) —</option>
                                    ${item && item.clienteId ? (dados.locais || []).filter(l => l.clienteId === item.clienteId).map(l => `<option value="${l.id}" ${item.localId === l.id ? 'selected' : ''}>${l.nome}</option>`).join('') : ''}
                                    <option value="__novo__">➕ Criar novo local</option>
                                </select>
                                <div class="help-text">Por defeito usa a Sede (morada principal do cliente). Escolhe outra instalação se o cliente tiver mais que uma, ou cria uma nova.</div>
                            </div>
                            <div id="ob_novo_local" class="ff-span2" style="display:none;padding:10px;background:#f8fafc;border-radius:8px;">
                                <div class="form-group" style="margin-bottom:8px;"><label>Nome do novo local *</label><input type="text" id="ob_local_nome" placeholder="Ex: Loja Centro" /></div>
                                <div class="form-group" style="margin-bottom:8px;"><label>Morada da instalação</label><input type="text" id="ob_morada" placeholder="Rua, número..." autocomplete="off" /></div>
                                <div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-bottom:8px;">
                                    <div class="form-group" style="margin-bottom:0;"><label>Número de porta</label><input type="text" id="ob_local_numero" placeholder="ex.: 3, 3A" /></div>
                                    <div class="form-group" style="margin-bottom:0;"><label>Código Postal</label><input type="text" id="ob_cp" placeholder="0000-000" autocomplete="off" oninput="aplicarMascaraCP(this); _cttPreencherPorCP(this.value,{cidade:'ob_cidade',freguesia:'ob_local_freguesia',morada:'ob_morada'})" maxlength="8" /></div>
                                </div>
                                <div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-bottom:8px;">
                                    <div class="form-group" style="margin-bottom:0;"><label>Cidade</label><input type="text" id="ob_cidade" autocomplete="off" /></div>
                                    <div class="form-group" style="margin-bottom:0;"><label>Freguesia</label><input type="text" id="ob_local_freguesia" autocomplete="off" /></div>
                                </div>
                                <div class="form-group" style="margin-bottom:0;"><label><i class="fas fa-map-pin" style="color:#dc2626;"></i> Pin do Google Maps (opcional) <a href="https://www.google.com/maps" target="_blank" rel="noopener" style="font-weight:400;font-size:.78rem;color:#2563eb;text-decoration:none;margin-left:8px;"><i class="fas fa-up-right-from-square"></i> Abrir Google Maps</a></label><input type="text" id="ob_local_pin_mapa" placeholder="Cola aqui o link ou as coordenadas copiadas do Google Maps" autocomplete="off" oninput="_clienteAtualizarLinkPin('ob_local_pin_mapa','ob_local_pin_mapa_link')" /><div id="ob_local_pin_mapa_link" style="margin-top:6px;font-size:.82rem;"></div></div>
                            </div>
                        </div>
                    </div>

                    <div class="ff-secao ff-tint-prof">
                        <div class="ff-secao-head"><i class="fas fa-building-shield"></i> Gestão da Obra</div>
                        <div class="ff-secao-body">
                            <div class="form-group ff-span2">
                                <label style="display:flex;align-items:center;gap:8px;font-weight:600;">
                                    <input type="checkbox" id="ob_longa_duracao" ${item && item.longaDuracao ? 'checked' : ''} style="width:auto;" />
                                    Obra de longa duração
                                </label>
                                <div class="help-text">Obras que podem demorar meses/anos. Ativa picagem de entrada/saída na obra, folha de obra obrigatória ao terminar o dia, e aparece em "Gestão de Obras".</div>
                            </div>
                            <div class="form-group ff-span2">
                                <label>Funcionários atribuídos à obra</label>
                                <div style="max-height:150px;overflow-y:auto;border:1px solid #e2e8f0;border-radius:8px;padding:8px;">
                                    <label style="display:flex;align-items:center;gap:8px;padding:4px 0 8px;border-bottom:1px solid #f1f5f9;margin-bottom:4px;cursor:pointer;font-weight:700;">
                                        <input type="checkbox" id="ob_todos" onchange="document.querySelectorAll('.ob-func-check').forEach(c=>c.checked=this.checked);_obAtualizarResponsavelFolha();" style="width:auto;" /> Selecionar todos
                                    </label>
                                    ${[...(dados.funcionarios||[]).filter(f=>f.adminId===usuarioLogado.id && f.role!=='admin' && !f.suspenso), ...(dados.encarregados||[]).filter(e=>e.adminId===usuarioLogado.id && !e.suspenso)].map(p => {
                                        const idsAtuais = (item?.responsaveisIds?.length ? item.responsaveisIds : (item?.responsavelId ? [item.responsavelId] : []));
                                        return `<label style="display:flex;align-items:center;gap:8px;padding:4px 0;cursor:pointer;"><input type="checkbox" class="ob-func-check" value="${p.id}" onchange="_obAtualizarResponsavelFolha()" ${idsAtuais.includes(p.id) ? 'checked' : ''} style="width:auto;" /> ${p.nome}</label>`;
                                    }).join('')}
                                </div>
                                <div class="help-text">Podes escolher mais que uma pessoa — cada uma pica a sua própria entrada/saída.</div>
                            </div>
                            <div class="form-group ff-span2" id="ob_relatorio_responsavel_cont" style="display:none;">
                                <label>Quem é o responsável por assinar a folha de obra e o relatório final?</label>
                                <select id="ob_relatorio_responsavel"></select>
                                <div class="help-text">Só esta pessoa vai ser convidada a preencher, ao dar saída. Os restantes atribuídos só picam entrada/saída.</div>
                            </div>
                            ${obrasAvancadoAtivo(adminAtual()) ? `
                            <div class="form-group"><label>Início previsto</label>
                                <input type="date" id="ob_data_inicio_prevista" value="${item && item.dataInicioPrevista ? item.dataInicioPrevista : ''}" />
                            </div>
                            <div class="form-group"><label>Fim previsto</label>
                                <input type="date" id="ob_data_fim_prevista" value="${item && item.dataFimPrevista ? item.dataFimPrevista : ''}" />
                                <div class="help-text">Se a obra ainda não estiver concluída depois desta data, a app avisa que está em atraso.</div>
                            </div>
                            ` : ''}
                            ${usuarioLogado?.role === 'admin' || usuarioLogado?.role === 'subadmin' ? `
                            <div class="form-group"><label>Valor a faturar (€)</label>
                                <input type="number" id="ob_valor" step="0.01" min="0" value="${item && item.valor != null ? item.valor : ''}" placeholder="opcional" />
                                <div class="help-text">O que vai ser cobrado ao cliente por esta obra.</div>
                            </div>
                            <div class="form-group"><label>Mão de obra / h (€)</label>
                                <input type="number" id="ob_custo_hora" step="0.01" min="0" value="${item && item.custoHora != null ? item.custoHora : ''}" placeholder="ex: 12.50" />
                                <div class="help-text">Usado para calcular o custo real da obra (horas das folhas de obra × este valor). Só visível para a empresa, nunca para o cliente.</div>
                            </div>
                            ${moduloCrmAtivo(adminAtual()) ? `
                            <div class="form-group">
                                <label style="display:flex;align-items:center;gap:8px;cursor:pointer;">
                                    <input type="checkbox" id="ob_tem_autos_medicao" ${item?.temAutosMedicao ? 'checked' : ''} style="width:auto;" />
                                    Esta obra vai ter Autos de Medição
                                </label>
                                <div class="help-text">Se marcado, aparece um botão "Auto de Medição" dentro de "Ver Obra", para criares relatórios periódicos com o que foi gasto/trabalhado desde o último auto, e faturares cada um.</div>
                            </div>` : ''}
                            ` : ''}
                        </div>
                    </div>

                    <div class="ff-secao ff-tint-contacto">
                        <div class="ff-secao-head"><i class="fas fa-note-sticky"></i> Notas</div>
                        <div class="ff-secao-body">
                            <div class="form-group ff-span2"><label>Descrição da obra * <span class="help-text" style="font-weight:400;">(mínimo 3 caracteres)</span></label><textarea id="ob_obs" rows="2" required minlength="3" placeholder="Ex.: Instalação de sistema de videovigilância no armazém, com 12 câmaras...">${item ? (item.observacoes || '') : ''}</textarea></div>
                        </div>
                    </div>
                    </div>
                `;
    return html;
  }
  window.TotalGestModalObra = { render: render };
})();
