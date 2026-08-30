// Service Worker — Total Gest PWA
const CACHE = 'totalgest-v19';
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
  './assets/js/app-connectivity.js',
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
