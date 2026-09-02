/* Total Gest — aplicação local comum do resultado dos formulários. */
(function () {
  'use strict';

  function apply(options) {
    const opts = options || {};
    const data = opts.data || {};
    const entity = opts.entity;
    const value = opts.value || {};
    let list;

    if (entity === 'funcionario') list = data.funcionarios || [];
    else if (entity === 'cliente') list = data.clientes || [];
    else if (entity === 'servico') list = data.servicos || [];
    else if (entity === 'folha') list = data.folhasObra || [];
    else return { ok: false, value: value, list: null, oldService: null, oldEmployee: null };

    let oldService = null;
    let oldEmployee = null;

    if (opts.isEdit) {
      const idx = list.findIndex(function (item) { return item.id === opts.editingId; });
      if (idx !== -1) {
        if (entity === 'servico') oldService = { ...list[idx] };
        if (entity === 'funcionario') oldEmployee = { ...list[idx] };
        list[idx] = { ...list[idx], ...value };
      }
    } else {
      if (!value.id) value.id = opts.generateId();
      list.push(value);
    }

    return {
      ok: true,
      value: value,
      list: list,
      oldService: oldService,
      oldEmployee: oldEmployee
    };
  }

  window.TotalGestSaveFormPersist = { apply: apply };
})();
