/* Total Gest — conteúdo do modal de perfil de funcionário/encarregado. */
(function () {
  'use strict';

  function render(options) {
    const opts = options || {};
    const func = opts.employee || null;
    const role = opts.role || '';
    if (!func) return null;

    const _fmtData = (d) => d ? new Date(d + 'T00:00:00').toLocaleDateString('pt-PT') : null;
    const _apoliceHtml = (func.apoliceNumero || func.apoliceSeguradora || func.apoliceValidade) ? `
                        <div class="ff-secao ff-tint-doc">
                            <div class="ff-secao-head"><i class="fas fa-shield-halved"></i> Apólice de Seguro de Acidentes de Trabalho</div>
                            <div class="ff-secao-body">
                                <div class="form-group"><label>Número da apólice</label><input type="text" value="${func.apoliceNumero || '—'}" disabled style="background:#e9edf2;" /></div>
                                <div class="form-group"><label>Seguradora</label><input type="text" value="${func.apoliceSeguradora || '—'}" disabled style="background:#e9edf2;" /></div>
                                <div class="form-group"><label>Validade</label><input type="text" value="${_fmtData(func.apoliceValidade) || '—'}" disabled style="background:#e9edf2;" /></div>
                            </div>
                        </div>` : '';
    const _saudeHtml = (func.saudeApoliceNumero || func.saudeApoliceSeguradora || func.saudeApoliceValidade) ? `
                        <div class="ff-secao ff-tint-doc">
                            <div class="ff-secao-head"><i class="fas fa-heart-pulse"></i> Seguro de Saúde</div>
                            <div class="ff-secao-body">
                                <div class="form-group"><label>Número da apólice</label><input type="text" value="${func.saudeApoliceNumero || '—'}" disabled style="background:#e9edf2;" /></div>
                                <div class="form-group"><label>Seguradora</label><input type="text" value="${func.saudeApoliceSeguradora || '—'}" disabled style="background:#e9edf2;" /></div>
                                <div class="form-group"><label>Validade</label><input type="text" value="${_fmtData(func.saudeApoliceValidade) || '—'}" disabled style="background:#e9edf2;" /></div>
                            </div>
                        </div>` : '';

    return `
                        <div class="ff-wrap">
                        <div class="ff-hero">
                            <div class="ff-avatar-drop" onclick="document.getElementById('perf_foto').click()" title="Alterar foto">
                                <img id="perf_foto_img" src="${func.foto || ''}" style="${func.foto ? '' : 'display:none;'}" />
                                <div id="perf_foto_placeholder" class="ff-avatar-ph" style="${func.foto ? 'display:none;' : 'display:flex;'}"><i class="fas fa-user"></i></div>
                                <div class="ff-avatar-badge"><i class="fas fa-camera"></i></div>
                            </div>
                            <input type="file" id="perf_foto" accept="image/*" style="display:none;" onchange="previewPerfilFoto(event)" />
                            <div class="ff-hero-fields">
                                <input type="text" id="perf_nome" class="ff-nome-input" placeholder="Nome *" value="${func.nome}" required />
                                <input type="text" class="ff-cargo-input" value="${func.cargo || ''}" disabled />
                            </div>
                        </div>

                        <div class="ff-secao ff-tint-acesso">
                            <div class="ff-secao-head"><i class="fas fa-bell"></i> Notificações</div>
                            <div class="ff-secao-body">
                                <div class="form-group ff-span2">
                                    <div class="help-text" style="margin:-2px 0 8px;">Recebe um aviso no telemóvel se te esqueceres de picar o ponto, ou quando um pedido de férias/faltas for aprovado.</div>
                                    <button type="button" class="btn btn-sm" style="background:#0ea5e9;color:#fff;" onclick="_ativarNotificacoesPush()"><i class="fas fa-bell"></i> Ativar notificações neste dispositivo</button>
                                </div>
                            </div>
                        </div>

                        <div class="ff-secao ff-tint-contacto">
                            <div class="ff-secao-head"><i class="fas fa-address-book"></i> Contacto</div>
                            <div class="ff-secao-body">
                                <div class="form-group"><label>Telefone</label><input type="text" id="perf_telefone" value="${func.telefone || ''}" /></div>
                                <div class="form-group"><label>Email (não editável)</label><input type="text" value="${func.email}" disabled style="background:#e9edf2;" /></div>
                            </div>
                        </div>
                        ${_apoliceHtml}
                        ${_saudeHtml}

                        <div class="ff-secao ff-tint-acesso">
                            <div class="ff-secao-head"><i class="fas fa-lock"></i> Acesso ao Sistema</div>
                            <div class="ff-secao-body">
                                <div class="form-group ff-span2"><label>Nova Senha</label><input type="password" id="perf_senha" placeholder="Deixe em branco para manter a atual" /></div>
                            </div>
                        </div>
                        ${(role === 'subadmin' || role === 'encarregado') ? `
                        <div class="ff-secao ff-tint-doc">
                            <div class="ff-secao-head"><i class="fas fa-tablet-screen-button"></i> Modo Quiosque</div>
                            <div class="ff-secao-body">
                                <div class="form-group ff-span2">
                                    <p class="help-text" style="margin:0 0 10px;">Transforma este aparelho num ponto de picagem fixo, partilhado por toda a equipa (ex.: um tablet colado à entrada da obra). Cada pessoa toca no seu nome e escreve o PIN para picar entrada/saída.</p>
                                    <button type="button" class="btn btn-outline" style="width:100%;" onclick="fecharModalPerfil(); ativarModoQuiosque();"><i class="fas fa-tablet-screen-button"></i> Ativar Modo Quiosque neste aparelho</button>
                                </div>
                            </div>
                        </div>` : ''}
                        </div>
                    `;
  }

  window.TotalGestProfileModalWorker = { render: render };
})();
