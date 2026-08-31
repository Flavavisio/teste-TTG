/* Total Gest — preparação da assinatura da folha de obra. */
(function () {
  'use strict';

  async function prepare(options) {
    const opts = options || {};
    const assinaturaBase64 = opts.captureSignature() || null;
    const folhaId = opts.editingId || opts.generateId();
    let assinaturaPath = null;

    if (assinaturaBase64) {
      const path = opts.adminId + '/folhas/' + folhaId + '.png';
      const ok = await opts.uploadImage(path, assinaturaBase64);
      if (ok) assinaturaPath = path;
    }

    return {
      base64: assinaturaBase64,
      id: folhaId,
      path: assinaturaPath
    };
  }

  window.TotalGestSaveFormFolhaSignature = { prepare: prepare };
})();
