var SUPABASE_URL = 'https://rfniufasivfnrqfntzog.supabase.co';
var SUPABASE_ANON_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJmbml1ZmFzaXZmbnJxZm50em9nIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODE4NzI2MjcsImV4cCI6MjA5NzQ0ODYyN30.1hJ7JBpCKo-Wp93HM5skXVnYk3ghyC7mo0rubbvCXyI';
var supa = window.supabase.createClient(SUPABASE_URL, SUPABASE_ANON_KEY);
var cartao = document.getElementById('cartao');

function senhaValida(s) {
  return s.length >= 9 && /[A-Z]/.test(s) && /[^A-Za-z0-9]/.test(s);
}

function mostrarErro(titulo, mensagem) {
  cartao.innerHTML =
    '<div class="dominio">🔒 totalgest.pt</div>' +
    '<img class="logo" src="logo-totalgest.png" alt="Total Gest" />' +
    '<h1 class="erro">' + titulo + '</h1>' +
    '<p>' + mensagem + '</p>' +
    '<a class="botao" href="login.html">Voltar ao login</a>';
}

function mostrarFormulario() {
  cartao.innerHTML =
    '<div class="dominio">🔒 totalgest.pt</div>' +
    '<img class="logo" src="logo-totalgest.png" alt="Total Gest" />' +
    '<h1>Defina a sua nova password</h1>' +
    '<p>Escolha uma password segura para a sua conta.</p>' +
    '<div class="campo">' +
      '<label>Nova password</label>' +
      '<input type="password" id="rp_senha" placeholder="Mínimo 9 caracteres, 1 maiúscula, 1 símbolo" />' +
      '<button type="button" id="rp_olho1">👁</button>' +
    '</div>' +
    '<div class="campo">' +
      '<label>Confirmar password</label>' +
      '<input type="password" id="rp_senha2" placeholder="Repita a password" />' +
      '<button type="button" id="rp_olho2">👁</button>' +
    '</div>' +
    '<div class="msg" id="rp_msg"></div>' +
    '<button class="botao" id="rp_botao">Guardar nova password</button>';

  function alternarOlho(idCampo, btn) {
    var campo = document.getElementById(idCampo);
    if (campo.type === 'password') { campo.type = 'text'; btn.textContent = '🙈'; }
    else { campo.type = 'password'; btn.textContent = '👁'; }
  }
  document.getElementById('rp_olho1').onclick = function () { alternarOlho('rp_senha', this); };
  document.getElementById('rp_olho2').onclick = function () { alternarOlho('rp_senha2', this); };

  function validar() {
    var s1 = document.getElementById('rp_senha').value;
    var s2 = document.getElementById('rp_senha2').value;
    var msg = document.getElementById('rp_msg');
    if (!s1) { msg.textContent = ''; return; }
    if (!senhaValida(s1)) {
      msg.textContent = 'Precisa de pelo menos 9 caracteres, 1 maiúscula e 1 símbolo.';
      msg.style.color = '#dc2626';
      return;
    }
    if (s2 && s1 !== s2) {
      msg.textContent = 'As passwords não coincidem.';
      msg.style.color = '#dc2626';
      return;
    }
    msg.textContent = s2 ? '✓ Password válida.' : 'Password válida — confirme-a abaixo.';
    msg.style.color = '#16a34a';
  }
  document.getElementById('rp_senha').addEventListener('input', validar);
  document.getElementById('rp_senha2').addEventListener('input', validar);

  document.getElementById('rp_botao').onclick = async function () {
    var s1 = document.getElementById('rp_senha').value;
    var s2 = document.getElementById('rp_senha2').value;
    if (!senhaValida(s1)) { alert('A password precisa de pelo menos 9 caracteres, 1 maiúscula e 1 símbolo.'); return; }
    if (s1 !== s2) { alert('As passwords não coincidem.'); return; }
    var btn = document.getElementById('rp_botao');
    btn.disabled = true;
    btn.textContent = 'A guardar…';
    try {
      var { error } = await supa.auth.updateUser({ password: s1 });
      if (error) throw error;
      cartao.innerHTML =
        '<div class="dominio">🔒 totalgest.pt</div>' +
        '<img class="logo" src="logo-totalgest.png" alt="Total Gest" />' +
        '<div class="selo">✓ Password alterada</div>' +
        '<h1 class="ok">Tudo pronto!</h1>' +
        '<p>A sua password foi alterada com sucesso. Já pode entrar com a nova password.</p>' +
        '<a class="botao" href="login.html">Ir para o login</a>';
    } catch (e) {
      alert('Não foi possível guardar a nova password: ' + (e && e.message ? e.message : 'tente novamente.'));
      btn.disabled = false;
      btn.textContent = 'Guardar nova password';
    }
  };
}

var jaMostrou = false;
supa.auth.onAuthStateChange(function (evento, sessao) {
  if (evento === 'PASSWORD_RECOVERY' && !jaMostrou) {
    jaMostrou = true;
    mostrarFormulario();
  }
});

setTimeout(function () {
  if (!jaMostrou) {
    mostrarErro('Link inválido ou expirado', 'Este link de recuperação já não é válido. Volte ao site e peça um novo através de "Esqueci-me da password".');
  }
}, 4000);
