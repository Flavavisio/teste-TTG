(function(){
  'use strict';

  var cfg=window.TG_AUTH_CONFIG;
  var form=document.getElementById('signupForm');
  var btn=document.getElementById('signupButton');
  var status=document.getElementById('signupStatus');
  var passwordMsg=document.getElementById('passwordMsg');
  if(!cfg||!window.supabase||!form)return;

  var supa=window.supabase.createClient(cfg.supabaseUrl,cfg.supabaseAnonKey);

  function senhaValida(senha){
    return String(senha||'').length>=9&&/[A-Z]/.test(senha)&&/[^A-Za-z0-9]/.test(senha);
  }

  function validarPasswords(){
    var s1=document.getElementById('su_senha').value;
    var s2=document.getElementById('su_senha2').value;
    passwordMsg.className='password-msg';
    if(!s1){passwordMsg.textContent='';return false;}
    if(!senhaValida(s1)){
      passwordMsg.textContent='Precisa de pelo menos 9 caracteres, 1 maiúscula e 1 símbolo (ex: ! @ # $ %).';
      passwordMsg.classList.add('error');
      return false;
    }
    if(s2&&s1!==s2){
      passwordMsg.textContent='As palavras-passe não coincidem.';
      passwordMsg.classList.add('error');
      return false;
    }
    if(s2&&s1===s2){
      passwordMsg.textContent='Palavra-passe válida e confirmada.';
      passwordMsg.classList.add('ok');
      return true;
    }
    passwordMsg.textContent='Agora repita a palavra-passe.';
    return false;
  }

  function mostrarEstado(msg,tipo){
    status.textContent=msg||'';
    status.className='status'+(tipo?' '+tipo:'');
  }

  function alternarPassword(id,button){
    var campo=document.getElementById(id);
    if(!campo)return;
    var mostrar=campo.type==='password';
    campo.type=mostrar?'text':'password';
    button.textContent=mostrar?'🙈':'👁';
    button.setAttribute('aria-label',mostrar?'Ocultar palavra-passe':'Mostrar palavra-passe');
  }

  document.querySelectorAll('[data-toggle-password]').forEach(function(button){
    button.addEventListener('click',function(){alternarPassword(button.getAttribute('data-toggle-password'),button);});
  });
  document.getElementById('su_senha').addEventListener('input',validarPasswords);
  document.getElementById('su_senha2').addEventListener('input',validarPasswords);
  document.getElementById('su_nif').addEventListener('input',function(e){e.target.value=e.target.value.replace(/\D/g,'').slice(0,9);});

  async function extrairMensagemErro(error){
    if(!error)return '';
    try{
      if(error.context&&typeof error.context.json==='function'){
        var corpo=await error.context.json();
        if(corpo&&corpo.erro)return corpo.erro;
      }
    }catch(e){}
    return error.message||'';
  }

  form.addEventListener('submit',async function(e){
    e.preventDefault();
    mostrarEstado('','');

    var dados={
      empresa:document.getElementById('su_empresa').value.trim(),
      nome:document.getElementById('su_nome').value.trim(),
      email:document.getElementById('su_email').value.trim().toLowerCase(),
      telefone:document.getElementById('su_telefone').value.trim(),
      colaboradores:document.getElementById('su_colaboradores').value.trim(),
      nif:document.getElementById('su_nif').value.trim(),
      senha:document.getElementById('su_senha').value
    };
    var senha2=document.getElementById('su_senha2').value;

    if(!dados.empresa||!dados.nome||!dados.email||!dados.telefone||!dados.colaboradores||!dados.nif){
      mostrarEstado('Preencha todos os campos para continuar.','error');
      return;
    }
    if(dados.nif.length!==9){
      mostrarEstado('O NIF deve ter 9 dígitos.','error');
      return;
    }
    if(!senhaValida(dados.senha)){
      mostrarEstado('A palavra-passe precisa de pelo menos 9 caracteres, 1 maiúscula e 1 símbolo.','error');
      return;
    }
    if(dados.senha!==senha2){
      mostrarEstado('As palavras-passe não coincidem.','error');
      return;
    }

    btn.disabled=true;
    btn.textContent='A criar o seu teste…';
    try{
      var resposta=await supa.functions.invoke('criar_pedido_trial',{body:dados});
      if(resposta.error){
        var mensagem=await extrairMensagemErro(resposta.error);
        throw new Error(mensagem||'Não foi possível enviar o pedido. Tente novamente.');
      }
      if(!resposta.data||resposta.data.erro)throw new Error((resposta.data&&resposta.data.erro)||'Falha ao criar o pedido.');

      form.innerHTML='<div class="success"><div class="success-icon">✓</div><h2>Confirme o seu email</h2><p>Enviámos um link de confirmação para <strong>'+dados.email.replace(/[&<>"']/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c];})+'</strong>. Assim que confirmar, a sua conta fica ativa com <strong>14 dias gratuitos</strong>.</p><a href="login.html">Já confirmou? Entrar no Total Gest →</a></div>';
      mostrarEstado('','');
    }catch(err){
      console.error('registo trial:',err);
      mostrarEstado(err&&err.message?err.message:'Não foi possível enviar o pedido. Tente novamente.','error');
      btn.disabled=false;
      btn.textContent='Começar 14 dias grátis';
    }
  });
})();