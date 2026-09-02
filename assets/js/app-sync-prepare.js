/* Total Gest — preparação local antes da sincronização
 * Corrige apenas referências locais inválidas; não faz pedidos de rede.
 */
(function () {
  'use strict';

  function repairInvalidEquipmentLocations(data) {
    const source = data || {};
    const validLocationIds = new Set((source.locais || []).map(function (location) { return location.id; }));
    (source.equipamentos || []).forEach(function (equipment) {
      if (equipment.localId && !validLocationIds.has(equipment.localId)) equipment.localId = null;
    });
  }

  window.TotalGestSyncPrepare = {
    repairInvalidEquipmentLocations: repairInvalidEquipmentLocations
  };
})();
