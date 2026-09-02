/* Total Gest — formulário do modal de funcionário. */
(function () {
  'use strict';

  function render(options) {
    const opts = options || {};
    const item = opts.item || null;
    const usuarioLogado = opts.user || null;
    const adminAtual = function () { return opts.admin || null; };
    const moduloRondasAtivo = opts.moduloRondasAtivo;
    const getFuncionariosByAdmin = opts.getFuncionariosByAdmin;
    const _tenantId = function () { return opts.tenantId; };
    const escapeHtmlSimples = opts.escapeHtmlSimples;
    const opcoesVeiculos = opts.opcoesVeiculos;

    return `
                        <div class="ff-wrap">
                        <div class="ff-hero">
                            <div class="ff-avatar-drop" onclick="document.getElementById('f_foto').click()" title="Alterar foto">
                                <img id="f_foto_preview" src="${item && item.foto ? item.foto : ''}" style="${item && item.foto ? '' : 'display:none;'}" />
                                <div id="f_foto_placeholder" class="ff-avatar-ph" style="${item && item.foto ? 'display:none;' : ''}"><i class="fas fa-user"></i></div>
                                <div class="ff-avatar-badge"><i class="fas fa-camera"></i></div>
                            </div>
                            <input type="hidden" id="f_foto_data" value="${item && item.foto ? item.foto : ''}" />
                            <input type="file" id="f_foto" accept="image/*" style="display:none;" onchange="funcFotoSelecionada(event)" />
                            <div class="ff-hero-fields">
                                <input type="text" id="f_nome" class="ff-nome-input" placeholder="Nome completo *" value="${item ? (item.nome||'') : ''}" required />
                                <input type="text" id="f_cargo" class="ff-cargo-input" placeholder="Cargo *" value="${item ? (item.cargo||'') : ''}" required />
                            </div>
                        </div>
                        ${!item && (usuarioLogado?.role === 'admin' || usuarioLogado?.role === 'subadmin') ? `
                        <div class="form-group" style="margin:-14px 0 14px;">
                            <label>Função no sistema *</label>
                            <select id="f_role_tipo" onchange="_fToggleEquipaEncarregado();_fToggleVigilanteSupervisor();">
                                <option value="funcionario">Funcionário</option>
                                <option value="vendedor">Vendedor — acesso restrito (ponto, férias/faltas, frota própria)</option>
                                <option value="subadmin">Sub-Admin — acesso total, exceto apagar o Admin</option>
                                <option value="encarregado">Encarregado — gere uma equipa de funcionários</option>
                                ${moduloRondasAtivo(adminAtual()) ? `
                                <option value="vigilante">Vigilante — faz rondas de vigilância</option>
                                <option value="supervisor_vigilantes">Supervisor de Vigilantes — gere uma equipa de vigilantes</option>
                                ` : ''}
                            </select>
                            <div class="help-text">Escolhe o nível de acesso desta pessoa no sistema.</div>
                        </div>
                        <div id="f_vigilante_supervisor_wrap" style="display:none;margin:-6px 0 14px;">
                            <label>Supervisor de Vigilantes (opcional — podes atribuir depois)</label>
                            <select id="f_vigilante_supervisor_id">
                                <option value="">— Sem supervisor —</option>
                            </select>
                            <div class="help-text">Um vigilante só pode estar atribuído a um Supervisor de Vigilantes — nunca a um funcionário normal.</div>
                        </div>
                        <div id="f_equipa_encarregado_wrap" style="display:none;margin:-6px 0 14px;">
                            <label>Equipa que este encarregado vai gerir (opcional — podes ajustar depois)</label>
                            <div id="f_equipa_encarregado_lista" style="max-height:180px;overflow:auto;border:1px solid #e2e8f0;border-radius:8px;padding:8px;"></div>
                        </div>
                        ` : ''}
                        ${item && item.role === 'vigilante' && (usuarioLogado?.role === 'admin' || usuarioLogado?.role === 'subadmin') ? `
                        <div class="form-group" style="margin:-6px 0 14px;">
                            <label>Supervisor de Vigilantes</label>
                            <select id="f_vigilante_supervisor_id_edit">
                                <option value="">— Sem supervisor —</option>
                                ${getFuncionariosByAdmin(_tenantId()).filter(f => f.role === 'supervisor_vigilantes').map(s => `<option value="${s.id}" ${item.vigilanteSupervisorId === s.id ? 'selected' : ''}>${escapeHtmlSimples(s.nome)}</option>`).join('')}
                            </select>
                        </div>` : ''}

                        <div class="ff-secao ff-tint-id">
                            <div class="ff-secao-head"><i class="fas fa-id-card"></i> Identificação</div>
                            <div class="ff-secao-body">
                                <div class="form-group"><label>Data de Nascimento</label><input type="date" id="f_nasc" value="${item ? (item.dataNascimento||'') : ''}" /></div>
                                <div class="form-group"><label>Morada *</label><input type="text" id="f_morada" value="${item ? (item.morada||'') : ''}" required /></div>
                                <div class="form-group"><label>Código Postal *</label><input type="text" id="f_cp" value="${item ? (item.codigoPostal||'') : ''}" placeholder="0000-000" oninput="aplicarMascaraCP(this)" maxlength="8" required /></div>
                            </div>
                        </div>

                        <div class="ff-secao ff-tint-contacto">
                            <div class="ff-secao-head"><i class="fas fa-address-book"></i> Contacto</div>
                            <div class="ff-secao-body">
                                <div class="form-group"><label>Telefone</label><input type="text" id="f_telefone" value="${item ? (item.telefone||'') : ''}" placeholder="+351 912345678" oninput="aplicarMascaraTelefone(this)" /></div>
                                <div class="form-group"><label>Email *</label><input type="email" id="f_email" value="${item ? (item.email||'') : ''}" required /></div>
                            </div>
                        </div>

                        <div class="ff-secao ff-tint-prof">
                            <div class="ff-secao-head"><i class="fas fa-briefcase"></i> Dados Profissionais</div>
                            <div class="ff-secao-body">
                                <div class="form-group"><label>Horas Semanais de trabalho *</label><input type="number" id="f_horas" value="${item ? (item.horasSemanais ?? 40) : 40}" step="1" min="1" required /></div>
                                ${usuarioLogado?.role === 'admin' ? `<div class="form-group"><label>Dias de férias por ano</label><input type="number" id="f_dias_ferias" value="${item ? (item.diasFerias ?? 22) : 22}" step="1" min="0" /></div>` : ''}
                                ${usuarioLogado?.role === 'admin' ? `<div class="form-group"><label>Ordenado bruto (€)</label><input type="number" id="f_ordenado" value="${item && item.ordenadoBruto != null ? item.ordenadoBruto : ''}" step="0.01" min="0" placeholder="0.00" /></div>` : ''}
                                ${(usuarioLogado?.role === 'admin' || usuarioLogado?.role === 'subadmin') && adminAtual()?.segurosAtivo ? `
                                <div class="form-group ff-span2" style="border-top:1px dashed #e2e8f0;padding-top:12px;margin-top:4px;">
                                    <label style="font-weight:700;color:#0e7490;"><i class="fas fa-shield-halved"></i> Apólice de Seguro de Acidentes de Trabalho</label>
                                </div>
                                <div class="form-group"><label>Número da apólice</label><input type="text" id="f_apolice_numero" value="${item && item.apoliceNumero ? item.apoliceNumero : ''}" placeholder="Ex.: 123456789" /></div>
                                <div class="form-group"><label>Seguradora</label><input type="text" id="f_apolice_seguradora" value="${item && item.apoliceSeguradora ? item.apoliceSeguradora : ''}" placeholder="Ex.: Fidelidade" /></div>
                                <div class="form-group"><label>Validade</label><input type="date" id="f_apolice_validade" value="${item && item.apoliceValidade ? item.apoliceValidade : ''}" /></div>
                                <div class="form-group ff-span2" style="border-top:1px dashed #e2e8f0;padding-top:12px;margin-top:4px;">
                                    <label style="font-weight:700;color:#0e7490;"><i class="fas fa-heart-pulse"></i> Seguro de Saúde</label>
                                </div>
                                <div class="form-group"><label>Número da apólice</label><input type="text" id="f_saude_numero" value="${item && item.saudeApoliceNumero ? item.saudeApoliceNumero : ''}" placeholder="Ex.: 987654321" /></div>
                                <div class="form-group"><label>Seguradora</label><input type="text" id="f_saude_seguradora" value="${item && item.saudeApoliceSeguradora ? item.saudeApoliceSeguradora : ''}" placeholder="Ex.: Médis" /></div>
                                <div class="form-group"><label>Validade</label><input type="date" id="f_saude_validade" value="${item && item.saudeApoliceValidade ? item.saudeApoliceValidade : ''}" /></div>
                                ` : ''}
                                ${(usuarioLogado?.role === 'admin' || usuarioLogado?.role === 'subadmin') && adminAtual()?.shstAtivo ? (() => {
                                    // SHST — calcula sozinho a periodicidade a partir da idade (data de nascimento
                                    // do próprio funcionário, já existente na ficha) e a data de vencimento a
                                    // partir da última consulta. Sem data de nascimento, assume periodicidade
                                    // anual por defeito (mais seguro do que assumir 2 em 2 anos).
                                    let idadeTxt = 'não definida — a assumir periodicidade anual', periodicidadeAnos = 1;
                                    if (item?.dataNascimento) {
                                        const nasc = new Date(item.dataNascimento + 'T00:00:00');
                                        const hoje = new Date();
                                        let idade = hoje.getFullYear() - nasc.getFullYear();
                                        const aindaNaoFezAnos = (hoje.getMonth() < nasc.getMonth()) || (hoje.getMonth() === nasc.getMonth() && hoje.getDate() < nasc.getDate());
                                        if (aindaNaoFezAnos) idade--;
                                        periodicidadeAnos = idade >= 50 ? 1 : 2;
                                        idadeTxt = idade + ' anos';
                                    }
                                    const ultimaConsulta = item?.shstUltimaConsulta || '';
                                    let vencimentoTxt = '—';
                                    if (ultimaConsulta) {
                                        const venc = new Date(ultimaConsulta + 'T00:00:00');
                                        venc.setFullYear(venc.getFullYear() + periodicidadeAnos);
                                        vencimentoTxt = venc.toLocaleDateString('pt-PT');
                                    }
                                    return `
                                <div class="form-group ff-span2" style="border-top:1px dashed #e2e8f0;padding-top:12px;margin-top:4px;">
                                    <label style="font-weight:700;color:#0e7490;"><i class="fas fa-user-doctor"></i> Saúde, Higiene e Segurança no Trabalho (SHST)</label>
                                    <div class="help-text" style="margin-top:2px;">Idade: ${idadeTxt} · Periodicidade: consulta a cada ${periodicidadeAnos} ano${periodicidadeAnos > 1 ? 's' : ''}.</div>
                                </div>
                                <div class="form-group"><label>Última consulta efetuada</label><input type="date" id="f_shst_ultima_consulta" value="${ultimaConsulta}" /></div>
                                <div class="form-group"><label>Quando vence</label><input type="text" value="${vencimentoTxt}" disabled style="background:#e9edf2;" /><span class="help-text">Calculado sozinho — avisa 30 dias antes de vencer.</span></div>
                                    `;
                                })() : ''}
                                ${usuarioLogado?.role === 'admin' ? `<div class="form-group ff-span2"><div class="help-text" style="margin:-2px 0 6px;">Dias de férias: por defeito 22/ano. Fins de semana e feriados nacionais não contam.</div></div>` : ''}
                                ${usuarioLogado?.role === 'admin' ? `<div class="form-group ff-span2"><label>Carro de empresa</label>
                                    <div style="display:flex;gap:8px;align-items:center;">
                                        <select id="f_veiculo" style="flex:1;">${opcoesVeiculos(item?.veiculoId)}</select>
                                        <button type="button" class="btn btn-outline" onclick="toggleNovoVeiculoFunc()" title="Criar novo veículo"><i class="fas fa-plus"></i></button>
                                    </div>
                                    <div id="novoVeiculoFunc" style="display:none;margin-top:8px;padding:10px;border:1px dashed #cbd5e1;border-radius:8px;">
                                        <div class="form-group" style="margin-bottom:6px;"><label>Matrícula *</label><input type="text" id="nv_matricula" placeholder="00-AA-00" /></div>
                                        <div class="form-group" style="margin-bottom:6px;"><label>Marca / Modelo</label><input type="text" id="nv_marca" placeholder="Ex.: Renault Clio" /></div>
                                        <button type="button" class="btn btn-success" onclick="criarVeiculoInline()"><i class="fas fa-check"></i> Criar e atribuir</button>
                                    </div>
                                </div>` : ''}
                            </div>
                        </div>

                        <div class="ff-secao ff-tint-acesso">
                            <div class="ff-secao-head"><i class="fas fa-lock"></i> Acesso ao Sistema</div>
                            <div class="ff-secao-body">
                                <div class="form-group ff-span2"><label>Senha${item ? '' : ' *'}</label><input type="password" id="f_senha" value="" placeholder="${item ? 'Deixe em branco para manter a atual' : ''}" ${item ? '' : 'required'} /></div>
                                ${(usuarioLogado?.role === 'admin' || usuarioLogado?.role === 'subadmin') ? `<div class="form-group ff-span2"><label style="display:flex;align-items:center;gap:8px;cursor:pointer;font-weight:500;">
                                    <input type="checkbox" id="f_gps_ponto" ${(!item || item.gpsPonto !== false) ? 'checked' : ''} style="width:auto;margin:0;" />
                                    Aplicar GPS na picagem de ponto
                                </label><span class="help-text" style="margin-top:4px;">Se desligado, este funcionário pica o ponto sem registar localização.</span></div>
                                <div class="form-group ff-span2"><label style="display:flex;align-items:center;gap:8px;cursor:pointer;font-weight:500;">
                                    <input type="checkbox" id="f_pode_assinar_relatorios" ${(!item || item.podeAssinarRelatorios !== false) ? 'checked' : ''} style="width:auto;margin:0;" />
                                    Pode assinar relatórios
                                </label><span class="help-text" style="margin-top:4px;">Se desligado, este funcionário pode preencher relatórios e guardar como rascunho, mas não pode concluir/assinar — só o encarregado responsável ou o admin podem concluir.</span></div>` : ''}
                            </div>
                        </div>
                        </div>
                    `;
  }

  window.TotalGestModalFuncionario = { render: render };
})();
