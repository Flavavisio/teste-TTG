/* Total Gest — contexto de funcionário, admin e local da gravação de OS. */
(function () {
  'use strict';

  function prepare(options) {
    const opts = options || {};
    const doc = opts.document || document;
    const data = opts.data || {};
    const user = opts.user || null;

    let employeeId = doc.getElementById('s_funcionario').value || null;
    if (employeeId === '') employeeId = null;

    const checkboxContainer = doc.getElementById('s_func_checkboxes');
    const employeeIds = checkboxContainer
      ? [...checkboxContainer.querySelectorAll('input.s-func-check:checked')].map(function (checkbox) { return checkbox.value; })
      : (employeeId ? [employeeId] : []);

    let adminId = null;
    if (user?.role === 'admin' || user?.role === 'subadmin') {
      adminId = opts.tenantId();
    } else if (user?.role === 'encarregado') {
      const encarregado = data.encarregados?.find(function (item) { return item.id === user.id; });
      if (encarregado) adminId = encarregado.adminId;
    } else if (user?.role === 'funcionario') {
      const funcionario = data.funcionarios?.find(function (item) { return item.id === user.id; });
      if (funcionario) adminId = funcionario.adminId;
    }

    const existingOrder = opts.isEdit ? (data.servicos || []).find(function (item) { return item.id === opts.editingId; }) : null;
    let localId = doc.getElementById('s_local') ? doc.getElementById('s_local').value : (existingOrder ? existingOrder.localId : null);

    if (localId === '__novo__') {
      const newLocalName = (doc.getElementById('s_local_nome')?.value || '').trim();
      if (!newLocalName) {
        opts.showAlert('Indique o nome do novo local.');
        return { ok: false };
      }
      const clientId = doc.getElementById('s_cliente').value;
      const existingLocal = (data.locais || []).find(function (item) {
        return item.clienteId === clientId && item.nome.trim().toLowerCase() === newLocalName.toLowerCase();
      });
      if (existingLocal) {
        const createDuplicate = !opts.showConfirm(`Já existe um local chamado "${newLocalName}" para este cliente. Usar esse local existente (recomendado), em vez de criar um novo com o mesmo nome?\n\nOK = usar o existente · Cancelar = criar mesmo assim um novo (não recomendado)`);
        if (!createDuplicate) localId = existingLocal.id;
      }
    }

    if (localId === '__novo__') {
      const newLocalName = (doc.getElementById('s_local_nome')?.value || '').trim();
      const newLocalId = opts.generateId();
      data.locais = data.locais || [];
      data.locais.push({
        id: newLocalId,
        adminId: user.role === 'admin' ? user.id : user.adminId,
        clienteId: doc.getElementById('s_cliente').value,
        nome: newLocalName,
        morada: doc.getElementById('s_morada')?.value.trim() || '',
        numeroPorta: doc.getElementById('s_numero_porta')?.value.trim() || null,
        codigoPostal: doc.getElementById('s_codigo_postal')?.value.trim() || null,
        cidade: doc.getElementById('s_cidade')?.value.trim() || null,
        freguesia: doc.getElementById('s_freguesia')?.value.trim() || null,
        pinMapa: doc.getElementById('s_local_pin_mapa')?.value.trim() || null,
        dataCriacao: Date.now()
      });
      localId = newLocalId;
    }

    return {
      ok: true,
      employeeId: employeeId,
      employeeIds: employeeIds,
      adminId: adminId,
      existingOrder: existingOrder,
      localId: localId
    };
  }

  window.TotalGestSaveFormServicoContext = { prepare: prepare };
})();
