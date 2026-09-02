/* Total Gest — conteúdo do modal de perfil de admin/subadmin. */
(function () {
  'use strict';

  function render(options) {
    const opts = options || {};
    const admin = opts.admin || null;
    const func = opts.employee || null;
    const FERIADOS_MUNICIPAIS = opts.municipalHolidays || {};
    const moduloContratosAtivo = opts.contractsModuleEnabled;

    return `
                        <div class="ff-wrap">
                        <div class="ff-hero">
                            <div class="ff-avatar-drop" onclick="document.getElementById('perf_logo').click()" title="Alterar logótipo">
                                <img id="perf_logo_img" src="${admin?.logo || ''}" style="${admin?.logo ? '' : 'display:none;'}" />
                                <div id="perf_logo_placeholder" class="ff-avatar-ph" style="${admin?.logo ? 'display:none;' : ''}"><i class="fas fa-building"></i></div>
                                <div class="ff-avatar-badge"><i class="fas fa-camera"></i></div>
                            </div>
                            <input type="file" id="perf_logo" accept="image/*" style="display:none;" onchange="previewPerfilLogo(event)" />
                            <div class="ff-hero-fields">
                                <input type="text" id="perf_empresa" class="ff-nome-input" placeholder="Nome da empresa" value="${admin?.empresa || ''}" />
                                <input type="text" id="perf_nome" class="ff-cargo-input" placeholder="Nome do responsável *" value="${admin?.nome || ''}" required />
                            </div>
                        </div>
                        <div id="perf_logo_preview" style="display:none;"></div>

                        <div class="ff-secao ff-tint-contacto">
                            <div class="ff-secao-head"><i class="fas fa-address-book"></i> Contacto</div>
                            <div class="ff-secao-body">
                                <div class="form-group"><label>Telefone</label><input type="text" id="perf_telefone" value="${func?.telefone || ''}" /></div>
                                <div class="form-group"><label>Email (não editável)</label><input type="text" value="${admin?.email || ''}" disabled style="background:#e9edf2;" /></div>
                            </div>
                        </div>

                        <div class="ff-secao ff-tint-acesso">
                            <div class="ff-secao-head"><i class="fas fa-lock"></i> Acesso ao Sistema</div>
                            <div class="ff-secao-body">
                                <div class="form-group ff-span2"><label>Nova Senha</label><input type="password" id="perf_senha" placeholder="Deixe em branco para manter a atual" /></div>
                            </div>
                        </div>

                        <div class="ff-secao ff-tint-prof">
                            <div class="ff-secao-head"><i class="fas fa-table-columns"></i> Aspeto da Aplicação</div>
                            <div class="ff-secao-body">
                                <div class="form-group ff-span2">
                                    <label>Layout (aplica-se a toda a equipa)</label>
                                    <select id="perf_layout">
                                        <option value="sidebar" ${(admin?.layout || 'sidebar') === 'sidebar' ? 'selected' : ''}>Barra lateral (moderno)</option>
                                        <option value="cards" ${admin?.layout === 'cards' ? 'selected' : ''}>Clássico (cards no topo)</option>
                                        <option value="foco" ${admin?.layout === 'foco' ? 'selected' : ''}>Total Gest Foco (grupos + painel lateral)</option>
                                        <option value="aurora" ${admin?.layout === 'aurora' ? 'selected' : ''}>Total Gest Aurora (visual moderno, escuro)</option>
                                    </select>
                                </div>
                            </div>
                        </div>

                        <div class="ff-secao ff-tint-doc">
                            <div class="ff-secao-head"><i class="fas fa-id-badge"></i> Identificação Fiscal e Visual</div>
                            <div class="ff-secao-body">
                                <div class="form-group"><label>NIF da empresa</label><input type="text" id="perf_nif" value="${admin?.nif || ''}" placeholder="000000000" /></div>
                                <div class="form-group"><label>Cor corporativa (usada nos relatórios)</label><input type="text" id="perf_cor" value="${admin?.corCorporativa || '#152A52'}" placeholder="#152A52" /></div>
                            </div>
                        </div>

                        <div class="ff-secao ff-tint-doc">
                            <div class="ff-secao-head"><i class="fas fa-sliders"></i> Áreas de Atuação</div>
                            <div class="ff-secao-body">
                                <div class="form-group ff-span2">
                                    <label style="display:flex;align-items:center;gap:8px;cursor:pointer;">
                                        <input type="checkbox" id="perf_seguranca_ativo" ${admin?.segurancaAtivo ? 'checked' : ''} style="width:auto;margin:0;" onchange="_perfAlternarBlocoCondicional('seguranca', this.checked)" />
                                        Trabalha na área de segurança (CCTV, Intrusão, Incêndio)?
                                    </label>
                                    <div class="help-text">Se sim, ativa os registos ANEPC, registo prévio e o logótipo da entidade certificadora, usados nos relatórios de especialidade.</div>
                                </div>
                                <div class="form-group ff-span2">
                                    <label style="display:flex;align-items:center;gap:8px;cursor:pointer;">
                                        <input type="checkbox" id="perf_seguros_ativo" ${admin?.segurosAtivo ? 'checked' : ''} style="width:auto;margin:0;" />
                                        Quer adicionar os seguros da empresa (Responsabilidade Civil e Saúde)?
                                    </label>
                                    <div class="help-text">Se sim, a ficha de cada funcionário passa a ter os campos de apólice (nº, seguradora, validade) para os dois seguros.</div>
                                </div>
                                <div class="form-group ff-span2">
                                    <label style="display:flex;align-items:center;gap:8px;cursor:pointer;">
                                        <input type="checkbox" id="perf_shst_ativo" ${admin?.shstAtivo ? 'checked' : ''} style="width:auto;margin:0;" />
                                        Quer ativar Saúde, Higiene e Segurança no Trabalho (SHST)?
                                    </label>
                                    <div class="help-text">Se sim, a ficha de cada funcionário passa a controlar a validade da consulta de medicina do trabalho — anual a partir dos 50 anos, de 2 em 2 anos antes disso — com aviso automático quando faltarem 30 dias.</div>
                                </div>
                            </div>
                        </div>

                        <div class="ff-secao ff-tint-doc" id="perf_bloco_seguranca" style="${admin?.segurancaAtivo ? '' : 'display:none;'}">
                            <div class="ff-secao-head"><i class="fas fa-certificate"></i> Certificações (Segurança)</div>
                            <div class="ff-secao-body">
                                <div class="form-group ff-span2"><label>Nº de registo ANEPC</label><input type="text" id="perf_anepc" value="${admin?.numeroAnepc || ''}" placeholder="Deixe em branco se não tiver" /></div>
                                <div class="form-group"><label>Data de emissão ANEPC</label><input type="date" id="perf_anepc_data" value="${admin?.dataAnepc || ''}" /></div>
                                <div class="form-group"><label>Validade / renovação do registo ANEPC</label><input type="date" id="perf_anepc_validade" value="${admin?.anepcValidade || ''}" /><span class="help-text">Fica em alerta vermelho nas pendências quando faltarem 6 meses.</span></div>
                                <div class="form-group ff-span2"><label>Nº de registo prévio</label><input type="text" id="perf_registo_previo" value="${admin?.numeroRegistoPrevio || ''}" placeholder="Deixe em branco se não tiver" /></div>
                                <div class="form-group"><label>Data de emissão do registo prévio</label><input type="date" id="perf_registo_previo_data" value="${admin?.dataRegistoPrevio || ''}" /><span class="help-text">Usada na Declaração de Instalação, junto ao nº de registo.</span></div>
                                <div class="form-group"><label>Validade / renovação do registo prévio</label><input type="date" id="perf_registo_previo_validade" value="${admin?.registoPrevioValidade || ''}" /><span class="help-text">Fica em alerta vermelho nas pendências quando faltarem 6 meses.</span></div>
                                <div class="form-group ff-span2">
                                    <label>Logótipo da entidade certificadora (extintores — REX)</label>
                                    <span class="help-text" style="display:block;margin-bottom:6px;">Aparece no canto superior direito do relatório REX, no lugar do logótipo padrão da APCER — usa o logótipo da entidade que certifica a tua empresa (APCER, Bureau Veritas, SGS, TÜV Rheinland, etc.), o que for.</span>
                                    ${admin?.certificadoraLogo ? `<img src="${admin.certificadoraLogo}" style="max-height:70px;max-width:160px;display:block;margin-bottom:8px;border:1px solid #e2e8f0;border-radius:6px;padding:4px;background:#fff;" />` : ''}
                                    <input type="file" id="perf_certificadora_logo" accept="image/*" onchange="_perfPreviewCertificadoraLogo(this)" />
                                    ${admin?.certificadoraLogo ? `<button type="button" class="btn btn-sm btn-danger" style="margin-top:6px;" onclick="document.getElementById('perf_certificadora_logo').value=''; window._perfCertificadoraLogoRemover=true; this.previousElementSibling.style.display='none'; this.style.display='none';">Remover logótipo</button>` : ''}
                                </div>
                            </div>
                        </div>

                        <div class="ff-secao ff-tint-doc">
                            <div class="ff-secao-head"><i class="fas fa-tablet-screen-button"></i> Modo Quiosque</div>
                            <div class="ff-secao-body">
                                <div class="form-group ff-span2">
                                    <p class="help-text" style="margin:0 0 10px;">Transforma este aparelho num ponto de picagem fixo, partilhado por toda a equipa (ex.: um tablet colado à entrada da obra). Cada pessoa toca no seu nome e escreve o PIN para picar entrada/saída.</p>
                                    <button type="button" class="btn btn-outline" style="width:100%;" onclick="fecharModalPerfil(); ativarModoQuiosque();"><i class="fas fa-tablet-screen-button"></i> Ativar Modo Quiosque neste aparelho</button>
                                </div>
                            </div>
                        </div>

                        <div class="ff-secao ff-tint-doc">
                            <div class="ff-secao-head"><i class="fas fa-tv"></i> Painel TV</div>
                            <div class="ff-secao-body">
                                <div class="form-group ff-span2">
                                    <p class="help-text" style="margin:0 0 10px;">Transforma este aparelho (monitor/TV da empresa) num painel fixo, em ecrã inteiro, com o Mapa da Equipa e a Agenda de Obras lado a lado. Fica sempre ligado — mesmo que o ecrã reinicie, volta a abrir sozinho.</p>
                                    <button type="button" class="btn btn-outline" style="width:100%;" onclick="fecharModalPerfil(); ativarPainelTV();"><i class="fas fa-tv"></i> Ativar Painel TV neste aparelho</button>
                                </div>
                            </div>
                        </div>

                        <div class="ff-secao ff-tint-doc">
                            <div class="ff-secao-head"><i class="fas fa-clock"></i> Horário de entrada e tolerância de atraso</div>
                            <div class="ff-secao-body">
                                <p class="help-text" style="margin:0 0 10px;">Usado para avisar no Registo de Ponto quando alguém chega atrasado.</p>
                                <div class="form-group"><label>Hora de entrada habitual</label><input type="time" id="perf_hora_entrada" value="${admin?.horaEntradaHabitual || '09:00'}" /></div>
                                <div class="form-group"><label>Tolerância (minutos)</label><input type="number" id="perf_tolerancia_atraso" value="${admin?.toleranciaAtrasoMin != null ? admin.toleranciaAtrasoMin : 15}" min="0" max="120" /></div>
                            </div>
                        </div>

                        <div class="ff-secao ff-tint-doc">
                            <div class="ff-secao-head"><i class="fas fa-calendar-days"></i> Feriado Municipal</div>
                            <div class="ff-secao-body">
                                <div class="form-group ff-span2">
                                    <label>Concelho</label>
                                    <select id="perf_concelho">
                                        <option value="">— Não mostrar feriado municipal —</option>
                                        ${Object.keys(FERIADOS_MUNICIPAIS).sort().map(c => `<option value="${c}" ${admin?.concelho === c ? 'selected' : ''}>${c}</option>`).join('')}
                                    </select>
                                    <div class="help-text" style="margin-top:4px;">O feriado municipal deste concelho passa a aparecer no Calendário de Equipa, junto com os feriados nacionais.</div>
                                </div>
                            </div>
                        </div>

                        <div class="ff-secao ff-tint-doc">
                            <div class="ff-secao-head"><i class="fas fa-list-ol"></i> Criação de Ordens de Serviço</div>
                            <div class="ff-secao-body">
                                <div class="form-group ff-span2">
                                    <label style="display:flex;align-items:center;gap:8px;cursor:pointer;">
                                        <input type="checkbox" id="perf_os_modo_wizard" ${admin?.osModoWizard ? 'checked' : ''} style="width:auto;margin:0;" />
                                        Criar novas OS em modo Wizard (passo a passo)
                                    </label>
                                    <div class="help-text" style="margin-top:4px;">Em vez do formulário único, a criação de uma nova Ordem de Serviço passa a ser feita por perguntas, uma de cada vez.</div>
                                </div>
                            </div>
                        </div>

                        ${moduloContratosAtivo(admin) ? `
                        <div class="ff-secao ff-tint-doc">
                            <div class="ff-secao-head"><i class="fas fa-list-ol"></i> Criação de Contratos de Manutenção</div>
                            <div class="ff-secao-body">
                                <div class="form-group ff-span2">
                                    <label style="display:flex;align-items:center;gap:8px;cursor:pointer;">
                                        <input type="checkbox" id="perf_contrato_modo_wizard" ${admin?.contratoModoWizard ? 'checked' : ''} style="width:auto;margin:0;" />
                                        Criar novos Contratos em modo Wizard (passo a passo)
                                    </label>
                                    <div class="help-text" style="margin-top:4px;">Em vez do formulário único, a criação de um novo Contrato de Manutenção passa a ser feita por perguntas, uma de cada vez.</div>
                                </div>
                            </div>
                        </div>
                        ` : ''}
                        </div>
`;
  }

  window.TotalGestProfileModalAdmin = { render: render };
})();
