/* Total Gest — gravação do perfil de distribuidor. */
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

    function aplicarDist(logoData) {
      admin.nome = nome;
      admin.empresa = empresa;
      admin.layout = documentRef.getElementById('perf_layout')?.value || 'sidebar';
      if (senha) admin.senha = senha;
      if (logoData !== undefined) admin.logo = logoData;
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

    const fileInputDist = documentRef.getElementById('perf_logo');
    if (fileInputDist && fileInputDist.files && fileInputDist.files[0]) {
      const reader = new FileReader();
      reader.onload = function (ev) { aplicarDist(ev.target.result); };
      reader.readAsDataURL(fileInputDist.files[0]);
    } else {
      aplicarDist(undefined);
    }
  }

  window.TotalGestProfileSaveDistributor = { run: run };
})();
