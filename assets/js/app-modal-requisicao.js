/* Total Gest — formulário do modal de requisição. */
(function () {
  'use strict';

  function render(options) {
    const opts = options || {};
    const item = opts.item || null;
    const usuarioLogado = opts.user || null;
    const getDataHoje = opts.getDataHoje;
    const _pessoasParaAtribuir = opts.pessoasParaAtribuir;
                const hoje = getDataHoje();
                const itensHtml = item && item.itens && item.itens.length > 0 ?
                    item.itens.map((it, idx) => `
                            <div class="item-linha">
                                <input type="text" class="item-produto" value="${it.nome}" placeholder="Produto" />
                                <input type="number" class="item-qtd" value="${it.quantidade}" placeholder="Qtd" style="width:80px;" />
                                <button type="button" class="btn-remove-item" onclick="removerItem(this)"><i class="fas fa-times"></i></button>
                            </div>
                        `).join('') :
                    `
                            <div class="item-linha">
                                <input type="text" class="item-produto" placeholder="Produto" />
                                <input type="number" class="item-qtd" placeholder="Qtd" style="width:80px;" />
                                <button type="button" class="btn-remove-item" onclick="removerItem(this)"><i class="fas fa-times"></i></button>
                            </div>
                        `;
                return `
                        <div class="ff-wrap">
                        <div class="ff-hero">
                            <div class="ff-avatar-drop" style="cursor:default;">
                                <div class="ff-avatar-ph" style="display:flex;"><i class="fas fa-boxes-stacked"></i></div>
                            </div>
                            <div class="ff-hero-fields">
                                <input type="text" id="req_obra_desc" class="ff-nome-input" placeholder="Obra (descrição) *" value="${item ? item.obraDescricao : ''}" required />
                                <input type="date" id="req_data" class="ff-cargo-input" value="${item ? item.data : hoje}" />
                            </div>
                        </div>

                        <div class="ff-secao ff-tint-id">
                            <div class="ff-secao-head"><i class="fas fa-note-sticky"></i> Pedido</div>
                            <div class="ff-secao-body">
                                <div class="form-group ff-span2"><label>Fornecedor</label><input type="text" id="req_fornecedor" value="${item ? item.fornecedor : ''}" /></div>
                                <div class="form-group ff-span2"><label>Descrição *</label><textarea id="req_descricao" required>${item ? item.descricao : ''}</textarea></div>
                                ${usuarioLogado?.role === 'admin' ? `
                                    <div class="form-group ff-span2"><label>Funcionário (opcional)</label>
                                        <select id="req_funcionario">
                                            <option value="">Selecione</option>
                                            ${_pessoasParaAtribuir(usuarioLogado.id).map(f => `<option value="${f.id}" ${item && item.funcionarioId === f.id ? 'selected' : ''}>${f.nome}</option>`).join('')}
                                        </select>
                                    </div>
                                ` : ''}
                            </div>
                        </div>

                        <div class="ff-secao ff-tint-prof">
                            <div class="ff-secao-head"><i class="fas fa-list-check"></i> Itens</div>
                            <div class="ff-secao-body">
                                <div class="form-group ff-span2">
                                    <div id="itensContainer">
                                        ${itensHtml}
                                    </div>
                                    <button type="button" class="btn-add-item" onclick="adicionarItem()"><i class="fas fa-plus"></i> Adicionar mais</button>
                                    <button type="button" class="btn btn-outline btn-sm" style="margin-left:8px;" onclick="abrirScannerCodigoBarras(_reqCodigoLido)"><i class="fas fa-barcode"></i> Ler código de barras</button>
                                </div>
                            </div>
                        </div>

                        <div class="ff-secao ff-tint-contacto">
                            <div class="ff-secao-head"><i class="fas fa-paperclip"></i> Anexo</div>
                            <div class="ff-secao-body">
                                <div class="form-group ff-span2">
                                    <label>Anexo (opcional)</label>
                                    <input type="file" id="req_anexo" accept=".pdf,.jpg,.jpeg,.png,.doc,.docx" />
                                    ${item && item.anexo ? `<div class="help-text">Anexo atual já enviado.</div>` : ''}
                                </div>
                            </div>
                        </div>
                        </div>
                        <input type="hidden" id="req_funcionario_id" value="${usuarioLogado.id}" />
                    `;
  }

  window.TotalGestModalRequisicao = { render: render };
})();
