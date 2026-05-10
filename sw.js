const CACHE_NAME = 'wa-scheduler-v2';
const ASSETS = ['./index.html', './manifest.json'];

// ── INSTALL: cache assets ──
self.addEventListener('install', e => {
  e.waitUntil(caches.open(CACHE_NAME).then(c => c.addAll(ASSETS)));
  self.skipWaiting();
});

// ── ACTIVATE: clean old caches ──
self.addEventListener('activate', e => {
  e.waitUntil(
    caches.keys().then(keys =>
      Promise.all(keys.filter(k => k !== CACHE_NAME).map(k => caches.delete(k)))
    )
  );
  self.clients.claim();
});

// ── FETCH: serve from cache, fallback to network ──
self.addEventListener('fetch', e => {
  e.respondWith(
    caches.match(e.request).then(r => r || fetch(e.request).catch(() => caches.match('./index.html')))
  );
});

// ── PUSH NOTIFICATION (from main thread via postMessage) ──
self.addEventListener('message', e => {
  if (e.data && e.data.type === 'SHOW_NOTIFICATION') {
    const { title, body, tag, data } = e.data;
    self.registration.showNotification(title, {
      body,
      tag,
      data,
      icon: './icon-192.png',
      badge: './icon-192.png',
      vibrate: [200, 100, 200, 100, 200],
      requireInteraction: true,
      actions: [
        { action: 'open', title: '📱 Abrir WhatsApp' },
        { action: 'dismiss', title: 'Descartar' }
      ]
    });
  }
});

// ── NOTIFICATION CLICK ──
self.addEventListener('notificationclick', e => {
  e.notification.close();
  const { phone, text } = e.notification.data || {};
  if (e.action === 'open' || !e.action) {
    const url = phone
      ? `https://wa.me/${phone}?text=${encodeURIComponent(text || '')}`
      : './index.html';
    e.waitUntil(
      clients.matchAll({ type: 'window', includeUncontrolled: true }).then(list => {
        for (const client of list) {
          if ('focus' in client) { client.focus(); return; }
        }
        return clients.openWindow(url);
      })
    );
  }
});

// ── BACKGROUND SYNC: check scheduled messages every minute ──
self.addEventListener('periodicsync', e => {
  if (e.tag === 'check-messages') {
    e.waitUntil(checkScheduled());
  }
});

async function checkScheduled() {
  // This fires even when app is closed (Android only, if Periodic Background Sync granted)
  const allClients = await clients.matchAll({ includeUncontrolled: true });
  allClients.forEach(c => c.postMessage({ type: 'CHECK_MESSAGES' }));
}
