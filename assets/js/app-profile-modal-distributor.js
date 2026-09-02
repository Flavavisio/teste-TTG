/* Total Gest — conteúdo do modal de perfil do distribuidor. */
(function () {
  'use strict';

  function render(options) {
    const opts = options || {};
    const admin = opts.admin || null;
    const func = opts.employee || null;

    return `
                        <div class="ff-wrap">
                        <div class="ff-hero">
                            <div class="ff-avatar-drop" onclick="document.getElementById('perf_logo').click()" title="Alterar logótipo">
                                <img id="perf_logo_img" src="${admin?.logo || ''}" style="${admin?.logo ? '' : 'display:none;'}" />
                                <div id="perf_logo_placeholder" class="ff-avatar-ph" style="${admin?.logo ? 'display:none;' : ''}"><i class="fas fa-diagram-project"></i></div>
                                <div class="ff-avatar-badge"><i class="fas fa-camera"></i></div>
                            </div>
                            <input type="file" id="perf_logo" accept="image/*" style="display:none;" onchange="previewPerfilLogo(event)" />
                            <div class="ff-hero-fields">
                                <input type="text" id="perf_empresa" class="ff-nome-input" placeholder="Nome da empresa/negócio" value="${admin?.empresa || ''}" />
                                <input type="text" id="perf_nome" class="ff-cargo-input" placeholder="Nome do responsável *" value="${admin?.nome || ''}" required />
                            </div>
                        </div>
                        <div id="perf_logo_preview" style="display:none;"></div>

                        <div class="ff-secao ff-tint-id">
                            <div class="ff-secao-head"><i class="fas fa-diagram-project"></i> Conta de Distribuidor</div>
                            <div class="ff-secao-body">
                                <div class="form-group ff-span2"><div class="help-text" style="margin:0;">Desconto atribuído: <strong>${admin?.distribuidorDesconto ?? 0}%</strong> sobre o preço de catálogo, em cada licença/add-on que emitas. Só a Total Gest pode alterar este valor.</div></div>
                            </div>
                        </div>

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
                                    <label>Layout</label>
                                    <select id="perf_layout">
                                        <option value="sidebar" ${(admin?.layout || 'sidebar') === 'sidebar' ? 'selected' : ''}>Barra lateral (moderno)</option>
                                        <option value="cards" ${admin?.layout === 'cards' ? 'selected' : ''}>Clássico (cards no topo)</option>
                                        <option value="foco" ${admin?.layout === 'foco' ? 'selected' : ''}>Total Gest Foco (grupos + painel lateral)</option>
                                        <option value="aurora" ${admin?.layout === 'aurora' ? 'selected' : ''}>Total Gest Aurora (visual moderno, escuro)</option>
                                    </select>
                                </div>
                            </div>
                        </div>
                        </div>
                    `;
  }

  window.TotalGestProfileModalDistributor = { render: render };
})();
