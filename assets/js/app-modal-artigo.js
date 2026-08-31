/* Total Gest — formulário do modal de artigo. */
(function () {
  'use strict';
  function render(options) {
    const opts = options || {};
    const item = opts.item || null;
    const _marcasTenant = opts.marcasTenant;
    const _optsCategoria = opts.optsCategoria;
    const UNIDADES_ARTIGO = opts.unidadesArtigo || [];
                const marcas = _marcasTenant();
                return `
                    <div class="ff-wrap">
                    <div class="ff-hero">
                        <div class="ff-avatar-drop" style="cursor:default;">
                            <div class="ff-avatar-ph" style="display:flex;"><i class="fas fa-box"></i></div>
                        </div>
                        <div class="ff-hero-fields">
                            <input type="text" id="ar_nome" class="ff-nome-input" placeholder="Nome do artigo *" value="${item ? (item.nome||'') : ''}" required />
                            <input type="text" id="ar_ref" class="ff-cargo-input" placeholder="Referência" value="${item ? (item.referencia||'') : ''}" />
                        </div>
                    </div>

                    <div class="ff-secao ff-tint-id">
                        <div class="ff-secao-head"><i class="fas fa-tags"></i> Classificação</div>
                        <div class="ff-secao-body">
                            <div class="form-group"><label>Marca</label>
                                <input type="text" id="ar_marca" list="ar_marcas_dl" value="${item ? (item.marca || '') : ''}" placeholder="Ex.: Hikvision, Ajax…" />
                                <datalist id="ar_marcas_dl">${marcas.map(m => `<option value="${m}">`).join('')}</datalist>
                            </div>
                            <div class="form-group"><label>Categoria</label>
                                <select id="ar_categoria" onchange="if(this.value==='__nova'){const n=criarCategoria(); this.innerHTML=_optsCategoria(n);}">${_optsCategoria(item ? item.categoria : '')}</select>
                            </div>
                            <div class="form-group ff-span2"><label>Unidade *</label><select id="ar_unidade">${UNIDADES_ARTIGO.map(u => `<option value="${u.v}" ${item && item.unidade === u.v ? 'selected' : ''}>${u.l}</option>`).join('')}</select></div>
                            <div class="form-group ff-span2"><label>Código de barras</label>
                                <div style="display:flex;gap:8px;">
                                    <input type="text" id="ar_codbarras" value="${item ? (item.codigoBarras || '') : ''}" placeholder="Lê com a pistola/telemóvel ou escreve à mão" style="flex:1;" ${item && item.temNumeroSerie ? 'disabled' : ''} />
                                    <button type="button" id="ar_codbarras_btn" class="btn btn-outline" onclick="abrirScannerCodigoBarras(v => document.getElementById('ar_codbarras').value = v)" ${item && item.temNumeroSerie ? 'disabled' : ''}><i class="fas fa-barcode"></i></button>
                                </div>
                                <div id="ar_codbarras_aviso" class="help-text" style="${item && item.temNumeroSerie ? '' : 'display:none;'}">Desativado — cada unidade tem o seu próprio número de série, em vez de um código de barras único para o artigo.</div>
                            </div>
                            <div class="form-group ff-span2" style="display:flex;align-items:center;">
                                <label style="display:flex;align-items:center;gap:8px;cursor:pointer;font-weight:500;">
                                    <input type="checkbox" id="ar_temserie" ${item && item.temNumeroSerie ? 'checked' : ''} style="width:auto;margin:0;" onchange="_arToggleCodBarras()" />
                                    Este artigo tem número de série individual (ex: câmaras, centrais de alarme)
                                </label>
                                <div class="help-text" style="margin-top:4px;">Se marcares, as entradas/saídas deste artigo pedem sempre o número de série de cada unidade, em vez de só uma quantidade.</div>
                            </div>
                            ${item && item.temNumeroSerie ? `<div class="form-group ff-span2"><button type="button" class="btn btn-outline btn-sm" onclick="verNumerosSerieArtigo('${item.id}')"><i class="fas fa-list"></i> Ver números de série em stock</button></div>` : ''}
                        </div>
                    </div>

                    <div class="ff-secao ff-tint-prof">
                        <div class="ff-secao-head"><i class="fas fa-warehouse"></i> Stock</div>
                        <div class="ff-secao-body">
                            <div class="form-group"><label>Stock inicial</label><input type="number" id="ar_stockini" value="${item && item.stockInicial!=null ? Math.round(item.stockInicial) : 0}" step="1" min="0" ${item?'disabled title="O stock altera-se por encomendas, consumos e ajustes"':''} /></div>
                            <div class="form-group"><label>Stock mínimo (alerta)</label><input type="number" id="ar_stockmin" value="${item && item.stockMinimo!=null ? Math.round(item.stockMinimo) : ''}" step="1" min="0" placeholder="opcional" /></div>
                            <div class="form-group"><label>Preço de venda (€)</label><input type="number" id="ar_preco" value="${item && item.precoVenda!=null ? item.precoVenda : ''}" step="0.01" placeholder="opcional" /></div>
                            <div class="form-group"><label>Preço de compra (€)</label><input type="number" id="ar_preco_compra" value="${item && item.precoCompra!=null ? item.precoCompra : ''}" step="0.01" placeholder="opcional" /><div class="help-text">Usado para calcular a margem de lucro nas obras/OS.</div></div>
                            <div class="form-group" style="display:flex;align-items:flex-end;">
                                <label style="display:flex;align-items:center;gap:8px;cursor:pointer;font-weight:500;">
                                    <input type="checkbox" id="ar_alerta" ${item && item.alertaStock ? 'checked' : ''} style="width:auto;margin:0;" />
                                    Avisar quando abaixo do mínimo
                                </label>
                            </div>
                        </div>
                    </div>

                    <div class="ff-secao ff-tint-contacto">
                        <div class="ff-secao-head"><i class="fas fa-note-sticky"></i> Notas</div>
                        <div class="ff-secao-body">
                            <div class="form-group ff-span2"><label>Observações</label><textarea id="ar_obs" rows="2">${item ? (item.observacoes||'') : ''}</textarea></div>
                        </div>
                    </div>
                    </div>
                `;
  }
  window.TotalGestModalArtigo = { render: render };
})();
