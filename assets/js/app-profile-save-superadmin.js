/* Total Gest — gravação do perfil de superadmin. */
(function () {
  'use strict';

  function run(options) {
    const opts = options || {};
    const documentRef = opts.document;
    const data = opts.data;
    const user = opts.user;
    const nome = opts.name;
    const senha = opts.password;

    const config = opts.getConfig();
    config.nome = nome;
    const novoEmailSA = documentRef.getElementById('perf_email')?.value.trim();
    if (novoEmailSA) config.email = novoEmailSA;
    if (senha) config.senha = senha;
    config.mostrarEstadoOnline = documentRef.getElementById('perf_estado_online_equipa')?.checked || false;
    config.layout = documentRef.getElementById('perf_layout')?.value || 'sidebar';

    const saRec = data.administradores?.find(function (admin) { return admin.id === 'superadmin'; }) || (function () {
      const novo = { id: 'superadmin', nome: 'Super Admin', email: 'superadmin@totalgest.pt', senha: 'nao-usado-login-separado', empresa: 'Total Gest', ativo: true, dataCriacao: Date.now() };
      data.administradores = data.administradores || [];
      data.administradores.push(novo);
      return novo;
    })();

    saRec.dadosBancarios = {
      titular: documentRef.getElementById('perf_titular')?.value.trim() || '',
      iban: documentRef.getElementById('perf_iban')?.value.trim() || '',
      banco: documentRef.getElementById('perf_banco')?.value.trim() || '',
      swift: documentRef.getElementById('perf_swift')?.value.trim() || '',
      mbway: documentRef.getElementById('perf_mbway')?.value.trim() || '',
      instrucoes: documentRef.getElementById('perf_instrucoes')?.value.trim() || ''
    };

    function concluir() {
      opts.saveConfig(config);
      const superAdmin = data.funcionarios?.find(function (employee) { return employee.role === 'superadmin'; });
      if (superAdmin) {
        superAdmin.nome = nome;
        if (senha) superAdmin.senha = senha;
      }
      opts.saveData(data);
      opts.closeModal();
      user.nome = nome;
      opts.renderAll();
      opts.alert('Perfil atualizado com sucesso!');
    }

    const fileInput = documentRef.getElementById('perf_logo');
    if (fileInput && fileInput.files && fileInput.files[0]) {
      const reader = new FileReader();
      reader.onload = function (ev) {
        config.logo = ev.target.result;
        concluir();
      };
      reader.readAsDataURL(fileInput.files[0]);
    } else {
      concluir();
    }
  }

  window.TotalGestProfileSaveSuperadmin = { run: run };
})();
