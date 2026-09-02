/* Total Gest — criação pós-gravação das contas Auth de funcionário e cliente. */
(function () {
  'use strict';

  async function run(options) {
    const opts = options || {};
    const value = opts.value || {};

    const becameSubadmin = opts.entity === 'funcionario' && value.role === 'subadmin' && (
      !opts.isEdit || (opts.oldEmployee && opts.oldEmployee.role !== 'subadmin')
    );

    if (opts.entity === 'funcionario' && (!opts.isEdit || becameSubadmin) && value.email && value.senha) {
      try {
        await opts.saveData(opts.data);
      } catch (error) {
        opts.showAlert(`⚠️ O funcionário ${value.nome} foi criado no ecrã, mas ainda não foi possível confirmar a gravação no servidor (${error && error.message ? error.message : error}).\n\nNão foi criada a conta de login para evitar inconsistências (ficaria uma conta "fantasma" sem funcionário associado) — verifica a ligação e tenta novamente mais tarde.`);
        return;
      }

      const accountRole = value.role === 'subadmin'
        ? 'subadmin'
        : (value.role === 'vigilante' || value.role === 'supervisor_vigilantes')
          ? value.role
          : 'funcionario';

      opts.createAuth(value.email, value.senha, accountRole, value.adminId, value.id, value.nome).then(function (result) {
        if (!result.ok) {
          opts.showAlert('✅ Funcionário guardado.\n⚠️ A conta de login não foi criada/atualizada automaticamente: ' + result.erro + '\n\nSe o email já tiver sido usado antes (ex.: um funcionário apagado há mais tempo), a conta pode ter ficado "presa" de uma eliminação antiga que falhou. Contacta o suporte técnico para a removerem de vez, ou tenta apagar este registo e voltar a criar (a partir de agora, a app avisa logo se uma eliminação de conta falhar).');
        }
      });
    }

    if (opts.entity === 'cliente' && value.portalAtivo && value.nif && value.nif !== '999999990' && value.senha) {
      try {
        await opts.saveData(opts.data);
      } catch (error) {
        opts.showAlert(`⚠️ O cliente ${value.nome} foi criado no ecrã, mas ainda não foi possível confirmar a gravação no servidor (${error && error.message ? error.message : error}).\n\nNão foi criada a conta do portal para evitar inconsistências — tenta novamente mais tarde.`);
        return;
      }

      const clientAccountEmail = opts.clientTechnicalEmail(value.nif, value.adminId);
      opts.createAuth(clientAccountEmail, value.senha, 'cliente', value.adminId, value.id, value.nome).then(function (result) {
        if (!result.ok) {
          opts.showAlert('✅ Cliente criado.\n⚠️ A conta do portal não foi criada automaticamente: ' + result.erro + '\n\nSe o NIF já tiver sido usado antes (ex.: um cliente apagado há mais tempo), a conta pode ter ficado "presa" de uma eliminação antiga que falhou. Contacta o suporte técnico para a removerem de vez, ou tenta apagar este registo e voltar a criar (a partir de agora, a app avisa logo se uma eliminação de conta falhar).');
        }
      });
    }
  }

  window.TotalGestSaveFormAuth = { run: run };
})();
