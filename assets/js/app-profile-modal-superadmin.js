/* Total Gest — conteúdo do modal de perfil do superadmin. */
(function () {
  'use strict';

  function render(options) {
    const opts = options || {};
    const config = opts.config || {};
    const db = opts.bankData || {};
    const getConfig = opts.getConfig;

    return `
                        <div class="ff-wrap">
                        <div class="ff-hero">
                            <div class="ff-avatar-drop" onclick="document.getElementById('perf_logo').click()" title="Alterar logótipo">
                                <img id="perf_logo_img" src="${config.logo || ''}" style="${config.logo ? '' : 'display:none;'}" />
                                <div id="perf_logo_placeholder" class="ff-avatar-ph" style="${config.logo ? 'display:none;' : ''}"><i class="fas fa-crown"></i></div>
                                <div class="ff-avatar-badge"><i class="fas fa-camera"></i></div>
                            </div>
                            <input type="file" id="perf_logo" accept="image/*" style="display:none;" onchange="previewPerfilLogo(event)" />
                            <div class="ff-hero-fields">
                                <input type="text" id="perf_nome" class="ff-nome-input" placeholder="Nome *" value="${config.nome || ''}" required />
                                <input type="email" id="perf_email" class="ff-cargo-input" placeholder="Email (login)" value="${config.email || ''}" />
                            </div>
                        </div>
                        <div id="perf_logo_preview" style="display:none;"></div>

                        <div class="ff-secao ff-tint-acesso">
                            <div class="ff-secao-head"><i class="fas fa-lock"></i> Acesso ao Sistema</div>
                            <div class="ff-secao-body">
                                <div class="form-group ff-span2"><label>Nova Senha</label><input type="password" id="perf_senha" placeholder="Deixe em branco para manter a atual" /></div>
                                <div class="form-group ff-span2"><div class="help-text" style="margin-top:-4px;">Use o mesmo email da conta de autenticação (Supabase Auth).</div></div>
                            </div>
                        </div>

                        <div class="ff-secao ff-tint-prof">
                            <div class="ff-secao-head"><i class="fas fa-university"></i> Dados Bancários para Pagamento</div>
                            <div class="ff-secao-body">
                                <div class="form-group ff-span2"><div class="help-text" style="margin-top:-2px;">Aparecem ao cliente e no email quando emite uma licença.</div></div>
                                <div class="form-group"><label>Titular da conta</label><input type="text" id="perf_titular" value="${(db.titular || '').replace(/"/g, '&quot;')}" placeholder="Nome do titular" /></div>
                                <div class="form-group"><label>IBAN</label><input type="text" id="perf_iban" value="${(db.iban || '').replace(/"/g, '&quot;')}" placeholder="PT50 0000 0000 0000 0000 0000 0" /></div>
                                <div class="form-group"><label>Banco</label><input type="text" id="perf_banco" value="${(db.banco || '').replace(/"/g, '&quot;')}" placeholder="Nome do banco" /></div>
                                <div class="form-group"><label>BIC/SWIFT</label><input type="text" id="perf_swift" value="${(db.swift || '').replace(/"/g, '&quot;')}" placeholder="Opcional" /></div>
                                <div class="form-group"><label>Nº de telemóvel MB WAY</label><input type="text" id="perf_mbway" value="${(db.mbway || '').replace(/"/g, '&quot;')}" placeholder="Ex: 9XX XXX XXX" /></div>
                                <div class="form-group ff-span2"><label>Instruções adicionais</label><textarea id="perf_instrucoes" rows="2" placeholder="Ex: enviar comprovativo para...">${db.instrucoes || ''}</textarea></div>
                            </div>
                        </div>

                        <div class="ff-secao ff-tint-id">
                            <div class="ff-secao-head"><i class="fas fa-table-columns"></i> Aspeto da Aplicação</div>
                            <div class="ff-secao-body">
                                <div class="form-group ff-span2">
                                    <label>Layout</label>
                                    <select id="perf_layout">
                                        <option value="sidebar" ${(getConfig()?.layout || 'sidebar') === 'sidebar' ? 'selected' : ''}>Barra lateral (moderno)</option>
                                        <option value="cards" ${getConfig()?.layout === 'cards' ? 'selected' : ''}>Clássico (cards no topo)</option>
                                        <option value="foco" ${getConfig()?.layout === 'foco' ? 'selected' : ''}>Total Gest Foco (grupos + painel lateral)</option>
                                        <option value="aurora" ${getConfig()?.layout === 'aurora' ? 'selected' : ''}>Total Gest Aurora (visual moderno, escuro)</option>
                                    </select>
                                </div>
                            </div>
                        </div>

                        <div class="ff-secao ff-tint-doc">
                            <div class="ff-secao-head"><i class="fas fa-shield-halved"></i> Segurança (RLS)</div>
                            <div class="ff-secao-body">
                                <div class="form-group ff-span2"><p style="font-size:.82rem;color:#64748b;margin:0 0 10px;">Antes de ativar o RLS, crie as contas de autenticação para todos os utilizadores (incl. clientes do portal). É seguro repetir.</p>
                                    <button type="button" class="btn btn-primary" onclick="migrarContasAuth()" style="width:100%;"><i class="fas fa-user-shield"></i> Criar/atualizar contas de acesso</button>
                                </div>
                            </div>
                        </div>

                        <div class="ff-secao ff-tint-contacto">
                            <div class="ff-secao-head"><i class="fas fa-user-clock"></i> Monitorização</div>
                            <div class="ff-secao-body">
                                <div class="form-group ff-span2">
                                    <label style="display:flex;align-items:center;gap:8px;cursor:pointer;">
                                        <input type="checkbox" id="perf_estado_online_equipa" ${getConfig()?.mostrarEstadoOnline ? 'checked' : ''} style="width:auto;margin:0;" />
                                        Mostrar o estado online/offline dos funcionários e encarregados
                                    </label>
                                    <div class="help-text">Quando ativo, a vista "Online" passa a incluir os funcionários e encarregados de todas as empresas.</div>
                                </div>
                            </div>
                        </div>
                        </div>
                    `;
  }

  window.TotalGestProfileModalSuperadmin = { render: render };
})();
