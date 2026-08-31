// Service Worker — Total Gest PWA
const CACHE = 'totalgest-v92';
const ASSETS = [
  './index.html',
  './app.html',
  './login.html',
  './registar.html',
  './styles.css',
  './assets/css/app.css',
  './assets/css/index.css',
  './assets/css/social-proof.css',
  './assets/css/login.css',
  './assets/css/registar.css',
  './assets/js/index.js',
  './assets/js/auth-config.js',
  './assets/js/login.js',
  './assets/js/registar.js',
  './assets/js/app-shell.js',
  './assets/js/app-pwa.js',
  './assets/js/app-toast.js',
  './assets/js/app-ui.js',
  './assets/js/app-dialogs.js',
  './assets/js/app-cache.js',
  './assets/js/app-connectivity.js',
  './assets/js/app-sync-status.js',
  './assets/js/app-sync-helpers.js',
  './assets/js/app-sync-diff.js',
  './assets/js/app-sync-snapshots.js',
  './assets/js/app-sync-pending.js',
  './assets/js/app-period-loading.js',
  './assets/js/app-load-context.js',
  './assets/js/app-load-queries.js',
  './assets/js/app-load-transform.js',
  './assets/js/app-load-orchestrator.js',
  './assets/js/app-modal-funcionario.js',
  './assets/js/app-modal-cliente.js',
  './assets/js/app-modal-fornecedor.js',
  './assets/js/app-modal-requisicao.js',
  './assets/js/app-modal-artigo.js',
  './assets/js/app-modal-folha.js',
  './assets/js/app-modal-servico.js',
  './assets/js/app-modal-obra.js',
  './assets/js/app-save-form-fornecedor.js',
  './assets/js/app-save-form-artigo.js',
  './assets/js/app-save-form-requisicao.js',
  './assets/js/app-save-form-obra.js',
  './assets/js/app-save-form-folha-context.js',
  './assets/js/app-save-form-folha-signature.js',
  './assets/js/app-save-form-folha-object.js',
  './assets/js/app-save-form-folha-assist.js',
  './assets/js/app-save-form-folha-consumos.js',
  './assets/js/app-save-form-folha-manutencao.js',
  './assets/js/app-save-form-folha-ponto.js',
  './assets/js/app-save-form-folha.js',
  './assets/js/app-save-form-cliente.js',
  './assets/js/app-save-form-funcionario.js',
  './assets/js/app-save-form-funcionario-encarregado.js',
  './assets/js/app-save-form-funcionario-orchestrator.js',
  './assets/js/app-save-form-servico-validation.js',
  './assets/js/app-save-form-servico-context.js',
  './assets/js/app-save-form-servico-object.js',
  './assets/js/app-save-form-servico-conflicts.js',
  './assets/js/app-save-form-servico-registration.js',
  './assets/js/app-save-form-servico.js',
  './assets/js/app-save-form-persist.js',
  './assets/js/app-save-form-servico-notifications.js',
  './assets/js/app-save-form-folha-usage.js',
  './assets/js/app-save-form-folha-os-pending.js',
  './assets/js/app-save-form-folha-obra-pending.js',
  './assets/js/app-save-form-finalize.js',
  './assets/js/app-save-form-auth.js',
  './assets/js/app-save-form-contact-validation.js',
  './assets/js/app-save-form-dispatch.js',
  './assets/js/app-save-form-post-persist.js',
  './assets/js/app-profile-modal-superadmin.js',
  './assets/js/app-profile-modal-distributor.js',
  './assets/js/app-profile-modal-admin.js',
  './assets/js/app-profile-modal-worker.js',
  './assets/js/app-profile-modal.js',
  './assets/js/app-profile-helpers.js',
  './assets/js/app-profile-save-superadmin.js',
  './assets/js/app-profile-save-distributor.js',
  './assets/js/app-profile-save-admin.js',
  './assets/js/app-profile-save-worker.js',
  './assets/js/app-profile-save.js',
  './assets/js/app-sync-prepare.js',
  './assets/js/app-sync-files.js',
  './assets/js/app-sync-collections.js',
  './assets/js/app-sync-orchestrator.js',
  './assets/js/app-sync-finalize.js',
  './assets/js/app-sync-upsert.js',
  './assets/js/app-sync-licenses.js',
  './assets/js/app-sync-encarregados.js',
  './assets/js/app-sync-delete.js',
  './assets/js/app-save-queue.js',
  './assets/js/app-bootstrap.js',
  './manifest.json',
  './logo-totalgest.png',
  './icon-192.png',
  './icon-512.png',
  './apple-touch-icon.png'
];

self.addEventListener('install', e => {
  e.waitUntil(caches.open(CACHE).then(c => c.addAll(ASSETS).catch(() => {})));
  self.skipWaiting();
});

self.addEventListener('activate', e => {
  e.waitUntil(
    caches.keys()
      .then(keys => Promise.all(keys.filter(k => k !== CACHE).map(k => caches.delete(k))))
      .then(() => self.clients.claim())
      .then(() => self.clients.matchAll({ type: 'window' }))
      .then(clientsList => {
        clientsList.forEach(client => client.postMessage({ type: 'SW_UPDATED' }));
      })
  );
});

self.addEventListener('fetch', e => {
  const req = e.request;
  if (req.method !== 'GET') return;

  e.respondWith(
    fetch(req).then(res => {
      try {
        if (new URL(req.url).origin === location.origin && res && res.ok) {
          const copy = res.clone();
          caches.open(CACHE).then(c => c.put(req, copy)).catch(() => {});
        }
      } catch (err) {}
      return res;
    }).catch(() => {
      if (req.mode === 'navigate') {
        const path = new URL(req.url).pathname;
        if (path === '/' || path.endsWith('/index.html')) {
          return caches.match('./index.html');
        }
        if (path.endsWith('/login.html')) {
          return caches.match('./login.html').then(r => r || caches.match('./index.html'));
        }
        if (path.endsWith('/registar.html')) {
          return caches.match('./registar.html').then(r => r || caches.match('./index.html'));
        }
        return caches.match('./app.html').then(r => r || caches.match('./login.html'));
      }
      return caches.match(req);
    })
  );
});

// ===== Notificações push =====
self.addEventListener('push', e => {
  let dados = {};
  try { dados = e.data ? e.data.json() : {}; } catch (err) { dados = { titulo: 'Total Gest', corpo: e.data ? e.data.text() : '' }; }

  const titulo = dados.titulo || dados.title || 'Total Gest';
  const iconePersonalizado = dados.icone || dados.icon || dados.logo_url || '';
  const opcoes = {
    body: dados.corpo || dados.body || '',
    icon: iconePersonalizado || './icon-192.png',
    badge: './icon-192.png',
    tag: dados.tag || 'totalgest-notificacao',
    renotify: true,
    data: { url: dados.url || './app.html' },
    vibrate: [120, 60, 120]
  };

  e.waitUntil(self.registration.showNotification(titulo, opcoes));
});

self.addEventListener('notificationclick', e => {
  e.notification.close();
  const url = (e.notification.data && e.notification.data.url) || './app.html';

  e.waitUntil(
    self.clients.matchAll({ type: 'window', includeUncontrolled: true }).then(clientsList => {
      for (const client of clientsList) {
        if (client.url.includes(location.origin) && 'focus' in client) {
          return client.focus();
        }
      }
      if (self.clients.openWindow) return self.clients.openWindow(url);
    })
  );
});
