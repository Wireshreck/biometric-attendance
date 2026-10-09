/* App-shell service worker: lets an already-visited console render its
 * shell while the backend is unreachable so queued check-ins stay usable.
 * API calls are network-first (never served stale); only the static shell
 * (HTML/CSS/JS) is cached. First visit still requires the server. */
const CACHE = 'attendance-shell-v1';
const SHELL = [
  './',
  './index.html',
  './styles.css',
  './api.js',
  './offline.js',
  './app.js',
  './ble.js',
  './vendor/ble_protocol.js',
];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE).then((cache) => cache.addAll(SHELL)).then(() => self.skipWaiting()),
  );
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys()
      .then((keys) => Promise.all(keys.filter((k) => k !== CACHE).map((k) => caches.delete(k))))
      .then(() => self.clients.claim()),
  );
});

self.addEventListener('fetch', (event) => {
  const url = new URL(event.request.url);
  if (url.pathname.startsWith('/api/') || url.pathname === '/health') {
    // Attendance data must never be served stale.
    event.respondWith(fetch(event.request));
    return;
  }
  event.respondWith(
    fetch(event.request)
      .then((res) => {
        const copy = res.clone();
        caches.open(CACHE).then((cache) => cache.put(event.request, copy));
        return res;
      })
      .catch(() => caches.match(event.request).then((hit) => hit || caches.match('./index.html'))),
  );
});
