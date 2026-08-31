/* Total Gest — migração de ficheiros pendentes antes da sincronização
 * Percorre campos configurados, delega o upload e mantém data URLs como fallback em caso de erro.
 */
(function () {
  'use strict';

  async function migratePending(options) {
    const opts = options || {};
    const data = opts.data || {};
    const fields = opts.fields || {};
    const uploadDataURL = opts.uploadDataURL;

    if (typeof uploadDataURL !== 'function') {
      throw new Error('TotalGestSyncFiles: uploadDataURL invalido');
    }

    for (const collection of Object.keys(fields)) {
      for (const item of (data[collection] || [])) {
        for (const field of fields[collection]) {
          const value = item[field];
          if (typeof value === 'string' && value.startsWith('data:')) {
            try {
              item[field] = await uploadDataURL(value, collection);
            } catch (error) {
              console.error('upload ' + collection + '.' + field + ':', error.message || error);
              // Mantém o data URL original como fallback, tal como no comportamento legado.
            }
          }
        }
      }
    }
  }

  window.TotalGestSyncFiles = { migratePending: migratePending };
})();
