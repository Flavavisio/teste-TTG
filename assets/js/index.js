(function(){
  'use strict';

  function carregarTemaMarca() {
    if (document.querySelector('link[data-tg-brand-theme]')) return;
    const link = document.createElement('link');
    link.rel = 'stylesheet';
    link.href = './assets/css/brand-theme.css';
    link.dataset.tgBrandTheme = '1';
    document.head.appendChild(link);
    const meta = document.querySelector('meta[name="theme-color"]');
    if (meta) meta.setAttribute('content', '#243B8F');
  }

  carregarTemaMarca();

  var ano=document.getElementById('ano');
  if(ano)ano.textContent=new Date().getFullYear();

  document.querySelectorAll('a[href^="#"]').forEach(function(a){
    a.addEventListener('click',function(e){
      var id=a.getAttribute('href');
      if(!id||id==='#')return;
      var alvo=document.querySelector(id);
      if(alvo){
        e.preventDefault();
        alvo.scrollIntoView({behavior:'smooth',block:'start'});
      }
    });
  });

  // Durante a separação da landing, os CTAs de trial ainda estavam apontados
  // para WhatsApp. Encaminha apenas esses CTAs para o registo próprio; o CTA
  // de demonstração/contacto mantém-se no WhatsApp.
  document.querySelectorAll('a[href*="wa.me"]').forEach(function(a){
    var href=a.getAttribute('href')||'';
    var texto=(a.textContent||'').toLowerCase();
    var ehTrial=href.indexOf('14')!==-1&&(texto.indexOf('14')!==-1||href.toLowerCase().indexOf('experimentar')!==-1||href.toLowerCase().indexOf('ativar')!==-1);
    if(!ehTrial)return;
    a.setAttribute('href','registar.html');
    a.removeAttribute('target');
    a.removeAttribute('rel');
  });
})();