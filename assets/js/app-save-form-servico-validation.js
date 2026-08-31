/* Total Gest — validações iniciais do formulário de ordem de serviço. */
(function () {
  'use strict';

  function validate(options) {
    const opts = options || {};
    const doc = opts.document || document;
    const data = opts.data || {};
    const user = opts.user || null;
    const isEdit = opts.isEdit === true;
    const item = opts.item || null;

    if (!isEdit && user?.role === 'funcionario') {
      opts.showAlert('Os funcionários não podem criar ordens de serviço. Só podem alterar o estado (pendente / em andamento / concluído).');
      return { ok: false };
    }

    const descricao = doc.getElementById('s_descricao')?.value.trim();
    if (!descricao || descricao.length < 3) {
      opts.showError('Descreve o trabalho a realizar nesta Ordem de Serviço (pelo menos 3 caracteres).');
      doc.getElementById('s_descricao')?.focus();
      return { ok: false };
    }

    const statusNovo = doc.getElementById('s_status')?.value;
    if (statusNovo === 'concluído' && (!isEdit || item?.status !== 'concluído')) {
      const adminId = user.role === 'admin' ? user.id : user.adminId;
      const admin = data.administradores?.find(a => a.id === adminId);
      const itens = (admin?.obrasChecklistItens || []).filter(it => it.ativo !== false);
      const concluido = item?.checklist || {};
      const porMarcar = itens.filter(it => !concluido[it.id]);
      if (porMarcar.length) {
        opts.showAlert('Não é possível concluir esta OS: falta marcar ' + porMarcar.length + ' ponto(s) do checklist de saída:\n\n' + porMarcar.map(it => '• ' + it.texto).join('\n') + '\n\nAbre "Checklist de Saída em OS / Obra" para os marcar.');
        return { ok: false };
      }
    }

    return { ok: true };
  }

  window.TotalGestSaveFormServicoValidation = { validate: validate };
})();
