/* Total Gest — atribuição do número de registo da Ordem de Serviço. */
(function () {
  'use strict';

  async function apply(options) {
    const opts = options || {};
    const value = opts.value || {};
    if (!opts.isEdit) {
      value.numeroRegisto = await opts.generateRegistrationNumber();
    }
    return value;
  }

  window.TotalGestSaveFormServicoRegistration = { apply: apply };
})();
