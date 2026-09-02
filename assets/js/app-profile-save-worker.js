/* Total Gest — gravação do perfil de colaborador/encarregado. */
(function () {
  'use strict';

  function run(options) {
    const opts = options || {};
    const documentRef = opts.document;
    const data = opts.data;
    const user = opts.user;
    const nome = opts.name;
    const senha = opts.password;
    const func = data.funcionarios?.find(function (employee) { return employee.id === user.id; }) ||
      data.encarregados?.find(function (foreman) { return foreman.id === user.id; });
    if (!func) return;

    func.nome = nome;
    const telefone = documentRef.getElementById('perf_telefone')?.value.trim();
    if (telefone !== undefined) func.telefone = telefone;
    if (senha) func.senha = senha;

    function concluir() {
      opts.saveData(data);
      opts.closeModal();
      user.nome = nome;
      opts.renderAll();
      opts.alert('Perfil atualizado com sucesso!');
    }

    const fotoInput = documentRef.getElementById('perf_foto');
    if (fotoInput && fotoInput.files && fotoInput.files[0]) {
      const reader = new FileReader();
      reader.onload = function (ev) {
        func.foto = ev.target.result;
        concluir();
      };
      reader.readAsDataURL(fotoInput.files[0]);
      return;
    }
    concluir();
  }

  window.TotalGestProfileSaveWorker = { run: run };
})();
