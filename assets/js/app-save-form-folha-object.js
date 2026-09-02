/* Total Gest — objeto base da folha de obra. */
(function () {
  'use strict';

  function prepare(options) {
    const opts = options || {};
    const doc = opts.document;
    const obj = {
      clienteId: opts.clientId || null,
      localId: opts.localId || null,
      obraDescricao: opts.workDescription,
      descricao: doc.getElementById('fo_descricao').value.trim(),
      materiais: doc.getElementById('fo_materiais').value.trim(),
      horasTrabalhadas: opts.hours,
      data: doc.getElementById('fo_data').value,
      funcionarioId: opts.employeeId,
      servicoId: doc.getElementById('fo_servico_id')?.value || null,
      obraId: doc.getElementById('fo_obra')?.value || null,
      assinatura: opts.signaturePath ? '' : opts.signatureBase64,
      assinaturaPath: opts.signaturePath,
      assinaturaNome: doc.getElementById('fo_assinatura_nome')?.value.trim() || null,
      dataAtualizacao: Date.now(),
      adminId: opts.adminId
    };

    if (!opts.isEdit) obj.id = opts.sheetId;
    if (!obj.obraDescricao) {
      opts.showAlert('A descrição da obra é obrigatória.');
      return { ok: false };
    }

    const sim = doc.getElementById('fo_mat_sim');
    const nao = doc.getElementById('fo_mat_nao');
    if (sim && !sim.classList.contains('ativo') && !nao.classList.contains('ativo')) {
      opts.showAlert('Indica se usaste materiais desta obra (Sim/Não).');
      return { ok: false };
    }

    if (!obj.funcionarioId) {
      opts.showAlert('Funcionário não identificado.');
      return { ok: false };
    }

    return { ok: true, value: obj };
  }

  window.TotalGestSaveFormFolhaObject = { prepare: prepare };
})();
