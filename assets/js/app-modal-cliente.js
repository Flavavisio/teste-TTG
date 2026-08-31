/* Total Gest — formulário do modal de cliente. */
(function () {
  'use strict';

  function render(options) {
    const opts = options || {};
    const item = opts.item || null;
    const adminAtual = function () { return opts.admin || null; };
    const moduloErpAtivo = opts.moduloErpAtivo;

    return `
                        <div class="ff-wrap">
                        <div class="ff-hero" style="padding:14px 20px;">
                            <div class="ff-avatar-drop" style="cursor:default;">
                                <div class="ff-avatar-ph" style="display:flex;"><i class="fas fa-building"></i></div>
                            </div>
                            <div class="ff-hero-fields">
                                <input type="text" id="c_nome" class="ff-nome-input" placeholder="Nome do cliente" value="${item ? (item.nome||'') : ''}" />
                                <div style="display:flex;gap:6px;align-items:center;">
                                    <input type="text" id="c_nif" class="ff-cargo-input" style="flex:1;" placeholder="NIF *" value="${item ? (item.nif||'') : ''}" maxlength="9" inputmode="numeric" pattern="[0-9]*" oninput="this.value=this.value.replace(/\D/g,'').slice(0,9);" required />
                                    ${moduloErpAtivo(adminAtual()) ? `<button type="button" class="btn btn-sm" style="background:#7c3aed;color:#fff;white-space:nowrap;" onclick="_consultarNifMoloni()" title="Preencher nome e morada automaticamente a partir do NIF"><i class="fas fa-magnifying-glass"></i> Ir buscar</button>` : ''}
                                </div>
                            </div>
                        </div>

                        <div class="ff-secao ff-tint-id">
                            <div class="ff-secao-head"><i class="fas fa-location-dot"></i> Morada</div>
                            <div class="ff-secao-body">
                                <div class="form-group ff-span2"><label>Número de cliente</label><input type="text" id="c_numero_cliente" value="${item ? (item.numeroCliente||'') : ''}" maxlength="8" inputmode="numeric" pattern="[0-9]*" placeholder="Até 8 dígitos" /></div>
                                <div class="form-group ff-span2"><label>Morada</label><input type="text" id="c_morada" value="${item ? (item.morada||item.endereco||'') : ''}" autocomplete="off" /></div>
                                <div class="form-group"><label>Número de porta</label><input type="text" id="c_numero_porta" value="${item ? (item.numeroPorta||'') : ''}" placeholder="ex.: 3, 3A, Lote 2" /></div>
                                <div class="form-group"><label>Código Postal</label><input type="text" id="c_cp" value="${item ? (item.codigoPostal||'') : ''}" placeholder="0000-000" autocomplete="off" oninput="aplicarMascaraCP(this); _cttPreencherPorCP(this.value,{cidade:'c_cidade',freguesia:'c_freguesia',morada:'c_morada'})" maxlength="8" /></div>
                                <div class="form-group"><label>Cidade</label><input type="text" id="c_cidade" value="${item ? (item.cidade||'') : ''}" autocomplete="off" /></div>
                                <div class="form-group ff-span2"><label>Freguesia</label><input type="text" id="c_freguesia" value="${item ? (item.freguesia||'') : ''}" autocomplete="off" /></div>
                                <div class="form-group ff-span2"><label><i class="fas fa-map-pin" style="color:#dc2626;"></i> Pin do Google Maps (opcional) <a href="https://www.google.com/maps" target="_blank" rel="noopener" style="font-weight:400;font-size:.78rem;color:#2563eb;text-decoration:none;margin-left:8px;"><i class="fas fa-up-right-from-square"></i> Abrir Google Maps</a></label><input type="text" id="c_pin_mapa" value="${item ? (item.pinMapa||'') : ''}" placeholder="Cola aqui o link ou as coordenadas copiadas do Google Maps" autocomplete="off" oninput="_clienteAtualizarLinkPin()" /><span class="help-text">No Google Maps: toca no local certo do mapa, depois "Partilhar" → "Copiar link", e cola aqui. Isso garante o ponto exato, mesmo que a morada escrita não seja suficiente para o localizar.</span><div id="c_pin_mapa_link" style="margin-top:6px;font-size:.82rem;"></div></div>
                            </div>
                        </div>

                        <div class="ff-secao ff-tint-contacto">
                            <div class="ff-secao-head"><i class="fas fa-address-book"></i> Contacto</div>
                            <div class="ff-secao-body">
                                <div class="form-group"><label>Telefone</label><input type="text" id="c_telefone" value="${item ? (item.telefone||'') : ''}" placeholder="+351 912345678" oninput="aplicarMascaraTelefone(this)" /></div>
                                <div class="form-group"><label>Email</label><input type="email" id="c_email" value="${item ? (item.email||'') : ''}" /></div>
                                <div class="form-group ff-span2"><label>Pessoa de contacto principal</label><input type="text" id="c_contacto" value="${item ? (item.pessoaContacto||'') : ''}" /></div>
                            </div>
                        </div>

                        <div class="ff-secao ff-tint-acesso">
                            <div class="ff-secao-head"><i class="fas fa-user-lock"></i> Acesso ao Portal do Cliente</div>
                            <div class="ff-secao-body">
                                <div class="form-group ff-span2">
                                    <label style="display:flex;align-items:center;gap:8px;cursor:pointer;">
                                        <input type="checkbox" id="c_portal_ativo" ${item && item.portalAtivo ? 'checked' : ''} style="width:auto;margin:0;" />
                                        Ativar o Portal do Cliente para este cliente (entra com o email acima)
                                    </label>
                                </div>
                                <div class="form-group ff-span2"><label>Senha do portal ${item ? '(deixar em branco mantém a atual)' : ''}</label><input type="password" id="c_senha" value="" placeholder="${item && item.senha ? '••••••••' : 'Definir senha'}" autocomplete="new-password" /></div>
                                <div class="form-group ff-span2"><div class="help-text" style="margin-top:-4px;">O Portal do Cliente está incluído na licença base. Ative aqui o acesso para cada cliente que precise dele.</div></div>
                            </div>
                        </div>
                        </div>
                    `;
  }

  window.TotalGestModalCliente = { render: render };
})();
