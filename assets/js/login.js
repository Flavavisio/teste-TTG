(function () {
  'use strict';

  var cfg = window.TG_AUTH_CONFIG;
  var form = document.getElementById('loginForm');
  var campoUtilizador = document.getElementById('loginEmail');
  var campoSenha = document.getElementById('loginSenha');
  var botaoEntrar = document.getElementById('loginButton');
  var botaoRecuperar = document.getElementById('forgotButton');
  var msg = document.getElementById('loginMsg');
  var togglePassword = document.getElementById('togglePassword');
  var overlay = document.getElementById('companyChooser');
  var companyList = document.getElementById('companyList');
  var companyCancel = document.getElementById('companyCancel');

  function mostrar(texto, erro) {
    msg.textContent = texto || '';
    msg.className = 'msg' + (texto ? (erro ? ' erro' : ' ok') : '');
  }

  if (!cfg || !window.supabase) {
    mostrar('Não foi possível iniciar o login.', true);
    return;
  }

  var supa = window.supabase.createClient(cfg.supabaseUrl, cfg.supabaseAnonKey);

  function emailFantasmaCliente(nif, adminId) {
    var limpo = String(nif || '').trim().toLowerCase().replace(/[^a-z0-9]/g, '');
    var empresaCurta = String(adminId || '').trim().toLowerCase().replace(/[^a-z0-9]/g, '').slice(0, 12);
    return limpo + (empresaCurta ? '.' + empresaCurta : '') + '@clientes.totalgest.pt';
  }

  function escolherEmpresa(empresas) {
    return new Promise(function (resolve) {
      companyList.innerHTML = '';
      overlay.hidden = false;

      function fechar(valor) {
        overlay.hidden = true;
        companyList.innerHTML = '';
        companyCancel.onclick = null;
        resolve(valor || null);
      }

      (empresas || []).forEach(function (emp) {
        var b = document.createElement('button');
        b.type = 'button';
        b.className = 'company-option';
        b.textContent = emp.nome || 'Empresa';
        b.onclick = function () { fechar(emp.adminId); };
        companyList.appendChild(b);
      });

      companyCancel.onclick = function () { fechar(null); };
    });
  }

  async function resolverUtilizador(valor) {
    var utilizador = valor.trim();
    if (utilizador.includes('@')) return utilizador.toLowerCase();

    var resposta = await supa.functions.invoke('resolver-login-cliente', { body: { nif: utilizador } });
    var resolucao = resposta.data;
    if (resposta.error || !resolucao || resolucao.situacao === 'nenhuma') {
      throw new Error('Credenciais inválidas ou conta sem acesso.');
    }

    if (resolucao.situacao === 'varias') {
      var adminId = await escolherEmpresa(resolucao.empresas || []);
      if (!adminId) return null;
      return emailFantasmaCliente(utilizador, adminId);
    }

    return resolucao.emailTecnico;
  }

  async function entrar(ev) {
    ev.preventDefault();
    mostrar('');
    var valor = campoUtilizador.value.trim();
    var senha = campoSenha.value;
    if (!valor || !senha) {
      mostrar('Indique email (ou NIF, para clientes) e palavra-passe.', true);
      return;
    }

    botaoEntrar.disabled = true;
    botaoEntrar.textContent = 'A entrar…';

    try {
      var email = await resolverUtilizador(valor);
      if (!email) return;
      var resultado = await supa.auth.signInWithPassword({ email: email.toLowerCase(), password: senha });
      if (resultado.error || !resultado.data || !resultado.data.user) {
        throw new Error('Credenciais inválidas ou conta sem acesso.');
      }
      mostrar('Sessão iniciada. A abrir a aplicação…', false);
      window.location.replace(cfg.appUrl);
    } catch (e) {
      mostrar((e && e.message) || 'Não foi possível iniciar sessão.', true);
    } finally {
      botaoEntrar.disabled = false;
      botaoEntrar.textContent = 'Entrar';
    }
  }

  async function recuperarPassword() {
    mostrar('');
    var valor = campoUtilizador.value.trim();
    if (!valor) {
      mostrar('Escreva primeiro o email ou NIF.', true);
      campoUtilizador.focus();
      return;
    }

    botaoRecuperar.disabled = true;
    try {
      if (!valor.includes('@')) {
        var emailReal = window.prompt('Indique o email registado na ficha de cliente para confirmar a recuperação:');
        if (!emailReal || !emailReal.trim()) return;
        var resCliente = await supa.functions.invoke('recuperar-password-cliente', {
          body: { nif: valor, email: emailReal.trim().toLowerCase() }
        });
        if (resCliente.error) throw resCliente.error;
        mostrar((resCliente.data && resCliente.data.mensagem) || 'Se os dados corresponderem a um Portal ativo, foi enviado um link de recuperação.', false);
        return;
      }

      var resEmail = await supa.functions.invoke('recuperar-password', { body: { email: valor.toLowerCase() } });
      if (resEmail.error) throw resEmail.error;
      mostrar((resEmail.data && resEmail.data.mensagem) || 'Se existir uma conta com esse email, foi enviado um link de recuperação.', false);
    } catch (e) {
      mostrar('Não foi possível pedir a recuperação. Tente novamente mais tarde.', true);
    } finally {
      botaoRecuperar.disabled = false;
    }
  }

  togglePassword.addEventListener('click', function () {
    var visivel = campoSenha.type === 'text';
    campoSenha.type = visivel ? 'password' : 'text';
    togglePassword.textContent = visivel ? '👁' : '🙈';
    togglePassword.setAttribute('aria-label', visivel ? 'Mostrar palavra-passe' : 'Ocultar palavra-passe');
  });

  form.addEventListener('submit', entrar);
  botaoRecuperar.addEventListener('click', recuperarPassword);

  supa.auth.getSession().then(function (resultado) {
    if (resultado && resultado.data && resultado.data.session) {
      window.location.replace(cfg.appUrl);
    }
  }).catch(function () {});
})();
