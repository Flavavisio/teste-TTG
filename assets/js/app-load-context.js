/* Total Gest — resolução do contexto de carregamento
 * Determina tenant, superadmin e cliente sem efetuar chamadas de rede.
 */
(function () {
  'use strict';

  function resolve(options) {
    const opts = options || {};
    let tenantId = opts.tenantIdParam;
    let superAdmin = opts.superAdminParam;
    let clienteId = opts.clienteIdParam;
    const user = opts.user;

    if (tenantId === undefined) {
      if (user) {
        superAdmin = user.role === 'superadmin';
        tenantId = superAdmin ? null : (user.role === 'admin' ? user.id : user.adminId);
        clienteId = user.role === 'cliente' ? user.id : null;
      } else {
        tenantId = null;
        superAdmin = true;
      }
    }

    return { tenantId: tenantId, superAdmin: superAdmin, clienteId: clienteId };
  }

  window.TotalGestLoadContext = { resolve: resolve };
})();
