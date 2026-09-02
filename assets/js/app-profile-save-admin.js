/* Total Gest — gravação do perfil admin/subadmin. */
(function () {
  'use strict';

  function run(options) {
    const opts = options || {};
    const documentRef = opts.document;
    const data = opts.data;
    const user = opts.user;
    const nome = opts.name;
    const senha = opts.password;
    const admin = opts.getAdmin();
    if (!admin) return;

    const empresa = documentRef.getElementById('perf_empresa')?.value.trim() || '';
    const telefone = documentRef.getElementById('perf_telefone')?.value.trim() || '';
    const func = data.funcionarios?.find(function (employee) { return employee.id === user.id; });
    const anepc = documentRef.getElementById('perf_anepc')?.value.trim() || '';
    const anepcData = documentRef.getElementById('perf_anepc_data')?.value || '';
    const anepcValidade = documentRef.getElementById('perf_anepc_validade')?.value || '';
    const registoPrevio = documentRef.getElementById('perf_registo_previo')?.value.trim() || '';
    const registoPrevioData = documentRef.getElementById('perf_registo_previo_data')?.value || '';
    const registoPrevioValidade = documentRef.getElementById('perf_registo_previo_validade')?.value || '';
    const nifEmpresa = documentRef.getElementById('perf_nif')?.value.trim() || '';
    const cor = documentRef.getElementById('perf_cor')?.value.trim() || '';

    if (anepc && opts.numberAlreadyUsed('numeroAnepc', anepc, admin.id)) {
      opts.alert('Já existe outra empresa registada com esse número de ANEPC.');
      return;
    }
    if (registoPrevio && opts.numberAlreadyUsed('numeroRegistoPrevio', registoPrevio, admin.id)) {
      opts.alert('Já existe outra empresa com esse número de registo prévio.');
      return;
    }
    if (cor && !/^#[0-9a-fA-F]{6}$/.test(cor)) {
      opts.alert('A cor deve estar no formato #RRGGBB (ex.: #152A52).');
      return;
    }

    function aplicar(logoData) {
      admin.nome = nome;
      admin.empresa = empresa;
      admin.nif = nifEmpresa || null;
      admin.layout = documentRef.getElementById('perf_layout')?.value || 'sidebar';
      admin.numeroAnepc = anepc || null;
      admin.dataAnepc = anepcData || null;
      admin.anepcValidade = anepcValidade || null;
      admin.numeroRegistoPrevio = registoPrevio || null;
      admin.dataRegistoPrevio = registoPrevioData || null;
      admin.registoPrevioValidade = registoPrevioValidade || null;
      admin.corCorporativa = cor || null;
      admin.horaEntradaHabitual = documentRef.getElementById('perf_hora_entrada')?.value || '09:00';
      const tolerancia = documentRef.getElementById('perf_tolerancia_atraso')?.value;
      admin.toleranciaAtrasoMin = tolerancia !== '' && tolerancia != null ? parseInt(tolerancia, 10) : 15;
      admin.osModoWizard = documentRef.getElementById('perf_os_modo_wizard')?.checked || false;
      admin.contratoModoWizard = documentRef.getElementById('perf_contrato_modo_wizard')?.checked || false;
      admin.concelho = documentRef.getElementById('perf_concelho')?.value || null;
      admin.segurancaAtivo = documentRef.getElementById('perf_seguranca_ativo')?.checked || false;
      admin.segurosAtivo = documentRef.getElementById('perf_seguros_ativo')?.checked || false;
      admin.shstAtivo = documentRef.getElementById('perf_shst_ativo')?.checked || false;
      if (senha) admin.senha = senha;
      if (logoData !== undefined) admin.logo = logoData;
      if (window._perfCertificadoraLogoRemover) {
        admin.certificadoraLogo = null;
        window._perfCertificadoraLogoRemover = false;
      }
      if (window._perfCertificadoraLogoNova !== undefined) {
        admin.certificadoraLogo = window._perfCertificadoraLogoNova || null;
        window._perfCertificadoraLogoNova = undefined;
      }
      if (func) {
        func.nome = nome;
        func.telefone = telefone;
        if (senha) func.senha = senha;
      }
      opts.saveData(data);
      opts.closeModal();
      user.nome = nome;
      opts.applyHeaderConfig();
      opts.renderAll();
      opts.alert('Perfil atualizado com sucesso!');
    }

    const fileInput = documentRef.getElementById('perf_logo');
    if (fileInput && fileInput.files && fileInput.files[0]) {
      const reader = new FileReader();
      reader.onload = function (ev) { aplicar(ev.target.result); };
      reader.readAsDataURL(fileInput.files[0]);
    } else {
      aplicar(undefined);
    }
  }

  window.TotalGestProfileSaveAdmin = { run: run };
})();
