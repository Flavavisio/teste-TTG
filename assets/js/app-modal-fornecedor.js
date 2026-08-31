/* Total Gest — formulário do modal de fornecedor. */
(function () {
  'use strict';
  function render(options) {
    const opts = options || {};
    const item = opts.item || null;
    return `
                    <div class="ff-wrap">
                    <div class="ff-hero">
                        <div class="ff-avatar-drop" style="cursor:default;">
                            <div class="ff-avatar-ph" style="display:flex;"><i class="fas fa-industry"></i></div>
                        </div>
                        <div class="ff-hero-fields">
                            <input type="text" id="fr_nome" class="ff-nome-input" placeholder="Nome do fornecedor *" value="${item ? (item.nome||'') : ''}" required />
                            <input type="text" id="fr_nif" class="ff-cargo-input" placeholder="NIF" value="${item ? (item.nif||'') : ''}" />
                        </div>
                    </div>

                    <div class="ff-secao ff-tint-contacto">
                        <div class="ff-secao-head"><i class="fas fa-address-book"></i> Contacto</div>
                        <div class="ff-secao-body">
                            <div class="form-group"><label>Contacto</label><input type="text" id="fr_contacto" value="${item ? (item.contacto||'') : ''}" /></div>
                            <div class="form-group"><label>Email</label><input type="email" id="fr_email" value="${item ? (item.email||'') : ''}" /></div>
                        </div>
                    </div>

                    <div class="ff-secao ff-tint-prof">
                        <div class="ff-secao-head"><i class="fas fa-note-sticky"></i> Notas</div>
                        <div class="ff-secao-body">
                            <div class="form-group ff-span2"><label>Observações</label><textarea id="fr_obs" rows="2">${item ? (item.observacoes||'') : ''}</textarea></div>
                        </div>
                    </div>
                    </div>
                `;
  }
  window.TotalGestModalFornecedor = { render: render };
})();
