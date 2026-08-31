/* Total Gest — validações comuns de contacto dos formulários. */
(function () {
  'use strict';

  function validate(options) {
    const opts = options || {};
    const doc = opts.document || document;

    for (const id of ['f_cp', 'c_cp']) {
      const field = doc.getElementById(id);
      if (field && field.value.trim() && !opts.postalCodeValid(field.value)) {
        opts.showError('Código postal inválido. Usa o formato 0000-000.');
        return false;
      }
    }

    for (const id of ['f_telefone', 'c_telefone']) {
      const field = doc.getElementById(id);
      if (field && field.value.trim() && !opts.phoneValid(field.value)) {
        opts.showError('Telefone inválido. O número (sem o indicativo) deve ter 9 dígitos.');
        return false;
      }
    }

    return true;
  }

  window.TotalGestSaveFormContactValidation = { validate: validate };
})();
